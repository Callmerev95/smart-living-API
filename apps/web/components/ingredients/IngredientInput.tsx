"use client";

import { useState, type FormEvent, type KeyboardEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { INPUT_LIMITS, content, fill } from "@/lib/constants/content";

type IngredientInputProps = {
  onSubmit: (ingredients: string[]) => void;
  loading?: boolean;
};

/** Pecah teks bebas menjadi daftar bahan. Normalisasi canonical adalah tugas server. */
export function parseIngredients(raw: string): string[] {
  return raw
    .split(/[,\n]/)
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
}

/** Validasi UI ringan (`docs/content-schema.md` §B.9). Server tetap memvalidasi ulang. */
export function validateIngredients(ingredients: string[]): string | null {
  if (ingredients.length === 0) return content.input.validation.empty;

  if (ingredients.length > INPUT_LIMITS.maxIngredients) {
    return fill(content.input.validation.tooMany, { max: INPUT_LIMITS.maxIngredients });
  }

  if (ingredients.some((item) => item.length > INPUT_LIMITS.maxNameLength)) {
    return content.input.validation.tooLong;
  }

  return null;
}

/**
 * Input bahan comma-separated (`docs/component-architecture.md` §6).
 *
 * Component ini tidak memanggil API dan tidak melakukan normalisasi canonical —
 * hanya memanggil `onSubmit` dengan daftar bahan mentah.
 */
export function IngredientInput({ onSubmit, loading = false }: IngredientInputProps) {
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(event?: FormEvent) {
    event?.preventDefault();

    const ingredients = parseIngredients(value);
    const validationError = validateIngredients(ingredients);

    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    onSubmit(ingredients);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      handleSubmit();
    }
  }

  function handleExample(example: string) {
    setValue(example);
    setError(null);
  }

  function handleClear() {
    setValue("");
    setError(null);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3" noValidate>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start">
        <div className="flex-1">
          <Input
            id="ingredient-input"
            label={content.input.label}
            placeholder={content.input.placeholder}
            helpText={content.input.helper}
            value={value}
            error={error}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={handleKeyDown}
            autoComplete="off"
          />
        </div>

        <div className="flex gap-2 sm:pt-7">
          <Button type="submit" loading={loading} onClick={() => handleSubmit()}>
            {loading ? content.input.submitLoading : content.input.submit}
          </Button>
          {value.length > 0 && (
            <Button variant="ghost" onClick={handleClear}>
              {content.input.clear}
            </Button>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-zinc-500">{content.input.exampleLabel}</span>
        {content.input.examples.map((example) => (
          <Button
            key={example}
            variant="secondary"
            className="px-2.5 py-1 text-xs"
            onClick={() => handleExample(example)}
          >
            {example}
          </Button>
        ))}
      </div>
    </form>
  );
}
