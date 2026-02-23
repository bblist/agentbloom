import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "sonner";
import { QueryProvider } from "@/lib/query-provider";
import { ThemeProvider } from "next-themes";

export const metadata: Metadata = {
    title: "AgentBloom — Speak it. Build it. Bloom.",
    description:
        "AI-powered business builder: websites, email, CRM, courses, bookings & more. Just tell our AI agent what you need.",
    icons: {
        icon: "/favicon.ico",
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body>
                <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
                    <QueryProvider>
                        {children}
                        <Toaster richColors position="top-right" />
                    </QueryProvider>
                </ThemeProvider>
            </body>
        </html>
    );
}
