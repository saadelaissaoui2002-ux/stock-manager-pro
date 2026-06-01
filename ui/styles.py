"""
Feuille de style QSS pour l'interface moderne du Gestionnaire de Stock Intelligent.
Thème sombre professionnel inspiré des interfaces modernes.
"""

MODERN_STYLE = """
/* ──────────────────────────────────────
   Style Global
   ────────────────────────────────────── */
QMainWindow {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}

QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}

/* ──────────────────────────────────────
   QTabWidget
   ────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #2d2d44;
    background-color: #16213e;
    border-radius: 4px;
    top: -1px;
}

QTabBar::tab {
    background-color: #1a1a2e;
    color: #a0a0b0;
    padding: 10px 24px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
    font-size: 13px;
    min-width: 120px;
}

QTabBar::tab:selected {
    background-color: #16213e;
    color: #00d2ff;
    border-bottom: 3px solid #00d2ff;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #2d2d44;
    color: #c0c0d0;
}

/* ──────────────────────────────────────
   QPushButton
   ────────────────────────────────────── */
QPushButton {
    background-color: #0f3460;
    color: #e0e0e0;
    border: 1px solid #1a4a7a;
    padding: 8px 20px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #1a4a7a;
    border-color: #00d2ff;
}

QPushButton:pressed {
    background-color: #0a2540;
}

QPushButton:disabled {
    background-color: #2d2d44;
    color: #5a5a6a;
    border-color: #3a3a4a;
}

/* Boutons d'action spécialisés */
QPushButton#btnAjouter {
    background-color: #1b5e20;
    border-color: #2e7d32;
}
QPushButton#btnAjouter:hover {
    background-color: #2e7d32;
    border-color: #4caf50;
}

QPushButton#btnModifier {
    background-color: #e65100;
    border-color: #ef6c00;
}
QPushButton#btnModifier:hover {
    background-color: #ef6c00;
    border-color: #ff9800;
}

QPushButton#btnSupprimer {
    background-color: #b71c1c;
    border-color: #c62828;
}
QPushButton#btnSupprimer:hover {
    background-color: #c62828;
    border-color: #ef5350;
}

QPushButton#btnAcheter {
    background-color: #0d47a1;
    border-color: #1565c0;
}
QPushButton#btnAcheter:hover {
    background-color: #1565c0;
    border-color: #42a5f5;
}

QPushButton#btnVendre {
    background-color: #4a148c;
    border-color: #6a1b9a;
}
QPushButton#btnVendre:hover {
    background-color: #6a1b9a;
    border-color: #ab47bc;
}

QPushButton#btnExport {
    background-color: #00695c;
    border-color: #00897b;
}
QPushButton#btnExport:hover {
    background-color: #00897b;
    border-color: #26a69a;
}

/* ──────────────────────────────────────
   QLineEdit
   ────────────────────────────────────── */
QLineEdit {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #2d2d44;
    padding: 8px 12px;
    border-radius: 6px;
    selection-background-color: #0f3460;
    font-size: 13px;
}

QLineEdit:focus {
    border-color: #00d2ff;
    border-width: 2px;
}

QLineEdit:disabled {
    background-color: #2d2d44;
    color: #5a5a6a;
}

/* ──────────────────────────────────────
   QComboBox
   ────────────────────────────────────── */
QComboBox {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #2d2d44;
    padding: 8px 12px;
    border-radius: 6px;
    min-height: 20px;
}

QComboBox:focus {
    border-color: #00d2ff;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #2d2d44;
    selection-background-color: #0f3460;
}

/* ──────────────────────────────────────
   QSpinBox / QDoubleSpinBox
   ────────────────────────────────────── */
QSpinBox, QDoubleSpinBox {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #2d2d44;
    padding: 6px 10px;
    border-radius: 6px;
    min-height: 20px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #00d2ff;
}

/* ──────────────────────────────────────
   QTableWidget
   ────────────────────────────────────── */
QTableWidget {
    background-color: #16213e;
    alternate-background-color: #1a2744;
    color: #e0e0e0;
    border: 1px solid #2d2d44;
    gridline-color: #2d2d44;
    border-radius: 4px;
    selection-background-color: #0f3460;
    selection-color: #ffffff;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:hover {
    background-color: #2d2d44;
}

QHeaderView::section {
    background-color: #0f3460;
    color: #00d2ff;
    padding: 8px;
    border: 1px solid #1a4a7a;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
}

QTableWidget QTableCornerButton::section {
    background-color: #0f3460;
    border: 1px solid #1a4a7a;
}

/* ──────────────────────────────────────
   QScrollBar
   ────────────────────────────────────── */
QScrollBar:vertical {
    background-color: #1a1a2e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #3a3a5a;
    min-height: 30px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5a5a7a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1a1a2e;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #3a3a5a;
    min-width: 30px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #5a5a7a;
}

/* ──────────────────────────────────────
   QLabel
   ────────────────────────────────────── */
QLabel {
    color: #e0e0e0;
    font-size: 13px;
}

QLabel#labelTitre {
    color: #00d2ff;
    font-size: 18px;
    font-weight: 700;
}

QLabel#labelSousTitre {
    color: #a0a0b0;
    font-size: 14px;
    font-weight: 400;
}

QLabel#labelStatValeur {
    color: #00d2ff;
    font-size: 28px;
    font-weight: 700;
}

QLabel#labelStatLabel {
    color: #a0a0b0;
    font-size: 12px;
    font-weight: 400;
}

QLabel#labelAlerte {
    color: #ff5252;
    font-size: 13px;
    font-weight: 600;
}

/* ──────────────────────────────────────
   QGroupBox
   ────────────────────────────────────── */
QGroupBox {
    background-color: #16213e;
    border: 1px solid #2d2d44;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 16px;
    font-weight: 600;
    color: #00d2ff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}

/* ──────────────────────────────────────
   QMessageBox
   ────────────────────────────────────── */
QMessageBox {
    background-color: #1a1a2e;
}

QMessageBox QLabel {
    color: #e0e0e0;
    font-size: 14px;
}

/* ──────────────────────────────────────
   QDateEdit
   ────────────────────────────────────── */
QDateEdit {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #2d2d44;
    padding: 6px 10px;
    border-radius: 6px;
}

QDateEdit:focus {
    border-color: #00d2ff;
}

/* ──────────────────────────────────────
   QFrame (carte statistique)
   ────────────────────────────────────── */
QFrame#carteStat {
    background-color: #16213e;
    border: 1px solid #2d2d44;
    border-radius: 12px;
    padding: 16px;
}

QFrame#carteAlerte {
    background-color: #2a1a1a;
    border: 2px solid #c62828;
    border-radius: 12px;
    padding: 16px;
}

/* ──────────────────────────────────────
   QStatusBar
   ────────────────────────────────────── */
QStatusBar {
    background-color: #0f0f1a;
    color: #a0a0b0;
    border-top: 1px solid #2d2d44;
    font-size: 12px;
}

/* ──────────────────────────────────────
   QMenuBar / QMenu
   ────────────────────────────────────── */
QMenuBar {
    background-color: #0f0f1a;
    color: #e0e0e0;
    border-bottom: 1px solid #2d2d44;
}

QMenuBar::item:selected {
    background-color: #0f3460;
}

QMenu {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #2d2d44;
}

QMenu::item:selected {
    background-color: #0f3460;
}
"""
