"""
Utilitaires d'export de données en CSV.
Aucune dépendance externe nécessaire - utilise uniquement la bibliothèque standard Python.
"""

import csv
import os
from datetime import datetime
from typing import List, Optional


def _get_default_export_dir() -> str:
    """Retourne le dossier 'export' dans le répertoire de l'application."""
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_dir = os.path.join(app_dir, "export")
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def export_csv(data: List[dict], filename: str, filepath: Optional[str] = None) -> str:
    """
    Exporte une liste de dictionnaires vers un fichier CSV.

    Args:
        data: Liste de dictionnaires à exporter.
        filename: Nom du fichier (sans extension).
        filepath: Chemin du dossier de destination. Par défaut le dossier export/.

    Returns:
        Le chemin complet du fichier créé.
    """
    if not data:
        raise ValueError("Aucune donnée à exporter.")

    if filepath is None:
        filepath = _get_default_export_dir()
    os.makedirs(filepath, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_path = os.path.join(filepath, f"{filename}_{timestamp}.csv")

    fieldnames = list(data[0].keys())
    with open(full_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    return full_path
