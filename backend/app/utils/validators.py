"""
Utilitaires pour la validation des données
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, date


class ValidationUtils:
    """Utilitaires de validation pour l'application"""
    
    @staticmethod
    def validate_pin(pin: str) -> Tuple[bool, Optional[str]]:
        """
        Valider un code PIN
        
        Args:
            pin: Code PIN à valider
            
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not pin:
            return False, "Le PIN est requis"
        
        if not pin.isdigit():
            return False, "Le PIN ne peut contenir que des chiffres"
        
        if len(pin) < 4:
            return False, "Le PIN doit contenir au moins 4 chiffres"
        
        if len(pin) > 8:
            return False, "Le PIN ne peut pas contenir plus de 8 chiffres"
        
        # Vérifier les patterns faibles
        if pin == pin[0] * len(pin):  # Tous les chiffres identiques
            return False, "Le PIN ne peut pas contenir que des chiffres identiques"
        
        if pin in ['1234', '0000', '1111', '1357', '2468']:
            return False, "Ce PIN est trop simple"
        
        return True, None
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, Optional[str]]:
        """
        Valider un nom d'utilisateur
        
        Args:
            username: Nom d'utilisateur à valider
            
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not username:
            return False, "Le nom d'utilisateur est requis"
        
        if len(username) < 3:
            return False, "Le nom d'utilisateur doit contenir au moins 3 caractères"
        
        if len(username) > 50:
            return False, "Le nom d'utilisateur ne peut pas dépasser 50 caractères"
        
        # Pattern autorisé: lettres, chiffres, tirets et underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores"
        
        # Ne peut pas commencer par un chiffre
        if username[0].isdigit():
            return False, "Le nom d'utilisateur ne peut pas commencer par un chiffre"
        
        return True, None
    
    @staticmethod
    def validate_license_number(license_number: str, country: str = "FR") -> Tuple[bool, Optional[str]]:
        """
        Valider un numéro de licence professionnelle
        
        Args:
            license_number: Numéro de licence à valider
            country: Code pays (par défaut FR)
            
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not license_number:
            return False, "Le numéro de licence est requis"
        
        # Pour la France (RPPS ou ADELI)
        if country == "FR":
            # RPPS: 11 chiffres
            if re.match(r'^\d{11}$', license_number):
                return True, None
            
            # ADELI: 9 chiffres
            if re.match(r'^\d{9}$', license_number):
                return True, None
            
            return False, "Numéro de licence invalide (format RPPS ou ADELI attendu)"
        
        # Validation générique pour autres pays
        if len(license_number) < 5:
            return False, "Le numéro de licence doit contenir au moins 5 caractères"
        
        return True, None
    
    @staticmethod
    def validate_age_range(age_range: str) -> Tuple[bool, Optional[str]]:
        """
        Valider une tranche d'âge
        
        Args:
            age_range: Tranche d'âge à valider
            
        Returns:
            Tuple (valide, message d'erreur)
        """
        valid_ranges = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
        
        if age_range not in valid_ranges:
            return False, f"Tranche d'âge invalide. Valeurs autorisées: {', '.join(valid_ranges)}"
        
        return True, None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Nettoyer un nom de fichier
        
        Args:
            filename: Nom de fichier à nettoyer
            
        Returns:
            Nom de fichier nettoyé
        """
        # Remplacer les caractères problématiques
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Limiter la longueur
        if len(filename) > 200:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:200-len(ext)-1] + '.' + ext if ext else name[:200]
        
        return filename
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Valider l'extension d'un fichier
        
        Args:
            filename: Nom du fichier
            allowed_extensions: Extensions autorisées (sans le point)
            
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not filename:
            return False, "Nom de fichier requis"
        
        if '.' not in filename:
            return False, "Extension de fichier manquante"
        
        extension = filename.lower().split('.')[-1]
        allowed_extensions = [ext.lower() for ext in allowed_extensions]
        
        if extension not in allowed_extensions:
            return False, f"Extension non autorisée. Extensions acceptées: {', '.join(allowed_extensions)}"
        
        return True, None


class DataCleaner:
    """Utilitaires pour nettoyer et normaliser les données"""
    
    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """
        Nettoyer un numéro de téléphone
        
        Args:
            phone: Numéro de téléphone
            
        Returns:
            Numéro nettoyé
        """
        # Supprimer tous les caractères non numériques sauf le +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Normaliser le format français
        if phone.startswith('0'):
            phone = '+33' + phone[1:]
        elif phone.startswith('33'):
            phone = '+' + phone
        
        return phone
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normaliser un texte (suppression espaces multiples, etc.)
        
        Args:
            text: Texte à normaliser
            
        Returns:
            Texte normalisé
        """
        if not text:
            return ""
        
        # Supprimer les espaces en début et fin
        text = text.strip()
        
        # Remplacer les espaces multiples par un seul
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    @staticmethod
    def anonymize_name(name: str) -> str:
        """
        Anonymiser un nom (garder initiales)
        
        Args:
            name: Nom à anonymiser
            
        Returns:
            Nom anonymisé
        """
        if not name:
            return ""
        
        parts = name.split()
        anonymized_parts = []
        
        for part in parts:
            if len(part) > 0:
                anonymized_parts.append(part[0].upper() + '***')
        
        return ' '.join(anonymized_parts)
