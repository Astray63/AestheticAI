/**
 * Client API modernisé pour AestheticAI
 * Utilise axios avec intercepteurs et gestion d'erreur centralisée
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_CONFIG, ERROR_MESSAGES } from '../constants/config';

/**
 * Classe de base pour les erreurs API
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Client API centralisé avec gestion d'erreur et authentification
 */
class ApiClient {
  private instance: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.instance = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.loadTokenFromStorage();
  }

  /**
   * Configuration des intercepteurs
   */
  private setupInterceptors(): void {
    // Intercepteur de requête - ajouter le token
    this.instance.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Intercepteur de réponse - gestion des erreurs
    this.instance.interceptors.response.use(
      (response) => response,
      (error) => {
        const apiError = this.handleError(error);
        
        // Déconnexion automatique en cas d'erreur 401
        if (apiError.status === 401) {
          this.clearToken();
          window.location.href = '/login';
        }
        
        return Promise.reject(apiError);
      }
    );
  }

  /**
   * Gestion centralisée des erreurs
   */
  private handleError(error: any): ApiError {
    if (!error.response) {
      // Erreur réseau
      return new ApiError(ERROR_MESSAGES.NETWORK_ERROR, 0, 'NETWORK_ERROR');
    }

    const { status, data } = error.response;
    let message: string = ERROR_MESSAGES.SERVER_ERROR;

    switch (status) {
      case 400:
        message = data?.detail || ERROR_MESSAGES.VALIDATION_ERROR;
        break;
      case 401:
        message = ERROR_MESSAGES.UNAUTHORIZED;
        break;
      case 403:
        message = ERROR_MESSAGES.FORBIDDEN;
        break;
      case 404:
        message = ERROR_MESSAGES.NOT_FOUND;
        break;
      case 413:
        message = ERROR_MESSAGES.FILE_TOO_LARGE;
        break;
      case 422:
        message = data?.detail || ERROR_MESSAGES.VALIDATION_ERROR;
        break;
      case 500:
      default:
        message = ERROR_MESSAGES.SERVER_ERROR;
        break;
    }

    return new ApiError(
      message,
      status,
      data?.code || `HTTP_${status}`,
      data
    );
  }

  /**
   * Charger le token depuis le localStorage
   */
  private loadTokenFromStorage(): void {
    this.token = localStorage.getItem('auth_token');
  }

  /**
   * Définir le token d'authentification
   */
  setToken(token: string): void {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  /**
   * Supprimer le token d'authentification
   */
  clearToken(): void {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  /**
   * Vérifier si l'utilisateur est authentifié
   */
  isAuthenticated(): boolean {
    return !!this.token;
  }

  /**
   * Méthodes HTTP génériques
   */
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.get(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.post(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.put(url, data, config);
    return response.data;
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.patch(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.delete(url, config);
    return response.data;
  }

  /**
   * Upload de fichier avec progress
   */
  async uploadFile<T = any>(
    url: string,
    file: File,
    additionalData?: Record<string, any>,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData();
    formData.append('image', file);

    // Ajouter les données additionnelles
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, String(value));
      });
    }

    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    };

    const response: AxiosResponse<T> = await this.instance.post(url, formData, config);
    return response.data;
  }

  /**
   * Téléchargement de fichier
   */
  async downloadFile(url: string, filename?: string): Promise<void> {
    const response = await this.instance.get(url, {
      responseType: 'blob',
    });

    // Créer un lien de téléchargement
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }
}

// Instance singleton du client API
export const apiClient = new ApiClient();

// Export du type pour utilisation dans les services
export type { ApiClient };
