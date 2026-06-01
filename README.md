# 📦 Stock Manager Pro

Application desktop professionnelle de gestion de stock, développée avec **Python**, **PyQt6** et **SQLite**.

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green?logo=qt)
![SQLite](https://img.shields.io/badge/SQLite-3-orange?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📸 Aperçu

- **Tableau de bord** avec statistiques en temps réel et alertes de stock
- **Gestion des produits** : ajout, modification, suppression, recherche avancée
- **Gestion du stock** : achat/vente avec prix moyen pondéré
- **Historique** : suivi complet des actions avec filtres
- **Statistiques** : graphiques interactifs (matplotlib)
- **Export CSV** : exportation des données produits et historique
- **Interface moderne** : thème sombre professionnel (QSS)

---

## 🛠️ Technologies

| Technologie | Rôle |
|---|---|
| Python 3.12+ | Langage de programmation |
| PyQt6 | Interface graphique |
| SQLite | Base de données locale |
| Matplotlib | Graphiques et visualisations |

---

## 📁 Structure du projet

```
stock_manager_pro/
├── main.py                  # Point d'entrée
├── requirements.txt         # Dépendances
├── database/
│   ├── __init__.py
│   └── db_manager.py        # Gestionnaire SQLite
├── models/
│   ├── __init__.py
│   └── product.py           # Modèle Product
├── ui/
│   ├── __init__.py
│   ├── main_window.py       # Fenêtre principale
│   ├── dashboard_tab.py     # Tableau de bord
│   ├── products_tab.py      # Gestion des produits
│   ├── stock_tab.py         # Gestion du stock
│   ├── history_tab.py       # Historique des actions
│   ├── stats_tab.py         # Statistiques et graphiques
│   └── styles.py            # Thème QSS sombre
├── utils/
│   ├── __init__.py
│   ├── export.py            # Export CSV
│   └── validators.py        # Validation des entrées
└── export/                  # Dossier des exports (auto-créé)
```

---

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/saadelaissaoui2002-ux/stock-manager-pro.git
cd stock-manager-pro
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancer l'application

```bash
python main.py
```

---

## 💡 Fonctionnalités

### Tableau de Bord
- 8 cartes de statistiques (produits, stock, valeur, marges, alertes)
- Table des produits en alerte de stock faible
- Actualisation automatique toutes les 30 secondes

### Gestion des Produits
- CRUD complet (Créer, Lire, Modifier, Supprimer)
- Recherche multi-critères (nom, catégorie, prix, stock faible)
- Filtrage par catégorie
- Validation automatique des entrées

### Gestion du Stock
- Achat de stock avec calcul du prix moyen pondéré
- Vente de stock avec vérification de disponibilité
- Sélection par combo ou par clic dans le tableau
- Alertes visuelles de stock insuffisant

### Historique
- Suivi de toutes les actions (ajout, achat, vente, modification, suppression)
- Filtrage par type d'action, produit et dates
- Code couleur par type d'action
- Compteur d'actions

### Statistiques
- Stock par catégorie (graphique en barres)
- Top 5 des ventes (graphique en barres)
- Répartition par catégorie (camembert)
- Chiffre d'affaires par catégorie (graphique en barres)

### Export
- Export CSV des produits et de l'historique
- Fichiers sauvegardés dans le dossier `export/`
- Encodage UTF-8 avec BOM (compatible Excel)

---

## 💰 Devise

L'application utilise le **Dirham Marocain (DH)** comme devise.

---

## 📊 Base de données

La base SQLite (`stock.db`) est créée automatiquement au premier lancement.

### Table `produits`
| Champ | Type | Description |
|---|---|---|
| id | INTEGER | Clé primaire auto-incrémentée |
| nom | TEXT | Nom du produit |
| categorie | TEXT | Catégorie du produit |
| prix_achat | REAL | Prix d'achat unitaire (DH) |
| prix_vente | REAL | Prix de vente unitaire (DH) |
| quantite | INTEGER | Quantité en stock |
| seuil_alerte | INTEGER | Seuil d'alerte stock faible |
| date_creation | TEXT | Date de création |
| date_modification | TEXT | Date de dernière modification |

### Table `historique`
| Champ | Type | Description |
|---|---|---|
| id | INTEGER | Clé primaire auto-incrémentée |
| produit_id | INTEGER | ID du produit (clé étrangère) |
| produit_nom | TEXT | Nom du produit |
| action | TEXT | Type d'action (achat, vente, ajout...) |
| quantite | INTEGER | Quantité concernée |
| prix_unitaire | REAL | Prix unitaire de la transaction |
| date | TEXT | Date et heure de l'action |
| details | TEXT | Détails supplémentaires |

---

## 👤 Auteur

**Saad El Aissaoui**
- GitHub : [@saadelaissaoui2002-ux](https://github.com/saadelaissaoui2002-ux)
- Linkedin : [@saadelaissaoui](https://www.linkedin.com/in/saad-el-aissaoui-73b498294)

---

## 📄 Licence

Ce projet est sous AGPL-3.0 pour un usage personnel et éducatif.

Pour une utilisation commerciale, veuillez me contacter :📧 saadelaissaoui2002@gmail.com
