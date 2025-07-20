import torch
import cv2
import numpy as np
from PIL import Image
import logging
from typing import Tuple, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import os
import io

# Check if we're in test mode
TESTING_MODE = os.getenv("TESTING_MODE", "false").lower() == "true"
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"


# Mock classes for testing
class MockControlNetModel:
    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()


class MockStableDiffusionControlNetPipeline:
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()

    def to(self, device):
        return self

    def enable_xformers_memory_efficient_attention(self):
        pass

    def __call__(self, *args, **kwargs):
        # Return a mock PIL Image
        return type(
            "MockResult", (), {"images": [Image.new("RGB", (512, 512), color="red")]}
        )()


class MockCannyDetector:
    def __call__(self, image):
        return Image.new("L", image.size, color=128)


# Use mocks in testing mode, real imports otherwise
if TESTING_MODE:
    StableDiffusionControlNetPipeline = MockStableDiffusionControlNetPipeline
    ControlNetModel = MockControlNetModel
    CannyDetector = MockCannyDetector
    print("Using mock AI models for testing")
else:
    try:
        from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
        from controlnet_aux import CannyDetector
    except ImportError as e:
        print(f"Warning: Could not import AI models: {e}")
        print("Falling back to mock models")
        StableDiffusionControlNetPipeline = MockStableDiffusionControlNetPipeline
        ControlNetModel = MockControlNetModel
        CannyDetector = MockCannyDetector

from config import DEVICE, MODEL_NAME, CONTROLNET_MODEL, INFERENCE_STEPS, GUIDANCE_SCALE

logger = logging.getLogger(__name__)


