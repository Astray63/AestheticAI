// ***********************************************************
// This example support/e2e.ts is processed and
// loaded automatically before your test files.
// ***********************************************************

import './commands';

// Intercept API calls for consistent testing
beforeEach(() => {
  // Mock API responses
  cy.intercept('POST', '**/auth/login', {
    statusCode: 200,
    body: {
      access_token: 'mock-jwt-token',
      token_type: 'bearer',
      user: {
        id: '1',
        username: 'doctor_test',
        specialty: 'Médecine Esthétique'
      }
    }
  }).as('login');

  cy.intercept('POST', '**/patients', {
    statusCode: 201,
    body: {
      id: 'patient-123',
      age: 35,
      gender: 'female',
      skin_type: 'normal',
      created_at: new Date().toISOString()
    }
  }).as('createPatient');

  cy.intercept('POST', '**/simulations', {
    statusCode: 201,
    body: {
      id: 'simulation-456',
      patient_id: 'patient-123',
      intervention_type: 'lips',
      dose: 2.0,
      original_image_url: '/uploads/original_123.jpg',
      result_image_url: '/uploads/result_123.jpg',
      status: 'completed',
      created_at: new Date().toISOString()
    }
  }).as('createSimulation');

  cy.intercept('POST', '**/upload', {
    statusCode: 200,
    body: {
      filename: 'uploaded_image_123.jpg',
      url: '/uploads/uploaded_image_123.jpg'
    }
  }).as('uploadImage');
});
