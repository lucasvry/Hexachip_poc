import random

from src.utils.formule import Component, State

components = []
for i in range(1, 51):
    component = Component(
        id=i,
        etat_fabrication=random.choice([State.FABRICATION, State.NRND, State.OBSOLETE]),
        prix_moyen_marche=random.uniform(0.1, 1.0),
        variation_stock=random.uniform(-1.0, 1.0),
        stock_mondial=random.randint(5000, 50000),
        annee_achat=random.randint(2010, 2022)
    )
    components.append(component)
