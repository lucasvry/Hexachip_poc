import random

from src.utils.formule import Component, State

components = []
component = Component(
    id = "TPS27081ADDCR",
    etat_fabrication=State.FABRICATION,
    prix_moyen_marche=0.2,
    variation_stock=-0.85,
    stock_mondial=28550,
    annee_achat=2022
)
components.append(component)
