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
        api.post("/api/v1/auth/register/", data),
    login: (data: { email: string; password: string }) =>
        api.post("/api/v1/auth/login/", data),
    logout: () => api.post("/api/v1/auth/logout/"),
    refreshToken: () => api.post("/api/v1/auth/token/refresh/"),
    me: () => api.get("/api/v1/auth/me/"),
    updateMe: (data: Record<string, unknown>) =>
        api.patch("/api/v1/auth/me/", data),
};

export const orgAPI = {
    list: () => api.get("/api/v1/auth/orgs/"),
    create: (data: { name: string; niche?: string; description?: string }) =>
        api.post("/api/v1/auth/orgs/", data),
    get: (id: string) => api.get(`/api/v1/auth/orgs/${id}/`),
    update: (id: string, data: Record<string, unknown>) =>
        api.patch(`/api/v1/auth/orgs/${id}/`, data),
    members: (id: string) => api.get(`/api/v1/auth/orgs/${id}/members/`),
    invite: (id: string, data: { email: string; role?: string }) =>
        api.post(`/api/v1/auth/orgs/${id}/invite/`, data),
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
    contact: (id: string) => api.get(`/api/v1/crm/contacts/${id}/`),
    updateContact: (id: string, data: Record<string, unknown>) =>
        api.patch(`/api/v1/crm/contacts/${id}/`, data),
    deleteContact: (id: string) => api.delete(`/api/v1/crm/contacts/${id}/`),
    unsubscribe: (id: string) =>
        api.post(`/api/v1/crm/contacts/${id}/unsubscribe/`),
    importCSV: (file: File) => {
        const form = new FormData();
        form.append("file", file);
        return api.post("/api/v1/crm/contacts/import_csv/", form, {
            headers: { "Content-Type": "multipart/form-data" },
        });
    },
    segments: () => api.get("/api/v1/crm/segments/"),
    campaigns: () => api.get("/api/v1/crm/campaigns/"),
    campaign: (id: string) => api.get(`/api/v1/crm/campaigns/${id}/`),
    createCampaign: (data: Record<string, unknown>) =>
        api.post("/api/v1/crm/campaigns/", data),
    sendCampaign: (id: string) =>
        api.post(`/api/v1/crm/campaigns/${id}/send/`),
    deals: () => api.get("/api/v1/crm/deals/"),
    createDeal: (data: Record<string, unknown>) =>
        api.post("/api/v1/crm/deals/", data),
    templates: () => api.get("/api/v1/crm/email-templates/"),
};

export const coursesAPI = {
    list: () => api.get("/api/v1/courses/courses/"),
    get: (id: string) => api.get(`/api/v1/courses/courses/${id}/`),
    create: (data: Record<string, unknown>) =>
        api.post("/api/v1/courses/courses/", data),
    update: (id: string, data: Record<string, unknown>) =>
        api.patch(`/api/v1/courses/courses/${id}/`, data),
    delete: (id: string) => api.delete(`/api/v1/courses/courses/${id}/`),
    publish: (id: string) =>
        api.post(`/api/v1/courses/courses/${id}/publish/`),
    archive: (id: string) =>
        api.post(`/api/v1/courses/courses/${id}/archive/`),
    stats: (id: string) =>
        api.get(`/api/v1/courses/courses/${id}/stats/`),
    enrollments: () => api.get("/api/v1/courses/enrollments/"),
    announcements: () => api.get("/api/v1/courses/announcements/"),
};

export const bookingsAPI = {
    services: () => api.get("/api/v1/calendar/services/"),
    service: (id: string) => api.get(`/api/v1/calendar/services/${id}/`),
    createService: (data: Record<string, unknown>) =>
        api.post("/api/v1/calendar/services/", data),
    updateService: (id: string, data: Record<string, unknown>) =>
        api.patch(`/api/v1/calendar/services/${id}/`, data),
    availableSlots: (id: string, date: string) =>
        api.get(`/api/v1/calendar/services/${id}/available_slots/?date=${date}`),
    bookings: () => api.get("/api/v1/calendar/bookings/"),
    booking: (id: string) => api.get(`/api/v1/calendar/bookings/${id}/`),
    confirmBooking: (id: string) =>
        api.post(`/api/v1/calendar/bookings/${id}/confirm/`),
    cancelBooking: (id: string) =>
        api.post(`/api/v1/calendar/bookings/${id}/cancel/`),
    schedules: () => api.get("/api/v1/calendar/schedules/"),
    events: () => api.get("/api/v1/calendar/events/"),
};

export const paymentsAPI = {
    payments: () => api.get("/api/v1/payments/payments/"),
    summary: () => api.get("/api/v1/payments/payments/summary/"),
    products: () => api.get("/api/v1/payments/products/"),
    createProduct: (data: Record<string, unknown>) =>
        api.post("/api/v1/payments/products/", data),
    subscriptions: () => api.get("/api/v1/payments/subscriptions/"),
    invoices: () => api.get("/api/v1/payments/invoices/"),
    sendInvoice: (id: string) =>
        api.post(`/api/v1/payments/invoices/${id}/send_invoice/`),
    coupons: () => api.get("/api/v1/payments/coupons/"),
    refunds: () => api.get("/api/v1/payments/refunds/"),
    stripeConnection: () => api.get("/api/v1/payments/stripe-connection/"),
    onboardStripe: () =>
        api.post("/api/v1/payments/stripe-connection/onboard/"),
    revenue: () => api.get("/api/v1/payments/revenue-snapshots/"),
};

