import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SimulationResult from '../../components/SimulationResult';
import { Simulation, InterventionType } from '../../types';

const mockSimulation: Simulation = {
  id: 1,
  patient_id: 1,
  intervention_type: 'lips',
  dose: 2.0,
  status: 'completed',
  original_image_path: '/uploads/original_123.jpg',
  generated_image_path: '/uploads/result_123.jpg',
  generation_time: 45,
  created_at: '2025-07-19T10:00:00Z',
  completed_at: '2025-07-19T10:01:00Z'
};

const mockInterventionType: InterventionType = {
  name: 'Lèvres',
  min_dose: 0.5,
  max_dose: 5.0,
  unit: 'ml'
};

describe('SimulationResult Component', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders simulation result correctly', () => {
    render(
      <SimulationResult 
        simulation={mockSimulation}
        interventionType={mockInterventionType}
        onClose={mockOnClose}
      />
    );
    
    expect(screen.getAllByText(/résultat de la simulation/i)[0]).toBeInTheDocument();
    expect(screen.getByText(/lèvres/i)).toBeInTheDocument();
    expect(screen.getByText(/2\.0/i)).toBeInTheDocument();
  });

  test('displays before and after images when comparison view is selected', async () => {
    const user = userEvent.setup();
    render(
      <SimulationResult 
        simulation={mockSimulation}
        interventionType={mockInterventionType}
        onClose={mockOnClose}
      />
    );
    
    // Cliquer sur le bouton "Avant / Après" pour passer en mode comparaison
    const comparisonButton = screen.getByRole('button', { name: /avant \/ après/i });
    await user.click(comparisonButton);
    
    const beforeImage = screen.getByAltText(/état initial/i);
    const afterImage = screen.getByAltText(/résultat de simulation/i);
    
    expect(beforeImage).toBeInTheDocument();
    expect(afterImage).toBeInTheDocument();
  });

  test('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <SimulationResult 
        simulation={mockSimulation}
        interventionType={mockInterventionType}
        onClose={mockOnClose}
      />
    );
    
    // Le bouton de fermeture est le premier bouton dans l'en-tête (avec l'icône X)
    const buttons = screen.getAllByRole('button');
    const closeButton = buttons.find(button => 
      button.className.includes('text-medical-500') && 
      button.className.includes('hover:text-medical-700')
    );
    
    expect(closeButton).toBeDefined();
    expect(closeButton).not.toBeNull();
    
    await user.click(closeButton!);
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('displays processing status correctly', () => {
    const processingSimulation = { ...mockSimulation, status: 'processing' as const };
    
    render(
      <SimulationResult 
        simulation={processingSimulation}
        interventionType={mockInterventionType}
        onClose={mockOnClose}
      />
    );
    
    expect(screen.getByText(/génération en cours/i)).toBeInTheDocument();
  });

  test('displays error status correctly', () => {
    const errorSimulation = { ...mockSimulation, status: 'failed' as const };
    
    render(
      <SimulationResult 
        simulation={errorSimulation}
        interventionType={mockInterventionType}
        onClose={mockOnClose}
      />
    );
    
    expect(screen.getByText(/erreur/i)).toBeInTheDocument();
  });

  test('shows download button when simulation is completed', () => {
    render(
      <SimulationResult 
        simulation={mockSimulation}
        interventionType={mockInterventionType}
        onClose={mockOnClose}
      />
    );
    
    expect(screen.getByRole('button', { name: /télécharger/i })).toBeInTheDocument();
  });

  test('hides download button when result is not ready', () => {
    const processingSimulation = { ...mockSimulation, status: 'processing' as const };
    
    render(
      <SimulationResult 
        simulation={processingSimulation}
        interventionType={mockInterventionType}
        onClose={mockOnClose}
      />
    );
    
    expect(screen.queryByRole('button', { name: /télécharger/i })).not.toBeInTheDocument();
  });

  test('displays generation time when available', () => {
    render(
      <SimulationResult 
        simulation={mockSimulation}
        interventionType={mockInterventionType}
        onClose={mockOnClose}
      />
    );
    
    expect(screen.getByText(/45/)).toBeInTheDocument(); // Generation time
  });
});
