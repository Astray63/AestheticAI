/**
 * Service d'authentification pour AestheticAI
 */

import { apiClient } from './api-client';
import { LoginCredentials, RegisterData, User, TokenResponse } from '../types';

export class AuthService {
  /**
   * Connexion utilisateur
   */
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/api/auth/login', credentials);
    
    // Stocker le token
    apiClient.setToken(response.access_token);
    
    return response;
  }

  /**
   * Inscription d'un nouveau professionnel
   */
  async register(userData: RegisterData): Promise<User> {
    return apiClient.post<User>('/api/auth/register', userData);
  }

  /**
   * Obtenir les informations de l'utilisateur connecté
   */
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/api/auth/me');
  }

  /**
   * Déconnexion
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/api/auth/logout');
    } finally {
      // Nettoyer le token même si la requête échoue
      apiClient.clearToken();
    }
  }

  /**
   * Renouveler le token
   */
  async refreshToken(): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/api/auth/refresh');
    
    // Mettre à jour le token
    apiClient.setToken(response.access_token);
    
    return response;
  }

  /**
   * Vérifier si l'utilisateur est connecté
   */
  isAuthenticated(): boolean {
    return apiClient.isAuthenticated();
  }
}

// Instance singleton du service d'authentification
export const authService = new AuthService();
