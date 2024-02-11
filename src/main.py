import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, ttk
import pandas as pd

from src.services.SearchEngineService import SearchEngineService


class ProductSection(tk.Frame):
    def __init__(self, master, title, default_values):
        super().__init__(master)
        self.title = title
        self.default_values = default_values
        self._create_gui()

    def _create_gui(self):
        label = tk.Label(self, text=self.title)
        label.grid(column=0, row=1, columnspan=2, pady=15)

        labels = ["Stock mondial", "Date de fabrication", "Durée de fabrication"]
        for i, label_text in enumerate(labels, start=2):
            self._create_label_and_entry(label_text, i)

        sep = ttk.Separator(self, orient="vertical")
        sep.grid(column=2, row=1, rowspan=len(labels) + 1, sticky="ns")

    def _create_label_and_entry(self, label_text, row):
        label = tk.Label(self, text=label_text)
        label.grid(column=0, row=row, pady=5)

        var = tk.IntVar(value=self.default_values[row - 2])
        champ = tk.Entry(self, textvariable=var, validate="key")
        champ.grid(column=1, row=row, padx=15, pady=5)

        champ.bind("<KeyRelease>", lambda event: self._validate_entry(event, row - 2, champ))

    def _validate_entry(self, event, index, champ):
        try:
            value = int(champ.get())
            self.default_values[index] = value
        except ValueError:
            champ.bell()
            champ.delete(0, tk.END)


class Application(tk.Frame):

    def __init__(self, root):
        super().__init__(root)
        self._create_gui()
        self.pack()

    def _create_gui(self):
        self.sections = [
            ("En production", [50, 30, 20]),
            ("NRND", [65, 20, 15]),
            ("Obsolete", [100, 0, 0])
        ]

        # Bouton import fichier excel
        tk.Button(self, text="Importer un fichier CSV", command=self.importer_fichier).grid(column=0, row=0, pady=20)

        self.filePathLabel = tk.Label(self, text="Aucun fichier sélectionné")
        self.filePathLabel.grid(column=1, row=0, columnspan=6, pady=20)

        # Sections
        for i, (title, default_values) in enumerate(self.sections):
            section = ProductSection(self, title, default_values)
            section.grid(column=i * 2, row=1)

        # Bouton génération des prix
        tk.Button(self, text="Générer les prix", command=self.affichage).grid(column=0, row=5, columnspan=8, pady=20)

    def importer_fichier(self):
        # Ouvrir une fenêtre de dialogue pour choisir le fichier
        fichier = filedialog.askopenfilename(filetypes=[("Excel files", ".xlsx .xls .csv")])

        if fichier:
            self.file_path = fichier
            self.filePathLabel.config(text=self.file_path)
            df = pd.read_excel(fichier)
            print(df)

    def affichage(self):
        print('--------------------')
        for i, (title, default_values) in enumerate(self.sections):
            print(title, default_values)


def main():
    """
    app = tk.Tk()
    app.geometry("900x300")  # You want the size of the app to be 500x500
    app.resizable(0, 0)  # Don't allow resizing in the x or y direction    app.iconbitmap(".venv/assets/logo.png")
    app.title("Demo Widgets")
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


if __name__ == "__main__":
    main()
