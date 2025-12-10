import os, configparser
import class_dokumenttyp
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QGridLayout,
    QLabel, 
    QGroupBox,
    QLineEdit,
    QMessageBox
)
from PySide6.QtGui import Qt

basedir = os.path.dirname(__file__)

class DokumenttypAuswaehlen(QDialog):
    def __init__(self, updateSafePath:str, configPath:str):
        super().__init__()

        # config.ini lesen
        configIni = configparser.ConfigParser()
        configIni.read(os.path.join(configPath, "config.ini"))
        self.maximaleKategoriespalten = int(configIni["Allgemein"]["maximalekategoriespalten"])

        self.fontNormal = QFont()
        self.fontNormal.setBold(False)
        self.fontBold = QFont()
        self.fontBold.setBold(True)

        self.setWindowTitle("SignoGDT Dokumenttyp-Auswahl")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        dialogLayoutV = QVBoxLayout()
        dialogLayoutG = QGridLayout()
        dialogLayoutTextfeldH = QHBoxLayout()
        dokumenttypen = class_dokumenttyp.getAlleDokumenttypen(os.path.join(updateSafePath, "dokumenttypen.xml"))

        dtDict = {}
        kategorien = [dt.getKategorie() for dt in dokumenttypen]
        kategorien.sort()
        for kat in kategorien:
            namen = []
            for dt in dokumenttypen:
                if dt.getKategorie() == kat:
                    namen.append(dt.getName())
            namen.sort()
            dtDict[kat] = namen
        
        groupBoxKategorien = []
        i = 0
        for kat in dtDict:
            groupBoxKategorien.append(QGroupBox(kat))
            groupBoxKategorien[i].setFont(self.fontBold)
            j = 0
            labelNamen = []
            self.pushButtonAuswahl = []
            groupBoxLayoutG = QGridLayout()
            groupBoxLayoutG.setAlignment(Qt.AlignmentFlag.AlignTop)
            for name in dtDict[kat]:
                labelNamen.append(QLabel(name))
                labelNamen[j].setFont(self.fontNormal)
                groupBoxLayoutG.addWidget(labelNamen[j], j, 0)
                self.pushButtonAuswahl.append(QPushButton("Auswahl"))
                self.pushButtonAuswahl[j].setFont(self.fontNormal)
                self.pushButtonAuswahl[j].clicked.connect(lambda checked=False, kategorie=kat, name=name: self.pushButtonAuswahlClicked(checked, kategorie, name))
                groupBoxLayoutG.addWidget(self.pushButtonAuswahl[j], j, 1)
                j += 1
            groupBoxKategorien[i].setLayout(groupBoxLayoutG)
            dialogLayoutG.addWidget(groupBoxKategorien[i], int(i / self.maximaleKategoriespalten), i - int(i / self.maximaleKategoriespalten) * self.maximaleKategoriespalten)
            i += 1
        dialogLayoutV.addLayout(dialogLayoutG)
        labelAusgewaehlt = QLabel("Ausgewählter Dokumenttyp:")
        self.lineEditAusgewaehlt = QLineEdit()
        self.lineEditAusgewaehlt.setReadOnly(True)
        dialogLayoutTextfeldH.addWidget(labelAusgewaehlt)
        dialogLayoutTextfeldH.addWidget(self.lineEditAusgewaehlt)
        dialogLayoutV.addLayout(dialogLayoutTextfeldH)
        dialogLayoutV.addWidget(self.buttonBox, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(dialogLayoutV)
    
    def pushButtonAuswahlClicked(self, checked, kategorie, name):
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        if kategorie == "Standard":
            self.lineEditAusgewaehlt.setText(name)
        else:
            self.lineEditAusgewaehlt.setText(kategorie + "_" + name)
        
    def accept(self):
        if self.lineEditAusgewaehlt.text() != "":
            self.done(1)
        else:
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von SignoGDT", "Bitte wählen Sie einen Dokumenttyp aus.", QMessageBox.StandardButton.Ok)
            mb.exec()
