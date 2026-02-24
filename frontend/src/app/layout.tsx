import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "sonner";
import { QueryProvider } from "@/lib/query-provider";
import { ThemeProvider } from "next-themes";
import { AuthProvider } from "@/components/auth-provider";
import { ErrorBoundary } from "@/components/error-boundary";
import { CookieConsent } from "@/components/cookie-consent";

export const metadata: Metadata = {
    title: "AgentBloom — Speak it. Build it. Bloom.",
    description:
        "AI-powered business builder: websites, email, CRM, courses, bookings & more. Just tell our AI agent what you need.",
    icons: {
        icon: "/favicon.ico",
    },
    metadataBase: new URL("https://bloom.nobleblocks.com"),
    openGraph: {
        title: "AgentBloom — Speak it. Build it. Bloom.",
        description: "AI-powered business builder: websites, email, CRM, courses, bookings & more.",
        type: "website",
        siteName: "AgentBloom",
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
                {/* Accessibility: skip to main content */}
                <a
                    href="#main-content"
                    className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[100] focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg"
                >
                    Skip to main content
                </a>
                <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
                    <QueryProvider>
                        <AuthProvider>
                            <ErrorBoundary>
                                <div id="main-content">
                                    {children}
                                </div>
                            </ErrorBoundary>
                        </AuthProvider>
                        <Toaster richColors position="top-right" />
                        <CookieConsent />
                    </QueryProvider>
                </ThemeProvider>
            </body>
        </html>
    );
}
