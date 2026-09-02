import { content } from "@/lib/constants/content";
import type { ApiError, ErrorCode } from "@/types/api";

const DEFAULT_TIMEOUT_MS = 10_000;

/** Base URL API. Wajib dari env — tidak ada fallback hardcode ke production. */
function baseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!url) {
    throw new ApiClientError(
      "INTERNAL_ERROR",
      "NEXT_PUBLIC_API_BASE_URL belum diset.",
    );
  }
  return url.replace(/\/$/, "");
}

/**
 * Error yang sudah dipetakan ke pesan user.
 * `code` adalah kontrak stabil dari API; `userMessage` berasal dari `content.ts` (§B.8).
 */
export class ApiClientError extends Error {
  readonly code: ErrorCode | "NETWORK_ERROR" | "UNKNOWN_ERROR";
  readonly status: number | null;
  readonly userMessage: string;
  readonly details: unknown;

  constructor(
    code: ErrorCode | "NETWORK_ERROR" | "UNKNOWN_ERROR",
    developerMessage: string,
    options: { status?: number | null; details?: unknown } = {},
  ) {
    super(developerMessage);
    this.name = "ApiClientError";
    this.code = code;
    this.status = options.status ?? null;
    this.details = options.details ?? null;
    this.userMessage = userMessageFor(code);
  }
}

/** Petakan code API menjadi pesan yang layak dibaca user (§B.8). */
export function userMessageFor(code: string): string {
  const messages: Record<string, string> = content.errors;

  if (code === "NETWORK_ERROR") return content.errors.network;
  if (code in messages) return messages[code];
  return content.errors.unknown;
}

function isApiError(payload: unknown): payload is ApiError {
  if (typeof payload !== "object" || payload === null) return false;
  const candidate = payload as { error?: unknown };
  if (typeof candidate.error !== "object" || candidate.error === null) return false;
  return "code" in (candidate.error as object);
}

type RequestOptions = {
  method?: "GET" | "POST";
  body?: unknown;
  signal?: AbortSignal;
  timeoutMs?: number;
};

/**
 * Satu-satunya pintu HTTP ke Smart Living API.
 * Component tidak boleh menyusun URL sendiri (`docs/component-architecture.md` §11).
 */
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, signal, timeoutMs = DEFAULT_TIMEOUT_MS } = options;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  // Batalkan juga ketika caller membatalkan (mis. request baru menggantikan yang lama).
  const onAbort = () => controller.abort();
  signal?.addEventListener("abort", onAbort);

  let response: Response;
  try {
    response = await fetch(`${baseUrl()}${path}`, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
  } catch (cause) {
    throw new ApiClientError("NETWORK_ERROR", `Gagal menghubungi ${path}`, {
      details: cause instanceof Error ? cause.message : String(cause),
    });
  } finally {
    clearTimeout(timeout);
    signal?.removeEventListener("abort", onAbort);
  }

  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }

    if (isApiError(payload)) {
      const { code, message, details } = payload.error;
      throw new ApiClientError(code as ErrorCode, message, {
        status: response.status,
        details,
      });
    }

    throw new ApiClientError("UNKNOWN_ERROR", `HTTP ${response.status} pada ${path}`, {
      status: response.status,
    });
  }

  try {
    return (await response.json()) as T;
  } catch (cause) {
    throw new ApiClientError("UNKNOWN_ERROR", `Response ${path} bukan JSON valid`, {
      status: response.status,
      details: cause instanceof Error ? cause.message : String(cause),
    });
  }
}
