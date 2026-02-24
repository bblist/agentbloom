"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/lib/store";

/**
 * Hydrates the auth store from cookies on mount.
 * Place this inside the root layout so it runs once on page load.
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
    const hydrate = useAuthStore((s) => s.hydrate);
    const isLoading = useAuthStore((s) => s.isLoading);

    useEffect(() => {
        hydrate();
    }, [hydrate]);

    // Optionally show a global loading screen on first hydration
    // For now, render children immediately and let pages handle loading
    return <>{children}</>;
}
