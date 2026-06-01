"""
Utilitaires de validation des entrées utilisateur.
Fournit des fonctions de validation robustes pour les formulaires.
"""

import re
from typing import Optional, Tuple


def validate_text(value: str, field_name: str, min_length: int = 2,
                  max_length: int = 100) -> Tuple[bool, str]:
    """
    Valide un champ texte (nom, catégorie, etc.).

    Returns:
        Tuple (est_valide, message_erreur)
    """
    if not value or not value.strip():
        return False, f"Le champ '{field_name}' est obligatoire."
    value = value.strip()
    if len(value) < min_length:
        return False, f"Le champ '{field_name}' doit contenir au moins {min_length} caractères."
    if len(value) > max_length:
        return False, f"Le champ '{field_name}' ne doit pas dépasser {max_length} caractères."
    # Vérifier les caractères autorisés (lettres, chiffres, espaces, tirets, apostrophes)
    if not re.match(r"^[a-zA-ZÀ-ÿ0-9\s\-'_]+$", value):
        return False, f"Le champ '{field_name}' contient des caractères non autorisés."
    return True, ""


def validate_float(value: str, field_name: str, min_val: float = 0.0,
                   max_val: float = 1_000_000.0) -> Tuple[bool, str]:
    """
    Valide un champ numérique décimal (prix, etc.).

    Returns:
        Tuple (est_valide, message_erreur)
    """
    if not value or not value.strip():
        return False, f"Le champ '{field_name}' est obligatoire."
    try:
        num = float(value.strip().replace(",", "."))
    except ValueError:
        return False, f"Le champ '{field_name}' doit être un nombre valide (ex: 19.99)."
    if num < min_val:
        return False, f"Le champ '{field_name}' doit être supérieur ou égal à {min_val}."
    if num > max_val:
        return False, f"Le champ '{field_name}' ne peut pas dépasser {max_val:,.2f}."
    return True, ""


def validate_integer(value: str, field_name: str, min_val: int = 0,
                     max_val: int = 100_000_000) -> Tuple[bool, str]:
    """
    Valide un champ numérique entier (quantité, seuil, etc.).

    Returns:
        Tuple (est_valide, message_erreur)
    """
    if not value or not value.strip():
        return False, f"Le champ '{field_name}' est obligatoire."
    try:
        num = int(value.strip())
    except ValueError:
        return False, f"Le champ '{field_name}' doit être un nombre entier valide."
    if num < min_val:
        return False, f"Le champ '{field_name}' doit être supérieur ou égal à {min_val}."
    if num > max_val:
        return False, f"Le champ '{field_name}' ne peut pas dépasser {max_val:,}."
    return True, ""


def validate_prix_vente(prix_vente: float, prix_achat: float) -> Tuple[bool, str]:
    """
    Vérifie la cohérence entre prix de vente et prix d'achat.
    Avertit si le prix de vente est inférieur au prix d'achat (pas bloquant).
    """
    if prix_vente < prix_achat:
        return True, "Attention : le prix de vente est inférieur au prix d'achat (vente à perte)."
    return True, ""


def sanitize_input(value: str) -> str:
    """
    Nettoie une entrée utilisateur en supprimant les espaces superflus
    et les caractères potentiellement dangereux.
    """
    if not value:
        return ""
    # Supprimer les espaces en début et fin
    cleaned = value.strip()
    # Supprimer les caractères de contrôle
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", cleaned)
    return cleaned