class AestheticAIGenerator:
    """Générateur IA pour simulations esthétiques"""

    def __init__(self):
        self.pipeline = None
        self.controlnet = None
        self.canny_detector = CannyDetector()
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def initialize(self):
        """Initialiser les modèles IA"""
        if self.pipeline is None:
            logger.info("Initialisation des modèles IA...")

            # Charger en arrière-plan pour ne pas bloquer
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self._load_models)

            logger.info("Modèles IA initialisés avec succès")

    def _load_models(self):
        """Charger les modèles (exécuté en arrière-plan)"""
        try:
            # Charger ControlNet
            self.controlnet = ControlNetModel.from_pretrained(
                CONTROLNET_MODEL,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            )

            # Charger le pipeline Stable Diffusion
            self.pipeline = StableDiffusionControlNetPipeline.from_pretrained(
                MODEL_NAME,
                controlnet=self.controlnet,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            )

            if DEVICE == "cuda":
                self.pipeline = self.pipeline.to("cuda")
                # Optimisations GPU
                self.pipeline.enable_model_cpu_offload()
                self.pipeline.enable_xformers_memory_efficient_attention()

        except Exception as e:
            logger.error(f"Erreur lors du chargement des modèles: {e}")
            # Fallback: utiliser un générateur mock pour le développement
            self.pipeline = "mock"

    async def generate_aesthetic_simulation(
        self,
        image_path: str,
        intervention_type: str,
        dose: float,
        parameters: dict = None,
    ) -> Tuple[str, float]:
        """
        Générer une simulation d'intervention esthétique

        Args:
            image_path: Chemin vers l'image originale
            intervention_type: Type d'intervention (lips, cheeks, etc.)
            dose: Dose/quantité d'intervention
            parameters: Paramètres additionnels

        Returns:
            Tuple[str, float]: (chemin_image_générée, temps_génération)
        """
        start_time = time.time()

        try:
            # Charger l'image
            original_image = Image.open(image_path).convert("RGB")

            if self.pipeline == "mock":
                # Mode mock pour le développement
                return await self._generate_mock_result(
                    original_image, image_path, intervention_type, dose
                )

            # Préparer le prompt basé sur l'intervention
            prompt = self._create_prompt(intervention_type, dose, parameters)

            # Préparer l'image de contrôle avec Canny
            control_image = self._prepare_control_image(original_image)

            # Générer l'image en arrière-plan
            loop = asyncio.get_event_loop()
            generated_image = await loop.run_in_executor(
                self.executor,
                self._generate_image,
                prompt,
                control_image,
                original_image,
            )

            # Sauvegarder le résultat
            output_path = image_path.replace("original_", "generated_")
            generated_image.save(output_path)

            generation_time = time.time() - start_time
            logger.info(f"Génération terminée en {generation_time:.2f}s")

            return output_path, generation_time

        except Exception as e:
            logger.error(f"Erreur lors de la génération: {e}")
            raise

    def _create_prompt(
        self, intervention_type: str, dose: float, parameters: dict = None
    ) -> str:
        """Créer le prompt pour l'IA selon le type d'intervention"""
        base_prompts = {
            "lips": f"professional medical aesthetic enhancement, natural lip augmentation {dose}ml hyaluronic acid, subtle enhancement, realistic medical photography, professional lighting",
            "cheeks": f"professional cheek enhancement, {dose}ml dermal filler, natural volumization, medical aesthetic photography, realistic results",
            "chin": f"professional chin augmentation, {dose}ml hyaluronic acid, natural definition, medical aesthetic enhancement, realistic lighting",
            "forehead": f"professional forehead treatment, {dose} units botox, natural smoothing, medical aesthetic photography, subtle results",
        }

        prompt = base_prompts.get(
            intervention_type,
            "professional aesthetic enhancement, natural results, medical photography",
        )
        prompt += ", high quality, detailed, photorealistic, professional medical photography, natural lighting"

        return prompt

    def _prepare_control_image(self, image: Image.Image) -> Image.Image:
        """Préparer l'image de contrôle avec détection Canny"""
        # Redimensionner si nécessaire
        if max(image.size) > 768:
            image = image.resize((768, int(768 * image.size[1] / image.size[0])))

        # Appliquer Canny
        control_image = self.canny_detector(image)
        return control_image

    def _generate_image(
        self, prompt: str, control_image: Image.Image, original_image: Image.Image
    ) -> Image.Image:
        """Générer l'image avec le pipeline IA"""
        negative_prompt = "unrealistic, fake, artificial, exaggerated, cartoon, distorted, blurry, low quality"

        result = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=control_image,
            num_inference_steps=INFERENCE_STEPS,
            guidance_scale=GUIDANCE_SCALE,
            controlnet_conditioning_scale=0.8,
        )

        return result.images[0]

    async def _generate_mock_result(
        self,
        original_image: Image.Image,
        image_path: str,
        intervention_type: str,
        dose: float,
    ) -> Tuple[str, float]:
        """Générer un résultat mock pour le développement"""
        logger.info(f"Génération MOCK pour {intervention_type} avec dose {dose}")

        # Simuler le temps de traitement
        await asyncio.sleep(2)

        # Créer une version légèrement modifiée (simulée)
        modified_image = original_image.copy()

        # Ajouter un overlay subtil pour simuler la modification
        if intervention_type == "lips":
            # Simulation très basique - dans la vraie version, ControlNet ferait le travail
            modified_image = self._apply_mock_enhancement(modified_image, "lips", dose)

        # Sauvegarder
        output_path = image_path.replace("original_", "generated_mock_")
        modified_image.save(output_path)

        return output_path, 2.0

    def _apply_mock_enhancement(
        self, image: Image.Image, area: str, dose: float
    ) -> Image.Image:
        """Application mock d'une modification (pour le développement)"""
        # Cette fonction sera remplacée par la vraie IA
        # Pour l'instant, on retourne l'image originale avec un petit ajustement

        # Convertir en array numpy pour traitement
        img_array = np.array(image)

        if area == "lips":
            # Simulation très basique d'augmentation des lèvres
            # Dans la réalité, ControlNet + Stable Diffusion feront ce travail
            height, width = img_array.shape[:2]

            # Zone approximative des lèvres (centre-bas du visage)
            lip_region = img_array[
                int(height * 0.65) : int(height * 0.85),
                int(width * 0.3) : int(width * 0.7),
            ]

            # Augmenter légèrement la saturation pour simuler l'effet
            if len(lip_region) > 0:
                lip_region = np.clip(lip_region * 1.1, 0, 255).astype(np.uint8)
                img_array[
                    int(height * 0.65) : int(height * 0.85),
                    int(width * 0.3) : int(width * 0.7),
                ] = lip_region

        return Image.fromarray(img_array)


# Instance globale du générateur IA
ai_generator = AestheticAIGenerator()


# Fonctions utilitaires pour les tests et l'API
def load_ai_models() -> bool:
    """Charger les modèles IA"""
    return ai_generator.load_models()


def preprocess_image(image) -> Image.Image:
    """Préprocesser une image"""
    # Handle bytes input
    if isinstance(image, bytes):
        import io

        image = Image.open(io.BytesIO(image))

    # Ensure we have a PIL Image
    if not isinstance(image, Image.Image):
        raise ValueError("Input must be a PIL Image or bytes")

    # Convert to RGB if needed
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Redimensionner à 512x512 pour Stable Diffusion
    image = image.resize((512, 512), Image.Resampling.LANCZOS)
    return image


