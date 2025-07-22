import { useState, useEffect } from 'react';
import { subscriptionAPI } from '../api';
import { 
  CreditCard, 
  Check, 
  X, 
  Star, 
  Crown, 
  Building,
  Loader2,
  AlertCircle,
  TrendingUp
} from 'lucide-react';

interface SubscriptionPlan {
  name: string;
  price: number;
  features: {
    monthly_simulations: number;
    storage_mb: number;
    advanced_ai: boolean;
    priority_support: boolean;
    white_label: boolean;
  };
  description: string;
}

interface CurrentSubscription {
  subscription: {
    tier: string;
    start_date: string;
    end_date: string;
    is_active: boolean;
    auto_renew: boolean;
  };
  limits: any;
  usage: {
    simulations_count: number;
    storage_used_mb: number;
    ai_processing_time: number;
  };
  usage_check: {
    allowed: boolean;
    reason?: string;
    remaining_simulations?: number;
  };
}

const SubscriptionManager: React.FC = () => {
  const [plans, setPlans] = useState<Record<string, SubscriptionPlan>>({});
  const [currentSub, setCurrentSub] = useState<CurrentSubscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState<string | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    try {
      setLoading(true);
      const [plansData, currentData] = await Promise.all([
        subscriptionAPI.getPlans(),
        subscriptionAPI.getCurrentSubscription()
      ]);
      
      setPlans(plansData.plans);
      setCurrentSub(currentData);
    } catch (err: any) {
      setError(err.message || 'Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (tierName: string) => {
    try {
      setUpgrading(tierName);
      setError('');
      
      const response = await subscriptionAPI.createUpgradeSession({ tier: tierName });
      
      // Rediriger vers Stripe Checkout
      window.location.href = response.checkout_url;
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la création de la session de paiement');
      setUpgrading(null);
    }
  };

  const handleCancelSubscription = async () => {
    // eslint-disable-next-line no-restricted-globals
    if (!confirm('Êtes-vous sûr de vouloir annuler votre abonnement ?')) {
      return;
    }

    try {
      await subscriptionAPI.cancelSubscription();
      await loadSubscriptionData();
      alert('Abonnement annulé avec succès');
    } catch (err: any) {
      setError(err.message || 'Erreur lors de l\'annulation');
    }
  };

  const formatStorage = (mb: number) => {
    if (mb >= 1000) {
      return `${(mb / 1000).toFixed(1)} GB`;
    }
    return `${mb} MB`;
  };

  const formatSimulations = (count: number) => {
    return count === -1 ? 'Illimité' : count.toString();
  };

  const getUsagePercentage = (used: number, limit: number) => {
    if (limit === -1) return 0; // Illimité
    return Math.min((used / limit) * 100, 100);
  };

  const getPlanIcon = (tier: string) => {
    switch (tier) {
      case 'freemium': return <Star className="w-6 h-6 text-gray-500" />;
      case 'starter': return <Star className="w-6 h-6 text-blue-500" />;
      case 'professional': return <Crown className="w-6 h-6 text-purple-500" />;
      case 'enterprise': return <Building className="w-6 h-6 text-gold-500" />;
      default: return <Star className="w-6 h-6" />;
    }
  };

  const getPlanColor = (tier: string) => {
    switch (tier) {
      case 'freemium': return 'border-gray-200';
      case 'starter': return 'border-blue-200';
      case 'professional': return 'border-purple-200 ring-2 ring-purple-100';
      case 'enterprise': return 'border-yellow-200';
      default: return 'border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Gestion de votre abonnement
        </h1>
        <p className="text-lg text-gray-600">
          Choisissez le plan qui correspond à vos besoins professionnels
        </p>
      </div>

      {error && (
        <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center">
          <AlertCircle className="w-5 h-5 text-red-500 mr-3" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {/* Abonnement actuel */}
      {currentSub && (
        <div className="mb-12 bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Abonnement actuel : {currentSub.subscription.tier.charAt(0).toUpperCase() + currentSub.subscription.tier.slice(1)}
              </h2>
              <p className="text-gray-600">
                Actif jusqu'au {new Date(currentSub.subscription.end_date).toLocaleDateString('fr-FR')}
              </p>
            </div>
            <div className="flex items-center">
              {getPlanIcon(currentSub.subscription.tier)}
            </div>
          </div>

          {/* Statistiques d'utilisation */}
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-900">Simulations ce mois</span>
                <TrendingUp className="w-4 h-4 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-blue-900">
                {currentSub.usage.simulations_count}
                <span className="text-sm font-normal text-blue-600">
                  / {formatSimulations(currentSub.limits.monthly_simulations)}
                </span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2 mt-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ 
                    width: `${getUsagePercentage(currentSub.usage.simulations_count, currentSub.limits.monthly_simulations)}%` 
                  }}
                ></div>
              </div>
            </div>

            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-green-900">Stockage utilisé</span>
                <CreditCard className="w-4 h-4 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-green-900">
                {formatStorage(currentSub.usage.storage_used_mb)}
                <span className="text-sm font-normal text-green-600">
                  / {formatStorage(currentSub.limits.storage_mb)}
                </span>
              </div>
              <div className="w-full bg-green-200 rounded-full h-2 mt-2">
                <div 
                  className="bg-green-600 h-2 rounded-full" 
                  style={{ 
                    width: `${getUsagePercentage(currentSub.usage.storage_used_mb, currentSub.limits.storage_mb)}%` 
                  }}
                ></div>
              </div>
            </div>

            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-purple-900">Temps IA total</span>
                <Star className="w-4 h-4 text-purple-600" />
              </div>
              <div className="text-2xl font-bold text-purple-900">
                {Math.round(currentSub.usage.ai_processing_time / 60)}
                <span className="text-sm font-normal text-purple-600"> min</span>
              </div>
            </div>
          </div>

          {/* Statut d'utilisation */}
          {!currentSub.usage_check.allowed && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-500 mr-3" />
                <span className="text-red-700">{currentSub.usage_check.reason}</span>
              </div>
            </div>
          )}

          {/* Actions */}
          {currentSub.subscription.tier !== 'enterprise' && (
            <div className="flex justify-end">
              <button
                onClick={() => {/* Scroll to plans */}}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Améliorer mon abonnement
              </button>
            </div>
          )}
        </div>
      )}

      {/* Plans d'abonnement */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {Object.entries(plans).map(([tierKey, plan]) => (
          <div
            key={tierKey}
            className={`bg-white rounded-lg shadow-lg p-6 ${getPlanColor(tierKey)} ${
              currentSub?.subscription.tier === tierKey ? 'ring-2 ring-blue-500' : ''
            }`}
          >
            <div className="text-center mb-6">
              <div className="flex justify-center mb-4">
                {getPlanIcon(tierKey)}
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
              <div className="text-3xl font-bold text-gray-900">
                {plan.price === 0 ? 'Gratuit' : `${plan.price}€`}
                {plan.price > 0 && <span className="text-sm font-normal text-gray-600">/mois</span>}
              </div>
              <p className="text-sm text-gray-600 mt-2">{plan.description}</p>
            </div>

            <ul className="space-y-3 mb-6">
              <li className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-3" />
                <span className="text-sm text-gray-700">
                  {formatSimulations(plan.features.monthly_simulations)} simulations/mois
                </span>
              </li>
              <li className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-3" />
                <span className="text-sm text-gray-700">
                  {formatStorage(plan.features.storage_mb)} de stockage
                </span>
              </li>
              <li className="flex items-center">
                {plan.features.advanced_ai ? (
                  <Check className="w-5 h-5 text-green-500 mr-3" />
                ) : (
                  <X className="w-5 h-5 text-gray-400 mr-3" />
                )}
                <span className={`text-sm ${plan.features.advanced_ai ? 'text-gray-700' : 'text-gray-400'}`}>
                  IA avancée
                </span>
              </li>
              <li className="flex items-center">
                {plan.features.priority_support ? (
                  <Check className="w-5 h-5 text-green-500 mr-3" />
                ) : (
                  <X className="w-5 h-5 text-gray-400 mr-3" />
                )}
                <span className={`text-sm ${plan.features.priority_support ? 'text-gray-700' : 'text-gray-400'}`}>
                  Support prioritaire
                </span>
              </li>
              <li className="flex items-center">
                {plan.features.white_label ? (
                  <Check className="w-5 h-5 text-green-500 mr-3" />
                ) : (
                  <X className="w-5 h-5 text-gray-400 mr-3" />
                )}
                <span className={`text-sm ${plan.features.white_label ? 'text-gray-700' : 'text-gray-400'}`}>
                  Marque blanche
                </span>
              </li>
            </ul>

            <div className="text-center">
              {currentSub?.subscription.tier === tierKey ? (
                <span className="text-green-600 font-medium">Plan actuel</span>
              ) : tierKey === 'freemium' ? (
                <span className="text-gray-500">Plan gratuit</span>
              ) : (
                <button
                  onClick={() => handleUpgrade(tierKey)}
                  disabled={upgrading === tierKey}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {upgrading === tierKey ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : null}
                  {currentSub && currentSub.subscription.tier !== 'freemium' ? 'Changer de plan' : 'Commencer'}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Section d'annulation */}
      {currentSub && currentSub.subscription.tier !== 'freemium' && currentSub.subscription.auto_renew && (
        <div className="bg-gray-50 rounded-lg p-6 text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Besoin d'annuler votre abonnement ?
          </h3>
          <p className="text-gray-600 mb-4">
            Vous pouvez annuler à tout moment. Votre abonnement restera actif jusqu'à la fin de la période payée.
          </p>
          <button
            onClick={handleCancelSubscription}
            className="text-red-600 hover:text-red-700 font-medium"
          >
            Annuler mon abonnement
          </button>
        </div>
      )}
    </div>
  );
};

export default SubscriptionManager;
