"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState, type ReactNode } from "react";
import { Toaster } from "sonner";
import { initAnalytics } from "@/lib/analytics";

export function Providers({ children }: { children: ReactNode }) {
  useEffect(() => {
    initAnalytics();
  }, []);

  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            background: "var(--color-bg-elevated)",
            border: "1px solid var(--color-glass-border)",
            color: "var(--color-text-primary)",
          },
        }}
      />
    </QueryClientProvider>
  );
}
