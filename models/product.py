"""
Modèle Produit - Représente un produit dans le système de stock.
"""


class Product:
    """Classe modèle pour un produit du stock."""

    def __init__(self, id: int = 0, nom: str = "", categorie: str = "",
                 prix_achat: float = 0.0, prix_vente: float = 0.0,
                 quantite: int = 0, seuil_alerte: int = 5,
                 date_creation: str = "", date_modification: str = ""):
        self.id = id
        self.nom = nom
        self.categorie = categorie
        self.prix_achat = prix_achat
        self.prix_vente = prix_vente
        self.quantite = quantite
        self.seuil_alerte = seuil_alerte
        self.date_creation = date_creation
        self.date_modification = date_modification

    @property
    def marge(self) -> float:
        """Calcule la marge unitaire du produit."""
        return round(self.prix_vente - self.prix_achat, 2)

    @property
    def marge_pourcentage(self) -> float:
        """Calcule la marge en pourcentage."""
        if self.prix_achat == 0:
            return 0.0
        return round(((self.prix_vente - self.prix_achat) / self.prix_achat) * 100, 2)

    @property
    def valeur_stock(self) -> float:
        """Calcule la valeur totale du stock pour ce produit (prix achat)."""
        return round(self.quantite * self.prix_achat, 2)

    @property
    def est_en_alerte(self) -> bool:
        """Vérifie si le produit est en alerte de stock faible."""
        return self.quantite <= self.seuil_alerte

    @property
    def est_en_rupture(self) -> bool:
        """Vérifie si le produit est en rupture de stock."""
        return self.quantite == 0

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Crée un objet Product à partir d'un dictionnaire."""
        return cls(
            id=data.get("id", 0),
            nom=data.get("nom", ""),
            categorie=data.get("categorie", ""),
            prix_achat=data.get("prix_achat", 0.0),
            prix_vente=data.get("prix_vente", 0.0),
            quantite=data.get("quantite", 0),
            seuil_alerte=data.get("seuil_alerte", 5),
            date_creation=data.get("date_creation", ""),
            date_modification=data.get("date_modification", ""),
        )

    def to_dict(self) -> dict:
        """Convertit l'objet Product en dictionnaire."""
        return {
            "id": self.id,
            "nom": self.nom,
            "categorie": self.categorie,
            "prix_achat": self.prix_achat,
            "prix_vente": self.prix_vente,
            "quantite": self.quantite,
            "seuil_alerte": self.seuil_alerte,
            "date_creation": self.date_creation,
            "date_modification": self.date_modification,
        }

    def __repr__(self) -> str:
        return (f"Product(id={self.id}, nom='{self.nom}', categorie='{self.categorie}', "
                f"quantite={self.quantite}, prix_vente={self.prix_vente})")
