import type { Metadata, Viewport } from "next";
import { Providers } from "@/components/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "FilmMatch AI",
  description: "AI-powered movie recommendations for solo or group viewing",
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
    <html lang="en" className="dark">
      <body className="min-h-screen bg-bg-primary antialiased">
        <Providers>
          <main className="pb-20 md:pb-0">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
