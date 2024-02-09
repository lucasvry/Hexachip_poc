import os
import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd





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
            section.grid(column=i * 2 , row=1)

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
            print(title,default_values)


if __name__ == '__main__':
    app = tk.Tk()
    app.geometry("900x300")  # You want the size of the app to be 500x500
    app.resizable(0, 0)  #Don't allow resizing in the x or y direction    app.iconbitmap(".venv/assets/logo.png")
    app.title("Demo Widgets")
    Application(app)
    app.mainloop()