export const seoAPI = {
    settings: (siteId: string) =>
        api.get(`/api/v1/seo/settings/?site=${siteId}`),
    audits: () => api.get("/api/v1/seo/audits/"),
    runAudit: (siteId: string) =>
        api.post("/api/v1/seo/audits/run_audit/", { site_id: siteId }),
    keywords: () => api.get("/api/v1/seo/keywords/"),
    addKeywords: (data: { keywords: string[] }) =>
        api.post("/api/v1/seo/keywords/bulk_add/", data),
    generateSitemap: (siteId: string) =>
        api.post(`/api/v1/seo/settings/generate_sitemap/`, { site_id: siteId }),
    pageSpeed: () => api.get("/api/v1/seo/page-speed/"),
    linkSuggestions: () => api.get("/api/v1/seo/link-suggestions/"),
};

export const kbAPI = {
    documents: () => api.get("/api/v1/kb/documents/"),
    document: (id: string) => api.get(`/api/v1/kb/documents/${id}/`),
    uploadDocument: (file: File, title: string) => {
        const form = new FormData();
        form.append("file", file);
        form.append("title", title);
        return api.post("/api/v1/kb/documents/", form, {
            headers: { "Content-Type": "multipart/form-data" },
        });
    },
    deleteDocument: (id: string) => api.delete(`/api/v1/kb/documents/${id}/`),
    reprocessDocument: (id: string) =>
        api.post(`/api/v1/kb/documents/${id}/reprocess/`),
    sources: () => api.get("/api/v1/kb/sources/"),
    createSource: (data: Record<string, unknown>) =>
        api.post("/api/v1/kb/sources/", data),
    deleteSource: (id: string) => api.delete(`/api/v1/kb/sources/${id}/`),
    search: (query: string) =>
        api.get(`/api/v1/kb/search/?q=${encodeURIComponent(query)}`),
};

export const adminAPI = {
    featureFlags: () => api.get("/api/v1/admin-panel/feature-flags/"),
    updateFeatureFlag: (id: string, data: Record<string, unknown>) =>
        api.patch(`/api/v1/admin-panel/feature-flags/${id}/`, data),
    supportTickets: () => api.get("/api/v1/admin-panel/tickets/"),
    supportTicket: (id: string) =>
        api.get(`/api/v1/admin-panel/tickets/${id}/`),
    updateTicket: (id: string, data: Record<string, unknown>) =>
        api.patch(`/api/v1/admin-panel/tickets/${id}/`, data),
    assignTicket: (id: string, data: { assignee_id: string }) =>
        api.post(`/api/v1/admin-panel/tickets/${id}/assign/`, data),
    moderationQueue: () => api.get("/api/v1/admin-panel/moderation/"),
    moderateContent: (id: string, data: { action: string }) =>
        api.post(`/api/v1/admin-panel/moderation/${id}/moderate/`, data),
    systemHealth: () => api.get("/api/v1/admin-panel/system-health/"),
    auditLog: () => api.get("/api/v1/admin-panel/audit-log/"),
    revenue: () => api.get("/api/v1/admin-panel/revenue/"),
    users: () => api.get("/api/v1/admin-panel/users/"),
    impersonate: (userId: string) =>
        api.post(`/api/v1/admin-panel/users/${userId}/impersonate/`),
};

export const notificationsAPI = {
    list: () => api.get("/api/v1/notifications/"),
    markRead: (id: string) =>
        api.post(`/api/v1/notifications/${id}/read/`),
    markAllRead: () => api.post("/api/v1/notifications/read-all/"),
    preferences: () => api.get("/api/v1/notifications/preferences/"),
    updatePreferences: (data: Record<string, unknown>) =>
        api.patch("/api/v1/notifications/preferences/", data),
};

export const webhooksAPI = {
    list: () => api.get("/api/v1/webhooks/endpoints/"),
    create: (data: Record<string, unknown>) =>
        api.post("/api/v1/webhooks/endpoints/", data),
    get: (id: string) => api.get(`/api/v1/webhooks/endpoints/${id}/`),
    update: (id: string, data: Record<string, unknown>) =>
        api.patch(`/api/v1/webhooks/endpoints/${id}/`, data),
    delete: (id: string) => api.delete(`/api/v1/webhooks/endpoints/${id}/`),
    deliveries: (id: string) =>
        api.get(`/api/v1/webhooks/endpoints/${id}/deliveries/`),
    retryDelivery: (endpointId: string, deliveryId: string) =>
        api.post(`/api/v1/webhooks/endpoints/${endpointId}/deliveries/${deliveryId}/retry/`),
};
