import axios from 'axios';
import { LoginCredentials, RegisterData, User, Patient, Simulation, InterventionType, SimulationRequest } from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Configuration d'axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercepteur pour gérer les erreurs d'authentification
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<{ access_token: string; token_type: string }> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  register: async (userData: RegisterData): Promise<User> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
};

export const patientsAPI = {
  create: async (patientData: Omit<Patient, 'id' | 'anonymous_id' | 'created_at'>): Promise<Patient> => {
    const response = await api.post('/patients', patientData);
    return response.data;
  },

  list: async (): Promise<Patient[]> => {
    const response = await api.get('/patients');
    return response.data;
  },
};

export const interventionsAPI = {
  getTypes: async (): Promise<Record<string, InterventionType>> => {
    const response = await api.get('/interventions');
    return response.data;
  },
};

export const subscriptionAPI = {
  getPlans: async () => {
    const response = await api.get('/subscription/plans');
    return response.data;
  },

  getCurrentSubscription: async () => {
    const response = await api.get('/subscription/current');
    return response.data;
  },

  createUpgradeSession: async (planData: { tier: string }) => {
    const response = await api.post('/subscription/upgrade', planData);
    return response.data;
  },

  cancelSubscription: async () => {
    const response = await api.post('/subscription/cancel');
    return response.data;
  },

  getUsageStats: async () => {
    const response = await api.get('/subscription/usage');
    return response.data;
  },
};

export const simulationsAPI = {
  create: async (simulationData: SimulationRequest): Promise<Simulation> => {
    const formData = new FormData();
    formData.append('patient_id', simulationData.patient_id.toString());
    formData.append('intervention_type', simulationData.intervention_type);
    formData.append('dose', simulationData.dose.toString());
    
    if (simulationData.image) {
      formData.append('image', simulationData.image);
    }
    
    const response = await api.post('/simulations', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async (): Promise<Simulation[]> => {
    const response = await api.get('/simulations');
    return response.data;
  },

  getById: async (id: number): Promise<Simulation> => {
    const response = await api.get(`/simulations/${id}`);
    return response.data;
  },
};

export const imageAPI = {
  getImageUrl: (filename: string): string => {
    return `${API_BASE_URL}/uploads/${filename}`;
  },
};

export default api;
