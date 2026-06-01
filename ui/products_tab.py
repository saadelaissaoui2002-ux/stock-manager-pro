"""
Onglet Gestion des Produits - Ajout, modification, suppression et recherche.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox,
    QGroupBox, QDialog, QFormLayout, QSpinBox,
    QDoubleSpinBox, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from models.product import Product
from utils.validators import validate_text, validate_float, validate_integer, validate_prix_vente


class ProductDialog(QDialog):
    """Dialogue pour ajouter ou modifier un produit."""

    def __init__(self, parent=None, produit: Product = None, categories: list = None):
        super().__init__(parent)
        self.produit = produit
        self.categories = categories or []
        self.setup_ui()
        if produit:
            self.fill_form(produit)

    def setup_ui(self):
        """Configure le formulaire du dialogue."""
        self.setWindowTitle("Modifier le produit" if self.produit else "Ajouter un produit")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: #e0e0e0;
            }
            QLabel { color: #e0e0e0; font-size: 13px; }
            QLineEdit, QComboBox {
                background-color: #16213e;
                color: #e0e0e0;
                border: 1px solid #2d2d44;
                padding: 8px;
                border-radius: 6px;
                min-height: 20px;
            }
            QDoubleSpinBox, QSpinBox {
                background-color: #16213e;
                color: #e0e0e0;
                border: 1px solid #2d2d44;
                padding: 6px;
                border-radius: 6px;
                min-height: 20px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Titre
        titre = QLabel("Modifier le produit" if self.produit else "Nouveau Produit")
        titre.setStyleSheet("color: #00d2ff; font-size: 18px; font-weight: bold;")
        layout.addWidget(titre)

        # Formulaire
        form = QFormLayout()
        form.setSpacing(10)

        self.input_nom = QLineEdit()
        self.input_nom.setPlaceholderText("Nom du produit")
        form.addRow("Nom * :", self.input_nom)

        self.input_categorie = QComboBox()
        self.input_categorie.setEditable(True)
        self.input_categorie.addItems(self.categories)
        self.input_categorie.setCurrentText("")
        self.input_categorie.setPlaceholderText("Catégorie du produit")
        form.addRow("Catégorie * :", self.input_categorie)

        self.input_prix_achat = QDoubleSpinBox()
        self.input_prix_achat.setRange(0, 1000000)
        self.input_prix_achat.setDecimals(2)
        self.input_prix_achat.setSuffix(" DH")
        self.input_prix_achat.setValue(0)
        form.addRow("Prix d'achat * :", self.input_prix_achat)

        self.input_prix_vente = QDoubleSpinBox()
        self.input_prix_vente.setRange(0, 1000000)
        self.input_prix_vente.setDecimals(2)
        self.input_prix_vente.setSuffix(" DH")
        self.input_prix_vente.setValue(0)
        form.addRow("Prix de vente * :", self.input_prix_vente)

        self.input_quantite = QSpinBox()
        self.input_quantite.setRange(0, 10000000)
        self.input_quantite.setValue(0)
        form.addRow("Quantité * :", self.input_quantite)

        self.input_seuil = QSpinBox()
        self.input_seuil.setRange(0, 100000)
        self.input_seuil.setValue(5)
        form.addRow("Seuil d'alerte :", self.input_seuil)

        layout.addLayout(form)

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_valider = QPushButton("Enregistrer")
        self.btn_valider.setObjectName("btnAjouter")
        self.btn_valider.clicked.connect(self.valider)

        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_annuler)
        btn_layout.addWidget(self.btn_valider)
        layout.addLayout(btn_layout)

    def fill_form(self, produit: Product):
        """Remplit le formulaire avec les données du produit existant."""
        self.input_nom.setText(produit.nom)
        self.input_categorie.setCurrentText(produit.categorie)
        self.input_prix_achat.setValue(produit.prix_achat)
        self.input_prix_vente.setValue(produit.prix_vente)
        self.input_quantite.setValue(produit.quantite)
        self.input_seuil.setValue(produit.seuil_alerte)

    def valider(self):
        """Valide les entrées et accepte le dialogue."""
        nom = self.input_nom.text().strip()
        categorie = self.input_categorie.currentText().strip()
        prix_achat = self.input_prix_achat.value()
        prix_vente = self.input_prix_vente.value()
        quantite = self.input_quantite.value()
        seuil = self.input_seuil.value()

        # Validations
        valid, msg = validate_text(nom, "Nom")
        if not valid:
            QMessageBox.warning(self, "Validation", msg)
            return

        valid, msg = validate_text(categorie, "Catégorie")
        if not valid:
            QMessageBox.warning(self, "Validation", msg)
            return

        # Avertissement prix de vente < prix d'achat
        valid, msg = validate_prix_vente(prix_vente, prix_achat)
        if msg:
            reply = QMessageBox.question(
                self, "Attention", msg + "\n\nContinuer quand même ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self.result_data = {
            "nom": nom,
            "categorie": categorie,
            "prix_achat": prix_achat,
            "prix_vente": prix_vente,
            "quantite": quantite,
            "seuil_alerte": seuil,
        }
        self.accept()

    def get_data(self) -> dict:
        """Retourne les données du formulaire validé."""
        return getattr(self, 'result_data', {})


class ProductsTab(QWidget):
    """Onglet de gestion des produits."""

    product_changed = pyqtSignal()  # Signal émis quand un produit est modifié

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        """Configure l'interface de gestion des produits."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # ── Titre ──
        titre = QLabel("Gestion des Produits")
        titre.setObjectName("labelTitre")
        font = QFont()
        font.setPointSize(20)
        font.setWeight(QFont.Weight.Bold)
        titre.setFont(font)
        main_layout.addWidget(titre)

        # ── Barre de recherche et filtres ──
        search_layout = QHBoxLayout()

        self.input_recherche = QLineEdit()
        self.input_recherche.setPlaceholderText("Rechercher un produit (nom, catégorie)...")
        self.input_recherche.textChanged.connect(self.on_search)
        self.input_recherche.setMinimumHeight(38)
        search_layout.addWidget(self.input_recherche, stretch=3)

        self.combo_categorie = QComboBox()
        self.combo_categorie.addItem("Toutes catégories")
        self.combo_categorie.currentTextChanged.connect(self.on_search)
        self.combo_categorie.setMinimumWidth(180)
        search_layout.addWidget(self.combo_categorie, stretch=1)

        self.btn_stock_faible = QPushButton("Stock Faible")
        self.btn_stock_faible.setCheckable(True)
        self.btn_stock_faible.clicked.connect(self.on_search)
        search_layout.addWidget(self.btn_stock_faible)

        main_layout.addLayout(search_layout)

        # ── Table des produits ──
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Catégorie", "Prix Achat", "Prix Vente",
            "Quantité", "Seuil Alerte", "Marge"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setShowGrid(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        main_layout.addWidget(self.table)

        # ── Boutons d'action ──
        btn_layout = QHBoxLayout()

        self.btn_ajouter = QPushButton("Ajouter un Produit")
        self.btn_ajouter.setObjectName("btnAjouter")
        self.btn_ajouter.setMinimumHeight(40)
        self.btn_ajouter.clicked.connect(self.ajouter_produit)
        btn_layout.addWidget(self.btn_ajouter)

        self.btn_modifier = QPushButton("Modifier")
        self.btn_modifier.setObjectName("btnModifier")
        self.btn_modifier.setMinimumHeight(40)
        self.btn_modifier.setEnabled(False)
        self.btn_modifier.clicked.connect(self.modifier_produit)
        btn_layout.addWidget(self.btn_modifier)

        self.btn_supprimer = QPushButton("Supprimer")
        self.btn_supprimer.setObjectName("btnSupprimer")
        self.btn_supprimer.setMinimumHeight(40)
        self.btn_supprimer.setEnabled(False)
        self.btn_supprimer.clicked.connect(self.supprimer_produit)
        btn_layout.addWidget(self.btn_supprimer)

        btn_layout.addStretch()

        # Label compteur
        self.label_compteur = QLabel("0 produit(s)")
        self.label_compteur.setStyleSheet("color: #a0a0b0; font-size: 12px;")
        btn_layout.addWidget(self.label_compteur)

        main_layout.addLayout(btn_layout)

    def load_products(self, produits: list = None):
        """Charge les produits dans la table."""
        if produits is None:
            produits = self.db.get_all_produits()

        self.table.setRowCount(len(produits))
        for row, p in enumerate(produits):
            product = Product.from_dict(p)
            self.table.setItem(row, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(p["nom"]))
            self.table.setItem(row, 2, QTableWidgetItem(p["categorie"]))
            self.table.setItem(row, 3, QTableWidgetItem(f"{p['prix_achat']:.2f} DH"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{p['prix_vente']:.2f} DH"))

            # Quantité avec couleur d'alerte
            qte_item = QTableWidgetItem(str(p["quantite"]))
            if p["quantite"] == 0:
                qte_item.setForeground(QColor("#ff5252"))
                qte_font = QFont()
                qte_font.setBold(True)
                qte_item.setFont(qte_font)
            elif p["quantite"] <= p["seuil_alerte"]:
                qte_item.setForeground(QColor("#ff9800"))
            self.table.setItem(row, 5, qte_item)

            self.table.setItem(row, 6, QTableWidgetItem(str(p["seuil_alerte"])))

            # Marge
            marge = product.marge
            marge_pct = product.marge_pourcentage
            marge_item = QTableWidgetItem(f"{marge:.2f} DH ({marge_pct:.1f}%)")
            if marge < 0:
                marge_item.setForeground(QColor("#ff5252"))
            else:
                marge_item.setForeground(QColor("#4caf50"))
            self.table.setItem(row, 7, marge_item)

        self.label_compteur.setText(f"{len(produits)} produit(s)")

        # Mettre à jour les catégories dans le filtre
        self.update_categories_filter()

    def update_categories_filter(self):
        """Met à jour la liste des catégories dans le filtre."""
        current = self.combo_categorie.currentText()
        self.combo_categorie.blockSignals(True)
        self.combo_categorie.clear()
        self.combo_categorie.addItem("Toutes catégories")
        categories = self.db.get_categories()
        self.combo_categorie.addItems(categories)
        idx = self.combo_categorie.findText(current)
        if idx >= 0:
            self.combo_categorie.setCurrentIndex(idx)
        self.combo_categorie.blockSignals(False)

    def on_search(self):
        """Recherche avancée de produits."""
        texte = self.input_recherche.text().strip()
        categorie = self.combo_categorie.currentText()
        if categorie == "Toutes catégories":
            categorie = ""
        stock_faible = self.btn_stock_faible.isChecked()

        produits = self.db.rechercher_produits(
            texte=texte if texte else "",
            categorie=categorie if categorie else "",
            stock_faible=stock_faible
        )
        self.load_products(produits)

    def on_selection_changed(self):
        """Active/désactive les boutons selon la sélection."""
        has_selection = len(self.table.selectedItems()) > 0
        self.btn_modifier.setEnabled(has_selection)
        self.btn_supprimer.setEnabled(has_selection)

    def get_selected_product_id(self) -> int:
        """Récupère l'ID du produit sélectionné dans la table."""
        rows = set(item.row() for item in self.table.selectedItems())
        if not rows:
            return -1
        row = rows.pop()
        id_item = self.table.item(row, 0)
        return int(id_item.text()) if id_item else -1

    def ajouter_produit(self):
        """Ouvre le dialogue d'ajout de produit."""
        categories = self.db.get_categories()
        dialog = ProductDialog(self, categories=categories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data:
                try:
                    self.db.ajouter_produit(
                        nom=data["nom"],
                        categorie=data["categorie"],
                        prix_achat=data["prix_achat"],
                        prix_vente=data["prix_vente"],
                        quantite=data["quantite"],
                        seuil_alerte=data["seuil_alerte"],
                    )
                    QMessageBox.information(
                        self, "Succès",
                        f"Produit '{data['nom']}' ajouté avec succès !"
                    )
                    self.load_products()
                    self.product_changed.emit()
                except RuntimeError as e:
                    QMessageBox.critical(self, "Erreur", str(e))

    def modifier_produit(self):
        """Ouvre le dialogue de modification du produit sélectionné."""
        produit_id = self.get_selected_product_id()
        if produit_id < 0:
            return

        produit_data = self.db.get_produit_by_id(produit_id)
        if not produit_data:
            return

        produit = Product.from_dict(produit_data)
        categories = self.db.get_categories()
        dialog = ProductDialog(self, produit=produit, categories=categories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data:
                try:
                    self.db.modifier_produit(
                        produit_id=produit_id,
                        nom=data["nom"],
                        categorie=data["categorie"],
                        prix_achat=data["prix_achat"],
                        prix_vente=data["prix_vente"],
                        quantite=data["quantite"],
                        seuil_alerte=data["seuil_alerte"],
                    )
                    QMessageBox.information(
                        self, "Succès",
                        f"Produit '{data['nom']}' modifié avec succès !"
                    )
                    self.load_products()
                    self.product_changed.emit()
                except RuntimeError as e:
                    QMessageBox.critical(self, "Erreur", str(e))

    def supprimer_produit(self):
        """Supprime le produit sélectionné après confirmation."""
        produit_id = self.get_selected_product_id()
        if produit_id < 0:
            return

        produit_data = self.db.get_produit_by_id(produit_id)
        if not produit_data:
            return

        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Etes-vous sûr de vouloir supprimer le produit '{produit_data['nom']}' ?\n"
            f"Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.supprimer_produit(produit_id)
                QMessageBox.information(self, "Succès", "Produit supprimé avec succès !")
                self.load_products()
                self.product_changed.emit()
            except RuntimeError as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def refresh(self):
        """Rafraîchit la liste des produits."""
        self.input_recherche.clear()
        self.combo_categorie.setCurrentIndex(0)
        self.btn_stock_faible.setChecked(False)
        self.load_products()
