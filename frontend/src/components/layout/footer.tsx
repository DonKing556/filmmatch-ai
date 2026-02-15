import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-glass-border bg-bg-secondary/30 pb-20 md:pb-0">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold bg-gradient-to-r from-accent to-accent-secondary bg-clip-text text-transparent">
              FilmMatch AI
            </span>
            <span className="text-xs text-text-tertiary">
              &copy; {new Date().getFullYear()}
            </span>
          </div>

          <nav
            className="flex items-center gap-6 text-sm text-text-tertiary"
            aria-label="Footer"
          >
            <Link href="/privacy" className="hover:text-text-secondary transition-colors">
              Privacy Policy
            </Link>
            <Link href="/terms" className="hover:text-text-secondary transition-colors">
              Terms of Service
            </Link>
          </nav>

          <p className="text-xs text-text-tertiary">
            Movie data from{" "}
            <a
              href="https://www.themoviedb.org/"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-text-secondary transition-colors"
            >
              TMDB
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}
