// Simple API client with JWT access token handling and refresh via HttpOnly cookie
// - Stores access token in localStorage
// - Sends Authorization header automatically
// - On 401, tries to refresh access token using refresh cookie, then retries once

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

const API_BASE_URL: string = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private accessToken: string | null;

  constructor() {
    this.accessToken = this.readAccessToken();
  }

  private readAccessToken(): string | null {
    try {
      return localStorage.getItem('accessToken');
    } catch {
      return null;
    }
  }

  private persistAccessToken(token: string | null) {
    this.accessToken = token;
    try {
      if (token) {
        localStorage.setItem('accessToken', token);
      } else {
        localStorage.removeItem('accessToken');
      }
    } catch {
      // ignore storage errors
    }
  }

  public getAccessToken(): string | null {
    return this.accessToken;
  }

  public setAccessToken(token: string | null) {
    this.persistAccessToken(token);
  }

  private buildUrl(path: string): string {
    if (path.startsWith('http://') || path.startsWith('https://')) return path;
    const base = API_BASE_URL.replace(/\/$/, '');
    const rel = path.replace(/^\//, '');
    return `${base}/${rel}`;
  }

  private async request<T>(method: HttpMethod, path: string, options?: {
    body?: any;
    headers?: Record<string, string>;
    isJson?: boolean;
    signal?: AbortSignal;
    retryOn401?: boolean;
  }): Promise<T> {
    const url = this.buildUrl(path);
    const isJson = options?.isJson ?? true;
    const headers: Record<string, string> = options?.headers ? { ...options.headers } : {};

    if (isJson) headers['Content-Type'] = 'application/json';
    if (this.accessToken) headers['Authorization'] = `Bearer ${this.accessToken}`;

    const fetchInit: RequestInit = {
      method,
      headers,
      credentials: 'include',
      signal: options?.signal,
    };

    if (options?.body !== undefined) {
      fetchInit.body = isJson ? JSON.stringify(options.body) : options.body;
    }

    let response = await fetch(url, fetchInit);

    if (response.status === 401 && (options?.retryOn401 ?? true)) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        if (this.accessToken) headers['Authorization'] = `Bearer ${this.accessToken}`;
        response = await fetch(url, { ...fetchInit, headers });
      }
    }

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      let error: any = text;
      try {
        error = text ? JSON.parse(text) : { status: response.status, message: response.statusText };
      } catch {
        error = { status: response.status, message: text || response.statusText };
      }
      throw { status: response.status, error };
    }

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return (await response.json()) as T;
    }
    // @ts-ignore
    return (await response.text()) as T;
  }

  public get<T>(path: string, options?: { headers?: Record<string, string>; signal?: AbortSignal }): Promise<T> {
    return this.request<T>('GET', path, { ...options, isJson: true });
  }

  public post<T>(path: string, body?: any, options?: { headers?: Record<string, string>; signal?: AbortSignal; isJson?: boolean }): Promise<T> {
    return this.request<T>('POST', path, { ...options, body, isJson: options?.isJson ?? true });
  }

  public upload<T>(path: string, formData: FormData, options?: { headers?: Record<string, string>; signal?: AbortSignal }): Promise<T> {
    // Do not set Content-Type for multipart; browser will set boundary
    return this.request<T>('POST', path, { ...options, body: formData, isJson: false });
  }

  public async refreshAccessToken(): Promise<boolean> {
    try {
      const data = await this.post<{ access: string }>('/api/token/refresh/');
      if (data?.access) {
        this.persistAccessToken(data.access);
        return true;
      }
      return false;
    } catch {
      this.persistAccessToken(null);
      return false;
    }
  }

  // Auth helpers
  public async login(username: string, password: string): Promise<void> {
    const data = await this.post<{ access: string }>('/api/token/', { username, password });
    if (data?.access) this.persistAccessToken(data.access);
  }

  public async register(params: { username: string; email: string; password: string; password_confirm: string }): Promise<void> {
    await this.post('/api/register/', params);
  }

  public async logout(): Promise<void> {
    try {
      await this.post('/api/logout/');
    } finally {
      this.persistAccessToken(null);
    }
  }

  public getProfile<T = any>(): Promise<T> {
    return this.get('/api/profile/');
  }

  // Documents
  public listPayslips<T = { results: any[]; count: number; next?: string; previous?: string }>(
    params?: { limit?: number; offset?: number }
  ): Promise<T> {
    const limit = params?.limit ?? 10;
    const offset = params?.offset ?? 0;
    const qs = `?limit=${limit}&offset=${offset}`;
    return this.get(`/api/payslips/${qs}`);
  }

  public getPayslipsStats<T = { totalAnalyses: number; avgScore: number; avgConformityScore: number; totalErrors: number; lastAnalysis?: string | null }>():
    Promise<T> {
    return this.get('/api/payslips/stats/');
  }

  public async uploadPayslip<T = any>(params: {
    file: File;
    convention_collective?: string;
    contractual_salary?: string | number | null;
    additional_details?: string | null;
    period?: string | null;
  }): Promise<T> {
    const form = new FormData();
    form.append('uploaded_file', params.file);
    if (params.convention_collective) form.append('convention_collective', String(params.convention_collective));
    if (params.contractual_salary !== undefined && params.contractual_salary !== null && `${params.contractual_salary}` !== '') {
      form.append('contractual_salary', String(params.contractual_salary));
    }
    if (params.additional_details) form.append('additional_details', params.additional_details);
    if (params.period) form.append('period', params.period);
    return this.upload('/api/payslips/upload/', form);
  }

  public getConventions<T = { value: string; label: string }[]>(): Promise<T> {
    return this.get('/api/payslips/conventions/');
  }

  // Analysis
  public analyzePayslip<T = any>(payslipId: number): Promise<T> {
    return this.post(`/api/analysis/payslip/${payslipId}/analyze/`);
  }

  public getPayslipAnalysis<T = any>(payslipId: number): Promise<T> {
    return this.get(`/api/analysis/payslip/${payslipId}/results/`);
  }
}

export const api = new ApiClient();
export { API_BASE_URL };



