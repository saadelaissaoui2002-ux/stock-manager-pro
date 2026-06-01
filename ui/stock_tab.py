"""
Onglet Gestion du Stock - Achat et vente de stock avec vérification automatique.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from models.product import Product
from utils.validators import validate_integer, validate_float


class StockTab(QWidget):
    """Onglet de gestion du stock (achat/vente)."""

    stock_changed = pyqtSignal()  # Signal émis quand le stock est modifié

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._product_ids = []  # Correspondance ligne table -> ID produit
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        """Configure l'interface de gestion du stock."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # ── Titre ──
        titre = QLabel("Gestion du Stock")
        titre.setObjectName("labelTitre")
        font = QFont()
        font.setPointSize(20)
        font.setWeight(QFont.Weight.Bold)
        titre.setFont(font)
        main_layout.addWidget(titre)

        # ── Splitter principal ──
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Panneau gauche : Sélection produit + opérations ──
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)

        # Groupe sélection produit
        select_group = QGroupBox("Sélection du Produit")
        select_layout = QGridLayout(select_group)

        select_layout.addWidget(QLabel("Produit :"), 0, 0)
        self.combo_produit = QComboBox()
        self.combo_produit.currentIndexChanged.connect(self.on_product_selected)
        select_layout.addWidget(self.combo_produit, 0, 1, 1, 2)

        # Infos du produit sélectionné
        self.label_info_nom = QLabel("—")
        self.label_info_nom.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 14px;")
        select_layout.addWidget(QLabel("Nom :"), 1, 0)
        select_layout.addWidget(self.label_info_nom, 1, 1, 1, 2)

        self.label_info_categorie = QLabel("—")
        select_layout.addWidget(QLabel("Catégorie :"), 2, 0)
        select_layout.addWidget(self.label_info_categorie, 2, 1, 1, 2)

        self.label_info_quantite = QLabel("—")
        self.label_info_quantite.setStyleSheet("font-weight: bold; font-size: 14px;")
        select_layout.addWidget(QLabel("Stock actuel :"), 3, 0)
        select_layout.addWidget(self.label_info_quantite, 3, 1, 1, 2)

        self.label_info_prix_achat = QLabel("—")
        select_layout.addWidget(QLabel("Prix d'achat :"), 4, 0)
        select_layout.addWidget(self.label_info_prix_achat, 4, 1, 1, 2)

        self.label_info_prix_vente = QLabel("—")
        select_layout.addWidget(QLabel("Prix de vente :"), 5, 0)
        select_layout.addWidget(self.label_info_prix_vente, 5, 1, 1, 2)

        left_layout.addWidget(select_group)

        # Groupe achat
        achat_group = QGroupBox("Acheter du Stock")
        achat_layout = QGridLayout(achat_group)

        achat_layout.addWidget(QLabel("Quantité :"), 0, 0)
        self.spin_achat_qte = QSpinBox()
        self.spin_achat_qte.setRange(1, 100000)
        self.spin_achat_qte.setValue(1)
        achat_layout.addWidget(self.spin_achat_qte, 0, 1)

        achat_layout.addWidget(QLabel("Prix unitaire :"), 1, 0)
        self.spin_achat_prix = QDoubleSpinBox()
        self.spin_achat_prix.setRange(0, 1000000)
        self.spin_achat_prix.setDecimals(2)
        self.spin_achat_prix.setSuffix(" DH")
        self.spin_achat_prix.setValue(0)
        achat_layout.addWidget(self.spin_achat_prix, 1, 1)

        self.btn_acheter = QPushButton("Acheter")
        self.btn_acheter.setObjectName("btnAcheter")
        self.btn_acheter.setMinimumHeight(40)
        self.btn_acheter.clicked.connect(self.acheter_stock)
        achat_layout.addWidget(self.btn_acheter, 2, 0, 1, 2)

        left_layout.addWidget(achat_group)

        # Groupe vente
        vente_group = QGroupBox("Vendre du Stock")
        vente_layout = QGridLayout(vente_group)

        vente_layout.addWidget(QLabel("Quantité :"), 0, 0)
        self.spin_vente_qte = QSpinBox()
        self.spin_vente_qte.setRange(1, 100000)
        self.spin_vente_qte.setValue(1)
        vente_layout.addWidget(self.spin_vente_qte, 0, 1)

        vente_layout.addWidget(QLabel("Prix unitaire :"), 1, 0)
        self.spin_vente_prix = QDoubleSpinBox()
        self.spin_vente_prix.setRange(0, 1000000)
        self.spin_vente_prix.setDecimals(2)
        self.spin_vente_prix.setSuffix(" DH")
        self.spin_vente_prix.setValue(0)
        vente_layout.addWidget(self.spin_vente_prix, 1, 1)

        # Label avertissement stock insuffisant
        self.label_avertissement = QLabel("")
        self.label_avertissement.setStyleSheet("color: #ff5252; font-weight: bold;")
        self.label_avertissement.setWordWrap(True)
        vente_layout.addWidget(self.label_avertissement, 2, 0, 1, 2)

        self.btn_vendre = QPushButton("Vendre")
        self.btn_vendre.setObjectName("btnVendre")
        self.btn_vendre.setMinimumHeight(40)
        self.btn_vendre.clicked.connect(self.vendre_stock)
        vente_layout.addWidget(self.btn_vendre, 3, 0, 1, 2)

        left_layout.addWidget(vente_group)
        left_layout.addStretch()

        # ── Panneau droit : Table des produits ──
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(QLabel("Cliquez sur un produit pour le sélectionner ↓"))

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Produit", "Catégorie", "Quantité", "Prix Achat", "Prix Vente"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.cellClicked.connect(self.on_table_row_clicked)
        right_layout.addWidget(self.table)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 500])

        main_layout.addWidget(splitter)

    def load_products(self):
        """Charge les produits dans le combo et la table."""
        produits = self.db.get_all_produits()

        # Stocker les IDs pour la correspondance table -> combo
        self._product_ids = [p["id"] for p in produits]

        # Combo
        self.combo_produit.blockSignals(True)
        self.combo_produit.clear()
        for p in produits:
            self.combo_produit.addItem(f"{p['nom']} ({p['categorie']})", p["id"])
        self.combo_produit.blockSignals(False)

        # Table
        self.table.setRowCount(len(produits))
        for row, p in enumerate(produits):
            self.table.setItem(row, 0, QTableWidgetItem(p["nom"]))
            self.table.setItem(row, 1, QTableWidgetItem(p["categorie"]))

            qte_item = QTableWidgetItem(str(p["quantite"]))
            if p["quantite"] == 0:
                qte_item.setForeground(QColor("#ff5252"))
                qte_font = QFont()
                qte_font.setBold(True)
                qte_item.setFont(qte_font)
            elif p["quantite"] <= p["seuil_alerte"]:
                qte_item.setForeground(QColor("#ff9800"))
            self.table.setItem(row, 2, qte_item)

            self.table.setItem(row, 3, QTableWidgetItem(f"{p['prix_achat']:.2f} DH"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{p['prix_vente']:.2f} DH"))

        if produits:
            self.combo_produit.setCurrentIndex(0)
            self.on_product_selected(0)
            self.table.selectRow(0)

    def on_product_selected(self, index: int):
        """Met à jour les informations du produit sélectionné."""
        if index < 0:
            self.clear_product_info()
            return

        produit_id = self.combo_produit.currentData()
        if not produit_id:
            self.clear_product_info()
            return

        # Surligner la ligne correspondante dans la table
        self._highlight_table_row(produit_id)

        produit = self.db.get_produit_by_id(produit_id)
        if not produit:
            self.clear_product_info()
            return

        self.label_info_nom.setText(produit["nom"])
        self.label_info_categorie.setText(produit["categorie"])

        qte = produit["quantite"]
        seuil = produit["seuil_alerte"]
        qte_text = str(qte)
        if qte == 0:
            qte_text += " (RUPTURE)"
            self.label_info_quantite.setStyleSheet(
                "color: #ff5252; font-weight: bold; font-size: 14px;"
            )
        elif qte <= seuil:
            qte_text += f" (Alerte < {seuil})"
            self.label_info_quantite.setStyleSheet(
                "color: #ff9800; font-weight: bold; font-size: 14px;"
            )
        else:
            self.label_info_quantite.setStyleSheet(
                "color: #4caf50; font-weight: bold; font-size: 14px;"
            )
        self.label_info_quantite.setText(qte_text)

        self.label_info_prix_achat.setText(f"{produit['prix_achat']:.2f} DH")
        self.label_info_prix_vente.setText(f"{produit['prix_vente']:.2f} DH")

        # Préremplir les prix
        self.spin_achat_prix.setValue(produit["prix_achat"])
        self.spin_vente_prix.setValue(produit["prix_vente"])

        # Vérification stock insuffisant pour la vente
        self.check_stock_suffisant()

        # Mettre à jour le max de la spinbox vente
        self.spin_vente_qte.setMaximum(max(qte, 1))

    def clear_product_info(self):
        """Efface les informations du produit."""
        self.label_info_nom.setText("—")
        self.label_info_categorie.setText("—")
        self.label_info_quantite.setText("—")
        self.label_info_prix_achat.setText("—")
        self.label_info_prix_vente.setText("—")
        self.label_avertissement.setText("")

    def check_stock_suffisant(self):
        """Vérifie si le stock est suffisant pour la vente demandée."""
        produit_id = self.combo_produit.currentData()
        if not produit_id:
            return

        produit = self.db.get_produit_by_id(produit_id)
        if not produit:
            return

        qte_demandee = self.spin_vente_qte.value()
        if qte_demandee > produit["quantite"]:
            self.label_avertissement.setText(
                f"Stock insuffisant ! Disponible : {produit['quantite']}, "
                f"Demandé : {qte_demandee}"
            )
        else:
            self.label_avertissement.setText("")

    def acheter_stock(self):
        """Effectue un achat de stock pour le produit sélectionné."""
        produit_id = self.combo_produit.currentData()
        if not produit_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un produit.")
            return

        quantite = self.spin_achat_qte.value()
        prix = self.spin_achat_prix.value()

        if quantite <= 0:
            QMessageBox.warning(self, "Validation", "La quantité doit être supérieure à 0.")
            return
        if prix <= 0:
            QMessageBox.warning(self, "Validation", "Le prix unitaire doit être supérieur à 0.")
            return

        try:
            self.db.acheter_stock(produit_id, quantite, prix)
            produit = self.db.get_produit_by_id(produit_id)
            QMessageBox.information(
                self, "Achat réussi",
                f"Achat de {quantite} unité(s) de '{produit['nom']}' à {prix:.2f} DH/unité.\n"
                f"Nouveau stock : {produit['quantite']} unité(s)."
            )
            self.load_products()
            self.stock_changed.emit()
        except RuntimeError as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def vendre_stock(self):
        """Effectue une vente de stock pour le produit sélectionné."""
        produit_id = self.combo_produit.currentData()
        if not produit_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un produit.")
            return

        quantite = self.spin_vente_qte.value()
        prix = self.spin_vente_prix.value()

        if quantite <= 0:
            QMessageBox.warning(self, "Validation", "La quantité doit être supérieure à 0.")
            return
        if prix <= 0:
            QMessageBox.warning(self, "Validation", "Le prix unitaire doit être supérieur à 0.")
            return

        try:
            self.db.vendre_stock(produit_id, quantite, prix)
            produit = self.db.get_produit_by_id(produit_id)
            total_vente = quantite * prix
            QMessageBox.information(
                self, "Vente réussie",
                f"Vente de {quantite} unité(s) de '{produit['nom']}' à {prix:.2f} DH/unité.\n"
                f"Total : {total_vente:.2f} DH\n"
                f"Stock restant : {produit['quantite']} unité(s)."
            )
            self.load_products()
            self.stock_changed.emit()
        except RuntimeError as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def on_table_row_clicked(self, row: int, column: int):
        """Quand on clique sur une ligne du tableau, sélectionne le produit correspondant dans le combo."""
        if 0 <= row < len(self._product_ids):
            produit_id = self._product_ids[row]
            # Trouver l'index dans le combo qui correspond à cet ID
            for i in range(self.combo_produit.count()):
                if self.combo_produit.itemData(i) == produit_id:
                    self.combo_produit.setCurrentIndex(i)
                    break

    def _highlight_table_row(self, produit_id: int):
        """Surligne la ligne du tableau correspondant au produit sélectionné dans le combo."""
        for row in range(len(self._product_ids)):
            if self._product_ids[row] == produit_id:
                self.table.selectRow(row)
                return

    def refresh(self):
        """Rafraîchit les données de l'onglet."""
        self.load_products()
