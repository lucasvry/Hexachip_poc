import json
import os
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from datetime import datetime
import re

import pandas as pd

from services.SearchEngineService import SearchEngineService
from src.test import test
from src.utils.formule import State, calculer_prix_vente_estime


class ProductSection(Frame):
    def __init__(self, master, title, default_values):
        super().__init__(master)
        self.title = title
        self.default_values = default_values
        self._create_gui()
        print(self.default_values)

    def _create_gui(self):
        label = Label(self, text=self.title.name)
        label.grid(column=0, row=1, columnspan=2, pady=15)

        labels = ["Stock mondial", "Variation du stock", "Date de fabrication"]
        for i, label_text in enumerate(labels, start=2):
            self._create_label_and_entry(label_text, i)

        sep = Separator(self, orient="vertical")
        sep.grid(column=2, row=1, rowspan=len(labels) + 1, sticky="ns")

    def _create_label_and_entry(self, label_text, row):
        label = Label(self, text=label_text)
        label.grid(column=0, row=row, pady=5)
        print(self.default_values[row - 2])
        var = IntVar(value=self.default_values[row - 2])
        champ = Entry(self, textvariable=var, validate="key")
        champ.grid(column=1, row=row, padx=15, pady=5)

        champ.bind("<KeyRelease>", lambda event: self._validate_entry(event, row - 2, champ))

    def _validate_entry(self, event, index, champ):
        try:
            value = int(champ.get())
            self.default_values[index] = value
        except ValueError:
            champ.bell()
            champ.delete(0, END)


class Application(Frame):

    def __init__(self, root):
        super().__init__(root)
        self.current_process = 0
        self._create_gui()
        self.pack()
        self.mpn_ids = []
        self.search_engine_service = SearchEngineService()
        self.file_path_export = None

        os.environ['DIGIKEY_CLIENT_ID'] = 'uFbyuoadeIp6BG1MDP5xVxZaYLgweyBL'
        os.environ['DIGIKEY_CLIENT_SECRET'] = 'CmNER7ConcrSIfLE'
        os.environ['DIGIKEY_CLIENT_SANDBOX'] = 'False'
        os.environ['DIGIKEY_STORAGE_PATH'] = "./cache"

    components = test.components

    def _create_gui(self):
        self.sections = [
            (State.FABRICATION, [50, 30, 20]),
            (State.NRND, [65, 20, 15]),
            (State.OBSOLETE, [100, 0, 0])
        ]

        # Bouton import fichier excel
        Button(self, text="Importer un fichier CSV", command=self.import_file).grid(column=0, row=0, pady=20)

        self.filePathLabel = Label(self, text="Aucun fichier sélectionné")
        self.filePathLabel.grid(column=1, row=0, columnspan=6, pady=20)

        # Sections
        for i, (title, default_values) in enumerate(self.sections):
            section = ProductSection(self, title, default_values)
            section.grid(column=i * 2, row=1)

        self.affichage()

        # progressbar
        self.progressbar = Progressbar(
            self,
            orient='horizontal',
            mode='determinate',
            length=280,
        )

        # place the progressbar
        self.progressbar.grid(column=0, row=5, columnspan=8, padx=10, pady=20)

        # label
        self.value_label = Label(self, text="Current Progress: 0 %")
        self.value_label.grid(column=0, row=5, columnspan=2)

        # Bouton génération des prix
        Button(self, text="Générer les prix", command=self.export_to_pdf).grid(column=0, row=6, columnspan=8, pady=20)

        # Bouton ouvrir l'excel
        self.open_excel_button = Button(self, text="Ouvrir l'excel", command=self.ouvrir_excel)
        self.open_excel_button.grid(column=0, row=7, columnspan=8, pady=20)

    def import_file(self):
        # Ouvrir une fenêtre de dialogue pour choisir le fichier
        fichier = filedialog.askopenfilename(filetypes=[("Excel files", ".xlsx .xls .csv")])
        if fichier:
            self.file_path = fichier
            self.filePathLabel.config(text=self.file_path)
            self.import_excel = pd.read_excel(fichier)
            date_code = self.get_date_code()
            self.mpn_ids = self.get_mpn_ids()

    def ouvrir_excel(self):
        try:
            # Ouvrir le fichier Excel avec l'application par défaut
            os.system(f"start excel {self.file_path_export}")
        except Exception as e:
            print(f"Erreur lors de l'ouverture du fichier : {e}")

    def get_mpn_ids(self):
        # Sélectionner les colonnes spécifiées dans la variable result
        columns_to_select = ["MPN"]
        result = self.import_excel[columns_to_select]
        flat_list = []
        for sublist in result.values:
            flat_list.extend(sublist)

        return flat_list

    def get_date_code(self):
        # Sélectionner les colonnes spécifiées dans la variable result
        columns_to_select = ["DATE_CODE"]
        result = self.import_excel[columns_to_select]
        flat_list = []
        for sublist in result.values:
            flat_list.append(self.transformer_chaine(sublist[0]))
        return flat_list

    def transformer_chaine(self, chaine, chaine_origine=None):
        chaine = str(chaine)
        chaine = chaine.replace(" ", "")
        currentYear = datetime.now().strftime('%Y')

        # Vérifier si la chaîne est vide
        if chaine == "nan":
            return int(currentYear)

        # le cas "XXYY"
        if re.match(r'\d{4}$', chaine):
            return int(currentYear[:2] + chaine[:2])

        # Vérifier si la chaîne contient un motif correspondant à une date
        match_date = re.match(r'\d{2}\+$', chaine)
        if match_date:
            return int(currentYear[:2] + match_date.group()[:-1])

        # Vérifier si la chaîne est un nombre
        try:
            return int(chaine)
        except ValueError:
            pass

        # Vérifier si la chaîne contient un motif correspondant à une date avec préfixe
        match_date_with_prefix = re.match(r'DC(\d+)\+?$', chaine)
        if match_date_with_prefix:
            return int(currentYear[:2] + match_date_with_prefix.group(1))

        # Vérifier si la chaîne contient un motif correspondant à un numéro de lot
        match_lot_number = re.match(r'N°Lot : (.+)$', chaine)
        if match_lot_number:
            return int(currentYear)

        # Vérifier si la chaîne peut être séparée en plusieurs parties
        match_separate = re.split(r'[|/,]', chaine)
        if match_separate and chaine_origine is None:
            years = [self.transformer_chaine(i, chaine) for i in match_separate]
            return int(min(years)) if years else int(currentYear)

        # Cas "XX+YY+"
        match_plus_sequence = re.match(r'(\d+)\+\d+\+?$', chaine)
        if match_plus_sequence:
            return int(currentYear[:2] + match_plus_sequence.group(1))

        # Retourner None si aucun motif n'est trouvé
        return int(currentYear)

    def affichage(self):
        print('--------------------')
        for i, (title, default_values) in enumerate(self.sections):
            print(title, default_values)

    def export_to_pdf(self):
        total_components = len(self.components)
        ids = []
        prices = []
        market_prices = []
        pourcentages = []

        folder_selected = filedialog.askdirectory()
        if folder_selected:
            for index, component in enumerate(self.components, start=1):
                prix_estime = calculer_prix_vente_estime(component, self.sections)

                ids.append(component.id)
                prices.append(prix_estime)
                market_prices.append(component.prix_moyen_marche)
                pourcentages.append(
                    f"{(prix_estime - component.prix_moyen_marche) / component.prix_moyen_marche * 100:.2f}%")

                self.progress()
                print("------------------------------------------------------")
                print(f"Traitement du composant {index}/{total_components}")

            data = {'REFS': ids,
                    'PRIX ESTIMES (en $)': prices,
                    'PRIX MARCHE (en $)': market_prices,
                    'DIFFERENCE (en %)': pourcentages
                    }

            df = pd.DataFrame(data)

            self.file_path_export = f'{folder_selected}/export_prices.xlsx'
            df.to_excel(self.file_path_export, index=False)
            print(f'Fichier enregistré avec succès à : {self.file_path_export}')
        else:
            print('Aucun dossier sélectionné. Annulation de l\'enregistrement.')

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./output/result_common_{timestamp}.json"
        with open(filename, "w") as file:
            json.dump([], file)

        for mpn in self.mpn_ids:
            result = self.search_engine_service.search_by_mpn(mpn=mpn)
            with open(filename, "r+") as file:
                data = json.load(file)
                data.append(result.to_json())
                file.seek(0)
                json.dump(data, file, indent=4)

    def progress(self):
        if self.current_process < 100:
            self.current_process += 100 / len(self.components)
            self.progressbar['value'] = self.current_process
            self.value_label.config(text=f"Current Progress: {round(self.current_process)} %")
        self.update_idletasks()  # Force la mise à jour de l'interface utilisateur


