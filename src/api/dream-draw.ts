import { ApiClient } from "@/api/client";

export interface LoginPayload {
  phone: string;
  code: string;
}

export interface QuotePayload {
  ratio_id: string;
  style_id: string;
  template_id: string;
  quality_level: string;
  reference_image_count: number;
}

export interface CreateTaskPayload {
  prompt: string;
  ratio_id: string;
  style_id: string;
  template_id: string;
  quality_level: string;
  reference_mode?: string | null;
  reference_image_urls: string[];
}

export interface PaymentOrderPayload {
  package_id: string;
  channel: "wechat" | "alipay";
}

export interface AdminLoginPayload {
  account: string;
  password: string;
}

export interface UpdateUserPointsPayload {
  delta: number;
  reason: string;
  confirm: boolean;
}

export interface UpdateUserStatusPayload {
  status: string;
  reason: string;
  confirm: boolean;
}

export interface ModelProviderPayload {
  provider_id: string;
  provider_name: string;
  base_url: string;
  api_key_ref?: string | null;
  model_name: string;
  api_mode: string;
  capabilities: string[];
  priority: number;
  status: string;
  timeout_seconds: number;
  qps_limit: number;
  cost_level: string;
}

export class DreamDrawApi {
  constructor(private readonly client: ApiClient) {}

  sendSmsCode(phone: string) {
    return this.client.post<{ success: boolean; cooldown_seconds: number; mock_code: string }>(
      "/auth/sms/send-code",
      { phone },
    );
  }

  login(payload: LoginPayload) {
    return this.client.post<{
      token: string;
      is_first_login: boolean;
      user: {
        id: number;
        phone: string;
        nickname: string;
        points_balance: number;
        status: string;
      };
    }>("/auth/login", payload);
  }

  getStyles() {
    return this.client.get<{ styles: unknown[] }>("/styles");
  }

  getTemplates(styleId?: string) {
    const query = styleId ? `?style_id=${encodeURIComponent(styleId)}` : "";
    return this.client.get<{ templates: unknown[]; groups: Record<string, string[]> }>(
      `/templates${query}`,
    );
  }

  getInspirations() {
    return this.client.get<{ groups: Record<string, string[]> }>("/prompts/inspirations");
  }

  quote(payload: QuotePayload) {
    return this.client.post<{
      base_points: number;
      style_extra_points: number;
      template_extra_points: number;
      reference_image_extra_points: number;
      ratio_extra_points: number;
      final_points: number;
    }>("/generate/quote", payload);
  }

  createTask(payload: CreateTaskPayload) {
    return this.client.post<{ task_id: number; status: string; final_points: number }>(
      "/generate/tasks",
      payload,
    );
  }

  getWorks() {
    return this.client.get<{ works: Array<Record<string, unknown>> }>("/works");
  }

  getWorkDetail(workId: number) {
    return this.client.get<{ work: Record<string, unknown> }>(`/works/${workId}`);
  }

  favoriteWork(workId: number) {
    return this.client.post<{ work_id: number; is_favorite: boolean }>(`/works/${workId}/favorite`);
  }

  unfavoriteWork(workId: number) {
    return this.client.request<{ work_id: number; is_favorite: boolean }>(
      `/works/${workId}/favorite`,
      "DELETE",
    );
  }

  shareWork(workId: number, channel: string) {
    return this.client.post<{
      share_payload: {
        title: string;
        channel: string;
        share_image_url: string;
        share_link: string;
      };
    }>(`/works/${workId}/share?channel=${encodeURIComponent(channel)}`);
  }

  getPoints() {
    return this.client.get<{
      balance: number;
      transactions: Array<Record<string, unknown>>;
    }>("/points");
  }

  createPaymentOrder(payload: PaymentOrderPayload) {
    return this.client.post<{ order: Record<string, unknown> }>("/pay/orders", payload);
  }

  adminLogin(payload: AdminLoginPayload) {
    return this.client.post<{ token: string; admin: { id: number; account: string } }>(
      "/admin/login",
      payload,
    );
  }

  getAdminUsers(keyword?: string, status?: string) {
    const search = new URLSearchParams();
    if (keyword) search.set("keyword", keyword);
    if (status) search.set("status", status);
    const query = search.toString();
    return this.client.get<{ users: Array<Record<string, unknown>> }>(
      `/admin/users${query ? `?${query}` : ""}`,
    );
  }

  getAdminUserDetail(userId: number) {
    return this.client.get<{
      user: Record<string, unknown>;
      points_transactions: Array<Record<string, unknown>>;
    }>(`/admin/users/${userId}`);
  }

  updateAdminUserPoints(userId: number, payload: UpdateUserPointsPayload) {
    return this.client.request<{ user_id: number; points_balance: number }>(
      `/admin/users/${userId}/points`,
      "PATCH",
      payload,
    );
  }

  updateAdminUserStatus(userId: number, payload: UpdateUserStatusPayload) {
    return this.client.request<{ user_id: number; status: string }>(
      `/admin/users/${userId}/status`,
      "PATCH",
      payload,
    );
  }

  getModelProviders() {
    return this.client.get<{ providers: Array<Record<string, unknown>> }>("/admin/model-providers");
  }

  createModelProvider(payload: ModelProviderPayload) {
    return this.client.post<{ provider: Record<string, unknown> }>("/admin/model-providers", payload);
  }

  updateModelProvider(providerId: number, payload: ModelProviderPayload) {
    return this.client.request<{ provider: Record<string, unknown> }>(
      `/admin/model-providers/${providerId}`,
      "PATCH",
      payload,
    );
  }

  updateModelProviderStatus(providerId: number, status: string) {
    return this.client.request<{ provider: Record<string, unknown> }>(
      `/admin/model-providers/${providerId}/status`,
      "PATCH",
      { status },
    );
  }

  getModelMonitoring() {
    return this.client.get<{ monitoring: Array<Record<string, unknown>> }>("/admin/model-monitoring");
  }

  getAdminOverview() {
    return this.client.get<{
      overview: {
        users_total: number;
        works_total: number;
        active_tasks_total: number;
        favorites_total: number;
        shares_total: number;
        provider_summary: Record<string, number>;
        providers: Array<Record<string, unknown>>;
      };
    }>("/admin/overview");
  }
}
