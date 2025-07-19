# Instructions Copilot - Application Médecine Esthétique

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Context du projet
Cette application est destinée aux professionnels de la médecine esthétique pour simuler des interventions avant/après avec IA générative.

## Stack technique
- **Backend**: FastAPI (Python) avec intégration Stable Diffusion/ControlNet
- **Frontend**: React + Tailwind CSS (responsive mobile-first)
- **IA**: Stable Diffusion + ControlNet pour modifications faciales réalistes
- **Base de données**: SQLite (MVP) → PostgreSQL (production)
- **Sécurité**: Authentification PIN, chiffrement des données patients

## Conventions de code
- Code en français pour les commentaires métier spécifiques
- Variables et fonctions en anglais
- Interface utilisateur en français
- Respect RGPD pour données médicales
- Style médical professionnel et épuré

## Fonctionnalités principales
1. Upload/capture photo patient
2. Sélection zones d'intervention (lèvres, pommettes, menton...)
3. Paramétrage dose/quantité (+3mm, etc.)
4. Génération IA réaliste en <2min
5. Visualisation avant/après
6. Sécurisation données patients

## Priorités
- Performance IA (génération rapide)
- Interface intuitive pour professionnels santé
- Sécurité et confidentialité maximales
- Rendu photo-réaliste et médical
