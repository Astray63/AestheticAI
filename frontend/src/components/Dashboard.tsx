import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Patient, InterventionType, Simulation } from '../types';
import { patientsAPI, interventionsAPI, simulationsAPI } from '../api';
import { useAuth } from '../AuthContext';
import ImageCapture from './ImageCapture';
import SimulationResult from './SimulationResult';
import { 
  Plus, 
  Settings, 
  User, 
  Calendar, 
  Sparkles, 
  Clock,
  CheckCircle,
  AlertCircle,
  CreditCard,
  LogOut
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [interventionTypes, setInterventionTypes] = useState<Record<string, InterventionType>>({});
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [showImageCapture, setShowImageCapture] = useState(false);
  const [showSimulationResult, setShowSimulationResult] = useState<Simulation | null>(null);
  const [selectedIntervention, setSelectedIntervention] = useState('');
  const [dose, setDose] = useState(1);
  const [loading, setLoading] = useState(false);

  // Formulaire nouveau patient
  const [showNewPatient, setShowNewPatient] = useState(false);
  const [newPatientData, setNewPatientData] = useState({
    age_range: '',
    gender: '',
    skin_type: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [patientsData, interventionsData, simulationsData] = await Promise.all([
        patientsAPI.list(),
        interventionsAPI.getTypes(),
        simulationsAPI.list()
      ]);
      
      setPatients(patientsData);
      setInterventionTypes(interventionsData);
      setSimulations(simulationsData);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    }
  };

  const handleCreatePatient = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newPatient = await patientsAPI.create(newPatientData);
      setPatients([newPatient, ...patients]);
      setNewPatientData({ age_range: '', gender: '', skin_type: '' });
      setShowNewPatient(false);
    } catch (error) {
      console.error('Erreur lors de la création du patient:', error);
    }
  };

  const handleImageCaptured = async (file: File) => {
    if (!selectedPatient || !selectedIntervention) return;

    setLoading(true);
    setShowImageCapture(false);

    try {
      const simulation = await simulationsAPI.create({
        patient_id: selectedPatient.id,
        intervention_type: selectedIntervention,
        dose,
        image: file
      });

      setSimulations([simulation, ...simulations]);
      setShowSimulationResult(simulation);
      
      // Polling pour vérifier le statut de la simulation
      pollSimulationStatus(simulation.id);
    } catch (error) {
      console.error('Erreur lors de la création de la simulation:', error);
    } finally {
      setLoading(false);
    }
  };

  const pollSimulationStatus = async (simulationId: number) => {
    const maxAttempts = 60; // 2 minutes max
    let attempts = 0;

    const poll = async () => {
      try {
        const simulation = await simulationsAPI.getById(simulationId);
        
        // Mettre à jour la simulation dans la liste
        setSimulations(prev => 
          prev.map(sim => sim.id === simulationId ? simulation : sim)
        );

        if (simulation.status === 'completed' || simulation.status === 'failed') {
          setShowSimulationResult(simulation);
          return;
        }

        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 2000); // Vérifier toutes les 2 secondes
        }
      } catch (error) {
        console.error('Erreur lors de la vérification du statut:', error);
      }
    };

    poll();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'processing':
        return <Clock className="h-5 w-5 text-aesthetic-500 animate-spin" />;
      default:
        return <Clock className="h-5 w-5 text-medical-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Terminé';
      case 'failed':
        return 'Échec';
      case 'processing':
        return 'En cours...';
      default:
        return 'En attente';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Sparkles className="h-8 w-8 text-blue-500 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">AestheticAI</h1>
            </div>
            
            <nav className="hidden md:flex items-center space-x-8">
              <span className="text-gray-900 font-medium">Dashboard</span>
              <button
                onClick={() => navigate('/subscription')}
                className="text-gray-600 hover:text-gray-900 flex items-center"
              >
                <CreditCard className="h-4 w-4 mr-1" />
                Abonnement
              </button>
            </nav>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                <p className="text-xs text-gray-600">{user?.speciality}</p>
              </div>
              <button
                onClick={() => navigate('/subscription')}
                className="text-gray-600 hover:text-gray-900"
                title="Gestion abonnement"
              >
                <Settings className="h-5 w-5" />
              </button>
              <button
                onClick={logout}
                className="text-gray-600 hover:text-red-600"
                title="Déconnexion"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Panel Patients */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-semibold text-gray-900">Patients</h2>
                <button
                  onClick={() => setShowNewPatient(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm flex items-center"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Nouveau
                </button>
              </div>

              {showNewPatient && (
                <form onSubmit={handleCreatePatient} className="mb-6 p-4 bg-medical-50 rounded-lg">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-medical-700 mb-1">
                        Tranche d'âge
                      </label>
                      <select
                        value={newPatientData.age_range}
                        onChange={(e) => setNewPatientData({...newPatientData, age_range: e.target.value})}
                        className="medical-input"
                        required
                      >
                        <option value="">Sélectionner</option>
                        <option value="18-25">18-25 ans</option>
                        <option value="26-35">26-35 ans</option>
                        <option value="36-45">36-45 ans</option>
                        <option value="46-55">46-55 ans</option>
                        <option value="56+">56+ ans</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-medical-700 mb-1">
                        Genre
                      </label>
                      <select
                        value={newPatientData.gender}
                        onChange={(e) => setNewPatientData({...newPatientData, gender: e.target.value})}
                        className="medical-input"
                        required
                      >
                        <option value="">Sélectionner</option>
                        <option value="F">Femme</option>
                        <option value="M">Homme</option>
                        <option value="NB">Non-binaire</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-medical-700 mb-1">
                        Type de peau
                      </label>
                      <select
                        value={newPatientData.skin_type}
                        onChange={(e) => setNewPatientData({...newPatientData, skin_type: e.target.value})}
                        className="medical-input"
                        required
                      >
                        <option value="">Sélectionner</option>
                        <option value="I">Type I (Très claire)</option>
                        <option value="II">Type II (Claire)</option>
                        <option value="III">Type III (Moyenne)</option>
                        <option value="IV">Type IV (Mate)</option>
                        <option value="V">Type V (Foncée)</option>
                        <option value="VI">Type VI (Très foncée)</option>
                      </select>
                    </div>

                    <div className="flex space-x-2">
                      <button type="submit" className="aesthetic-button text-sm py-2 px-4">
                        Créer
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowNewPatient(false)}
                        className="py-2 px-4 text-sm border border-medical-300 rounded-lg text-medical-700 hover:bg-medical-50"
                      >
                        Annuler
                      </button>
                    </div>
                  </div>
                </form>
              )}

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {patients.map((patient) => (
                  <div
                    key={patient.id}
                    onClick={() => setSelectedPatient(patient)}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedPatient?.id === patient.id
                        ? 'border-aesthetic-500 bg-aesthetic-50'
                        : 'border-medical-200 hover:border-medical-300 hover:bg-medical-50'
                    }`}
                  >
                    <div className="flex items-center">
                      <User className="h-4 w-4 text-medical-600 mr-2" />
                      <div>
                        <p className="font-medium text-medical-900">
                          Patient {patient.anonymous_id.slice(0, 8)}
                        </p>
                        <p className="text-sm text-medical-600">
                          {patient.gender} • {patient.age_range} • Type {patient.skin_type}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Panel Simulation */}
          <div className="lg:col-span-2">
            <div className="medical-card">
              <h2 className="text-lg font-semibold text-medical-900 mb-6">
                Nouvelle Simulation
              </h2>

              {selectedPatient ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-medical-700 mb-2">
                        Type d'intervention
                      </label>
                      <select
                        value={selectedIntervention}
                        onChange={(e) => setSelectedIntervention(e.target.value)}
                        className="medical-input"
                      >
                        <option value="">Sélectionner une intervention</option>
                        {Object.entries(interventionTypes).map(([key, intervention]) => (
                          <option key={key} value={key}>
                            {intervention.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    {selectedIntervention && (
                      <div>
                        <label className="block text-sm font-medium text-medical-700 mb-2">
                          Dose ({interventionTypes[selectedIntervention]?.unit})
                        </label>
                        <input
                          type="number"
                          value={dose}
                          onChange={(e) => setDose(Number(e.target.value))}
                          min={interventionTypes[selectedIntervention]?.min_dose}
                          max={interventionTypes[selectedIntervention]?.max_dose}
                          step={0.1}
                          className="medical-input"
                        />
                        <p className="text-xs text-medical-600 mt-1">
                          Range: {interventionTypes[selectedIntervention]?.min_dose} - {interventionTypes[selectedIntervention]?.max_dose} {interventionTypes[selectedIntervention]?.unit}
                        </p>
                      </div>
                    )}
                  </div>

                  {selectedIntervention && (
                    <div className="text-center">
                      <button
                        onClick={() => setShowImageCapture(true)}
                        disabled={loading}
                        className="aesthetic-button text-lg py-4 px-8"
                      >
                        {loading ? (
                          <div className="flex items-center">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
                            Génération en cours...
                          </div>
                        ) : (
                          <>
                            <Sparkles className="h-5 w-5 mr-2" />
                            Démarrer la simulation
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <User className="h-12 w-12 text-medical-300 mx-auto mb-4" />
                  <p className="text-medical-600">
                    Sélectionnez un patient pour commencer une simulation
                  </p>
                </div>
              )}
            </div>

            {/* Historique des simulations */}
            <div className="medical-card mt-8">
              <h2 className="text-lg font-semibold text-medical-900 mb-6">
                Simulations Récentes
              </h2>

              <div className="space-y-3">
                {simulations.length > 0 ? (
                  simulations.slice(0, 5).map((simulation) => (
                    <div
                      key={simulation.id}
                      onClick={() => simulation.status === 'completed' && setShowSimulationResult(simulation)}
                      className={`p-4 border border-medical-200 rounded-lg ${
                        simulation.status === 'completed' 
                          ? 'cursor-pointer hover:border-aesthetic-300 hover:bg-aesthetic-50' 
                          : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          {getStatusIcon(simulation.status)}
                          <div className="ml-3">
                            <p className="font-medium text-medical-900">
                              {interventionTypes[simulation.intervention_type]?.name} - {simulation.dose} {interventionTypes[simulation.intervention_type]?.unit}
                            </p>
                            <p className="text-sm text-medical-600">
                              {new Date(simulation.created_at).toLocaleDateString('fr-FR')}
                              {simulation.generation_time && ` • ${simulation.generation_time.toFixed(1)}s`}
                            </p>
                          </div>
                        </div>
                        <span className={`text-sm px-2 py-1 rounded-full ${
                          simulation.status === 'completed' 
                            ? 'bg-green-100 text-green-800'
                            : simulation.status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-aesthetic-100 text-aesthetic-800'
                        }`}>
                          {getStatusText(simulation.status)}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <Calendar className="h-8 w-8 text-medical-300 mx-auto mb-2" />
                    <p className="text-medical-600">Aucune simulation pour le moment</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showImageCapture && (
        <ImageCapture
          onImageCaptured={handleImageCaptured}
          onClose={() => setShowImageCapture(false)}
        />
      )}

      {showSimulationResult && (
        <SimulationResult
          simulation={showSimulationResult}
          interventionType={interventionTypes[showSimulationResult.intervention_type]}
          onClose={() => setShowSimulationResult(null)}
        />
      )}
    </div>
  );
};

export default Dashboard;
