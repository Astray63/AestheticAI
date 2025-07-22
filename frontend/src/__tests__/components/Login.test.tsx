import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthContext } from '../../AuthContext';
import Login from '../../components/Login';
import { User } from '../../types';

// Mock du contexte d'authentification
const mockLogin = jest.fn();
const mockLogout = jest.fn();

const createMockAuthContextValue = (overrides = {}) => ({
  user: null as User | null,
  token: null as string | null,
  login: mockLogin,
  logout: mockLogout,
  isAuthenticated: false,
  ...overrides
});

const renderWithAuthContext = (component: React.ReactElement, contextValue = {}) => {
  const mockAuthContextValue = createMockAuthContextValue(contextValue);
  return render(
    <AuthContext.Provider value={mockAuthContextValue}>
      {component}
    </AuthContext.Provider>
  );
};

describe('Login Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form correctly', () => {
    renderWithAuthContext(<Login />);
    
    expect(screen.getByLabelText(/nom d'utilisateur/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/code pin/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /se connecter/i })).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    const user = userEvent.setup();
    renderWithAuthContext(<Login />);
    
    const submitButton = screen.getByRole('button', { name: /se connecter/i });
    await user.click(submitButton);
    
    expect(screen.getByText(/nom d'utilisateur requis/i)).toBeInTheDocument();
    expect(screen.getByText(/code pin requis/i)).toBeInTheDocument();
  });

  test('validates PIN format (6 digits)', async () => {
    const user = userEvent.setup();
    renderWithAuthContext(<Login />);
    
    const usernameInput = screen.getByLabelText(/nom d'utilisateur/i);
    const pinInput = screen.getByLabelText(/code pin/i);
    const submitButton = screen.getByRole('button', { name: /se connecter/i });
    
    await user.type(usernameInput, 'doctor_test');
    await user.type(pinInput, '123'); // PIN trop court
    await user.click(submitButton);
    
    expect(screen.getByText(/le code pin doit contenir 6 chiffres/i)).toBeInTheDocument();
  });

  test('submits form with valid credentials', async () => {
    const user = userEvent.setup();
    mockLogin.mockResolvedValue({ success: true });
    
    renderWithAuthContext(<Login />);
    
    const usernameInput = screen.getByLabelText(/nom d'utilisateur/i);
    const pinInput = screen.getByLabelText(/code pin/i);
    const submitButton = screen.getByRole('button', { name: /se connecter/i });
    
    await user.type(usernameInput, 'doctor_test');
    await user.type(pinInput, '123456');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('doctor_test', '123456');
    });
  });

  test('displays error message on login failure', async () => {
    const user = userEvent.setup();
    mockLogin.mockRejectedValue(new Error('Identifiants invalides'));
    
    renderWithAuthContext(<Login />);
    
    const usernameInput = screen.getByLabelText(/nom d'utilisateur/i);
    const pinInput = screen.getByLabelText(/code pin/i);
    const submitButton = screen.getByRole('button', { name: /se connecter/i });
    
    await user.type(usernameInput, 'doctor_test');
    await user.type(pinInput, '123456');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/identifiants invalides/i)).toBeInTheDocument();
    });
  });

  test('disables submit button during loading', async () => {
    const user = userEvent.setup();
    mockLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));
    
    renderWithAuthContext(<Login />);
    
    const usernameInput = screen.getByLabelText(/nom d'utilisateur/i);
    const pinInput = screen.getByLabelText(/code pin/i);
    const submitButton = screen.getByRole('button', { name: /se connecter/i });
    
    await user.type(usernameInput, 'doctor_test');
    await user.type(pinInput, '123456');
    await user.click(submitButton);
    
    expect(submitButton).toBeDisabled();
    expect(screen.getByText(/connexion en cours/i)).toBeInTheDocument();
  });
});
