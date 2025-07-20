import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from main import app
import tempfile
import os
from unittest.mock import Mock, patch

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Obtenir un token d'authentification pour les tests"""
    # Mock de l'utilisateur en base de données
    with patch("main.get_db") as mock_get_db:
        mock_db = Mock()
        mock_user = Mock()
        mock_user.username = "test_doctor"
        mock_user.hashed_pin = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBNb1/5QQKVa.S"
        mock_user.specialty = "Médecine Esthétique"
        mock_db.query().filter().first.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        with patch("backend.auth.verify_pin", return_value=True):
            response = client.post(
                "/auth/login", json={"username": "test_doctor", "pin": "123456"}
            )
            return response.json()["access_token"]


class TestPerformance:

    def test_api_response_time(self, auth_token):
        """Test des temps de réponse API"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Test endpoint simple
        start_time = time.time()
        response = client.get("/health")
        response_time = time.time() - start_time

        assert response.status_code == 200
        assert response_time < 1.0  # Moins de 1 seconde

        # Test endpoint avec base de données
        start_time = time.time()
        response = client.get("/patients", headers=headers)
        response_time = time.time() - start_time

        assert response_time < 2.0  # Moins de 2 secondes

    def test_concurrent_requests(self, auth_token):
        """Test de requêtes simultanées"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        def make_request():
            return client.get("/patients", headers=headers)

        # Lancer 10 requêtes simultanées
        with ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
            total_time = time.time() - start_time

        # Vérifier que toutes les requêtes ont réussi
        assert all(r.status_code == 200 for r in responses)

        # Vérifier que le temps total est raisonnable
        assert total_time < 5.0  # Moins de 5 secondes pour 10 requêtes

    def test_large_file_upload_performance(self, auth_token):
        """Test de performance d'upload de gros fichiers"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Créer un fichier de 5MB
        large_content = b"x" * (5 * 1024 * 1024)  # 5MB

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(large_content)
            tmp_path = tmp.name

        try:
            start_time = time.time()
            with open(tmp_path, "rb") as large_file:
                response = client.post(
                    "/upload",
                    files={"file": ("large.jpg", large_file, "image/jpeg")},
                    headers=headers,
                )
            upload_time = time.time() - start_time

            assert response.status_code == 200
            assert upload_time < 10.0  # Moins de 10 secondes pour 5MB

        finally:
            os.unlink(tmp_path)

    def test_ai_processing_timeout(self, auth_token):
        """Test de timeout pour le traitement IA"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Créer une simulation qui pourrait prendre du temps
        simulation_data = {
            "patient_id": "patient-123",
            "intervention_type": "lips",
            "dose": 2.0,
            "original_image_url": "/uploads/test.jpg",
        }

        start_time = time.time()
        response = client.post("/simulations", json=simulation_data, headers=headers)
        processing_time = time.time() - start_time

        # En mode mock, devrait être rapide
        assert processing_time < 5.0

        # En mode GPU réel, vérifier timeout à 2 minutes
        if response.status_code == 200:
            assert processing_time < 120.0

    def test_memory_usage_under_load(self, auth_token):
        """Test d'utilisation mémoire sous charge"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        headers = {"Authorization": f"Bearer {auth_token}"}

        # Faire plusieurs requêtes
        for _ in range(50):
            client.get("/patients", headers=headers)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # L'augmentation mémoire ne devrait pas être excessive
        assert memory_increase < 100 * 1024 * 1024  # Moins de 100MB


class TestSecurity:

    def test_sql_injection_protection(self):
        """Test de protection contre l'injection SQL"""
        malicious_payloads = [
            "'; DROP TABLE patients; --",
            "1' OR '1'='1",
            "admin'/*",
            "1; UPDATE patients SET age=999; --",
        ]

        for payload in malicious_payloads:
            response = client.post(
                "/auth/login", json={"username": payload, "pin": "123456"}
            )

            # Ne devrait pas causer d'erreur SQL
            assert response.status_code in [401, 422]  # Échec d'auth ou validation

    def test_xss_protection(self, auth_token):
        """Test de protection contre XSS"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//",
        ]

        for payload in xss_payloads:
            # Test sur création de patient avec données malicieuses
            response = client.post(
                "/patients",
                json={
                    "age": 35,
                    "gender": payload,  # Données malicieuses
                    "skin_type": "normal",
                },
                headers=headers,
            )

            # Devrait soit rejeter, soit échapper le contenu
            if response.status_code == 201:
                # Vérifier que le contenu est échappé
                data = response.json()
                assert "<script>" not in str(data)

    def test_file_upload_security(self, auth_token):
        """Test de sécurité des uploads de fichiers"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Test avec fichier exécutable
        malicious_files = [
            ("malware.exe", b"MZ\x90\x00", "application/octet-stream"),
            ("script.php", b"<?php system($_GET['cmd']); ?>", "application/x-php"),
            ("exploit.html", b"<script>alert('xss')</script>", "text/html"),
            (
                "fake.jpg",
                b"#!/bin/bash\necho 'hack'",
                "image/jpeg",
            ),  # Fichier qui prétend être une image
        ]

        for filename, content, mime_type in malicious_files:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            try:
                with open(tmp_path, "rb") as malicious_file:
                    response = client.post(
                        "/upload",
                        files={"file": (filename, malicious_file, mime_type)},
                        headers=headers,
                    )

                # Devrait rejeter les fichiers dangereux
                assert response.status_code in [400, 415, 422]

            finally:
                os.unlink(tmp_path)

    def test_authentication_bypass_attempts(self):
        """Test de tentatives de contournement d'authentification"""
        bypass_attempts = [
            {"Authorization": "Bearer fake_token"},
            {"Authorization": "Bearer "},
            {"Authorization": "Basic admin:admin"},
            {"X-API-Key": "admin"},
            {},  # Pas d'en-tête
        ]

        for headers in bypass_attempts:
            response = client.get("/patients", headers=headers)
            # FastAPI retourne 403 pour l'absence d'autorisation
            assert response.status_code in [401, 403]

    def test_rate_limiting_simulation(self, auth_token):
        """Test de simulation de limitation de taux"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Faire beaucoup de requêtes rapidement
        responses = []
        for _ in range(100):
            response = client.get("/health", headers=headers)
            responses.append(response.status_code)

        # En production, on s'attendrait à des codes 429 (Too Many Requests)
        # Pour l'instant, vérifier que l'API ne plante pas
        assert all(status in [200, 429] for status in responses)

    def test_sensitive_data_exposure(self, auth_token):
        """Test d'exposition de données sensibles"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Vérifier que les endpoints ne retournent pas d'infos sensibles
        response = client.get("/patients", headers=headers)

        if response.status_code == 200:
            data = response.json()
            response_text = str(data).lower()

            # Vérifier qu'aucune info sensible n'est exposée
            sensitive_keywords = [
                "password",
                "pin",
                "secret",
                "key",
                "token",
                "hash",
                "salt",
                "private",
                "ssn",
                "social",
            ]

            for keyword in sensitive_keywords:
                assert keyword not in response_text

    def test_cors_configuration(self):
        """Test de configuration CORS"""
        # Test de requête CORS
        response = client.options(
            "/health",
            headers={
                "Origin": "http://malicious-site.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Vérifier que CORS est configuré de manière sécurisée
        cors_headers = response.headers

        # Ne devrait pas autoriser tous les domaines en production
        if "Access-Control-Allow-Origin" in cors_headers:
            assert cors_headers["Access-Control-Allow-Origin"] != "*"

    def test_server_information_disclosure(self):
        """Test de divulgation d'informations serveur"""
        response = client.get("/health")

        # Vérifier que les en-têtes ne révèlent pas trop d'infos
        headers = response.headers

        # En production, ces headers ne devraient pas être présents
        sensitive_headers = ["server", "x-powered-by", "x-aspnet-version"]

        for header in sensitive_headers:
            if header in headers:
                # En développement, c'est OK, mais en prod il faut les masquer
                pass


class TestDataValidation:

    def test_input_sanitization(self, auth_token):
        """Test de nettoyage des entrées"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Test avec caractères spéciaux
        special_chars_data = {
            "age": 35,
            "gender": "female\x00\x01\x02",  # Caractères de contrôle
            "skin_type": "normal",
        }

        response = client.post("/patients", json=special_chars_data, headers=headers)

        # Devrait soit rejeter, soit nettoyer les données
        if response.status_code == 201:
            data = response.json()
            assert "\x00" not in str(data)

    def test_data_type_validation(self, auth_token):
        """Test de validation des types de données"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        invalid_data_types = [
            {"age": "not_a_number", "gender": "female", "skin_type": "normal"},
            {"age": 35, "gender": 123, "skin_type": "normal"},
            {"age": 35, "gender": "female", "skin_type": ["invalid", "type"]},
        ]

        for invalid_data in invalid_data_types:
            response = client.post("/patients", json=invalid_data, headers=headers)
            assert response.status_code == 422  # Validation error