def main():
    app = Tk()
    app.geometry("1100x500")
    app.resizable(0, 0)
    app.title("Hexachip Simulation")
    Application(app)
    app.mainloop()


"""
    mpn_ids = [
        "STM32F765NIH6",
        "MK10DX128VLQ10",
        "AG9924M",
        "0818111",
        "BTS432E2E3062ABUMA1",
        "BG96MA-128-SGN",
        "DSPIC33EV256GM102-I/MM",
        "XPC250300S-02",
        "1734346-1",
        "EPG.1B.304.HLN",
        "BNX028-01",
        "BQ25306RTER",
        "ADuM4160BRWZ",
        "LT3750EMS#TRPBF",
        "MAX11254ATJ+",
        "25AA256-I/SN",
        "NUCLEO-F303K8",
        "LD1117S33TR",
        "MAX6070AAUT21+T",
        "1-1634200-7",
        "ISR3SAD200",
        "AMDLA4010S-2R2MT",
        "SIR876ADP-T1-GE3",
        "DA2034-ALD",
        "LPS103-M",
        "S1227-66BR",
        "ODROID-C2",
        "7448060814",
        "LP2985-50DBVR",
        "STM32F302C8T6TR",
        "OWA-60E-24",
        "3210237",
        "FTSH-105-05-F-DV-P-TR",
        "MCP7940NT-I/SN",
        "PIC16F88-E/SO",
        "PIC16F88-I/SO",
        "RS-15-12",
        "PMEG2005EH",
        "Radxa Pi Zero SBC",
        "ORG1510-MK05-TR2",
        "LQW15AN9N1H00D",
        "MAX17205G+00E",
        "NC4FDM3-H-BAG",
        "CR95HF-VMD5T",
        "SIM868",
        "LM5122MHX/NOPB",
        "STGIF7CH60TS-L",
        "STM32F303VCT6",
    ]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"../output/result_common_{timestamp}.json"
    with open(filename, "w") as file:
        json.dump([], file)

    for mpn in mpn_ids:
        search_engine_service = SearchEngineService()
        search_engine_service.search_price_by_mpn(mpn=mpn, filename=filename)

"""
if __name__ == "__main__":
    main()
