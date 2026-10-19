import type { NextRequest } from "next/server";

// API aynı origin'den sunulur; böylece oturum cookie'si httpOnly + SameSite=Lax kalabilir.
//
// next.config rewrites yerine route handler: harici rewrite'lar Next'in X-Forwarded-For
// eklediği adımdan önce yönlendirildiği için API istemcinin gerçek IP'sini göremiyordu
// (erişim günlüğü ve giriş hız sınırı buna bağlı). Route handler'a gelen istekte Next bu
// başlığı soket adresinden doldurur; burada olduğu gibi iletilir. Backend başlığa yalnızca
// frontend'den gelen isteklerde güvenir (docker-compose: FORWARDED_ALLOW_IPS).

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

// Bağlantıya özgü başlıklar iletilmez; gövde uzunluğunu fetch yeniden hesaplar.
const DROP_REQUEST = ["host", "connection", "keep-alive", "transfer-encoding", "upgrade", "te", "trailer", "content-length"];
// fetch yanıtı açılmış (sıkıştırması çözülmüş) gövdeyle döner.
const DROP_RESPONSE = ["content-encoding", "content-length", "transfer-encoding", "connection"];

async function forward(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const target = `${API_URL}/api/v1/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`;

  const headers = new Headers(request.headers);
  for (const name of DROP_REQUEST) headers.delete(name);
  const hasBody = request.method !== "GET" && request.method !== "HEAD";

  let upstream: Response;
  try {
    upstream = await fetch(target, {
      method: request.method,
      headers,
      body: hasBody ? await request.arrayBuffer() : undefined,
      redirect: "manual",
      cache: "no-store",
    });
  } catch {
    return Response.json({ detail: "API sunucusuna ulaşılamadı." }, { status: 502 });
  }

  const responseHeaders = new Headers(upstream.headers);
  for (const name of DROP_RESPONSE) responseHeaders.delete(name);
  return new Response(upstream.body, { status: upstream.status, statusText: upstream.statusText, headers: responseHeaders });
}

export { forward as DELETE, forward as GET, forward as PATCH, forward as POST, forward as PUT };
