
import os, configparser
import class_dokumenttyp
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QComboBox
)

class DokumenttypHinzufuegenBearbeiten(QDialog):
    def __init__(self, configPath, dokumenttypen:list, zuBearbeitenderDokumenttypname:str):
        super().__init__()
        self.setMinimumWidth(400)
        self.dokumenttypen = dokumenttypen
        self.zuBearbeitenderDokumenttyp = class_dokumenttyp.Dokumenttyp("", "Standard", [], [])
        if zuBearbeitenderDokumenttypname != "":
            self.gefundenerDokumenttypindex = 0
            for dt in self.dokumenttypen:
                if zuBearbeitenderDokumenttypname[zuBearbeitenderDokumenttypname.index("(") + 1:-1] == dt.getKategorie() and zuBearbeitenderDokumenttypname[:zuBearbeitenderDokumenttypname.index(" (")] == dt.getName():
                    self.zuBearbeitenderDokumenttyp = dt
                    break
                else:
                    self.gefundenerDokumenttypindex += 1

        # config.ini lesen
        configIni = configparser.ConfigParser()
        configIni.read(os.path.join(configPath, "config.ini"))
        self.dokumenttypkategorien = str.split(configIni["Allgemein"]["dokumenttypkategorien"], "::")
        self.dokumenttypkategorien.sort()

        self.setWindowTitle("Dokumenttyp hinzufügen")
        if zuBearbeitenderDokumenttypname != "":
            self.setWindowTitle("Dokumenttyp bearbeiten")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        dialogLayoutG = QGridLayout()
        labelName = QLabel("Name:")
        self.lineEditName = QLineEdit(self.zuBearbeitenderDokumenttyp.getName())
        labelKategorie = QLabel("Kategorie")
        self.comboBoxKategorie = QComboBox()
        self.comboBoxKategorie.addItems(self.dokumenttypkategorien)
        self.comboBoxKategorie.setCurrentText(self.zuBearbeitenderDokumenttyp.getKategorie())
        dialogLayoutG.addWidget(labelName, 0, 0)
        dialogLayoutG.addWidget(self.lineEditName, 0, 1)
        dialogLayoutG.addWidget(labelKategorie, 1, 0)
        dialogLayoutG.addWidget(self.comboBoxKategorie, 1, 1)
        dialogLayoutG.addWidget(self.buttonBox, 2, 0, 1, 2)
        dialogLayoutG.setSpacing(20)
        self.setLayout(dialogLayoutG)

        self.lineEditName.setFocus()

    def accept(self):
        # Name auf Eindeutigkeit prüfen
        i = 0
        dokumentExistiert = False
        for dokument in self.dokumenttypen:
            if self.lineEditName.text() == dokument.getName() and self.comboBoxKategorie.currentText() == dokument.getKategorie():
                mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von SignoGDT", "Der Dokumenttyp \"" + self.lineEditName.text() + " (" + self.comboBoxKategorie.currentText() + ")\" existiert bereits.", QMessageBox.StandardButton.Ok)
                mb.exec()
                dokumentExistiert = True
                self.lineEditName.setFocus()
                self.lineEditName.selectAll()
                break
            i += 1
        if self.lineEditName.text().strip() == "":
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von SignoGDT", "Bitte geben Sie den Namen des Dokumenttyps an.", QMessageBox.StandardButton.Ok)
            self.lineEditName.setFocus()
            self.lineEditName.selectAll()
            mb.exec()
        elif not dokumentExistiert:
            self.done(1)