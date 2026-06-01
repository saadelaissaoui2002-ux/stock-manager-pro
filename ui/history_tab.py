"""
Onglet Historique - Affichage et filtrage de l'historique des actions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDateEdit, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from utils.export import export_csv


class HistoryTab(QWidget):
    """Onglet de l'historique des actions sur le stock."""

    history_changed = pyqtSignal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        """Configure l'interface de l'historique."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # ── Titre ──
        titre = QLabel("Historique des Actions")
        titre.setObjectName("labelTitre")
        font = QFont()
        font.setPointSize(20)
        font.setWeight(QFont.Weight.Bold)
        titre.setFont(font)
        main_layout.addWidget(titre)

        # ── Filtres ──
        filter_group = QGroupBox("Filtres")
        filter_layout = QGridLayout(filter_group)

        # Filtre action
        filter_layout.addWidget(QLabel("Action :"), 0, 0)
        self.combo_action = QComboBox()
        self.combo_action.addItem("Toutes", "")
        self.combo_action.addItem("Ajout", "ajout")
        self.combo_action.addItem("Modification", "modification")
        self.combo_action.addItem("Achat", "achat")
        self.combo_action.addItem("Vente", "vente")
        self.combo_action.addItem("Suppression", "suppression")
        filter_layout.addWidget(self.combo_action, 0, 1)

        # Filtre produit
        filter_layout.addWidget(QLabel("Produit :"), 0, 2)
        self.combo_produit = QComboBox()
        self.combo_produit.addItem("Tous", None)
        filter_layout.addWidget(self.combo_produit, 0, 3)

        # Filtre dates
        filter_layout.addWidget(QLabel("Du :"), 1, 0)
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate().addMonths(-1))
        self.date_debut.setDisplayFormat("yyyy-MM-dd")
        filter_layout.addWidget(self.date_debut, 1, 1)

        filter_layout.addWidget(QLabel("Au :"), 1, 2)
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate())
        self.date_fin.setDisplayFormat("yyyy-MM-dd")
        filter_layout.addWidget(self.date_fin, 1, 3)

        # Boutons filtre
        self.btn_filtrer = QPushButton("Filtrer")
        self.btn_filtrer.clicked.connect(self.load_history)
        filter_layout.addWidget(self.btn_filtrer, 0, 4)

        self.btn_reset = QPushButton("Réinitialiser")
        self.btn_reset.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.btn_reset, 1, 4)

        main_layout.addWidget(filter_group)

        # ── Table historique ──
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Date", "Produit", "Action", "Quantité", "Prix Unitaire", "Détails"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 80)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 100)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        main_layout.addWidget(self.table)

        # ── Barre d'actions ──
        action_layout = QHBoxLayout()

        self.label_compteur = QLabel("0 action(s)")
        self.label_compteur.setStyleSheet("color: #a0a0b0; font-size: 12px;")
        action_layout.addWidget(self.label_compteur)

        action_layout.addStretch()

        self.btn_export_csv = QPushButton("Exporter CSV")
        self.btn_export_csv.setObjectName("btnExport")
        self.btn_export_csv.clicked.connect(self.exporter_csv)
        action_layout.addWidget(self.btn_export_csv)

        main_layout.addLayout(action_layout)

        # Charger les produits pour le filtre
        self.update_produits_filter()

    def update_produits_filter(self):
        """Met à jour la liste des produits dans le filtre."""
        produits = self.db.get_all_produits()
        self.combo_produit.blockSignals(True)
        self.combo_produit.clear()
        self.combo_produit.addItem("Tous", None)
        for p in produits:
            self.combo_produit.addItem(p["nom"], p["id"])
        self.combo_produit.blockSignals(False)

    def load_history(self):
        """Charge l'historique filtré dans la table."""
        action = self.combo_action.currentData() or ""
        produit_id = self.combo_produit.currentData()
        date_debut = self.date_debut.date().toString("yyyy-MM-dd")
        date_fin = self.date_fin.date().toString("yyyy-MM-dd")

        historique = self.db.get_historique(
            produit_id=produit_id,
            action=action,
            date_debut=date_debut,
            date_fin=date_fin
        )

        # Couleurs des actions
        action_colors = {
            "ajout": QColor("#4caf50"),
            "achat": QColor("#42a5f5"),
            "vente": QColor("#ab47bc"),
            "suppression": QColor("#ff5252"),
            "modification": QColor("#ff9800"),
        }

        self.table.setRowCount(len(historique))
        for row, h in enumerate(historique):
            self.table.setItem(row, 0, QTableWidgetItem(h["date"]))
            self.table.setItem(row, 1, QTableWidgetItem(h["produit_nom"]))

            action_item = QTableWidgetItem(h["action"].upper())
            color = action_colors.get(h["action"], QColor("#e0e0e0"))
            action_item.setForeground(color)
            action_font = QFont()
            action_font.setBold(True)
            action_item.setFont(action_font)
            self.table.setItem(row, 2, action_item)

            self.table.setItem(row, 3, QTableWidgetItem(str(h["quantite"])))
            self.table.setItem(row, 4, QTableWidgetItem(f"{h['prix_unitaire']:.2f} DH"))
            self.table.setItem(row, 5, QTableWidgetItem(h.get("details", "")))

        self.label_compteur.setText(f"{len(historique)} action(s)")
        self._current_data = historique

    def reset_filters(self):
        """Réinitialise tous les filtres."""
        self.combo_action.setCurrentIndex(0)
        self.combo_produit.setCurrentIndex(0)
        self.date_debut.setDate(QDate.currentDate().addMonths(-1))
        self.date_fin.setDate(QDate.currentDate())
        self.load_history()

    def exporter_csv(self):
        """Exporte l'historique actuel en CSV."""
        data = getattr(self, '_current_data', [])
        if not data:
            QMessageBox.warning(self, "Attention", "Aucune donnée à exporter.")
            return
        try:
            path = export_csv(data, "historique_stock")
            QMessageBox.information(self, "Export réussi", f"Fichier exporté : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export : {e}")

    def refresh(self):
        """Rafraîchit les données de l'onglet."""
        self.update_produits_filter()
        self.load_history()
