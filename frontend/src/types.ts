export interface User {
  id: number;
  username: string;
  full_name: string;
  speciality: string;
  is_active: boolean;
  created_at: string;
}

export interface Patient {
  id: number;
  anonymous_id: string;
  age_range: string;
  gender: string;
  skin_type: string;
  created_at: string;
}

export interface Simulation {
  id: number;
  patient_id: number;
  intervention_type: string;
  dose: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  original_image_path?: string;
  generated_image_path?: string;
  generation_time?: number;
  created_at: string;
  completed_at?: string;
}

export interface InterventionType {
  name: string;
  min_dose: number;
  max_dose: number;
  unit: string;
  description?: string;
  icon?: string;
}

export interface LoginCredentials {
  username: string;
  pin: string;
}

export interface RegisterData {
  username: string;
  pin: string;
  full_name: string;
  speciality: string;
  license_number: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface SimulationRequest {
  patient_id: number;
  intervention_type: string;
  dose: number;
  image: File;
}
