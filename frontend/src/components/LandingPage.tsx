import { 
  Sparkles, 
  Shield, 
  Zap, 
  Users, 
  Star, 
  CheckCircle,
  ArrowRight,
  Brain,
  Camera,
  Award
} from 'lucide-react';

const LandingPage: React.FC = () => {
  const features = [
    {
      icon: <Brain className="w-8 h-8 text-blue-600" />,
      title: "IA Avancée",
      description: "Technologie Stable Diffusion pour des simulations ultra-réalistes"
    },
    {
      icon: <Shield className="w-8 h-8 text-green-600" />,
      title: "RGPD Compliant",
      description: "Protection totale des données patients et respect de la vie privée"
    },
    {
      icon: <Zap className="w-8 h-8 text-yellow-600" />,
      title: "Résultats Instantanés",
      description: "Génération de simulations en moins de 30 secondes"
    },
    {
      icon: <Users className="w-8 h-8 text-purple-600" />,
      title: "Multi-praticiens",
      description: "Gestion de cabinet avec accès sécurisé pour toute votre équipe"
    },
    {
      icon: <Camera className="w-8 h-8 text-pink-600" />,
      title: "Haute Qualité",
      description: "Images 4K avec contrôle précis des interventions esthétiques"
    },
    {
      icon: <Award className="w-8 h-8 text-indigo-600" />,
      title: "Certifié Médical",
      description: "Conforme aux standards médicaux européens"
    }
  ];

  const testimonials = [
    {
      name: "Dr. Marie Dubois",
      role: "Chirurgien Esthétique",
      content: "AestheticAI a révolutionné ma pratique. Mes patients voient exactement le résultat avant l'intervention.",
      rating: 5
    },
    {
      name: "Dr. Pierre Martin",
      role: "Dermatologue",
      content: "Un outil indispensable pour l'éducation patient. Les simulations sont d'un réalisme saisissant.",
      rating: 5
    },
    {
      name: "Dr. Sophie Laurent",
      role: "Médecin Esthétique",
      content: "Interface intuitive et résultats professionnels. Mes consultations sont beaucoup plus efficaces.",
      rating: 5
    }
  ];

  const plans = [
    {
      name: "Freemium",
      price: "0€",
      description: "Parfait pour découvrir",
      features: ["5 simulations/mois", "100MB stockage", "Support email"],
      cta: "Commencer gratuitement",
      popular: false
    },
    {
      name: "Starter",
      price: "29,99€",
      description: "Idéal pour les petites cliniques",
      features: ["50 simulations/mois", "1GB stockage", "IA avancée", "Support prioritaire"],
      cta: "Essai gratuit 14 jours",
      popular: true
    },
    {
      name: "Professional",
      price: "99,99€",
      description: "Pour les professionnels exigeants",
      features: ["200 simulations/mois", "5GB stockage", "Toutes les fonctionnalités", "Support dédié"],
      cta: "Essai gratuit 14 jours",
      popular: false
    },
    {
      name: "Enterprise",
      price: "299,99€",
      description: "Solution complète",
      features: ["Simulations illimitées", "Stockage illimité", "Marque blanche", "Support 24/7"],
      cta: "Nous contacter",
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Sparkles className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">AestheticAI</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900">Fonctionnalités</a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900">Tarifs</a>
              <a href="#testimonials" className="text-gray-600 hover:text-gray-900">Témoignages</a>
              <a href="/login" className="text-blue-600 hover:text-blue-700">Se connecter</a>
              <a href="/register" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                Essai gratuit
              </a>
            </div>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Révolutionnez vos 
              <span className="text-blue-600"> consultations esthétiques</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              La première plateforme IA dédiée aux professionnels de la médecine esthétique. 
              Montrez le résultat avant l'intervention avec une précision inégalée.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a 
                href="/register" 
                className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center"
              >
                Essai gratuit 14 jours
                <ArrowRight className="ml-2 h-5 w-5" />
              </a>
              <a 
                href="#demo" 
                className="border border-gray-300 text-gray-700 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-50 transition-colors"
              >
                Voir la démo
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Pourquoi choisir AestheticAI ?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Une technologie de pointe au service de votre expertise médicale
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Ils nous font confiance
            </h2>
            <p className="text-xl text-gray-600">
              Plus de 1000+ professionnels utilisent AestheticAI
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white p-6 rounded-xl shadow-lg">
                <div className="flex mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-600 mb-4">"{testimonial.content}"</p>
                <div>
                  <p className="font-semibold text-gray-900">{testimonial.name}</p>
                  <p className="text-sm text-gray-500">{testimonial.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Choisissez votre plan
            </h2>
            <p className="text-xl text-gray-600">
              Des tarifs transparents, sans engagement
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {plans.map((plan, index) => (
              <div 
                key={index} 
                className={`bg-white rounded-xl shadow-lg p-6 relative ${
                  plan.popular ? 'ring-2 ring-blue-500 transform scale-105' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                    <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Plus populaire
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <div className="text-3xl font-bold text-gray-900 mb-2">
                    {plan.price}
                    {plan.price !== "0€" && <span className="text-sm font-normal text-gray-600">/mois</span>}
                  </div>
                  <p className="text-gray-600">{plan.description}</p>
                </div>
                
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, fIndex) => (
                    <li key={fIndex} className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span className="text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <button className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Prêt à transformer votre pratique ?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Rejoignez des milliers de professionnels qui utilisent déjà AestheticAI
          </p>
          <a 
            href="/register" 
            className="bg-white text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-50 transition-colors inline-flex items-center"
          >
            Commencer maintenant
            <ArrowRight className="ml-2 h-5 w-5" />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <Sparkles className="h-8 w-8 text-blue-400" />
                <span className="ml-2 text-xl font-bold">AestheticAI</span>
              </div>
              <p className="text-gray-400">
                La révolution de la médecine esthétique par l'intelligence artificielle.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Produit</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#features" className="hover:text-white">Fonctionnalités</a></li>
                <li><a href="#pricing" className="hover:text-white">Tarifs</a></li>
                <li><a href="#" className="hover:text-white">API</a></li>
                <li><a href="#" className="hover:text-white">Intégrations</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Documentation</a></li>
                <li><a href="#" className="hover:text-white">Guides</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
                <li><a href="#" className="hover:text-white">Status</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Légal</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Confidentialité</a></li>
                <li><a href="#" className="hover:text-white">CGU</a></li>
                <li><a href="#" className="hover:text-white">RGPD</a></li>
                <li><a href="#" className="hover:text-white">Mentions légales</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 AestheticAI. Tous droits réservés.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
