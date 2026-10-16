import { NextResponse, type NextRequest } from "next/server";

const SESSION_COOKIE = "nt_session";

/**
 * İyimser kontrol: yalnızca cookie'nin varlığına bakar. Asıl doğrulama API'dedir;
 * süresi dolmuş bir cookie ile gelen istek 401 alır ve istemci girişe yönlendirir.
 */
export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const hasSession = request.cookies.has(SESSION_COOKIE);
  const isAuthPage = pathname === "/login" || pathname === "/register";

  if (!hasSession && !isAuthPage) {
    const url = new URL("/login", request.url);
    url.searchParams.set("next", pathname + search);
    return NextResponse.redirect(url);
  }
  if (hasSession && isAuthPage) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/subjects/:path*",
    "/messages/:path*",
    "/notifications/:path*",
    "/assistant/:path*",
    "/login",
    "/register",
  ],
};
