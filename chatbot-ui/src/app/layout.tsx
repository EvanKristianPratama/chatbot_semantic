import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "GadgetBot - Asisten Pencari Smartphone",
  description: "Temukan smartphone impianmu dengan AI semantik. Rekomendasi HP Samsung, Apple, Xiaomi, dan brand lainnya berdasarkan kebutuhan dan budget Anda.",
  keywords: ["smartphone", "gadget", "chatbot", "AI", "Samsung", "Apple", "Xiaomi", "rekomendasi HP"],
  authors: [{ name: "GadgetBot" }],
  openGraph: {
    title: "GadgetBot - Asisten Pencari Smartphone",
    description: "Temukan smartphone impianmu dengan AI semantik",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
        <meta name="theme-color" content="#ffffffff" />
      </head>
      <body className={`${inter.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
