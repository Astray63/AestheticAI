import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../../App';

// Mock getUserMedia pour les tests
Object.defineProperty(navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: jest.fn().mockResolvedValue({
      getTracks: () => [{ stop: jest.fn() }]
    })
  }
});

// Mock canvas
HTMLCanvasElement.prototype.getContext = jest.fn(() => ({
  drawImage: jest.fn(),
  getImageData: jest.fn(() => ({ data: new Uint8ClampedArray(4) }))
})) as any;

HTMLCanvasElement.prototype.toBlob = jest.fn((callback) => {
  callback(new Blob(['fake-image-data'], { type: 'image/jpeg' }));
});

describe('App Integration Tests', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('complete workflow: login -> create patient -> take photo -> simulate', async () => {
    const user = userEvent.setup();
    render(<App />);

    // 1. Connexion
    expect(screen.getByText(/connexion/i)).toBeInTheDocument();
    
    const usernameInput = screen.getByLabelText(/nom d'utilisateur/i);
    const pinInput = screen.getByLabelText(/code pin/i);
    const loginButton = screen.getByRole('button', { name: /se connecter/i });

    await user.type(usernameInput, 'doctor_test');
    await user.type(pinInput, '123456');
    await user.click(loginButton);

    // 2. Vérifier que l'utilisateur est connecté (dashboard visible)
    await waitFor(() => {
      expect(screen.getByText(/tableau de bord/i)).toBeInTheDocument();
    });

    // 3. Créer un nouveau patient
    const newPatientButton = screen.getByRole('button', { name: /nouveau patient/i });
    await user.click(newPatientButton);

    const ageInput = screen.getByLabelText(/âge/i);
    const genderSelect = screen.getByLabelText(/genre/i);
    const skinTypeSelect = screen.getByLabelText(/type de peau/i);
    const createPatientButton = screen.getByRole('button', { name: /créer patient/i });

    await user.type(ageInput, '35');
    await user.selectOptions(genderSelect, 'female');
    await user.selectOptions(skinTypeSelect, 'normal');
    await user.click(createPatientButton);

    // 4. Vérifier que le patient a été créé
    await waitFor(() => {
      expect(screen.getByText(/patient créé avec succès/i)).toBeInTheDocument();
    });

    // 5. Démarrer une nouvelle simulation
    const newSimulationButton = screen.getByRole('button', { name: /nouvelle simulation/i });
    await user.click(newSimulationButton);

    // 6. Sélectionner le type d'intervention
    const interventionSelect = screen.getByLabelText(/type d'intervention/i);
    await user.selectOptions(interventionSelect, 'lips');

    const doseInput = screen.getByLabelText(/dose/i);
    await user.type(doseInput, '2.0');

    // 7. Prendre une photo (simulation avec fichier)
    const fileInput = screen.getByLabelText(/télécharger une image/i);
    const imageFile = new File(['fake-image'], 'patient.jpg', { type: 'image/jpeg' });
    await user.upload(fileInput, imageFile);

    // 8. Lancer la simulation
    const simulateButton = screen.getByRole('button', { name: /lancer la simulation/i });
    await user.click(simulateButton);

    // 9. Vérifier que la simulation est en cours
    await waitFor(() => {
      expect(screen.getByText(/simulation en cours/i)).toBeInTheDocument();
    });

    // 10. Vérifier que les résultats s'affichent
    await waitFor(() => {
      expect(screen.getByText(/résultat de la simulation/i)).toBeInTheDocument();
    }, { timeout: 5000 });
    
    expect(screen.getByAltText(/image avant/i)).toBeInTheDocument();
    expect(screen.getByAltText(/image après/i)).toBeInTheDocument();
  });

  // test('handles API errors gracefully', async () => {
  //   // Test temporairement désactivé - problème avec MSW setup
  // });

  test('persists authentication state on page reload', async () => {
    // Simuler un token existant dans localStorage
    localStorage.setItem('aesthetic_token', 'mock-jwt-token');
    localStorage.setItem('aesthetic_user', JSON.stringify({
      id: '1',
      username: 'doctor_test',
      specialty: 'Médecine Esthétique'
    }));

    render(<App />);

    // L'utilisateur devrait être automatiquement connecté
    await waitFor(() => {
      expect(screen.getByText(/tableau de bord/i)).toBeInTheDocument();
    });
    expect(screen.queryByText(/connexion/i)).not.toBeInTheDocument();
  });

  test('logout functionality works correctly', async () => {
    const user = userEvent.setup();
    
    // Connexion initiale
    localStorage.setItem('aesthetic_token', 'mock-jwt-token');
    localStorage.setItem('aesthetic_user', JSON.stringify({
      id: '1',
      username: 'doctor_test'
    }));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/tableau de bord/i)).toBeInTheDocument();
    });

    // Déconnexion
    const logoutButton = screen.getByRole('button', { name: /déconnexion/i });
    await user.click(logoutButton);

    // Vérifier le retour à l'écran de connexion
    await waitFor(() => {
      expect(screen.getByText(/connexion/i)).toBeInTheDocument();
    });
    expect(localStorage.getItem('aesthetic_token')).toBeNull();
    expect(localStorage.getItem('aesthetic_user')).toBeNull();
  });
});
