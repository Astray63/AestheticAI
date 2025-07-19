# 🧪 Guide Complet des Tests AestheticAI

Ce guide vous explique comment exécuter et maintenir la suite complète de tests automatiques pour l'application AestheticAI.

## 📋 Table des Matières

1. [Installation et Configuration](#installation-et-configuration)
2. [Tests Frontend](#tests-frontend)
3. [Tests Backend](#tests-backend) 
4. [Tests E2E](#tests-e2e)
5. [Tests de Sécurité](#tests-de-sécurité)
6. [CI/CD](#cicd)
7. [Rapports et Métriques](#rapports-et-métriques)
8. [Bonnes Pratiques](#bonnes-pratiques)

## 🛠️ Installation et Configuration

### Prérequis

- **Node.js** 18+ 
- **Python** 3.11+
- **npm** ou **yarn**
- **Git**

### Configuration Initiale

```bash
# Cloner le repository
git clone <votre-repo>
cd AestheticAI

# Installer les dépendances frontend
cd frontend
npm install

# Installer les dépendances backend  
cd ../backend
python -m venv ../venv
source ../venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx pytest-mock

# Retourner à la racine
cd ..
```

## 🎨 Tests Frontend

### Tests Unitaires

```bash
cd frontend

# Exécuter tous les tests
npm test

# Tests avec couverture
npm run test:coverage

# Tests en mode CI (une seule exécution)
npm run test:ci

# Tests spécifiques
npm test -- --testNamePattern="Login"
npm test -- src/components/Login.test.tsx
```

### Linting et Formatage

```bash
# Linting
npm run lint
npm run lint:fix

# Formatage
npm run format
npm run format:check

# Vérification des types TypeScript
npm run type-check
```

### Tests d'Intégration Frontend

```bash
# Tests d'intégration uniquement
npm run test:integration

# Tests avec MSW (Mock Service Worker)
npm test -- --testNamePattern="integration"
```

## 🐍 Tests Backend

### Tests Unitaires

```bash
cd backend
source ../venv/bin/activate

# Tous les tests
pytest

# Tests avec couverture détaillée
pytest --cov=. --cov-report=html --cov-report=term-missing

# Tests spécifiques
pytest tests/test_auth.py
pytest tests/test_endpoints.py::TestAuthEndpoints::test_login_success

# Tests par catégorie
pytest -m unit
pytest -m integration
pytest -m security
```

### Linting et Formatage

```bash
# Installation des outils
pip install flake8 black mypy

# Linting
flake8 . --max-line-length=88 --exclude=__pycache__,venv

# Formatage
black .
black --check .  # Vérification sans modification

# Type checking
mypy . --ignore-missing-imports
```

### Tests de Performance

```bash
# Tests de performance et charge
pytest tests/test_performance_security.py::TestPerformance -v

# Tests de sécurité
pytest tests/test_performance_security.py::TestSecurity -v
```

## 🎭 Tests E2E

### Configuration Cypress

```bash
cd frontend

# Ouvrir l'interface Cypress (développement)
npx cypress open

# Exécuter en mode headless (CI)
npx cypress run

# Tests spécifiques
npx cypress run --spec "cypress/e2e/aesthetic-ai.cy.ts"
```

### Workflow E2E Complet

```bash
# 1. Démarrer le backend
cd backend
source ../venv/bin/activate
export USE_GPU=false
python run.py &

# 2. Démarrer le frontend  
cd ../frontend
npm start &

# 3. Attendre que les serveurs soient prêts (30s)
sleep 30

# 4. Exécuter les tests E2E
npx cypress run

# 5. Nettoyer les processus
pkill -f "python run.py"
pkill -f "npm start"
```

## 🔒 Tests de Sécurité

### Audit des Dépendances

```bash
# Frontend
cd frontend
npm audit
npm audit --audit-level=high
npm audit fix

# Backend
cd backend
pip install safety
safety check
safety check --json
```

### Tests de Sécurité Statique

```bash
# Analyse de sécurité Python
pip install bandit
bandit -r . -f json -o bandit-report.json

# Scan de vulnérabilités avec Trivy
docker run --rm -v $(pwd):/workspace aquasec/trivy fs /workspace
```

## 🚀 Script Automatisé

### Exécution Complète

```bash
# Tous les tests
./run-all-tests.sh

# Tests spécifiques
./run-all-tests.sh frontend
./run-all-tests.sh backend  
./run-all-tests.sh e2e
./run-all-tests.sh security
```

### Options du Script

```bash
# Avec verbose
./run-all-tests.sh all --verbose

# Ignorer les erreurs non-critiques
./run-all-tests.sh all --continue-on-error

# Générer seulement le rapport
./run-all-tests.sh all --report-only
```

## 📊 CI/CD avec GitHub Actions

### Configuration

Le pipeline CI/CD se déclenche automatiquement sur :
- **Push** sur `main` et `develop`
- **Pull Requests** vers `main`

### Jobs du Pipeline

1. **frontend-tests** : Tests unitaires + build frontend
2. **backend-tests** : Tests unitaires + sécurité backend  
3. **e2e-tests** : Tests end-to-end complets
4. **security-scan** : Scans de sécurité
5. **build-docker** : Build des images Docker
6. **deploy-staging** : Déploiement en staging
7. **deploy-production** : Déploiement en production

### Secrets GitHub Requis

```bash
# Dans Settings > Secrets and variables > Actions
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-password
```

### Variables d'Environnement

```yaml
# .github/workflows/ci-cd.yml
env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'
  DATABASE_URL: postgresql://testuser:testpassword@localhost:5432/aesthetic_test
  SECRET_KEY: test-secret-key-for-ci
  USE_GPU: false
```

## 📈 Rapports et Métriques

### Couverture de Code

Les rapports de couverture sont générés automatiquement :

```bash
# Frontend
frontend/coverage/lcov-report/index.html

# Backend  
backend/htmlcov/index.html
```

### Métriques Importantes

- **Couverture minimale** : 80%
- **Temps de réponse API** : < 2s
- **Temps de build** : < 5min
- **Tests E2E** : < 10min

### Intégration Codecov

```bash
# Upload manuel
npm install -g codecov
codecov -t YOUR_CODECOV_TOKEN
```

## ✅ Bonnes Pratiques

### Structure des Tests

```
tests/
├── unit/           # Tests unitaires
├── integration/    # Tests d'intégration  
├── e2e/           # Tests end-to-end
├── fixtures/      # Données de test
├── mocks/         # Mocks et stubs
└── utils/         # Utilitaires de test
```

### Conventions de Nommage

```typescript
// ✅ Bon
describe('Login Component', () => {
  test('should display error for invalid credentials', () => {
    // test implementation
  });
});

// ❌ Éviter
describe('test login', () => {
  test('test1', () => {
    // test implementation  
  });
});
```

### Tests Data-Driven

```typescript
// ✅ Utiliser des paramètres
const testCases = [
  { input: 'valid@email.com', expected: true },
  { input: 'invalid-email', expected: false },
];

testCases.forEach(({ input, expected }) => {
  test(`should validate ${input} as ${expected}`, () => {
    expect(validateEmail(input)).toBe(expected);
  });
});
```

### Isolation des Tests

```typescript
// ✅ Nettoyer entre les tests
beforeEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

afterEach(() => {
  cleanup();
});
```

## 🐛 Débogage des Tests

### Tests Frontend qui Échouent

```bash
# Debug mode avec plus de détails
npm test -- --verbose

# Exécuter un seul test
npm test -- --testNamePattern="specific test name"

# Désactiver les mocks pour débugger
jest.unmock('module-name');
```

### Tests Backend qui Échouent

```bash
# Verbose avec détails des assertions
pytest -v -s

# Arrêter au premier échec
pytest -x

# Debug avec pdb
pytest --pdb

# Logs détaillés
pytest --log-cli-level=DEBUG
```

### Tests E2E qui Échouent

```bash
# Mode interactif
npx cypress open

# Vidéos et screenshots
npx cypress run --record

# Debug mode
DEBUG=cypress:* npx cypress run
```

## 🔧 Maintenance des Tests

### Mise à Jour des Dépendances

```bash
# Frontend
npm update
npm audit fix

# Backend
pip list --outdated
pip install --upgrade package-name
```

### Review Périodique

- **Hebdomadaire** : Vérifier les tests flaky
- **Mensuel** : Mise à jour des dépendances  
- **Trimestriel** : Review de la couverture de code
- **Semestriel** : Refactoring des tests obsolètes

### Métriques à Surveiller

- **Temps d'exécution** des tests
- **Taux de réussite** en CI/CD
- **Couverture de code** par module
- **Flakiness** des tests E2E

---

## 📞 Support

- **Documentation** : `/docs`
- **Issues** : GitHub Issues
- **CI/CD Status** : GitHub Actions
- **Coverage Reports** : Codecov

Pour toute question sur les tests, créez une issue avec le label `testing` 🧪
