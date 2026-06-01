"""
Onglet Dashboard - Affichage des statistiques globales et alertes.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class StatCard(QFrame):
    """Carte statistique avec icône, valeur et label."""

    def __init__(self, titre: str, valeur: str = "0", couleur: str = "#00d2ff",
                 parent=None):
        super().__init__(parent)
        self.setObjectName("carteStat")
        self.couleur = couleur

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(20, 16, 20, 16)

        # Label titre
        self.label_titre = QLabel(titre.upper())
        self.label_titre.setObjectName("labelStatLabel")
        self.label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_titre = QFont()
        font_titre.setPointSize(10)
        font_titre.setWeight(QFont.Weight.Normal)
        self.label_titre.setFont(font_titre)
        layout.addWidget(self.label_titre)

        # Label valeur
        self.label_valeur = QLabel(valeur)
        self.label_valeur.setObjectName("labelStatValeur")
        self.label_valeur.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_valeur = QFont()
        font_valeur.setPointSize(26)
        font_valeur.setWeight(QFont.Weight.Bold)
        self.label_valeur.setFont(font_valeur)
        self.label_valeur.setStyleSheet(f"color: {couleur};")
        layout.addWidget(self.label_valeur)

        # Style de la carte
        self.setStyleSheet(f"""
            QFrame#carteStat {{
                background-color: #16213e;
                border: 1px solid {couleur}33;
                border-left: 4px solid {couleur};
                border-radius: 12px;
            }}
        """)

    def set_valeur(self, valeur: str):
        """Met à jour la valeur affichée."""
        self.label_valeur.setText(valeur)


class DashboardTab(QWidget):
    """Onglet Dashboard principal avec statistiques et alertes."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        """Configure l'interface du dashboard."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # ── Titre ──
        titre = QLabel("Tableau de Bord")
        titre.setObjectName("labelTitre")
        font = QFont()
        font.setPointSize(20)
        font.setWeight(QFont.Weight.Bold)
        titre.setFont(font)
        main_layout.addWidget(titre)

        # ── Cartes statistiques ──
        cartes_layout = QGridLayout()
        cartes_layout.setSpacing(12)

        self.carte_produits = StatCard("Produits", "0", "#00d2ff")
        self.carte_stock = StatCard("Unités en Stock", "0", "#4caf50")
        self.carte_valeur = StatCard("Valeur Stock (Achat)", "0 DH", "#ff9800")
        self.carte_valeur_vente = StatCard("Valeur Stock (Vente)", "0 DH", "#ab47bc")
        self.carte_marge = StatCard("Marge Potentielle", "0 DH", "#26a69a")
        self.carte_alerte = StatCard("Alertes Stock", "0", "#ff5252")
        self.carte_rupture = StatCard("Ruptures", "0", "#d32f2f")
        self.carte_categories = StatCard("Catégories", "0", "#42a5f5")

        cartes_layout.addWidget(self.carte_produits, 0, 0)
        cartes_layout.addWidget(self.carte_stock, 0, 1)
        cartes_layout.addWidget(self.carte_valeur, 0, 2)
        cartes_layout.addWidget(self.carte_valeur_vente, 0, 3)
        cartes_layout.addWidget(self.carte_marge, 1, 0)
        cartes_layout.addWidget(self.carte_alerte, 1, 1)
        cartes_layout.addWidget(self.carte_rupture, 1, 2)
        cartes_layout.addWidget(self.carte_categories, 1, 3)

        main_layout.addLayout(cartes_layout)

        # ── Section Alertes Stock Faible ──
        alerte_frame = QFrame()
        alerte_frame.setObjectName("carteAlerte")
        alerte_layout = QVBoxLayout(alerte_frame)
        alerte_layout.setContentsMargins(16, 12, 16, 12)

        alerte_header = QHBoxLayout()
        self.label_alerte_titre = QLabel("Produits en Alerte Stock Faible")
        self.label_alerte_titre.setObjectName("labelAlerte")
        font_alerte = QFont()
        font_alerte.setPointSize(14)
        font_alerte.setWeight(QFont.Weight.Bold)
        self.label_alerte_titre.setFont(font_alerte)
        alerte_header.addWidget(self.label_alerte_titre)

        self.btn_refresh = QPushButton("Actualiser")
        self.btn_refresh.setFixedWidth(100)
        self.btn_refresh.clicked.connect(self.refresh_data)
        alerte_header.addWidget(self.btn_refresh)
        alerte_layout.addLayout(alerte_header)

        # Table des produits en alerte
        self.table_alerte = QTableWidget()
        self.table_alerte.setColumnCount(5)
        self.table_alerte.setHorizontalHeaderLabels([
            "Produit", "Catégorie", "Quantité", "Seuil Alerte", "Statut"
        ])
        self.table_alerte.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table_alerte.setAlternatingRowColors(True)
        self.table_alerte.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_alerte.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_alerte.setMaximumHeight(250)
        alerte_layout.addWidget(self.table_alerte)

        main_layout.addWidget(alerte_frame)

        # ── Section Statistiques Rapides ──
        stats_frame = QFrame()
        stats_frame.setObjectName("carteStat")
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setContentsMargins(16, 12, 16, 12)

        self.label_plus_vendu = QLabel("Produit le plus vendu : —")
        self.label_plus_vendu.setStyleSheet("color: #4caf50; font-size: 14px; font-weight: 500;")
        stats_layout.addWidget(self.label_plus_vendu, 0, 0)

        self.label_plus_rentable = QLabel("Produit le plus rentable : —")
        self.label_plus_rentable.setStyleSheet("color: #ff9800; font-size: 14px; font-weight: 500;")
        stats_layout.addWidget(self.label_plus_rentable, 0, 1)

        main_layout.addWidget(stats_frame)

        main_layout.addStretch()

    def refresh_data(self):
        """Rafraîchit toutes les données du dashboard."""
        # Statistiques globales
        stats = self.db.get_stats_dashboard()

        self.carte_produits.set_valeur(str(stats.get("total_produits", 0)))
        self.carte_stock.set_valeur(str(stats.get("quantite_totale", 0)))
        self.carte_valeur.set_valeur(f"{stats.get('valeur_stock_achat', 0):,.2f} DH")
        self.carte_valeur_vente.set_valeur(f"{stats.get('valeur_stock_vente', 0):,.2f} DH")
        self.carte_marge.set_valeur(f"{stats.get('marge_potentielle', 0):,.2f} DH")

        alerte_count = stats.get("produits_alerte", 0)
        self.carte_alerte.set_valeur(str(alerte_count))
        if alerte_count > 0:
            self.carte_alerte.setStyleSheet("""
                QFrame#carteStat {
                    background-color: #2a1a1a;
                    border: 2px solid #c62828;
                    border-left: 4px solid #ff5252;
                    border-radius: 12px;
                }
            """)

        rupture_count = stats.get("produits_rupture", 0)
        self.carte_rupture.set_valeur(str(rupture_count))
        self.carte_categories.set_valeur(str(stats.get("total_categories", 0)))

        # Produits en alerte
        produits_alerte = self.db.get_produits_alerte()
        self.table_alerte.setRowCount(len(produits_alerte))
        for row, p in enumerate(produits_alerte):
            self.table_alerte.setItem(row, 0, QTableWidgetItem(p["nom"]))
            self.table_alerte.setItem(row, 1, QTableWidgetItem(p["categorie"]))
            self.table_alerte.setItem(row, 2, QTableWidgetItem(str(p["quantite"])))
            self.table_alerte.setItem(row, 3, QTableWidgetItem(str(p["seuil_alerte"])))

            statut = "RUPTURE" if p["quantite"] == 0 else "ALERTE"
            statut_item = QTableWidgetItem(statut)
            if p["quantite"] == 0:
                statut_item.setForeground(Qt.GlobalColor.red)
                statut_font = QFont()
                statut_font.setBold(True)
                statut_item.setFont(statut_font)
            else:
                statut_item.setForeground(Qt.GlobalColor.yellow)
            self.table_alerte.setItem(row, 4, statut_item)

        # Statistiques rapides
        plus_vendu = self.db.get_produit_plus_vendu()
        if plus_vendu:
            self.label_plus_vendu.setText(
                f"Produit le plus vendu : {plus_vendu['produit_nom']} "
                f"({plus_vendu['total_vendu']} unités)"
            )

        plus_rentable = self.db.get_produit_plus_rentable()
        if plus_rentable:
            self.label_plus_rentable.setText(
                f"Produit le plus rentable : {plus_rentable['produit_nom']} "
                f"({plus_rentable['chiffre_affaires']:,.2f} DH CA)"
            )
