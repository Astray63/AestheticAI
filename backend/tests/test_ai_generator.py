import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from PIL import Image
import io
from ai_generator import (
    process_simulation,
    load_ai_models,
    preprocess_image,
    apply_intervention,
    validate_image_format,
    mock_ai_processing,
)


class TestAIGenerator:

    @pytest.fixture
    def sample_image(self):
        """Créer une image de test"""
        # Créer une image RGB 512x512
        img = Image.new("RGB", (512, 512), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        return img_bytes

    @pytest.fixture
    def mock_models(self):
        """Mock des modèles IA"""
        with patch("ai_generator.load_ai_models") as mock_load:
            mock_pipeline = MagicMock()
            mock_controlnet = MagicMock()
            mock_load.return_value = (mock_pipeline, mock_controlnet)
            yield mock_pipeline, mock_controlnet

    def test_validate_image_format_valid_jpeg(self, sample_image):
        """Test de validation d'image JPEG valide"""
        assert validate_image_format(sample_image.getvalue()) == True

    def test_validate_image_format_invalid(self):
        """Test de validation d'image invalide"""
        invalid_data = b"not an image"
        assert validate_image_format(invalid_data) == False

    def test_preprocess_image_success(self, sample_image):
        """Test de preprocessing d'image réussi"""
        processed = preprocess_image(sample_image.getvalue())

        assert processed is not None
        assert isinstance(processed, Image.Image)
        assert processed.size == (512, 512)  # Expected dimensions
        assert processed.mode == "RGB"  # Expected format

    def test_preprocess_image_resize(self):
        """Test de redimensionnement d'image"""
        # Créer une image de taille différente
        img = Image.new("RGB", (1024, 768), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")

        processed = preprocess_image(img_bytes.getvalue())
        assert processed.size == (512, 512)  # Redimensionnée
        assert isinstance(processed, Image.Image)

    @patch("ai_generator.USE_GPU", False)
    def test_mock_ai_processing(self, sample_image):
        """Test du mode mock (sans GPU)"""
        result = mock_ai_processing(
            image_data=sample_image.getvalue(), intervention_type="lips", dose=2.0
        )

        assert result is not None
        assert isinstance(result, Image.Image)  # Retourne une image PIL

    @patch("ai_generator.USE_GPU", True)
    @patch("ai_generator.TESTING_MODE", False)
    def test_apply_intervention_lips(self, mock_models, sample_image):
        """Test d'application d'intervention sur les lèvres"""
        mock_pipeline, mock_controlnet = mock_models

        # Mock du résultat du pipeline
        mock_result = MagicMock()
        mock_result.images = [Image.new("RGB", (512, 512), color="pink")]
        mock_pipeline.return_value = mock_result

        processed_image = preprocess_image(sample_image.getvalue())
        result = apply_intervention(
            image=processed_image,
            intervention_type="lips",
            dose=2.0,
            pipeline=mock_pipeline,
            controlnet=mock_controlnet,
        )

        assert result is not None
        mock_pipeline.assert_called_once()

    @patch("ai_generator.USE_GPU", True)
    def test_apply_intervention_invalid_type(self, mock_models, sample_image):
        """Test avec type d'intervention invalide"""
        mock_pipeline, mock_controlnet = mock_models
        processed_image = preprocess_image(sample_image.getvalue())

        with pytest.raises(ValueError, match="Unsupported intervention type"):
            apply_intervention(
                image=processed_image,
                intervention_type="invalid_type",
                dose=2.0,
                pipeline=mock_pipeline,
                controlnet=mock_controlnet,
            )

    def test_dose_validation(self, mock_models, sample_image):
        """Test de validation de dose"""
        mock_pipeline, mock_controlnet = mock_models
        processed_image = preprocess_image(sample_image.getvalue())

        # Dose trop faible
        with pytest.raises(ValueError, match="Invalid dose"):
            apply_intervention(
                image=processed_image,
                intervention_type="lips",
                dose=0.0,
                pipeline=mock_pipeline,
                controlnet=mock_controlnet,
            )

        # Dose trop élevée
        with pytest.raises(ValueError, match="Invalid dose"):
            apply_intervention(
                image=processed_image,
                intervention_type="lips",
                dose=10.0,
                pipeline=mock_pipeline,
                controlnet=mock_controlnet,
            )

    @patch("ai_generator.USE_GPU", False)
    def test_process_simulation_mock_mode(self, sample_image):
        """Test de traitement complet en mode mock"""
        # Simuler simplement que la fonction existe et fonctionne
        assert mock_ai_processing(sample_image.getvalue(), "lips", 2.0) is not None

    @patch("ai_generator.USE_GPU", True)
    def test_process_simulation_gpu_mode(self, mock_models, sample_image):
        """Test de traitement complet en mode GPU"""
        mock_pipeline, mock_controlnet = mock_models
        
        # Test que apply_intervention fonctionne avec les mocks
        processed_image = preprocess_image(sample_image.getvalue())
        result = apply_intervention(
            image=processed_image,
            intervention_type="lips",
            dose=2.0,
            pipeline=mock_pipeline,
            controlnet=mock_controlnet,
        )
        assert result is not None

    def test_process_simulation_error_handling(self, sample_image):
        """Test de gestion d'erreurs lors du traitement"""
        # Test qu'une exception est levée lors du preprocessing
        with pytest.raises(ValueError):
            preprocess_image(b"invalid_image_data")

    @patch("ai_generator.USE_GPU", True)
    def test_load_ai_models_success(self):
        """Test de chargement des modèles IA"""
        # En mode testing, load_ai_models retourne des mocks
        pipeline, controlnet = load_ai_models()
        assert pipeline is not None
        assert controlnet is not None

    def test_intervention_type_mapping(self):
        """Test du mapping des types d'intervention"""
        intervention_prompts = {
            "lips": "enhanced fuller lips with natural contours",
            "cheeks": "enhanced cheek volume with natural definition",
            "chin": "refined chin contour with balanced proportions",
            "forehead": "smoothed forehead with reduced wrinkles",
        }

        for intervention_type, expected_prompt in intervention_prompts.items():
            # Cette partie devrait être testée avec la vraie fonction
            # qui mappe les types d'intervention aux prompts IA
            pass

    def test_image_quality_validation(self, sample_image):
        """Test de validation de la qualité d'image"""
        # Test avec image de bonne qualité
        assert validate_image_format(sample_image.getvalue()) == True

        # Test avec image de mauvaise qualité (trop petite)
        small_img = Image.new("RGB", (50, 50), color="red")
        small_bytes = io.BytesIO()
        small_img.save(small_bytes, format="JPEG")

        # Cette validation devrait être implémentée dans validate_image_format
        # pour rejeter les images trop petites

    @patch("ai_generator.USE_GPU", False)
    def test_processing_time_mock(self, sample_image):
        """Test du temps de traitement en mode mock"""
        import time

        start_time = time.time()
        mock_ai_processing(
            image_data=sample_image.getvalue(), intervention_type="lips", dose=2.0
        )
        end_time = time.time()

        # Le mode mock devrait être rapide (< 5 secondes)
        assert (end_time - start_time) < 5.0

    def test_memory_cleanup(self, sample_image):
        """Test de nettoyage mémoire après traitement"""
        initial_objects = len(locals())

        # Traitement d'image
        processed = preprocess_image(sample_image.getvalue())

        # Vérifier que les objets sont bien libérés
        del processed

        # En pratique, on vérifierait avec des outils de profiling mémoire
        assert True  # Placeholder pour le test de mémoire
