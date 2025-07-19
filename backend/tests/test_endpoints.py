import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db
import tempfile
import os
from unittest.mock import Mock, patch

# Test client
client = TestClient(app)


# Mock database for tests
@pytest.fixture
def mock_db():
    mock = Mock()
    app.dependency_overrides[get_db] = lambda: mock
    yield mock
    app.dependency_overrides = {}


@pytest.fixture
def auth_headers():
    """Fixture pour les headers d'authentification"""
    # Mock login to get token
    response = client.post(
        "/auth/login", json={"username": "test_doctor", "pin": "123456"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuthEndpoints:
    def test_login_success(self, mock_db):
        """Test de connexion réussie"""
        # Mock user in database
        mock_user = Mock()
        mock_user.username = "test_doctor"
        mock_user.hashed_pin = "$2b$12$..."  # Mock hashed PIN
        mock_user.specialty = "Médecine Esthétique"
        mock_db.query().filter().first.return_value = mock_user

        with patch("backend.auth.verify_pin", return_value=True):
            response = client.post(
                "/auth/login", json={"username": "test_doctor", "pin": "123456"}
            )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "test_doctor"

    def test_login_invalid_credentials(self, mock_db):
        """Test de connexion avec identifiants invalides"""
        mock_db.query().filter().first.return_value = None

        response = client.post(
            "/auth/login", json={"username": "wrong_user", "pin": "000000"}
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_missing_fields(self):
        """Test de connexion avec champs manquants"""
        response = client.post(
            "/auth/login",
            json={
                "username": "test_doctor"
                # PIN manquant
            },
        )

        assert response.status_code == 422  # Validation error

    def test_protected_endpoint_without_token(self):
        """Test d'accès à un endpoint protégé sans token"""
        response = client.get("/patients")
        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self):
        """Test d'accès avec token invalide"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/patients", headers=headers)
        assert response.status_code == 401


class TestPatientEndpoints:
    def test_create_patient_success(self, mock_db, auth_headers):
        """Test de création de patient réussie"""
        patient_data = {"age": 35, "gender": "female", "skin_type": "normal"}

        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        response = client.post("/patients", json=patient_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["age"] == 35
        assert data["gender"] == "female"
        assert data["skin_type"] == "normal"
        assert "id" in data

    def test_create_patient_invalid_age(self, auth_headers):
        """Test de création avec âge invalide"""
        patient_data = {
            "age": -5,  # Âge invalide
            "gender": "female",
            "skin_type": "normal",
        }

        response = client.post("/patients", json=patient_data, headers=auth_headers)

        assert response.status_code == 422

    def test_get_patients_list(self, mock_db, auth_headers):
        """Test de récupération de la liste des patients"""
        mock_patients = [
            Mock(id="1", age=35, gender="female", skin_type="normal"),
            Mock(id="2", age=42, gender="male", skin_type="oily"),
        ]
        mock_db.query().all.return_value = mock_patients

        response = client.get("/patients", headers=auth_headers)

        assert response.status_code == 200
        assert len(response.json()) == 2


class TestSimulationEndpoints:
    def test_create_simulation_success(self, mock_db, auth_headers):
        """Test de création de simulation réussie"""
        simulation_data = {
            "patient_id": "patient-123",
            "intervention_type": "lips",
            "dose": 2.0,
            "original_image_url": "/uploads/original.jpg",
        }

        mock_db.add.return_value = None
        mock_db.commit.return_value = None

        with patch("backend.ai_generator.process_simulation") as mock_ai:
            mock_ai.return_value = "/uploads/result.jpg"

            response = client.post(
                "/simulations", json=simulation_data, headers=auth_headers
            )

        assert response.status_code == 201
        data = response.json()
        assert data["intervention_type"] == "lips"
        assert data["dose"] == 2.0
        assert data["status"] == "completed"

    def test_create_simulation_invalid_intervention(self, auth_headers):
        """Test avec type d'intervention invalide"""
        simulation_data = {
            "patient_id": "patient-123",
            "intervention_type": "invalid_type",
            "dose": 2.0,
            "original_image_url": "/uploads/original.jpg",
        }

        response = client.post(
            "/simulations", json=simulation_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_simulation_invalid_dose(self, auth_headers):
        """Test avec dose invalide"""
        simulation_data = {
            "patient_id": "patient-123",
            "intervention_type": "lips",
            "dose": -1.0,  # Dose négative
            "original_image_url": "/uploads/original.jpg",
        }

        response = client.post(
            "/simulations", json=simulation_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_get_simulation_by_id(self, mock_db, auth_headers):
        """Test de récupération d'une simulation par ID"""
        mock_simulation = Mock()
        mock_simulation.id = "sim-123"
        mock_simulation.intervention_type = "lips"
        mock_simulation.dose = 2.0
        mock_simulation.status = "completed"

        mock_db.query().filter().first.return_value = mock_simulation

        response = client.get("/simulations/sim-123", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "sim-123"

    def test_get_simulation_not_found(self, mock_db, auth_headers):
        """Test de récupération d'une simulation inexistante"""
        mock_db.query().filter().first.return_value = None

        response = client.get("/simulations/nonexistent", headers=auth_headers)

        assert response.status_code == 404


class TestImageUpload:
    def test_upload_valid_image(self, auth_headers):
        """Test d'upload d'image valide"""
        # Créer un fichier image temporaire
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(b"fake image content")
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as image_file:
                response = client.post(
                    "/upload",
                    files={"file": ("test.jpg", image_file, "image/jpeg")},
                    headers=auth_headers,
                )

            assert response.status_code == 200
            data = response.json()
            assert "filename" in data
            assert "url" in data
            assert data["filename"].endswith(".jpg")

        finally:
            os.unlink(tmp_path)

    def test_upload_invalid_file_type(self, auth_headers):
        """Test d'upload de fichier non-image"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"not an image")
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as text_file:
                response = client.post(
                    "/upload",
                    files={"file": ("test.txt", text_file, "text/plain")},
                    headers=auth_headers,
                )

            assert response.status_code == 400
            assert "Invalid file type" in response.json()["detail"]

        finally:
            os.unlink(tmp_path)

    def test_upload_file_too_large(self, auth_headers):
        """Test d'upload de fichier trop volumineux"""
        # Créer un fichier de plus de 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(large_content)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as large_file:
                response = client.post(
                    "/upload",
                    files={"file": ("large.jpg", large_file, "image/jpeg")},
                    headers=auth_headers,
                )

            assert response.status_code == 413  # Request Entity Too Large

        finally:
            os.unlink(tmp_path)

    def test_upload_no_file(self, auth_headers):
        """Test d'upload sans fichier"""
        response = client.post("/upload", headers=auth_headers)
        assert response.status_code == 422


class TestErrorHandling:
    def test_server_error_handling(self, mock_db, auth_headers):
        """Test de gestion des erreurs serveur"""
        # Simuler une erreur de base de données
        mock_db.query.side_effect = Exception("Database error")

        response = client.get("/patients", headers=auth_headers)
        assert response.status_code == 500

    def test_validation_error_response_format(self):
        """Test du format des erreurs de validation"""
        response = client.post(
            "/auth/login", json={"username": "", "pin": "123"}  # Vide  # Trop court
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)


class TestHealthCheck:
    def test_health_check_endpoint(self):
        """Test du endpoint de santé"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_api_version_endpoint(self):
        """Test du endpoint de version API"""
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "api_name" in data
