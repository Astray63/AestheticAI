import { useState } from 'react';
import { useAuth } from '../AuthContext';
import { authAPI } from '../api';
import { User } from '../types';
import { Activity, Shield, Stethoscope, ArrowRight, User as UserIcon } from 'lucide-react';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login({ username, pin });
      
      // Créer un utilisateur mock pour la démo (normalement retourné par l'API)
      const user: User = {
        id: 1,
        username,
        full_name: 'Dr. ' + username,
        speciality: 'Médecine Esthétique',
        is_active: true,
        created_at: new Date().toISOString(),
      };
      
      login(response.access_token, user);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-medical-50 via-white to-aesthetic-50 flex">
      {/* Panel gauche - Informations */}
      <div className="hidden lg:flex lg:w-1/2 bg-medical-900 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-medical-800/90 to-aesthetic-900/90" />
        
        {/* Contenu */}
        <div className="relative z-10 flex flex-col justify-center px-12 py-16 text-white">
          <div className="mb-8">
            <div className="flex items-center mb-6">
              <Stethoscope className="h-10 w-10 text-aesthetic-400 mr-3" />
              <h1 className="text-3xl font-bold">AestheticAI</h1>
            </div>
            <h2 className="text-xl font-medium text-medical-200 mb-4">
              Simulation d'interventions esthétiques par IA générative
            </h2>
            <p className="text-medical-300 leading-relaxed">
              Visualisez en temps réel les résultats de vos interventions grâce à 
              notre technologie d'intelligence artificielle avancée.
            </p>
          </div>

          <div className="space-y-6">
            <div className="flex items-start">
              <UserIcon className="h-6 w-6 text-aesthetic-400 mr-4 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold mb-1">Interface Professionnelle</h3>
                <p className="text-medical-300 text-sm">
                  Conçue spécifiquement pour les professionnels de santé
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <Activity className="h-6 w-6 text-aesthetic-400 mr-4 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold mb-1">Résultats en 2 minutes</h3>
                <p className="text-medical-300 text-sm">
                  Génération rapide et précise des simulations
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <Shield className="h-6 w-6 text-aesthetic-400 mr-4 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold mb-1">Données Sécurisées</h3>
                <p className="text-medical-300 text-sm">
                  Conformité RGPD et chiffrement des données patients
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Motifs décoratifs */}
        <div className="absolute bottom-0 right-0 w-64 h-64 bg-gradient-to-tl from-aesthetic-500/20 to-transparent rounded-full transform translate-x-32 translate-y-32" />
        <div className="absolute top-0 left-0 w-48 h-48 bg-gradient-to-br from-medical-600/20 to-transparent rounded-full transform -translate-x-24 -translate-y-24" />
      </div>

      {/* Panel droit - Formulaire */}
      <div className="w-full lg:w-1/2 flex items-center justify-center px-8 py-16">
        <div className="w-full max-w-md">
          <div className="medical-card">
            <div className="text-center mb-8">
              <div className="lg:hidden flex items-center justify-center mb-4">
                <Stethoscope className="h-8 w-8 text-aesthetic-500 mr-2" />
                <h1 className="text-2xl font-bold text-medical-900">AestheticAI</h1>
              </div>
              <h2 className="text-2xl font-bold text-medical-900 mb-2">Connexion</h2>
              <p className="text-medical-600">Accédez à votre espace professionnel</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-medical-700 mb-2">
                  Nom d'utilisateur
                </label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="medical-input"
                  placeholder="Votre nom d'utilisateur"
                  required
                />
              </div>

              <div>
                <label htmlFor="pin" className="block text-sm font-medium text-medical-700 mb-2">
                  Code PIN
                </label>
                <input
                  type="password"
                  id="pin"
                  value={pin}
                  onChange={(e) => setPin(e.target.value)}
                  className="medical-input"
                  placeholder="••••••"
                  maxLength={6}
                  required
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full medical-button flex items-center justify-center"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                ) : (
                  <>
                    Se connecter
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-medical-200">
              <p className="text-center text-sm text-medical-600">
                Pas encore de compte ?{' '}
                <span className="text-aesthetic-600 font-medium cursor-pointer hover:text-aesthetic-700">
                  Contactez votre administrateur
                </span>
              </p>
            </div>
          </div>

          <div className="mt-8 text-center">
            <p className="text-xs text-medical-500">
              © 2024 AestheticAI. Conforme aux normes médicales et RGPD.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
