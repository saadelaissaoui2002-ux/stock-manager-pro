"""
Fenêtre principale du Gestionnaire de Stock Intelligent.
Assemble tous les onglets et gère les signaux entre composants.
"""

import sys
import os
import csv
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QStatusBar, QMenuBar, QMessageBox, QLabel,
    QPushButton, QToolBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction

from database.db_manager import DatabaseManager
from ui.styles import MODERN_STYLE
from ui.dashboard_tab import DashboardTab
from ui.products_tab import ProductsTab
from ui.stock_tab import StockTab
from ui.history_tab import HistoryTab
from ui.stats_tab import StatsTab


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application Stock Manager Pro."""

    def __init__(self, db_path: str = "stock.db"):
        super().__init__()
        self.db = DatabaseManager(db_path)
        self.setup_ui()
        self.setup_toolbar()
        self.setup_menubar()
        self.setup_statusbar()
        self.connect_signals()
        self.start_auto_refresh()

    def setup_ui(self):
        """Configure l'interface principale."""
        self.setWindowTitle("Stock Manager Pro - Gestionnaire de Stock Intelligent")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 850)
        self.setStyleSheet(MODERN_STYLE)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Titre de l'application
        header = QLabel("  STOCK MANAGER PRO")
        header.setStyleSheet("""
            QLabel {
                background-color: #0f0f1a;
                color: #00d2ff;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-bottom: 2px solid #00d2ff;
                letter-spacing: 2px;
            }
        """)
        layout.addWidget(header)

        # Onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        # Créer les onglets
        self.dashboard_tab = DashboardTab(self.db)
        self.products_tab = ProductsTab(self.db)
        self.stock_tab = StockTab(self.db)
        self.history_tab = HistoryTab(self.db)
        self.stats_tab = StatsTab(self.db)

        self.tab_widget.addTab(self.dashboard_tab, "Tableau de Bord")
        self.tab_widget.addTab(self.products_tab, "Produits")
        self.tab_widget.addTab(self.stock_tab, "Gestion Stock")
        self.tab_widget.addTab(self.history_tab, "Historique")
        self.tab_widget.addTab(self.stats_tab, "Statistiques")

        layout.addWidget(self.tab_widget)

        # Vérifier les alertes au démarrage
        QTimer.singleShot(500, self.check_alerts_on_startup)

    def setup_toolbar(self):
        """Configure la barre d'outils avec les boutons d'export CSV."""
        toolbar = QToolBar("Barre d'outils")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #1a1a2e;
                border-bottom: 1px solid #333;
                padding: 4px 8px;
                spacing: 8px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton#btnExportHist {
                background-color: #FF9800;
            }
            QPushButton#btnExportHist:hover {
                background-color: #F57C00;
            }
        """)

        # Label
        label = QLabel("  EXPORT CSV : ")
        label.setStyleSheet("color: #aaa; font-weight: bold; font-size: 12px;")
        toolbar.addWidget(label)

        # Bouton Export Produits CSV
        btn_csv = QPushButton("Produits CSV")
        btn_csv.clicked.connect(self.export_produits_csv)
        toolbar.addWidget(btn_csv)

        # Séparateur
        sep = QLabel("  |  ")
        sep.setStyleSheet("color: #555;")
        toolbar.addWidget(sep)

        # Bouton Export Historique CSV
        btn_hist = QPushButton("Historique CSV")
        btn_hist.setObjectName("btnExportHist")
        btn_hist.clicked.connect(self.export_historique_csv)
        toolbar.addWidget(btn_hist)

        self.addToolBar(toolbar)

    def setup_menubar(self):
        """Configure la barre de menus."""
        menubar = self.menuBar()

        # Menu Fichier
        menu_fichier = menubar.addMenu("Fichier")

        action_refresh = QAction("Actualiser tout", self)
        action_refresh.setShortcut("Ctrl+R")
        action_refresh.triggered.connect(self.refresh_all)
        menu_fichier.addAction(action_refresh)

        menu_fichier.addSeparator()

        action_quitter = QAction("Quitter", self)
        action_quitter.setShortcut("Ctrl+Q")
        action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(action_quitter)

        # Menu Export
        menu_export = menubar.addMenu("Export")

        action_export_csv = QAction("Exporter Produits (CSV)", self)
        action_export_csv.triggered.connect(self.export_produits_csv)
        menu_export.addAction(action_export_csv)

        action_export_hist_csv = QAction("Exporter Historique (CSV)", self)
        action_export_hist_csv.triggered.connect(self.export_historique_csv)
        menu_export.addAction(action_export_hist_csv)

        # Menu Aide
        menu_aide = menubar.addMenu("Aide")

        action_about = QAction("A propos", self)
        action_about.triggered.connect(self.show_about)
        menu_aide.addAction(action_about)

    def setup_statusbar(self):
        """Configure la barre d'état."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.status_label = QLabel("Pret")
        self.status_label.setStyleSheet("padding: 4px 8px;")
        self.statusbar.addWidget(self.status_label)

        self.db_label = QLabel("Base de donnees : connectee")
        self.db_label.setStyleSheet("color: #4caf50; padding: 4px 8px;")
        self.statusbar.addPermanentWidget(self.db_label)

    def connect_signals(self):
        """Connecte les signaux entre les onglets."""
        self.products_tab.product_changed.connect(self.on_data_changed)
        self.stock_tab.stock_changed.connect(self.on_data_changed)

    def start_auto_refresh(self):
        """Démarre le rafraîchissement automatique périodique."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.silent_refresh)
        self.refresh_timer.start(30000)  # Toutes les 30 secondes

    def on_data_changed(self):
        """Appelé quand des données sont modifiées dans un onglet."""
        self.refresh_all()
        self.check_alerts()

    def refresh_all(self):
        """Rafraîchit tous les onglets."""
        self.dashboard_tab.refresh_data()
        self.products_tab.refresh()
        self.stock_tab.refresh()
        self.history_tab.refresh()
        self.stats_tab.refresh()
        self.status_label.setText("Donnees actualisees")

    def silent_refresh(self):
        """Rafraîchissement silencieux en arrière-plan."""
        self.dashboard_tab.refresh_data()
        self.check_alerts()

    def check_alerts_on_startup(self):
        """Vérifie les alertes de stock au démarrage de l'application."""
        produits_alerte = self.db.get_produits_alerte()
        if produits_alerte:
            ruptures = [p for p in produits_alerte if p["quantite"] == 0]
            alertes = [p for p in produits_alerte if p["quantite"] > 0]

            msg = ""
            if ruptures:
                msg += f"Produits en RUPTURE : {', '.join(p['nom'] for p in ruptures)}\n"
            if alertes:
                msg += f"Produits en ALERTE : {', '.join(p['nom'] for p in alertes)}"

            if msg:
                QMessageBox.warning(
                    self, "Alerte Stock",
                    f"Attention ! Certains produits necessitent votre attention :\n\n{msg}"
                )

    def check_alerts(self):
        """Vérifie les alertes de stock et affiche un avertissement si nécessaire."""
        produits_alerte = self.db.get_produits_alerte()
        if produits_alerte:
            count = len(produits_alerte)
            ruptures = sum(1 for p in produits_alerte if p["quantite"] == 0)
            if ruptures > 0:
                self.status_label.setText(
                    f"ALERTES : {count} produit(s) en alerte dont {ruptures} en rupture !"
                )
                self.status_label.setStyleSheet("color: #ff5252; padding: 4px 8px;")
            else:
                self.status_label.setText(
                    f"ATTENTION : {count} produit(s) en alerte de stock faible"
                )
                self.status_label.setStyleSheet("color: #ff9800; padding: 4px 8px;")
        else:
            self.status_label.setText("Pret - Aucune alerte")
            self.status_label.setStyleSheet("color: #4caf50; padding: 4px 8px;")

    # ─────────────────────────────────────────────
    # Méthodes d'export CSV
    # ─────────────────────────────────────────────

    def _get_export_dir(self) -> str:
        """Retourne le dossier export du projet et le crée si nécessaire."""
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        export_dir = os.path.join(app_dir, "export")
        os.makedirs(export_dir, exist_ok=True)
        return export_dir

    def _do_export_csv(self, data, prefix):
        """
        Exporte les données en CSV dans le dossier export/ du projet.
        Aucune dépendance externe nécessaire.
        """
        if not data:
            QMessageBox.warning(self, "Attention", "Aucune donnee a exporter.")
            return

        self.status_label.setText("Export CSV en cours...")
        self.status_label.setStyleSheet("color: #2196F3; padding: 4px 8px;")

        try:
            export_dir = self._get_export_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.csv"
            filepath = os.path.join(export_dir, filename)

            fieldnames = list(data[0].keys())
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            file_size = os.path.getsize(filepath)
            QMessageBox.information(
                self, "Export CSV reussi",
                f"Fichier exporte avec succes !\n\n"
                f"Chemin : {filepath}\n"
                f"Taille : {file_size} octets\n"
                f"Lignes : {len(data)}"
            )
            self.status_label.setText(f"Export reussi : {filepath}")
            self.status_label.setStyleSheet("color: #4CAF50; padding: 4px 8px;")

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Erreur d'export CSV",
                f"Erreur : {type(e).__name__}: {str(e)}"
            )
            self.status_label.setText("Export echoue")
            self.status_label.setStyleSheet("color: #ff5252; padding: 4px 8px;")

    def export_produits_csv(self):
        """Exporte les produits en CSV."""
        produits = self.db.get_all_produits()
        self._do_export_csv(produits, "produits_stock")

    def export_historique_csv(self):
        """Exporte l'historique en CSV."""
        historique = self.db.get_historique()
        self._do_export_csv(historique, "historique_stock")

    def show_about(self):
        """Affiche la boîte de dialogue 'À propos'."""
        QMessageBox.about(
            self,
            "A propos de Stock Manager Pro",
            "<h2 style='color: #00d2ff;'>Stock Manager Pro</h2>"
            "<p><b>Version 1.0.0</b></p>"
            "<p>Gestionnaire de Stock Intelligent - Application desktop professionnelle</p>"
            "<p>Developpe par : El Aissaoui Saad et Radi Taha</p>"
            "<hr>"
            "<p><b>Technologies :</b></p>"
            "<ul>"
            "<li>Python</li>"
            "<li>PyQt6 (Interface graphique)</li>"
            "<li>SQLite (Base de donnees)</li>"
            "<li>Matplotlib (Graphiques)</li>"
            "</ul>"
            "<p><b>Fonctionnalites :</b></p>"
            "<ul>"
            "<li>Gestion complete des produits (CRUD)</li>"
            "<li>Gestion du stock (achat/vente)</li>"
            "<li>Historique des actions avec filtres</li>"
            "<li>Tableau de bord avec statistiques</li>"
            "<li>Graphiques interactifs</li>"
            "<li>Alertes de stock faible</li>"
            "<li>Export CSV</li>"
            "<li>Recherche avancee multi-criteres</li>"
            "<li>Interface moderne sombre (QSS)</li>"
            "</ul>"
        )

    def closeEvent(self, event):
        """Gère la fermeture de l'application."""
        self.refresh_timer.stop()
        self.db.close()
        event.accept()
