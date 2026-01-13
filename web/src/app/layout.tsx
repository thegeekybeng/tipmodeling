import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TIPM - Trade & Industrial Policy Model",
  description:
    "Deterministic economic simulation engine for trade policy analysis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased font-sans">{children}</body>
    </html>
  );
}
