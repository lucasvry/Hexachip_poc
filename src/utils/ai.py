from src.utils.formule import Component

from pathlib import Path
import joblib

from sklearn.ensemble import RandomForestRegressor

import pandas as pd

from src.utils.dataTransformer import DataTransformer

import numpy


class Ai:
    class NotLoadedModelException(Exception):
        def __init__(self):
            super().__init__("Model non chargé")

    def __init__(self, modelFilePath):
        self.modelLoaded = False
        self.model: RandomForestRegressor = None
        self.loadModel(modelFilePath)

    def loadModel(self, filePath):
        path = Path(filePath)
        if (not path.exists()):
            raise FileNotFoundError
        self.model = joblib.load(filePath)
        self.modelLoaded = True

    def predict(self, component: Component):
        if not self.modelLoaded:
            raise Ai.NotLoadedModelException()

        dataFrame: pd.DataFrame = DataTransformer.transform(component.brut_scrapped_result.leadTime,
                                                            component.etat_fabrication,
                                                            component.brut_scrapped_result.totalStock,
                                                            component.variation_stock, component.date_codes,
                                                            component.vendor_stock, component.prix_moyen_marche, component.brut_scrapped_result)


        result  = self.model.predict(dataFrame)[0]
        if result > component.prix_moyen_marche:
            return component.prix_moyen_marche
        else:
            return result
