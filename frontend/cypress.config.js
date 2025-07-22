const { defineConfig } = require('cypress');

module.exports = defineConfig({
  baseUrl: "http://localhost:3000",
  viewportWidth: 1920,
  viewportHeight: 1080,
  defaultCommandTimeout: 10000,
  requestTimeout: 10000,
  responseTimeout: 10000,
  video: true,
  screenshotOnRunFailure: true,
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    specPattern: "cypress/e2e/**/*.cy.{js,jsx,ts,tsx}",
    supportFile: "cypress/support/e2e.ts"
  },
  env: {
    API_URL: "http://localhost:8000"
  }
});
