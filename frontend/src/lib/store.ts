import { create } from "zustand";
import { persist } from "zustand/middleware";
import Cookies from "js-cookie";
import api from "./api";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

export interface User {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    avatar_url?: string;
    is_staff: boolean;
}

export interface Org {
    id: string;
    name: string;
    slug: string;
    plan: string;
    logo_url?: string;
}

interface AuthState {
    /* state */
    user: User | null;
    org: Org | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;

    /* actions */
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
    setUser: (user: User) => void;
    setOrg: (org: Org) => void;
    setToken: (token: string) => void;
    hydrate: () => Promise<void>;
}

/* ------------------------------------------------------------------ */
/*  Store                                                              */
/* ------------------------------------------------------------------ */

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            org: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,

            login: async (email: string, password: string) => {
                set({ isLoading: true });
                try {
                    const { data } = await api.post("/api/v1/auth/login/", {
                        email,
                        password,
                    });
                    const token: string = data.token ?? data.key;
                    Cookies.set("auth_token", token, {
                        expires: 30,
                        sameSite: "lax",
                    });
                    set({
                        token,
                        user: data.user ?? null,
                        isAuthenticated: true,
                    });
                    // Fetch org if user has one
                    if (data.user?.default_org_id) {
                        const orgRes = await api.get(
                            `/api/v1/orgs/${data.user.default_org_id}/`
                        );
                        const org = orgRes.data;
                        Cookies.set("org_id", org.id, {
                            expires: 30,
                            sameSite: "lax",
                        });
                        set({ org });
                    }
                } finally {
                    set({ isLoading: false });
                }
            },

            logout: () => {
                Cookies.remove("auth_token");
                Cookies.remove("org_id");
                set({
                    user: null,
                    org: null,
                    token: null,
                    isAuthenticated: false,
                });
                if (typeof window !== "undefined") {
                    window.location.href = "/auth/login";
                }
            },

            setUser: (user: User) => set({ user }),
            setOrg: (org: Org) => {
                Cookies.set("org_id", org.id, {
                    expires: 30,
                    sameSite: "lax",
                });
                set({ org });
            },
            setToken: (token: string) => {
                Cookies.set("auth_token", token, {
                    expires: 30,
                    sameSite: "lax",
                });
                set({ token, isAuthenticated: true });
            },

            hydrate: async () => {
                const token = Cookies.get("auth_token");
                if (!token) {
                    set({ isAuthenticated: false });
                    return;
                }
                set({ isLoading: true, token, isAuthenticated: true });
                try {
                    const { data } = await api.get("/api/v1/auth/user/");
                    set({ user: data });
                    const orgId = Cookies.get("org_id");
                    if (orgId) {
                        const orgRes = await api.get(
                            `/api/v1/orgs/${orgId}/`
                        );
                        set({ org: orgRes.data });
                    }
                } catch {
                    // Token invalid — clear
                    Cookies.remove("auth_token");
                    Cookies.remove("org_id");
                    set({
                        user: null,
                        org: null,
                        token: null,
                        isAuthenticated: false,
                    });
                } finally {
                    set({ isLoading: false });
                }
            },
        }),
        {
            name: "agentbloom-auth",
            partialize: (state) => ({
                user: state.user,
                org: state.org,
                token: state.token,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
);
