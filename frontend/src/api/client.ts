const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api"

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function apiFetch<T>(
  path: string,
  params?: Record<string, unknown>,
  method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
  body?: unknown,
): Promise<T> {
  let url = `${BASE_URL}${path}`

  if (params && method === "GET") {
    const searchParams = new URLSearchParams()
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== "") {
        searchParams.set(key, String(value))
      }
    }
    const qs = searchParams.toString()
    if (qs) url += `?${qs}`
  }

  const options: RequestInit = { method }
  if (body && method !== "GET") {
    options.headers = { "Content-Type": "application/json" }
    options.body = JSON.stringify(body)
  }

  const res = await fetch(url, options)
  if (!res.ok) {
    throw new ApiError(res.status, `${method} ${path}: ${res.statusText}`)
  }
  return res.json()
}
