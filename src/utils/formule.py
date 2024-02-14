import math
from enum import Enum


def recuperer_liste_par_str(pourcentages, chaine_recherche):
    for elem in pourcentages:
        if elem[0] == chaine_recherche:
            return elem[1]
    return None  # Retourner None si la chaîne n'est pas trouvée


class State(Enum):
    FABRICATION = 1
    NRND = 2
    OBSOLETE = 3


class Component:
    def __init__(self, id, etat_fabrication, prix_moyen_marche, variation_stock, stock_mondial, annee_achat):
        self.id = id
        self.etat_fabrication = etat_fabrication
        self.prix_moyen_marche = prix_moyen_marche
        self.variation_stock = variation_stock
        self.stock_mondial = stock_mondial
        self.annee_achat = annee_achat


def reduction_annuelle(annee_achat):
    ANNEES_REDUCTION = 0.06
    return (1 - ANNEES_REDUCTION) ** (2024 - annee_achat - 5)


def calculate_fabrication(stock_mondial):
    POURCENTAGE_STOCK_ELEVE = 0.45
    POURCENTAGE_STOCK_NORMAL = 0.15

    if stock_mondial > 10000:
        pourcentage_stock = 1 - POURCENTAGE_STOCK_ELEVE
    else:
        pourcentage_stock = 1 - POURCENTAGE_STOCK_NORMAL

    return pourcentage_stock


def calculate_nrnd(stock_mondial):
    POURCENTAGE_STOCK_ELEVE = 0.45
    POURCENTAGE_STOCK_NORMAL = 0.15

    if stock_mondial > 10000:
        pourcentage_stock = 1 - POURCENTAGE_STOCK_ELEVE
    else:
        pourcentage_stock = 1 - POURCENTAGE_STOCK_NORMAL
    return pourcentage_stock


def calculate_obsolete(stock_mondial):
    POURCENTAGE_STOCK_ELEVE = 0.15
    POURCENTAGE_STOCK_NORMAL = 0

    if stock_mondial > 10000:
        pourcentage_stock = 1 - POURCENTAGE_STOCK_ELEVE
    else:
        pourcentage_stock = 1 - POURCENTAGE_STOCK_NORMAL
    return pourcentage_stock


def pourcentage_variation_stock(variation_stock):
    if variation_stock <= -0.75:
        return 1.3
    elif variation_stock <= -0.5:
        return 1.2
    elif variation_stock <= -0.25:
        return 1.15
    elif variation_stock < 0:
        return 1.1
    elif variation_stock == 0:
        return 1
    elif variation_stock <= 0.25:
        return 0.95
    elif variation_stock < 0.5:
        return 0.9
    elif variation_stock < 0.75:
        return 0.8
    elif variation_stock >= 0.75:
        return 0.7


def calculer_prix_vente_estime(component: Component, coefficients: list[[str, list[int]]]):
    etat_fabrication = component.etat_fabrication
    stock_mondial = component.stock_mondial
    prix_moyen_actuel = component.prix_moyen_marche
    variation_stock = component.variation_stock
    annee_achat = component.annee_achat

    coefficients_choisis = recuperer_liste_par_str(coefficients, etat_fabrication.name)

    match etat_fabrication:
        case (State.FABRICATION):
            pourcentage_stock = calculate_fabrication(stock_mondial)
        case (State.NRND):
            pourcentage_stock = calculate_nrnd(stock_mondial)
        case (State.OBSOLETE):
            pourcentage_stock = calculate_obsolete(stock_mondial)
        case _:
            pourcentage_stock = 1

    prix_reduit_stock_mondial = prix_moyen_actuel * pourcentage_stock

    pourcentage_variation = pourcentage_variation_stock(variation_stock)

    prix_reduit_variation = prix_moyen_actuel * pourcentage_variation

    prix_reduit_date_code = prix_moyen_actuel

    prix_reduits = [prix_reduit_stock_mondial, prix_reduit_variation, prix_reduit_date_code]

    if 2024 - annee_achat > 5:
        prix_reduit_date_code *= reduction_annuelle(annee_achat)

    compteur_coefficients = 0
    numerator = 0
    denominator = 1
    for index, coefficient in enumerate(coefficients_choisis):
        if coefficient != 0:
            compteur_coefficients += 1
            numerator += (coefficient / 100 + 1) * prix_reduits[index]
            denominator *= (coefficient / 100 + 1)

    prix_vente_estime = numerator / (denominator * compteur_coefficients)

    # Imprimer les valeurs utilisées dans le calcul
    print(f"ID: {component.id}")
    print(f"Etat de fabrication: {etat_fabrication.name}")
    print(f"Prix moyen actuel: {prix_moyen_actuel}")
    print(f"Variation du stock entre 2023 et 2024: {variation_stock * 100:.1f}%")
    print(f"Stock mondial: {stock_mondial}")
    print(f"Année de fabrication : {annee_achat}")
    print("--")
    prix_vente = min(prix_vente_estime, prix_moyen_actuel)
    print(
        f"Le prix de vente estimé est : {prix_vente:.5f}€ | Différence de {(prix_vente - prix_moyen_actuel) / prix_moyen_actuel * 100:.2f}% par rapport au marché")

    return prix_vente
