"""
Utilitaires pour la gestion des fichiers et images
"""

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageOps
import hashlib

from app.core.config import settings


class FileManager:
    """Gestionnaire de fichiers pour l'application"""
    
    @staticmethod
    def generate_unique_filename(extension: str = "jpg") -> str:
        """
        Générer un nom de fichier unique
        
        Args:
            extension: Extension du fichier
            
        Returns:
            Nom de fichier unique
        """
        return f"{uuid.uuid4()}.{extension.lstrip('.')}"
    
    @staticmethod
    def ensure_directory_exists(path: Path) -> None:
        """
        S'assurer qu'un répertoire existe
        
        Args:
            path: Chemin du répertoire
        """
        path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_file_hash(file_path: Path) -> str:
        """
        Calculer le hash SHA-256 d'un fichier
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            Hash SHA-256 en hexadécimal
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def clean_old_files(directory: Path, max_age_days: int = 30) -> int:
        """
        Nettoyer les fichiers anciens d'un répertoire
        
        Args:
            directory: Répertoire à nettoyer
            max_age_days: Âge maximum en jours
            
        Returns:
            Nombre de fichiers supprimés
        """
        import time
        
        if not directory.exists():
            return 0
        
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        deleted_count = 0
        
        for file_path in directory.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except OSError:
                        pass
        
        return deleted_count


class ImageProcessor:
    """Processeur d'images pour les simulations"""
    
    @staticmethod
    def validate_image(image: Image.Image) -> Tuple[bool, Optional[str]]:
        """
        Valider une image pour les simulations
        
        Args:
            image: Image PIL à valider
            
        Returns:
            Tuple (valide, message d'erreur)
        """
        # Vérifier la taille
        max_size = settings.max_image_size
        if max(image.size) > max_size * 2:  # Limite plus souple pour la validation
            return False, f"Image trop grande. Taille maximale: {max_size}px"
        
        # Vérifier le format
        if image.mode not in ['RGB', 'RGBA', 'L']:
            return False, "Format d'image non supporté"
        
        # Vérifier les dimensions minimales
        if min(image.size) < 256:
            return False, "Image trop petite. Dimensions minimales: 256px"
        
        return True, None
    
    @staticmethod
    def prepare_image_for_ai(image: Image.Image) -> Image.Image:
        """
        Préparer une image pour le traitement IA
        
        Args:
            image: Image PIL d'entrée
            
        Returns:
            Image préparée
        """
        # Convertir en RGB si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Corriger l'orientation EXIF
        image = ImageOps.exif_transpose(image)
        
        # Redimensionner si nécessaire
        max_size = settings.max_image_size
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # S'assurer que les dimensions sont multiples de 8
        width, height = image.size
        width = (width // 8) * 8
        height = (height // 8) * 8
        
        if (width, height) != image.size:
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def create_thumbnail(image: Image.Image, size: Tuple[int, int] = (300, 300)) -> Image.Image:
        """
        Créer une miniature d'image
        
        Args:
            image: Image source
            size: Taille de la miniature
            
        Returns:
            Image miniature
        """
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        return thumbnail
    
    @staticmethod
    def save_optimized_image(
        image: Image.Image, 
        path: Path, 
        quality: int = 90,
        optimize: bool = True
    ) -> None:
        """
        Sauvegarder une image optimisée
        
        Args:
            image: Image à sauvegarder
            path: Chemin de destination
            quality: Qualité JPEG (1-100)
            optimize: Optimiser la taille du fichier
        """
        # S'assurer que le répertoire existe
        FileManager.ensure_directory_exists(path.parent)
        
        # Déterminer le format basé sur l'extension
        extension = path.suffix.lower()
        if extension in ['.jpg', '.jpeg']:
            image.save(path, 'JPEG', quality=quality, optimize=optimize)
        elif extension == '.png':
            image.save(path, 'PNG', optimize=optimize)
        elif extension == '.webp':
            image.save(path, 'WEBP', quality=quality, optimize=optimize)
        else:
            # Par défaut, sauvegarder en JPEG
            image.save(path, 'JPEG', quality=quality, optimize=optimize)
