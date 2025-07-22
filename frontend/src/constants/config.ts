/**
 * Configuration et constantes de l'application AestheticAI
 */

// Configuration API
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
} as const;

// Messages d'erreur
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Erreur de connexion. Vérifiez votre connexion internet.',
  UNAUTHORIZED: 'Session expirée. Veuillez vous reconnecter.',
  FORBIDDEN: 'Accès refusé. Droits insuffisants.',
  NOT_FOUND: 'Ressource non trouvée.',
  SERVER_ERROR: 'Erreur serveur. Veuillez réessayer plus tard.',
  VALIDATION_ERROR: 'Données invalides. Vérifiez vos informations.',
  FILE_TOO_LARGE: 'Fichier trop volumineux. Taille maximale: 50MB.',
  INVALID_FILE_TYPE: 'Type de fichier non supporté.',
} as const;

// Messages de succès
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Connexion réussie !',
  LOGOUT_SUCCESS: 'Déconnexion réussie !',
  PATIENT_CREATED: 'Patient créé avec succès !',
  PATIENT_UPDATED: 'Patient mis à jour avec succès !',
  SIMULATION_CREATED: 'Simulation lancée avec succès !',
  SIMULATION_COMPLETED: 'Simulation terminée !',
} as const;

// Configuration des types d'interventions
export const INTERVENTION_TYPES = {
  lips: {
    name: 'Augmentation des lèvres',
    minDose: 0.5,
    maxDose: 5.0,
    unit: 'ml',
    description: 'Redéfinition et augmentation naturelle des lèvres',
    icon: '💋',
  },
  cheeks: {
    name: 'Redéfinition des pommettes',
    minDose: 1.0,
    maxDose: 8.0,
    unit: 'ml',
    description: 'Restructuration des pommettes pour un effet sculptant',
    icon: '✨',
  },
  chin: {
    name: 'Remodelage du menton',
    minDose: 1.0,
    maxDose: 6.0,
    unit: 'ml',
    description: 'Redéfinition du profil et de la ligne mandibulaire',
    icon: '🔺',
  },
  forehead: {
    name: 'Traitement du front',
    minDose: 10,
    maxDose: 50,
    unit: 'unités',
    description: 'Lissage des rides frontales et des rides d\'expression',
    icon: '🧠',
  },
  crow_feet: {
    name: 'Pattes d\'oie',
    minDose: 5,
    maxDose: 25,
    unit: 'unités',
    description: 'Traitement des rides périoculaires',
    icon: '👁️',
  },
} as const;

// Configuration des tranches d'âge
export const AGE_RANGES = [
  { value: '18-25', label: '18-25 ans' },
  { value: '26-35', label: '26-35 ans' },
  { value: '36-45', label: '36-45 ans' },
  { value: '46-55', label: '46-55 ans' },
  { value: '56-65', label: '56-65 ans' },
  { value: '65+', label: '65 ans et plus' },
] as const;

// Types de peau
export const SKIN_TYPES = [
  { value: 'Claire', label: 'Peau claire' },
  { value: 'Mate', label: 'Peau mate' },
  { value: 'Foncée', label: 'Peau foncée' },
  { value: 'Mixte', label: 'Peau mixte' },
] as const;

// Genres
export const GENDERS = [
  { value: 'F', label: 'Femme' },
  { value: 'M', label: 'Homme' },
  { value: 'Autre', label: 'Autre' },
] as const;

// Spécialités médicales
export const MEDICAL_SPECIALTIES = [
  { value: 'medecine_esthetique', label: 'Médecine esthétique' },
  { value: 'chirurgie_plastique', label: 'Chirurgie plastique' },
  { value: 'dermatologie', label: 'Dermatologie' },
  { value: 'chirurgie_maxillo_faciale', label: 'Chirurgie maxillo-faciale' },
  { value: 'autre', label: 'Autre' },
] as const;

// Statuts de simulation
export const SIMULATION_STATUSES = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const;

// Configuration des fichiers
export const FILE_CONFIG = {
  MAX_SIZE: 50 * 1024 * 1024, // 50MB
  ALLOWED_TYPES: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
  ALLOWED_EXTENSIONS: ['.jpg', '.jpeg', '.png', '.webp'],
} as const;

// Configuration de pagination
export const PAGINATION_CONFIG = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
} as const;

// Thème et couleurs
export const THEME_CONFIG = {
  COLORS: {
    primary: '#3B82F6',
    secondary: '#8B5CF6',
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#06B6D4',
  },
  BREAKPOINTS: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
} as const;

// Configuration de développement
export const DEV_CONFIG = {
  MOCK_DELAYS: {
    API_CALL: 1000,
    IMAGE_GENERATION: 5000,
  },
  DEBUG_MODE: process.env.NODE_ENV === 'development',
  ENABLE_MOCKS: process.env.REACT_APP_USE_MOCKS === 'true',
} as const;
