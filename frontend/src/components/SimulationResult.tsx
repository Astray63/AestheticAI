import { useState } from 'react';
import { Simulation, InterventionType } from '../types';
import { imageAPI } from '../api';
import { X, Download, RotateCcw, Sparkles, Clock, Calendar } from 'lucide-react';

interface SimulationResultProps {
  simulation: Simulation;
  interventionType: InterventionType;
  onClose: () => void;
}

const SimulationResult: React.FC<SimulationResultProps> = ({ 
  simulation, 
  interventionType, 
  onClose 
}) => {
  const [showComparison, setShowComparison] = useState(false);

  const getImageUrl = (imagePath?: string) => {
    if (!imagePath) return '';
    const filename = imagePath.split('/').pop() || '';
    return imageAPI.getImageUrl(filename);
  };

  const handleDownload = async () => {
    if (!simulation.generated_image_path) return;
    
    try {
      const response = await fetch(getImageUrl(simulation.generated_image_path));
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `simulation-${simulation.id}-${interventionType.name.toLowerCase()}.jpg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Erreur lors du téléchargement:', error);
    }
  };

  if (simulation.status === 'processing') {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4 text-center">
          <div className="mb-6">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-aesthetic-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-medical-900 mb-2">
              Génération en cours...
            </h3>
            <p className="text-medical-600">
              L'IA travaille sur votre simulation. Cela peut prendre jusqu'à 2 minutes.
            </p>
          </div>
          
          <div className="bg-medical-50 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-center mb-2">
              <Sparkles className="h-5 w-5 text-aesthetic-500 mr-2" />
              <span className="font-medium text-medical-900">
                {interventionType.name} - {simulation.dose} {interventionType.unit}
              </span>
            </div>
            <div className="flex items-center justify-center text-sm text-medical-600">
              <Clock className="h-4 w-4 mr-1" />
              Démarré {new Date(simulation.created_at).toLocaleTimeString('fr-FR')}
            </div>
          </div>

          <button
            onClick={onClose}
            className="medical-button w-full"
          >
            Continuer en arrière-plan
          </button>
        </div>
      </div>
    );
  }

  if (simulation.status === 'failed') {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4 text-center">
          <div className="mb-6">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <X className="h-8 w-8 text-red-600" />
            </div>
            <h3 className="text-xl font-semibold text-medical-900 mb-2">
              Échec de la génération
            </h3>
            <p className="text-medical-600">
              Une erreur s'est produite lors de la génération de votre simulation. 
              Veuillez réessayer avec une autre image.
            </p>
          </div>

          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="medical-button flex-1"
            >
              Fermer
            </button>
            <button
              onClick={onClose}
              className="aesthetic-button flex-1"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Réessayer
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Simulation terminée avec succès
  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-medical-200">
          <div>
            <h3 className="text-xl font-semibold text-medical-900">
              Résultat de la simulation
            </h3>
            <p className="text-medical-600">
              {interventionType.name} - {simulation.dose} {interventionType.unit}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-medical-500 hover:text-medical-700"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Informations de la simulation */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-medical-50 rounded-lg p-4 text-center">
              <Calendar className="h-5 w-5 text-medical-600 mx-auto mb-2" />
              <p className="text-sm text-medical-600">Date</p>
              <p className="font-semibold text-medical-900">
                {new Date(simulation.created_at).toLocaleDateString('fr-FR')}
              </p>
            </div>
            <div className="bg-aesthetic-50 rounded-lg p-4 text-center">
              <Clock className="h-5 w-5 text-aesthetic-600 mx-auto mb-2" />
              <p className="text-sm text-aesthetic-600">Temps de génération</p>
              <p className="font-semibold text-aesthetic-900">
                {simulation.generation_time?.toFixed(1)}s
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <Sparkles className="h-5 w-5 text-green-600 mx-auto mb-2" />
              <p className="text-sm text-green-600">Statut</p>
              <p className="font-semibold text-green-900">Terminé</p>
            </div>
          </div>

          {/* Boutons de contrôle */}
          <div className="flex justify-center mb-6">
            <div className="bg-medical-100 rounded-lg p-1 flex">
              <button
                onClick={() => setShowComparison(false)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  !showComparison
                    ? 'bg-white text-medical-900 shadow-sm'
                    : 'text-medical-600 hover:text-medical-900'
                }`}
              >
                Résultat final
              </button>
              <button
                onClick={() => setShowComparison(true)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  showComparison
                    ? 'bg-white text-medical-900 shadow-sm'
                    : 'text-medical-600 hover:text-medical-900'
                }`}
              >
                Avant / Après
              </button>
            </div>
          </div>

          {/* Images */}
          <div className="text-center">
            {showComparison ? (
              // Vue comparaison Avant/Après
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold text-medical-900 mb-3">Avant</h4>
                  <div className="relative">
                    <img
                      src={getImageUrl(simulation.original_image_path)}
                      alt="État initial"
                      className="w-full h-auto rounded-lg shadow-lg"
                    />
                    <div className="absolute top-3 left-3 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-sm">
                      Original
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-aesthetic-900 mb-3">Après</h4>
                  <div className="relative">
                    <img
                      src={getImageUrl(simulation.generated_image_path)}
                      alt="Résultat de simulation"
                      className="w-full h-auto rounded-lg shadow-lg"
                    />
                    <div className="absolute top-3 left-3 bg-aesthetic-600 text-white px-2 py-1 rounded text-sm">
                      Simulation IA
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              // Vue résultat uniquement
              <div className="max-w-2xl mx-auto">
                <h4 className="text-lg font-semibold text-aesthetic-900 mb-3">
                  Résultat de la simulation
                </h4>
                <div className="relative">
                  <img
                    src={getImageUrl(simulation.generated_image_path)}
                    alt="Résultat de la simulation"
                    className="w-full h-auto rounded-lg shadow-lg"
                  />
                  <div className="absolute top-3 right-3 bg-aesthetic-600 text-white px-3 py-1 rounded-lg text-sm font-medium">
                    {interventionType.name} +{simulation.dose}{interventionType.unit}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-center space-x-4 mt-8">
            <button
              onClick={handleDownload}
              className="medical-button flex items-center"
            >
              <Download className="h-4 w-4 mr-2" />
              Télécharger
            </button>
            <button
              onClick={onClose}
              className="aesthetic-button"
            >
              Nouvelle simulation
            </button>
          </div>

          {/* Note médicale */}
          <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-sm text-amber-800">
              <strong>Note importante :</strong> Cette simulation est générée par IA à des fins 
              d'illustration uniquement. Les résultats réels peuvent varier selon l'anatomie 
              du patient et la technique utilisée. Toujours discuter des attentes avec le patient.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimulationResult;
