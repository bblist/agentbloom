import { NextRequest, NextResponse } from "next/server";

/**
 * Next.js Edge Middleware — protects /dashboard/* routes.
 * Redirects unauthenticated users to /auth/login.
 */

const PUBLIC_PATHS = [
    "/",
    "/auth/login",
    "/auth/register",
    "/auth/forgot-password",
    "/auth/reset-password",
    "/api",           // NextJS API routes (if any)
];

function isPublic(pathname: string): boolean {
    return PUBLIC_PATHS.some(
        (p) => pathname === p || pathname.startsWith(p + "/")
    );
}

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // Allow public paths and static assets
    if (
        isPublic(pathname) ||
        pathname.startsWith("/_next") ||
        pathname.startsWith("/favicon") ||
        pathname.match(/\.(svg|png|jpg|ico|css|js|woff2?)$/)
    ) {
        return NextResponse.next();
    }

    // Check for auth token cookie
    const token = request.cookies.get("auth_token")?.value;

    if (!token) {
        const loginUrl = request.nextUrl.clone();
        loginUrl.pathname = "/auth/login";
        loginUrl.searchParams.set("next", pathname);
        return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next();
}

export const config = {
    matcher: [
        /*
         * Match all request paths except:
         * - _next/static (static files)
         * - _next/image (image optimization)
         * - favicon.ico
         */
        "/((?!_next/static|_next/image|favicon.ico).*)",
    ],
};
