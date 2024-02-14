import json
import os
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import *
from datetime import datetime
import re
from playsound import playsound
from dotenv import load_dotenv

import pandas as pd

from services.SearchEngineService import SearchEngineService
from src.test import test
from src.utils.formule import State, calculer_prix_vente_estime, Component


class ProductSection(Frame):
    def __init__(self, master, title, default_values):
        super().__init__(master)
        self.title = title
        self.default_values = default_values
        self._create_gui()

    def _create_gui(self):
        label = Label(self, text=self.title)
        label.grid(column=0, row=1, columnspan=2, pady=15)

        labels = ["Stock mondial", "Variation du stock", "Date de fabrication"]
        for i, label_text in enumerate(labels, start=2):
            self._create_label_and_entry(label_text, i)

        sep = Separator(self, orient="vertical")
        sep.grid(column=2, row=1, rowspan=len(labels) + 1, sticky="ns")

    def _create_label_and_entry(self, label_text, row):
        label = Label(self, text=label_text)
        label.grid(column=0, row=row, pady=5)
        champ = Entry(self, validate="key")
        champ.insert(0, self.default_values[row - 2])
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
        self.pack()
        self.mpn_ids = []
        self.search_engine_service = SearchEngineService()
        self.file_path_export = None
        self.sections: [(str, [int])] = []
        self._create_gui()
        self.quantity = []

        os.environ['DIGIKEY_CLIENT_ID'] = 'uFbyuoadeIp6BG1MDP5xVxZaYLgweyBL'
        os.environ['DIGIKEY_CLIENT_SECRET'] = 'CmNER7ConcrSIfLE'
        os.environ['DIGIKEY_CLIENT_SANDBOX'] = 'False'
        os.environ['DIGIKEY_STORAGE_PATH'] = "./cache"

    components = test.components

    def _create_gui(self):
        default_values = f"./cache/default_values.json"
        with open(default_values, "r") as file:
            jsonLoaded = json.loads(file.read())
            for tuple in jsonLoaded:
                self.sections.append((tuple["state"], tuple["values"]))

        # Bouton import fichier excel
        Button(self, text="Importer un fichier CSV", command=self.import_file).grid(column=0, row=0, pady=20)

        self.filePathLabel = Label(self, text="Aucun fichier sélectionné")
        self.filePathLabel.grid(column=1, row=0, columnspan=6, pady=20)

        for i, (title, default_values) in enumerate(self.sections):
            section = ProductSection(self, title, default_values)
            section.grid(column=i * 2, row=1)

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
            self.date_codes = self.get_date_codes()
            self.mpn_ids = self.get_mpn_ids()
            self.quantity = self.get_quantity()

    def ouvrir_excel(self):
        try:
            os.system(f"start excel {self.file_path_export}")
        except Exception as e:
            messagebox.showerror("EXCEL", f"Erreur lors de l'ouverture du fichier : {self.file_path_export}")

    def get_mpn_ids(self):
        try:
            # Sélectionner les colonnes spécifiées dans la variable result
            columns_to_select = ["MPN"]
            result = self.import_excel[columns_to_select]
            flat_list = []
            for sublist in result.values:
                flat_list.extend(sublist)

            return flat_list
        except Exception:
            messagebox.showerror('IDS', "La colonne des réf doit être nommée 'MPN'")

    def get_date_codes(self):
        try:
            # Sélectionner les colonnes spécifiées dans la variable result
            columns_to_select = ["DATE_CODE"]
            result = self.import_excel[columns_to_select]
            flat_list = []
            for sublist in result.values:
                flat_list.append(self.transformer_chaine(sublist[0]))
            return flat_list
        except Exception:
            messagebox.showerror('DATE_CODE', "La colonne des dates doit être nommée 'DATE_CODE'")

    def get_quantity(self):
        try:
            # Sélectionner les colonnes spécifiées dans la variable result
            columns_to_select = ["QUANTITY"]
            result = self.import_excel[columns_to_select]
            flat_list = []
            for sublist in result.values:
                flat_list.append(self.transformer_chaine(sublist[0]))
            return flat_list
        except Exception:
            messagebox.showerror('QUANTITY', "La colonne des quantités doit être nommée 'QUANTITY'")

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
        self.sauvegarder_valeurs()
        ids = []
        prices = []
        market_prices = []
        pourcentages = []

        folder_selected = filedialog.askdirectory()
        if folder_selected:
            output_directory = "./output"
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"./output/result_common_{timestamp}.json"
            with open(filename, "w") as file:
                json.dump([], file)

            for mpn in self.mpn_ids:
                index = self.mpn_ids.index(mpn)

                print("------------------------------------------------------")
                print(f"Traitement du composant {index+1}/{len(self.mpn_ids)}")

                result = self.search_engine_service.search_by_mpn(mpn=mpn, quantity=self.quantity[index])
                with open(filename, "r+") as file:
                    data = json.load(file)
                    data.append(result.to_json())
                    file.seek(0)
                    json.dump(data, file, indent=4)

                if result.market_price is None or result.stock is None or result.market_price == 0 or result.stock == 0:
                    self.progress()
                    continue

                fabrication_state: State = State.OBSOLETE if result.is_obsolete else State.FABRICATION
                component = Component(
                    id=result.mpn,
                    prix_moyen_marche=result.market_price if result.market_price else 0,
                    variation_stock=0.85,
                    stock_mondial=result.stock if result.stock else 0,
                    annee_achat=self.date_codes[index],
                    etat_fabrication=fabrication_state
                )
                estimated_price = calculer_prix_vente_estime(component, self.sections)
                ids.append(component.id)
                prices.append(estimated_price)
                market_prices.append(component.prix_moyen_marche)
                pourcentages.append(
                    f"{(estimated_price - component.prix_moyen_marche) / component.prix_moyen_marche * 100:.2f}%")

                self.progress()

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

    def progress(self):
        if self.current_process < 100:
            print("increase progress")
            self.current_process += 100 / len(self.mpn_ids)
            self.progressbar['value'] = self.current_process
            self.value_label.config(text=f"Current Progress: {round(self.current_process)} %")
            self.update_idletasks()  # Mettre à jour l'interface utilisateur après chaque itération
        if self.current_process == 100:
            print(os.path.abspath("./sounds/msn.mp3"))
            playsound(os.path.abspath("./sounds/msn.mp3"))

    def sauvegarder_valeurs(self):
        data_to_save = [{"state": title, "values": default_values} for (title, default_values) in self.sections]
        with open("./cache/default_values.json", "w") as f:
            json.dump(data_to_save, f, indent=2)


def main():
    app = Tk()
    app.geometry("1100x500")
    app.resizable(0, 0)
    app.title("Hexachip Simulation")
    Application(app)
    app.mainloop()


if __name__ == "__main__":
    main()
