const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export interface RequestPasswordResetData {
  email: string;
}

export interface ResetPasswordData {
  token: string;
  new_password: string;
  confirm_password: string;
}

export interface ApiResponse {
  message?: string;
  error?: string;
}

class ApiClient {
  private async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw {
          response: {
            status: response.status,
            data
          },
          error: data.error || data.message || `HTTP ${response.status}`
        };
      }

      return data;
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw {
          error: 'Impossible de contacter le serveur. Vérifiez votre connexion.',
          response: { status: 0 }
        };
      }
      throw error;
    }
  }

  // Password reset API methods
  async requestPasswordReset(data: RequestPasswordResetData): Promise<ApiResponse> {
    return this.request('/api/request-password-reset/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async resetPassword(data: ResetPasswordData): Promise<ApiResponse> {
    return this.request('/api/reset-password/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const apiClient = new ApiClient();