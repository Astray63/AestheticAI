"""
Service IA pour la génération d'images esthétiques
Utilise Stable Diffusion et ControlNet pour les simulations d'interventions
"""

import torch
import cv2
import numpy as np
from PIL import Image
import logging
from typing import Tuple, Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import os
import io
from pathlib import Path

from app.core.config import settings, INTERVENTION_TYPES

# Configuration du logging
logger = logging.getLogger(__name__)


class MockImageResult:
    """Classe mock pour les résultats d'images en mode test"""
    def __init__(self, size: Tuple[int, int] = (512, 512)):
        self.images = [Image.new("RGB", size, color="lightblue")]


class MockControlNetModel:
    """Mock du modèle ControlNet pour les tests"""
    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()


class MockStableDiffusionPipeline:
    """Mock du pipeline Stable Diffusion pour les tests"""
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
        return MockImageResult()


class MockCannyDetector:
    """Mock du détecteur Canny pour les tests"""
    def __call__(self, image):
        return Image.new("L", image.size, color=128)


class AIGeneratorService:
    """
    Service principal pour la génération d'images avec IA
    Gère Stable Diffusion, ControlNet et les interventions esthétiques
    """

    def __init__(self):
        self.device = settings.device
        self.testing_mode = settings.environment == "test"
        self.models_loaded = False
        self.pipeline = None
        self.controlnet = None
        self.canny_detector = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        logger.info(f"Initialisation AIGeneratorService - Device: {self.device}, Test: {self.testing_mode}")

    async def initialize_models(self) -> None:
        """
        Initialiser les modèles IA de manière asynchrone
        Utilise des mocks en mode test pour éviter le téléchargement
        """
        if self.models_loaded:
            return

        try:
            if self.testing_mode:
                logger.info("Mode test - Initialisation des modèles mock")
                self.pipeline = MockStableDiffusionPipeline()
                self.controlnet = MockControlNetModel()
                self.canny_detector = MockCannyDetector()
            else:
                logger.info("Chargement des modèles IA réels...")
                await self._load_real_models()

            self.models_loaded = True
            logger.info("Modèles IA initialisés avec succès")

        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des modèles: {e}")
            # Fallback vers les mocks en cas d'erreur
            logger.warning("Fallback vers les modèles mock")
            self.pipeline = MockStableDiffusionPipeline()
            self.controlnet = MockControlNetModel()
            self.canny_detector = MockCannyDetector()
            self.models_loaded = True

    async def _load_real_models(self) -> None:
        """Charger les vrais modèles IA (pour la production)"""
        def load_models():
            try:
                from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
                from controlnet_aux import CannyDetector

                # Charger ControlNet
                self.controlnet = ControlNetModel.from_pretrained(
                    settings.controlnet_model,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )

                # Charger le pipeline principal
                self.pipeline = StableDiffusionControlNetPipeline.from_pretrained(
                    settings.model_name,
                    controlnet=self.controlnet,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    safety_checker=None,
                    requires_safety_checker=False
                )

                # Configuration de performance
                self.pipeline = self.pipeline.to(self.device)
                
                if self.device == "cuda":
                    try:
                        self.pipeline.enable_xformers_memory_efficient_attention()
                    except:
                        logger.warning("xformers non disponible")

                # Détecteur Canny
                self.canny_detector = CannyDetector()

                logger.info("Modèles réels chargés avec succès")
                
            except Exception as e:
                logger.error(f"Erreur lors du chargement des modèles réels: {e}")
                raise

        await asyncio.get_event_loop().run_in_executor(self.executor, load_models)

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Préprocesser l'image d'entrée
        
        Args:
            image: Image PIL d'entrée
            
        Returns:
            Image preprocessée
        """
        # Redimensionner si nécessaire
        max_size = settings.max_image_size
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # S'assurer que l'image est en RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Redimensionner à des multiples de 8 (requis pour Stable Diffusion)
        width, height = image.size
        width = (width // 8) * 8
        height = (height // 8) * 8
        image = image.resize((width, height))

        return image

    def _create_intervention_prompt(
        self, 
        intervention_type: str, 
        dose: float,
        parameters: Dict[str, Any]
    ) -> str:
        """
        Créer un prompt spécifique à l'intervention
        
        Args:
            intervention_type: Type d'intervention
            dose: Dosage de l'intervention
            parameters: Paramètres additionnels
            
        Returns:
            Prompt pour Stable Diffusion
        """
        intervention_info = INTERVENTION_TYPES.get(intervention_type, {})
        intervention_name = intervention_info.get("name", intervention_type)

        base_prompt = "professional medical aesthetic enhancement, "
        
        # Prompts spécifiques par intervention
        if intervention_type == "lips":
            intensity = "subtle" if dose < 2 else "moderate" if dose < 4 else "pronounced"
            base_prompt += f"{intensity} lip enhancement, fuller lips, natural looking"
        elif intervention_type == "cheeks":
            intensity = "subtle" if dose < 3 else "moderate" if dose < 6 else "pronounced"
            base_prompt += f"{intensity} cheek augmentation, defined cheekbones"
        elif intervention_type == "chin":
            intensity = "subtle" if dose < 2 else "moderate" if dose < 4 else "pronounced"
            base_prompt += f"{intensity} chin enhancement, improved profile"
        elif intervention_type == "forehead":
            intensity = "light" if dose < 20 else "moderate" if dose < 35 else "strong"
            base_prompt += f"{intensity} forehead smoothing, reduced wrinkles"
        elif intervention_type == "crow_feet":
            intensity = "light" if dose < 10 else "moderate" if dose < 18 else "strong"
            base_prompt += f"{intensity} eye area smoothing, reduced crow's feet"

        base_prompt += ", high quality, professional photography, natural lighting"
        
        return base_prompt

    async def generate_simulation(
        self,
        original_image: Image.Image,
        intervention_type: str,
        dose: float,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Générer une simulation d'intervention esthétique
        
        Args:
            original_image: Image originale du patient
            intervention_type: Type d'intervention
            dose: Dosage de l'intervention
            parameters: Paramètres additionnels
            
        Returns:
            Tuple (image générée, métadonnées)
        """
        await self.initialize_models()
        
        start_time = time.time()
        parameters = parameters or {}
        
        try:
            # Préprocesser l'image
            processed_image = self._preprocess_image(original_image)
            
            # Créer le prompt
            prompt = self._create_intervention_prompt(intervention_type, dose, parameters)
            
            # Détecter les contours avec Canny
            canny_image = self.canny_detector(processed_image)
            
            # Générer l'image
            def generate():
                return self.pipeline(
                    prompt=prompt,
                    image=canny_image,
                    num_inference_steps=settings.inference_steps,
                    guidance_scale=settings.guidance_scale,
                    generator=torch.Generator(device=self.device).manual_seed(42)
                )
            
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor, generate
            )
            
            generated_image = result.images[0]
            generation_time = time.time() - start_time
            
            metadata = {
                "model_version": settings.model_name,
                "generation_time": generation_time,
                "intervention_type": intervention_type,
                "dose": dose,
                "prompt": prompt,
                "parameters": parameters,
                "image_size": processed_image.size,
                "device": self.device
            }
            
            logger.info(
                f"Simulation générée - Type: {intervention_type}, "
                f"Dose: {dose}, Temps: {generation_time:.2f}s"
            )
            
            return generated_image, metadata
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération: {e}")
            # En cas d'erreur, retourner une image de fallback
            fallback_image = Image.new("RGB", (512, 512), color="lightgray")
            metadata = {
                "error": str(e),
                "generation_time": time.time() - start_time,
                "fallback": True
            }
            return fallback_image, metadata

    async def get_available_interventions(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtenir la liste des interventions disponibles
        
        Returns:
            Dictionnaire des interventions disponibles
        """
        return INTERVENTION_TYPES.copy()

    def validate_intervention_parameters(
        self, 
        intervention_type: str, 
        dose: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Valider les paramètres d'une intervention
        
        Args:
            intervention_type: Type d'intervention
            dose: Dosage proposé
            
        Returns:
            Tuple (valide, message d'erreur)
        """
        if intervention_type not in INTERVENTION_TYPES:
            return False, f"Type d'intervention non supporté: {intervention_type}"
        
        intervention = INTERVENTION_TYPES[intervention_type]
        min_dose = intervention["min_dose"]
        max_dose = intervention["max_dose"]
        unit = intervention["unit"]
        
        if not (min_dose <= dose <= max_dose):
            return False, f"Dose invalide. Doit être entre {min_dose} et {max_dose} {unit}"
        
        return True, None

    async def cleanup(self) -> None:
        """Nettoyer les ressources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        
        if self.pipeline and hasattr(self.pipeline, 'to'):
            try:
                self.pipeline.to('cpu')
            except:
                pass


# Instance globale du service IA
ai_service = AIGeneratorService()
