import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/components/providers";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "FilmMatch AI — AI-Powered Movie Recommendations",
    template: "%s | FilmMatch AI",
  },
  description:
    "Tell us your mood and genre preferences. Our AI finds the perfect film for solo or group viewing in seconds.",
  metadataBase: new URL("https://filmmatch.ai"),
  openGraph: {
    title: "FilmMatch AI",
    description:
      "AI-powered movie picks for solo or group viewing. No more arguing over what to watch.",
    siteName: "FilmMatch AI",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "FilmMatch AI",
    description: "AI-powered movie picks — solo or with friends.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: "#0A0A0F",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`dark ${inter.variable}`}>
      <body className="min-h-screen bg-bg-primary antialiased font-sans">
        <Providers>
          {/* Skip to content link for keyboard users */}
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[100] focus:px-4 focus:py-2 focus:bg-accent focus:text-white focus:rounded-lg focus:text-sm focus:font-medium"
          >
            Skip to content
          </a>
          <main id="main-content" className="pb-20 md:pb-0" tabIndex={-1}>
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
