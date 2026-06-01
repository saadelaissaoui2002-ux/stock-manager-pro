"""
Stock Manager Pro - Gestionnaire de Stock Intelligent
=====================================================

Application desktop professionnelle de gestion de stock
avec PyQt6, SQLite, Matplotlib et export CSV/Excel.

Auteur : Stock Manager Pro Team
Version : 1.0.0
Licence : MIT

Utilisation :
    python main.py

Structure du projet :
    stock_manager_pro/
    ├── main.py              # Point d'entrée
    ├── database/
    │   ├── __init__.py
    │   └── db_manager.py    # Gestionnaire SQLite
    ├── models/
    │   ├── __init__.py
    │   └── product.py       # Modèle Produit
    ├── ui/
    │   ├── __init__.py
    │   ├── main_window.py   # Fenêtre principale
    │   ├── dashboard_tab.py # Tableau de bord
    │   ├── products_tab.py  # Gestion produits
    │   ├── stock_tab.py     # Gestion stock
    │   ├── history_tab.py   # Historique
    │   ├── stats_tab.py     # Statistiques
    │   └── styles.py        # Thème QSS
    ├── utils/
    │   ├── __init__.py
    │   ├── validators.py    # Validation des entrées
    │   └── export.py        # Export CSV/Excel
    └── requirements.txt
"""

import sys
import os

# Ajouter le répertoire du projet au path Python
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from ui.main_window import MainWindow


def main():
    """Point d'entrée principal de l'application."""
    # Créer l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Stock Manager Pro")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("StockManagerPro")

    # Police par défaut
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Chemin de la base de données 
    db_path = os.path.join(PROJECT_DIR, "stock.db")

    # S'assurer que le répertoire de la DB existe
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    # Créer et afficher la fenêtre principale
    window = MainWindow(db_path=db_path)
    window.show()

    # Exécuter la boucle d'événements
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
