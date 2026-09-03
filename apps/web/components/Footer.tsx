import { REPO_URL } from "@/lib/constants/links";
import { content } from "@/lib/constants/content";

export function Footer() {
  return (
    <footer className="border-t border-zinc-200 py-6">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-2 px-6 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-zinc-600">{content.footer.tagline}</p>
        <a
          href={REPO_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-medium text-zinc-700 underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-500"
        >
          {content.footer.repoLabel}
        </a>
      </div>
    </footer>
  );
}
