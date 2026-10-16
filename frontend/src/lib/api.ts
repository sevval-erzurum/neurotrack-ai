export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

type Detail = string | { msg: string; loc?: (string | number)[] }[] | undefined;

function describe(detail: Detail, status: number): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length) {
    const first = detail[0];
    const field = first.loc?.at(-1);
    return field ? `${String(field)}: ${first.msg}` : first.msg;
  }
  if (status >= 500) return "Sunucuda beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.";
  return "İstek tamamlanamadı.";
}

export async function api<T>(path: string, init: RequestInit & { json?: unknown } = {}): Promise<T> {
  const { json, headers, ...rest } = init;
  let response: Response;
  try {
    response = await fetch(`/api/v1${path}`, {
      ...rest,
      credentials: "same-origin",
      headers: { ...(json !== undefined ? { "Content-Type": "application/json" } : {}), ...headers },
      body: json !== undefined ? JSON.stringify(json) : rest.body,
    });
  } catch {
    throw new ApiError(0, "Sunucuya ulaşılamadı. Bağlantınızı kontrol edin.");
  }

  if (response.status === 204) return undefined as T;
  const payload = await response.json().catch(() => undefined);
  if (!response.ok) throw new ApiError(response.status, describe(payload?.detail, response.status));
  return payload as T;
}
