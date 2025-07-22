// ***********************************************
// Custom commands for AestheticAI testing
// ***********************************************

import 'cypress-file-upload';

declare global {
  namespace Cypress {
    interface Chainable {
      login(username?: string, pin?: string): Chainable<void>
      createPatient(age?: number, gender?: string, skinType?: string): Chainable<void>
      uploadImage(fileName?: string): Chainable<void>
    }
  }
}

// Login command
Cypress.Commands.add('login', (username = 'doctor_test', pin = '123456') => {
  cy.visit('/');
  cy.get('[data-testid="username-input"]').type(username);
  cy.get('[data-testid="pin-input"]').type(pin);
  cy.get('[data-testid="login-button"]').click();
  cy.wait('@login');
  cy.url().should('include', '/dashboard');
});

// Create patient command
Cypress.Commands.add('createPatient', (age = 35, gender = 'female', skinType = 'normal') => {
  cy.get('[data-testid="new-patient-button"]').click();
  cy.get('[data-testid="age-input"]').type(age.toString());
  cy.get('[data-testid="gender-select"]').select(gender);
  cy.get('[data-testid="skin-type-select"]').select(skinType);
  cy.get('[data-testid="create-patient-button"]').click();
  cy.wait('@createPatient');
});

// Upload image command
Cypress.Commands.add('uploadImage', (fileName = 'test-image.jpg') => {
  // Create a fake image file
  cy.fixture(fileName, 'base64').then(fileContent => {
    cy.get('[data-testid="file-input"]').selectFile({
      contents: Cypress.Buffer.from(fileContent, 'base64'),
      fileName,
      mimeType: 'image/jpeg'
    });
  });
});

export {};
