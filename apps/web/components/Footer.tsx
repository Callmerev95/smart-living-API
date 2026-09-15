import { REPO_URL } from "@/lib/constants/links";
import { content } from "@/lib/constants/content";

export function Footer() {
  return (
    <footer className="border-t border-line py-8">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-3 px-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p className="flex items-center gap-2 text-sm text-ink-soft">
          <span aria-hidden="true" className="size-2 rounded-full bg-clay" />
          {content.footer.tagline}
        </p>
        <a
          href={REPO_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-medium text-ink underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-solid focus-visible:outline-turmeric"
        >
          {content.footer.repoLabel}
        </a>
      </div>
    </footer>
  );
}
