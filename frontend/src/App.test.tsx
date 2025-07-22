import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders AestheticAI application', () => {
  render(<App />);
  const titleElements = screen.getAllByRole('heading', { name: /AestheticAI/i });
  expect(titleElements[0]).toBeInTheDocument();
});

test('renders login form', () => {
  render(<App />);
  const loginText = screen.getByText(/connexion/i);
  expect(loginText).toBeInTheDocument();
});
