"use client";

import * as Sentry from "@sentry/nextjs";
import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html lang="en">
      <body className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="text-center space-y-4">
          <h2 className="text-xl font-semibold text-white">
            Something went wrong
          </h2>
          <button
            onClick={reset}
            className="px-4 py-2 bg-accent text-white rounded-lg"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
