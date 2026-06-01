"""
Onglet Statistiques - Graphiques et analyses avancées du stock.
Utilise matplotlib pour les visualisations intégrées dans PyQt6.
Compatible Windows et Linux.
"""

import os
import platform

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QGroupBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

import matplotlib
# Utiliser le backend Qt pour un rendu correct dans PyQt6
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from utils.export import export_csv

# Devise utilisée dans l'application
CURRENCY = "DH"

# Configuration des polices pour matplotlib (compatible Windows/Linux)
system = platform.system()
if system == "Windows":
    # Sur Windows, utiliser les polices système
    win_dir = os.environ.get('WINDIR', r'C:\Windows')
    win_font_dir = os.path.join(win_dir, 'Fonts')
    for fname in ['segoeui.ttf', 'arial.ttf', 'tahoma.ttf']:
        fpath = os.path.join(win_font_dir, fname)
        if os.path.exists(fpath):
            try:
                fm.fontManager.addfont(fpath)
            except Exception:
                pass
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Tahoma', 'DejaVu Sans']
elif system == "Linux":
    try:
        fm.fontManager.addfont('/usr/share/fonts/truetype/chinese/NotoSansSC[wght].ttf')
    except Exception:
        pass
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Noto Sans SC', 'Arial']
else:
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

plt.rcParams['axes.unicode_minus'] = False


