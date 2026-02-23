import axios from "axios";
import Cookies from "js-cookie";

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    headers: {
        "Content-Type": "application/json",
    },
});

// Request interceptor — attach auth token and org ID
api.interceptors.request.use((config) => {
    const token = Cookies.get("auth_token");
    const orgId = Cookies.get("org_id");

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    if (orgId) {
        config.headers["X-Org-Id"] = orgId;
    }
    return config;
});

// Response interceptor — handle 401
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            Cookies.remove("auth_token");
            Cookies.remove("org_id");
            if (typeof window !== "undefined") {
                window.location.href = "/auth/login";
            }
        }
        return Promise.reject(error);
    }
);

export default api;

// ─── API helpers ───
export const authAPI = {
    register: (data: { email: string; full_name: string; password: string }) =>
        api.post("/api/v1/users/register/", data),
    login: (data: { email: string; password: string }) =>
        api.post("/api/v1/auth/login/", data),
    me: () => api.get("/api/v1/users/me/"),
    updateMe: (data: Record<string, unknown>) =>
        api.patch("/api/v1/users/me/", data),
};

export const orgAPI = {
    list: () => api.get("/api/v1/users/orgs/"),
    create: (data: { name: string; niche?: string; description?: string }) =>
        api.post("/api/v1/users/orgs/", data),
    get: (id: string) => api.get(`/api/v1/users/orgs/${id}/`),
    update: (id: string, data: Record<string, unknown>) =>
        api.patch(`/api/v1/users/orgs/${id}/`, data),
    members: (id: string) => api.get(`/api/v1/users/orgs/${id}/members/`),
    invite: (id: string, data: { email: string; role?: string }) =>
        api.post(`/api/v1/users/orgs/${id}/invite/`, data),
};

export const agentAPI = {
    chat: (data: { message: string; conversation_id?: string }) =>
        api.post("/api/v1/agent/chat/", data),
    conversations: () => api.get("/api/v1/agent/conversations/"),
    conversation: (id: string) => api.get(`/api/v1/agent/conversations/${id}/`),
    config: () => api.get("/api/v1/agent/config/"),
    updateConfig: (data: Record<string, unknown>) =>
        api.patch("/api/v1/agent/config/", data),
};

export const sitesAPI = {
    list: () => api.get("/api/v1/sites/sites/"),
    create: (data: Record<string, unknown>) =>
        api.post("/api/v1/sites/sites/", data),
    get: (id: string) => api.get(`/api/v1/sites/sites/${id}/`),
    update: (id: string, data: Record<string, unknown>) =>
        api.patch(`/api/v1/sites/sites/${id}/`, data),
    publish: (id: string) => api.post(`/api/v1/sites/sites/${id}/publish/`),
    pages: (siteId: string) => api.get(`/api/v1/sites/sites/${siteId}/pages/`),
    templates: () => api.get("/api/v1/sites/templates/"),
};

export const crmAPI = {
    contacts: () => api.get("/api/v1/crm/contacts/"),
    createContact: (data: Record<string, unknown>) =>
        api.post("/api/v1/crm/contacts/", data),
    campaigns: () => api.get("/api/v1/crm/campaigns/"),
    deals: () => api.get("/api/v1/crm/deals/"),
};
