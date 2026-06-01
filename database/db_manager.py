"""
Module de gestion de la base de données SQLite pour le Gestionnaire de Stock Intelligent.
Gère toutes les opérations CRUD sur les tables produits et historique.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional


class DatabaseManager:
    """Gestionnaire principal de la base de données SQLite."""

    def __init__(self, db_path: str = "stock.db"):
        """
        Initialise la connexion à la base de données et crée les tables si nécessaires.

        Args:
            db_path: Chemin vers le fichier SQLite. Par défaut 'stock.db'.
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Établit la connexion à la base de données SQLite."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise RuntimeError(f"Erreur de connexion à la base de données : {e}")

    def create_tables(self):
        """Crée les tables produits et historique si elles n'existent pas."""
        create_produits = """
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            categorie TEXT NOT NULL,
            prix_achat REAL NOT NULL DEFAULT 0.0,
            prix_vente REAL NOT NULL DEFAULT 0.0,
            quantite INTEGER NOT NULL DEFAULT 0,
            seuil_alerte INTEGER NOT NULL DEFAULT 5,
            date_creation TEXT NOT NULL,
            date_modification TEXT NOT NULL
        )
        """
        create_historique = """
        CREATE TABLE IF NOT EXISTS historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produit_id INTEGER NOT NULL,
            produit_nom TEXT NOT NULL,
            action TEXT NOT NULL,
            quantite INTEGER NOT NULL,
            prix_unitaire REAL DEFAULT 0.0,
            date TEXT NOT NULL,
            details TEXT DEFAULT '',
            FOREIGN KEY (produit_id) REFERENCES produits(id) ON DELETE CASCADE
        )
        """
        try:
            self.cursor.execute(create_produits)
            self.cursor.execute(create_historique)
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Erreur lors de la création des tables : {e}")

    # ─────────────────────────────────────────────
    # Opérations CRUD - Produits
    # ─────────────────────────────────────────────

    def ajouter_produit(self, nom: str, categorie: str, prix_achat: float,
                        prix_vente: float, quantite: int, seuil_alerte: int) -> int:
        """
        Ajoute un nouveau produit dans la base de données.

        Returns:
            L'ID du produit nouvellement créé.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """
        INSERT INTO produits (nom, categorie, prix_achat, prix_vente, quantite, seuil_alerte, date_creation, date_modification)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            self.cursor.execute(sql, (nom, categorie, prix_achat, prix_vente,
                                       quantite, seuil_alerte, now, now))
            self.conn.commit()
            produit_id = self.cursor.lastrowid
            # Enregistrer l'action dans l'historique
            self.ajouter_historique(produit_id, nom, "ajout", quantite, prix_achat,
                                     f"Création du produit '{nom}' avec {quantite} unités")
            return produit_id
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Erreur lors de l'ajout du produit : {e}")

    def modifier_produit(self, produit_id: int, nom: str, categorie: str,
                         prix_achat: float, prix_vente: float, quantite: int,
                         seuil_alerte: int) -> bool:
        """Modifie un produit existant."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """
        UPDATE produits
        SET nom=?, categorie=?, prix_achat=?, prix_vente=?, quantite=?,
            seuil_alerte=?, date_modification=?
        WHERE id=?
        """
        try:
            self.cursor.execute(sql, (nom, categorie, prix_achat, prix_vente,
                                       quantite, seuil_alerte, now, produit_id))
            self.conn.commit()
            self.ajouter_historique(produit_id, nom, "modification", quantite,
                                     prix_achat, f"Modification du produit '{nom}'")
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Erreur lors de la modification du produit : {e}")

    def supprimer_produit(self, produit_id: int) -> bool:
        """Supprime un produit de la base de données."""
        # Récupérer le nom avant suppression pour l'historique
        produit = self.get_produit_by_id(produit_id)
        if not produit:
            raise RuntimeError("Produit introuvable.")
        try:
            # Enregistrer dans l'historique AVANT la suppression (contrainte FK)
            self.ajouter_historique(produit_id, produit["nom"], "suppression",
                                     produit["quantite"], produit["prix_achat"],
                                     f"Suppression du produit '{produit['nom']}'")
            sql = "DELETE FROM produits WHERE id=?"
            self.cursor.execute(sql, (produit_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Erreur lors de la suppression du produit : {e}")

    def get_produit_by_id(self, produit_id: int) -> Optional[dict]:
        """Récupère un produit par son ID."""
        sql = "SELECT * FROM produits WHERE id=?"
        self.cursor.execute(sql, (produit_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all_produits(self) -> list:
        """Récupère tous les produits."""
        sql = "SELECT * FROM produits ORDER BY nom ASC"
        self.cursor.execute(sql)
        return [dict(row) for row in self.cursor.fetchall()]

    def rechercher_produits(self, texte: str, categorie: str = "",
                            seuil_min: Optional[float] = None,
                            seuil_max: Optional[float] = None,
                            stock_faible: bool = False) -> list:
        """
        Recherche avancée multi-critères de produits.

        Args:
            texte: Terme de recherche (nom ou catégorie).
            categorie: Filtre par catégorie exacte.
            seuil_min: Prix de vente minimum.
            seuil_max: Prix de vente maximum.
            stock_faible: Si True, ne retourne que les produits sous le seuil d'alerte.
        """
        conditions = []
        params = []

        if texte:
            conditions.append("(nom LIKE ? OR categorie LIKE ?)")
            params.extend([f"%{texte}%", f"%{texte}%"])

        if categorie:
            conditions.append("categorie = ?")
            params.append(categorie)

        if seuil_min is not None:
            conditions.append("prix_vente >= ?")
            params.append(seuil_min)

        if seuil_max is not None:
            conditions.append("prix_vente <= ?")
            params.append(seuil_max)

        if stock_faible:
            conditions.append("quantite <= seuil_alerte")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM produits WHERE {where_clause} ORDER BY nom ASC"
        self.cursor.execute(sql, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_categories(self) -> list:
        """Récupère toutes les catégories distinctes."""
        sql = "SELECT DISTINCT categorie FROM produits ORDER BY categorie ASC"
        self.cursor.execute(sql)
        return [row["categorie"] for row in self.cursor.fetchall()]

    # ─────────────────────────────────────────────
    # Opérations Stock (Achat / Vente)
    # ─────────────────────────────────────────────

    def acheter_stock(self, produit_id: int, quantite: int, prix_unitaire: float) -> bool:
        """
        Achète du stock (augmente la quantité d'un produit).

        Args:
            produit_id: ID du produit.
            quantite: Nombre d'unités à ajouter.
            prix_unitaire: Prix d'achat unitaire de cette transaction.
        """
        produit = self.get_produit_by_id(produit_id)
        if not produit:
            raise RuntimeError("Produit introuvable.")

        nouvelle_quantite = produit["quantite"] + quantite
        # Calcul du prix d'achat moyen pondéré
        ancien_total = produit["prix_achat"] * produit["quantite"]
        nouveau_total = prix_unitaire * quantite
        prix_moyen = (ancien_total + nouveau_total) / nouvelle_quantite if nouvelle_quantite > 0 else 0

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "UPDATE produits SET quantite=?, prix_achat=?, date_modification=? WHERE id=?"
        try:
            self.cursor.execute(sql, (nouvelle_quantite, round(prix_moyen, 2), now, produit_id))
            self.conn.commit()
            self.ajouter_historique(produit_id, produit["nom"], "achat", quantite,
                                     prix_unitaire,
                                     f"Achat de {quantite} unités à {prix_unitaire:.2f} DH/unité")
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Erreur lors de l'achat : {e}")

    def vendre_stock(self, produit_id: int, quantite: int, prix_unitaire: float) -> bool:
        """
        Vend du stock (diminue la quantité d'un produit).

        Vérifie que le stock est suffisant avant de vendre.

        Args:
            produit_id: ID du produit.
            quantite: Nombre d'unités à vendre.
            prix_unitaire: Prix de vente unitaire de cette transaction.
        """
        produit = self.get_produit_by_id(produit_id)
        if not produit:
            raise RuntimeError("Produit introuvable.")

        if produit["quantite"] < quantite:
            raise RuntimeError(
                f"Stock insuffisant ! Disponible : {produit['quantite']}, Demandé : {quantite}"
            )

        nouvelle_quantite = produit["quantite"] - quantite
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "UPDATE produits SET quantite=?, date_modification=? WHERE id=?"
        try:
            self.cursor.execute(sql, (nouvelle_quantite, now, produit_id))
            self.conn.commit()
            self.ajouter_historique(produit_id, produit["nom"], "vente", quantite,
                                     prix_unitaire,
                                     f"Vente de {quantite} unités à {prix_unitaire:.2f} DH/unité")
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Erreur lors de la vente : {e}")

    # ─────────────────────────────────────────────
    # Historique
    # ─────────────────────────────────────────────

    def ajouter_historique(self, produit_id: int, produit_nom: str, action: str,
                           quantite: int, prix_unitaire: float = 0.0,
                           details: str = ""):
        """Ajoute une entrée dans l'historique des actions."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """
        INSERT INTO historique (produit_id, produit_nom, action, quantite, prix_unitaire, date, details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            self.cursor.execute(sql, (produit_id, produit_nom, action, quantite,
                                       prix_unitaire, now, details))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Erreur historique : {e}")

    def get_historique(self, produit_id: Optional[int] = None,
                       action: str = "", date_debut: str = "",
                       date_fin: str = "") -> list:
        """
        Récupère l'historique avec filtres optionnels.

        Args:
            produit_id: Filtrer par ID produit.
            action: Filtrer par type d'action ("achat", "vente", "ajout", "suppression", "modification").
            date_debut: Date de début (format YYYY-MM-DD).
            date_fin: Date de fin (format YYYY-MM-DD).
        """
        conditions = []
        params = []

        if produit_id is not None:
            conditions.append("produit_id = ?")
            params.append(produit_id)

        if action:
            conditions.append("action = ?")
            params.append(action)

        if date_debut:
            conditions.append("date >= ?")
            params.append(f"{date_debut} 00:00:00")

        if date_fin:
            conditions.append("date <= ?")
            params.append(f"{date_fin} 23:59:59")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM historique WHERE {where_clause} ORDER BY date DESC"
        self.cursor.execute(sql, params)
        return [dict(row) for row in self.cursor.fetchall()]

    # ─────────────────────────────────────────────
    # Statistiques & Dashboard
    # ─────────────────────────────────────────────

    def get_stats_dashboard(self) -> dict:
        """Calcule les statistiques globales pour le dashboard."""
        stats = {}
        try:
            # Nombre total de produits
            self.cursor.execute("SELECT COUNT(*) as total FROM produits")
            stats["total_produits"] = self.cursor.fetchone()["total"]

            # Quantité totale en stock
            self.cursor.execute("SELECT COALESCE(SUM(quantite), 0) as total FROM produits")
            stats["quantite_totale"] = self.cursor.fetchone()["total"]

            # Valeur totale du stock (basée sur prix_achat)
            self.cursor.execute(
                "SELECT COALESCE(SUM(quantite * prix_achat), 0) as total FROM produits"
            )
            stats["valeur_stock_achat"] = round(self.cursor.fetchone()["total"], 2)

            # Valeur totale du stock (basée sur prix_vente)
            self.cursor.execute(
                "SELECT COALESCE(SUM(quantite * prix_vente), 0) as total FROM produits"
            )
            stats["valeur_stock_vente"] = round(self.cursor.fetchone()["total"], 2)

            # Produits en alerte (quantite <= seuil_alerte)
            self.cursor.execute(
                "SELECT COUNT(*) as total FROM produits WHERE quantite <= seuil_alerte"
            )
            stats["produits_alerte"] = self.cursor.fetchone()["total"]

            # Produits en rupture (quantite = 0)
            self.cursor.execute(
                "SELECT COUNT(*) as total FROM produits WHERE quantite = 0"
            )
            stats["produits_rupture"] = self.cursor.fetchone()["total"]

            # Nombre de catégories
            self.cursor.execute("SELECT COUNT(DISTINCT categorie) as total FROM produits")
            stats["total_categories"] = self.cursor.fetchone()["total"]

            # Marge potentielle
            stats["marge_potentielle"] = round(
                stats["valeur_stock_vente"] - stats["valeur_stock_achat"], 2
            )

        except sqlite3.Error as e:
            print(f"Erreur statistiques : {e}")
        return stats

    def get_produits_alerte(self) -> list:
        """Récupère les produits en alerte de stock faible."""
        sql = "SELECT * FROM produits WHERE quantite <= seuil_alerte ORDER BY quantite ASC"
        self.cursor.execute(sql)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_produit_plus_vendu(self) -> Optional[dict]:
        """Retourne le produit le plus vendu (basé sur l'historique)."""
        sql = """
        SELECT produit_id, produit_nom, SUM(quantite) as total_vendu
        FROM historique
        WHERE action = 'vente'
        GROUP BY produit_id
        ORDER BY total_vendu DESC
        LIMIT 1
        """
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_produit_plus_rentable(self) -> Optional[dict]:
        """Retourne le produit le plus rentable (basé sur le CA des ventes)."""
        sql = """
        SELECT produit_id, produit_nom,
               SUM(quantite) as total_vendu,
               SUM(quantite * prix_unitaire) as chiffre_affaires
        FROM historique
        WHERE action = 'vente'
        GROUP BY produit_id
        ORDER BY chiffre_affaires DESC
        LIMIT 1
        """
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_evolution_stock(self, produit_id: Optional[int] = None,
                            jours: int = 30) -> list:
        """
        Récupère les données d'évolution du stock pour les graphiques.

        Returns:
            Liste de dictionnaires avec date et mouvement cumulé.
        """
        if produit_id:
            sql = """
            SELECT date, action, quantite FROM historique
            WHERE produit_id = ? AND date >= date('now', ?)
            ORDER BY date ASC
            """
            self.cursor.execute(sql, (produit_id, f"-{jours} days"))
        else:
            sql = """
            SELECT date, action, SUM(quantite) as quantite FROM historique
            WHERE date >= date('now', ?)
            GROUP BY date, action
            ORDER BY date ASC
            """
            self.cursor.execute(sql, (f"-{jours} days",))

        return [dict(row) for row in self.cursor.fetchall()]

    def get_ventes_par_categorie(self) -> list:
        """Récupère les ventes groupées par catégorie de produit."""
        sql = """
        SELECT p.categorie, SUM(h.quantite) as total_vendu,
               SUM(h.quantite * h.prix_unitaire) as chiffre_affaires
        FROM historique h
        JOIN produits p ON h.produit_id = p.id
        WHERE h.action = 'vente'
        GROUP BY p.categorie
        ORDER BY chiffre_affaires DESC
        """
        self.cursor.execute(sql)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_top_produits_ventes(self, limit: int = 5) -> list:
        """Récupère le top des produits les plus vendus."""
        sql = """
        SELECT produit_nom, SUM(quantite) as total_vendu,
               SUM(quantite * prix_unitaire) as chiffre_affaires
        FROM historique
        WHERE action = 'vente'
        GROUP BY produit_id
        ORDER BY total_vendu DESC
        LIMIT ?
        """
        self.cursor.execute(sql, (limit,))
        return [dict(row) for row in self.cursor.fetchall()]

    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()
