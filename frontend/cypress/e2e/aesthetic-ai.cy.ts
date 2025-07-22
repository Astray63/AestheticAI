describe('AestheticAI E2E Tests', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    cy.clearLocalStorage();
  });

  it('should complete full user workflow', () => {
    // 1. Visit the application
    cy.visit('/');
    
    // 2. Login
    cy.get('[data-testid="username-input"]').should('be.visible');
    cy.get('[data-testid="username-input"]').type('doctor_test');
    cy.get('[data-testid="pin-input"]').type('123456');
    cy.get('[data-testid="login-button"]').click();
    
    // Wait for login API call
    cy.wait('@login');
    
    // 3. Verify dashboard is loaded
    cy.url().should('include', '/dashboard');
    cy.contains('Tableau de bord').should('be.visible');
    
    // 4. Create a new patient
    cy.get('[data-testid="new-patient-button"]').click();
    cy.get('[data-testid="age-input"]').type('35');
    cy.get('[data-testid="gender-select"]').select('female');
    cy.get('[data-testid="skin-type-select"]').select('normal');
    cy.get('[data-testid="create-patient-button"]').click();
    
    // Wait for patient creation
    cy.wait('@createPatient');
    
    // 5. Verify patient was created
    cy.contains('Patient créé avec succès').should('be.visible');
    
    // 6. Start a new simulation
    cy.get('[data-testid="new-simulation-button"]').click();
    
    // 7. Select intervention type and dose
    cy.get('[data-testid="intervention-select"]').select('lips');
    cy.get('[data-testid="dose-input"]').clear().type('2.0');
    
    // 8. Upload an image (mock file upload)
    cy.get('[data-testid="file-input"]').selectFile({
      contents: Cypress.Buffer.from('fake-image-content'),
      fileName: 'patient.jpg',
      mimeType: 'image/jpeg'
    });
    
    // Wait for upload
    cy.wait('@uploadImage');
    
    // 9. Start simulation
    cy.get('[data-testid="simulate-button"]').click();
    
    // Wait for simulation creation
    cy.wait('@createSimulation');
    
    // 10. Verify simulation results
    cy.contains('Résultat de la simulation').should('be.visible');
    cy.get('[data-testid="before-image"]').should('be.visible');
    cy.get('[data-testid="after-image"]').should('be.visible');
    
    // 11. Test download functionality
    cy.get('[data-testid="download-button"]').should('be.visible');
    
    // 12. Test new simulation button
    cy.get('[data-testid="new-simulation-button"]').should('be.visible');
  });

  it('should handle login errors gracefully', () => {
    // Mock login error
    cy.intercept('POST', '**/auth/login', {
      statusCode: 401,
      body: { detail: 'Invalid credentials' }
    }).as('loginError');
    
    cy.visit('/');
    cy.get('[data-testid="username-input"]').type('wrong_user');
    cy.get('[data-testid="pin-input"]').type('000000');
    cy.get('[data-testid="login-button"]').click();
    
    cy.wait('@loginError');
    cy.contains('Identifiants invalides').should('be.visible');
  });

  it('should handle simulation errors', () => {
    // Login first
    cy.login();
    
    // Mock simulation error
    cy.intercept('POST', '**/simulations', {
      statusCode: 500,
      body: { detail: 'AI processing failed' }
    }).as('simulationError');
    
    // Create patient and start simulation
    cy.createPatient();
    cy.get('[data-testid="new-simulation-button"]').click();
    cy.get('[data-testid="intervention-select"]').select('lips');
    cy.get('[data-testid="dose-input"]').clear().type('2.0');
    
    cy.get('[data-testid="file-input"]').selectFile({
      contents: Cypress.Buffer.from('fake-image-content'),
      fileName: 'patient.jpg',
      mimeType: 'image/jpeg'
    });
    
    cy.get('[data-testid="simulate-button"]').click();
    cy.wait('@simulationError');
    
    cy.contains('Erreur lors du traitement').should('be.visible');
  });

  it('should persist login state on page refresh', () => {
    // Login
    cy.login();
    
    // Reload page
    cy.reload();
    
    // Should still be logged in
    cy.url().should('include', '/dashboard');
    cy.contains('Tableau de bord').should('be.visible');
  });

  it('should logout successfully', () => {
    // Login first
    cy.login();
    
    // Logout
    cy.get('[data-testid="logout-button"]').click();
    
    // Should redirect to login page
    cy.url().should('not.include', '/dashboard');
    cy.get('[data-testid="username-input"]').should('be.visible');
  });

  it('should validate form inputs', () => {
    cy.visit('/');
    
    // Try to login with empty fields
    cy.get('[data-testid="login-button"]').click();
    cy.contains('Nom d\'utilisateur requis').should('be.visible');
    cy.contains('Code PIN requis').should('be.visible');
    
    // Try with invalid PIN format
    cy.get('[data-testid="username-input"]').type('doctor_test');
    cy.get('[data-testid="pin-input"]').type('123'); // Too short
    cy.get('[data-testid="login-button"]').click();
    cy.contains('Le code PIN doit contenir 6 chiffres').should('be.visible');
  });

  it('should handle file upload validation', () => {
    cy.login();
    cy.createPatient();
    
    cy.get('[data-testid="new-simulation-button"]').click();
    cy.get('[data-testid="intervention-select"]').select('lips');
    
    // Try to upload invalid file type
    cy.get('[data-testid="file-input"]').selectFile({
      contents: Cypress.Buffer.from('not-an-image'),
      fileName: 'document.txt',
      mimeType: 'text/plain'
    });
    
    cy.contains('Format de fichier non supporté').should('be.visible');
  });
});
