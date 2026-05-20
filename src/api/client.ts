export interface ApiClientOptions {
  baseUrl?: string;
  getToken?: () => string | null;
}

export class ApiClient {
  private readonly baseUrl: string;
  private readonly getToken?: () => string | null;

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = options.baseUrl ?? "/api";
    this.getToken = options.getToken;
  }

  async get<T>(path: string): Promise<T> {
    return this.requestInternal<T>(path, { method: "GET" });
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.requestInternal<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async request<T>(path: string, method: string, body?: unknown): Promise<T> {
    return this.requestInternal<T>(path, {
      method,
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  private async requestInternal<T>(path: string, init: RequestInit): Promise<T> {
    const headers = new Headers(init.headers);
    headers.set("Content-Type", "application/json");

    const token = this.getToken?.();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    return (await response.json()) as T;
  }
}