class MplCanvas(FigureCanvas):
    """Canvas matplotlib intégré dans PyQt6."""

    def __init__(self, parent=None, width=5, height=3, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#16213e')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#1a2744')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setMinimumHeight(220)


class StatsTab(QWidget):
    """Onglet Statistiques avec graphiques et analyses."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        """Configure l'interface des statistiques."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # ── Titre ──
        titre = QLabel("Statistiques & Analyses")
        titre.setObjectName("labelTitre")
        font = QFont()
        font.setPointSize(20)
        font.setWeight(QFont.Weight.Bold)
        titre.setFont(font)
        main_layout.addWidget(titre)

        # ── Zone défilable pour les graphiques ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #1a1a2e; }
            QScrollBar:vertical {
                background-color: #1a1a2e; width: 10px; border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a5a; min-height: 30px; border-radius: 5px;
            }
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)

        # ── Ligne 1 : 2 graphiques ──
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(8)

        # Graphique 1 : Stock par catégorie
        chart1_group = QGroupBox("Stock par Catégorie")
        chart1_layout = QVBoxLayout(chart1_group)
        chart1_layout.setContentsMargins(4, 16, 4, 4)
        self.canvas_stock_categorie = MplCanvas(self, width=5, height=3, dpi=100)
        chart1_layout.addWidget(self.canvas_stock_categorie)
        row1_layout.addWidget(chart1_group)

        # Graphique 2 : Top 5 produits les plus vendus
        chart2_group = QGroupBox("Top 5 Produits les Plus Vendus")
        chart2_layout = QVBoxLayout(chart2_group)
        chart2_layout.setContentsMargins(4, 16, 4, 4)
        self.canvas_top_ventes = MplCanvas(self, width=5, height=3, dpi=100)
        chart2_layout.addWidget(self.canvas_top_ventes)
        row1_layout.addWidget(chart2_group)

        scroll_layout.addLayout(row1_layout)

        # ── Ligne 2 : 2 graphiques ──
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(8)

        # Graphique 3 : Répartition par valeur (camembert)
        chart3_group = QGroupBox("Répartition de la Valeur du Stock")
        chart3_layout = QVBoxLayout(chart3_group)
        chart3_layout.setContentsMargins(4, 16, 4, 4)
        self.canvas_valeur_repartition = MplCanvas(self, width=5, height=3, dpi=100)
        chart3_layout.addWidget(self.canvas_valeur_repartition)
        row2_layout.addWidget(chart3_group)

        # Graphique 4 : Ventes par catégorie
        chart4_group = QGroupBox("Chiffre d'Affaires par Catégorie")
        chart4_layout = QVBoxLayout(chart4_group)
        chart4_layout.setContentsMargins(4, 16, 4, 4)
        self.canvas_ventes_categorie = MplCanvas(self, width=5, height=3, dpi=100)
        chart4_layout.addWidget(self.canvas_ventes_categorie)
        row2_layout.addWidget(chart4_group)

        scroll_layout.addLayout(row2_layout)

        # ── Tableau Statistiques ──
        stats_group = QGroupBox("Classement des Produits")
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setContentsMargins(8, 16, 8, 8)

        self.table_stats = QTableWidget()
        self.table_stats.setColumnCount(7)
        self.table_stats.setHorizontalHeaderLabels([
            "Produit", "Catégorie", "Quantité", "Prix Achat",
            "Prix Vente", "Marge", "Valeur Stock"
        ])
        self.table_stats.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table_stats.setAlternatingRowColors(True)
        self.table_stats.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_stats.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_stats.setMinimumHeight(150)
        self.table_stats.setMaximumHeight(220)
        stats_layout.addWidget(self.table_stats)

        # Boutons export
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        self.btn_export_produits_csv = QPushButton("Exporter Produits CSV")
        self.btn_export_produits_csv.setObjectName("btnExport")
        self.btn_export_produits_csv.clicked.connect(self.exporter_produits_csv)
        export_layout.addWidget(self.btn_export_produits_csv)



        stats_layout.addLayout(export_layout)

        scroll_layout.addWidget(stats_group)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def refresh(self):
        """Rafraîchit tous les graphiques et tableaux."""
        try:
            self.draw_stock_par_categorie()
        except Exception as e:
            print(f"Erreur graphique stock catégorie : {e}")
        try:
            self.draw_top_ventes()
        except Exception as e:
            print(f"Erreur graphique top ventes : {e}")
        try:
            self.draw_valeur_repartition()
        except Exception as e:
            print(f"Erreur graphique répartition : {e}")
        try:
            self.draw_ventes_categorie()
        except Exception as e:
            print(f"Erreur graphique ventes catégorie : {e}")
        try:
            self.load_stats_table()
        except Exception as e:
            print(f"Erreur tableau stats : {e}")

    def _style_axes(self, axes, title: str):
        """Applique un style cohérent aux axes matplotlib."""
        axes.set_title(title, color='#e0e0e0', fontsize=11, fontweight='bold', pad=8)
        axes.tick_params(colors='#a0a0b0', labelsize=8)
        axes.spines['bottom'].set_color('#2d2d44')
        axes.spines['left'].set_color('#2d2d44')
        axes.spines['top'].set_visible(False)
        axes.spines['right'].set_visible(False)
        axes.xaxis.label.set_color('#a0a0b0')
        axes.yaxis.label.set_color('#a0a0b0')

    def draw_stock_par_categorie(self):
        """Dessine le graphique du stock par catégorie."""
        produits = self.db.get_all_produits()
        if not produits:
            return

        # Agréger par catégorie
        cat_data = {}
        for p in produits:
            cat = p["categorie"]
            cat_data[cat] = cat_data.get(cat, 0) + p["quantite"]

        categories = list(cat_data.keys())
        quantites = list(cat_data.values())

        axes = self.canvas_stock_categorie.axes
        axes.clear()

        colors = ['#00d2ff', '#4caf50', '#ff9800', '#ab47bc',
                  '#42a5f5', '#ef5350', '#26a69a', '#ffeb3b']

        bars = axes.bar(categories, quantites, color=colors[:len(categories)],
                        edgecolor='#1a1a2e', linewidth=1.5)

        # Ajouter les valeurs sur les barres
        for bar, val in zip(bars, quantites):
            axes.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                      str(val), ha='center', va='bottom', color='#e0e0e0',
                      fontsize=9, fontweight='bold')

        self._style_axes(axes, "Quantité par Catégorie")
        axes.set_ylabel("Quantité")

        self.canvas_stock_categorie.fig.tight_layout(pad=1.5)
        self.canvas_stock_categorie.draw()

    def draw_top_ventes(self):
        """Dessine le graphique des top ventes."""
        top = self.db.get_top_produits_ventes(limit=5)
        axes = self.canvas_top_ventes.axes
        axes.clear()

        if not top:
            axes.text(0.5, 0.5, "Aucune vente enregistrée",
                      ha='center', va='center', color='#a0a0b0',
                      fontsize=12, transform=axes.transAxes)
            axes.set_facecolor('#1a2744')
            self.canvas_top_ventes.fig.tight_layout(pad=1.5)
            self.canvas_top_ventes.draw()
            return

        noms = [p["produit_nom"][:15] for p in top]
        quantites = [p["total_vendu"] for p in top]

        colors = ['#ab47bc', '#42a5f5', '#4caf50', '#ff9800', '#00d2ff']
        bars = axes.barh(noms, quantites, color=colors[:len(noms)],
                         edgecolor='#1a1a2e', linewidth=1.5)

        for bar, val in zip(bars, quantites):
            axes.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                      str(val), ha='left', va='center', color='#e0e0e0',
                      fontsize=9, fontweight='bold')

        self._style_axes(axes, "Top 5 Produits Vendus")
        axes.set_xlabel("Unités vendues")

        self.canvas_top_ventes.fig.tight_layout(pad=1.5)
        self.canvas_top_ventes.draw()

    def draw_valeur_repartition(self):
        """Dessine le camembert de répartition de la valeur du stock."""
        produits = self.db.get_all_produits()
        axes = self.canvas_valeur_repartition.axes
        axes.clear()

        if not produits:
            axes.text(0.5, 0.5, "Aucun produit",
                      ha='center', va='center', color='#a0a0b0',
                      fontsize=12, transform=axes.transAxes)
            axes.set_facecolor('#1a2744')
            self.canvas_valeur_repartition.fig.tight_layout(pad=1.5)
            self.canvas_valeur_repartition.draw()
            return

        # Calculer la valeur par produit
        noms = []
        valeurs = []
        for p in produits:
            val = p["quantite"] * p["prix_vente"]
            if val > 0:
                noms.append(p["nom"][:15])
                valeurs.append(val)

        if not valeurs:
            axes.text(0.5, 0.5, "Aucune valeur en stock",
                      ha='center', va='center', color='#a0a0b0',
                      fontsize=12, transform=axes.transAxes)
            axes.set_facecolor('#1a2744')
            self.canvas_valeur_repartition.fig.tight_layout(pad=1.5)
            self.canvas_valeur_repartition.draw()
            return

        # Si trop de produits, grouper les petits
        if len(noms) > 8:
            combined = sorted(zip(noms, valeurs), key=lambda x: x[1], reverse=True)
            top_noms = [c[0] for c in combined[:7]]
            top_valeurs = [c[1] for c in combined[:7]]
            other_val = sum(c[1] for c in combined[7:])
            top_noms.append("Autres")
            top_valeurs.append(other_val)
            noms = top_noms
            valeurs = top_valeurs

        colors = ['#00d2ff', '#4caf50', '#ff9800', '#ab47bc',
                  '#42a5f5', '#ef5350', '#26a69a', '#ffeb3b']

        wedges, texts, autotexts = axes.pie(
            valeurs, labels=noms, autopct='%1.1f%%',
            colors=colors[:len(valeurs)],
            startangle=90,
            textprops={'color': '#e0e0e0', 'fontsize': 8}
        )
        for autotext in autotexts:
            autotext.set_fontsize(7)
            autotext.set_color('#1a1a2e')
            autotext.set_fontweight('bold')

        axes.set_title(f"Répartition Valeur Stock (Prix Vente)",
                        color='#e0e0e0', fontsize=11, fontweight='bold', pad=8)

        self.canvas_valeur_repartition.fig.tight_layout(pad=1.5)
        self.canvas_valeur_repartition.draw()

    def draw_ventes_categorie(self):
        """Dessine le graphique du CA par catégorie."""
        data = self.db.get_ventes_par_categorie()
        axes = self.canvas_ventes_categorie.axes
        axes.clear()

        if not data:
            axes.text(0.5, 0.5, "Aucune vente enregistrée",
                      ha='center', va='center', color='#a0a0b0',
                      fontsize=12, transform=axes.transAxes)
            axes.set_facecolor('#1a2744')
            self.canvas_ventes_categorie.fig.tight_layout(pad=1.5)
            self.canvas_ventes_categorie.draw()
            return

        categories = [d["categorie"] for d in data]
        ca = [d["chiffre_affaires"] for d in data]

        colors = ['#26a69a', '#00d2ff', '#4caf50', '#ff9800',
                  '#ab47bc', '#42a5f5', '#ef5350']

        bars = axes.bar(categories, ca, color=colors[:len(categories)],
                        edgecolor='#1a1a2e', linewidth=1.5)

        for bar, val in zip(bars, ca):
            axes.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                      f"{val:.0f} {CURRENCY}", ha='center', va='bottom',
                      color='#e0e0e0', fontsize=8, fontweight='bold')

        self._style_axes(axes, "Chiffre d'Affaires par Catégorie")
        axes.set_ylabel(f"CA ({CURRENCY})")

        self.canvas_ventes_categorie.fig.tight_layout(pad=1.5)
        self.canvas_ventes_categorie.draw()

    def load_stats_table(self):
        """Charge le tableau des statistiques produits."""
        produits = self.db.get_all_produits()

        # Trier par valeur de stock (décroissant)
        produits_sorted = sorted(
            produits,
            key=lambda p: p["quantite"] * p["prix_vente"],
            reverse=True
        )

        self.table_stats.setRowCount(len(produits_sorted))
        for row, p in enumerate(produits_sorted):
            marge = p["prix_vente"] - p["prix_achat"]
            valeur = p["quantite"] * p["prix_vente"]

            self.table_stats.setItem(row, 0, QTableWidgetItem(p["nom"]))
            self.table_stats.setItem(row, 1, QTableWidgetItem(p["categorie"]))
            self.table_stats.setItem(row, 2, QTableWidgetItem(str(p["quantite"])))
            self.table_stats.setItem(row, 3, QTableWidgetItem(f"{p['prix_achat']:.2f} {CURRENCY}"))
            self.table_stats.setItem(row, 4, QTableWidgetItem(f"{p['prix_vente']:.2f} {CURRENCY}"))

            marge_item = QTableWidgetItem(f"{marge:.2f} {CURRENCY}")
            if marge < 0:
                marge_item.setForeground(QColor("#ff5252"))
            else:
                marge_item.setForeground(QColor("#4caf50"))
            self.table_stats.setItem(row, 5, marge_item)

            self.table_stats.setItem(row, 6, QTableWidgetItem(f"{valeur:,.2f} {CURRENCY}"))

    def exporter_produits_csv(self):
        """Exporte les produits en CSV."""
        produits = self.db.get_all_produits()
        if not produits:
            QMessageBox.warning(self, "Attention", "Aucune donnée à exporter.")
            return
        try:
            path = export_csv(produits, "produits_stock")
            QMessageBox.information(self, "Export réussi", f"Fichier exporté : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export : {e}")