def apply_intervention(
    image: Image.Image, intervention_type: str, dose: float, parameters: dict = None
) -> Image.Image:
    """Appliquer une intervention"""
    if parameters is None:
        parameters = {}
    # Use mock processing since we don't have the full AI pipeline in test mode
    return mock_ai_processing(image, intervention_type, dose)


def validate_image_format(image_path: str) -> bool:
    """Valider le format d'une image"""
    try:
        if isinstance(image_path, bytes):
            # Handle bytes input by creating a temporary image
            import io

            with Image.open(io.BytesIO(image_path)) as img:
                return img.format in ["JPEG", "PNG", "WEBP"]
        else:
            with Image.open(image_path) as img:
                return img.format in ["JPEG", "PNG", "WEBP"]
    except Exception:
        return False


def mock_ai_processing(
    image: Image.Image, intervention_type: str, dose: float
) -> Image.Image:
    """Traitement IA mock pour les tests"""
    return ai_generator._mock_processing(image, intervention_type, dose)


async def process_simulation(
    simulation_id: int,
    image_path: str,
    intervention_type: str,
    dose: float,
    parameters: dict = None,
) -> Tuple[bool, str, Optional[str]]:
    """Traiter une simulation"""
    return await ai_generator.process_simulation(
        simulation_id, image_path, intervention_type, dose, parameters
    )


def validate_image_format(image_data: bytes) -> bool:
    """Valider le format d'une image"""
    try:
        image = Image.open(io.BytesIO(image_data))
        # Vérifier que c'est une image valide
        image.verify()
        return True
    except Exception:
        return False


def preprocess_image(image_data: bytes) -> Image.Image:
    """Préprocesser une image pour l'IA"""
    try:
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        # Redimensionner à 512x512 pour ControlNet
        image = image.resize((512, 512), Image.Resampling.LANCZOS)
        return image
    except Exception as e:
        raise ValueError(f"Erreur lors du preprocessing de l'image: {e}")


def apply_intervention(
    image: Image.Image,
    intervention_type: str,
    dose: float,
    **kwargs
) -> Image.Image:
    """Appliquer une intervention esthétique"""
    from config import INTERVENTION_TYPES
    
    # Validation du type d'intervention
    if intervention_type not in INTERVENTION_TYPES:
        raise ValueError(f"Unsupported intervention type: {intervention_type}")
    
    # Validation de la dose
    intervention_config = INTERVENTION_TYPES[intervention_type]
    if dose <= 0 or dose < intervention_config["min_dose"] or dose > intervention_config["max_dose"]:
        raise ValueError(f"Invalid dose: {dose}. Must be between {intervention_config['min_dose']} and {intervention_config['max_dose']}")
    
    # En mode GPU avec pipeline fournie dans les kwargs
    pipeline = kwargs.get('pipeline')
    controlnet = kwargs.get('controlnet')
    
    if pipeline is not None and controlnet is not None and USE_GPU and not TESTING_MODE:
        # Utiliser le pipeline réel
        try:
            canny_detector = CannyDetector()
            control_image = canny_detector(image)
            prompt = f"beautiful face with enhanced {intervention_type}, dose {dose}"
            
            result = pipeline(
                prompt=prompt,
                image=control_image,
                num_inference_steps=20,
                guidance_scale=7.5
            )
            return result.images[0]
        except Exception as e:
            # Fallback to mock if real processing fails
            return mock_ai_processing(image, intervention_type, dose)
    else:
        # Mode mock
        return mock_ai_processing(image, intervention_type, dose)


def mock_ai_processing(image_data, intervention_type: str, dose: float) -> Image.Image:
    """Traitement IA mock pour les tests"""
    if isinstance(image_data, bytes):
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
    else:
        image = image_data
    
    # Modifier légèrement l'image selon l'intervention
    if intervention_type == "lips":
        # Faire une modification subtile pour simuler une augmentation des lèvres
        pixels = np.array(image)
        pixels[:, :, 0] = np.clip(pixels[:, :, 0] + int(dose * 10), 0, 255)  # Plus de rouge
        image = Image.fromarray(pixels)
    
    # Retourner l'image PIL directement
    return image


def load_ai_models():
    """Charger les modèles IA"""
    if TESTING_MODE or not USE_GPU:
        return MockStableDiffusionControlNetPipeline(), MockControlNetModel()
    
    # TODO: Implémenter le chargement des vrais modèles
    return None, None


def save_result_image(image: Image.Image, filename: str) -> str:
    """Sauvegarder l'image résultat et retourner le chemin"""
    from config import UPLOAD_DIR
    import os
    
    filepath = os.path.join(UPLOAD_DIR, filename)
    image.save(filepath, "JPEG")
    return f"/uploads/{filename}"
