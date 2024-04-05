import configparser, os
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QComboBox
)

zeichensatz = ["7Bit", "IBM (Standard) CP 437", "ISO8859-1 (ANSI) CP 1252"]

class EinstellungenGdt(QDialog):
    def __init__(self, configPath):
        super().__init__()

        #config.ini lesen
        configIni = configparser.ConfigParser()
        configIni.read(os.path.join(configPath, "config.ini"))
        self.idSignoGdt = configIni["GDT"]["idsignogdt"]
        self.idPraxisEdv = configIni["GDT"]["idpraxisedv"]
        self.gdtAustauschVerzeichnis = configIni["GDT"]["austauschverzeichnis"]
        if self.gdtAustauschVerzeichnis == "":
            self.gdtAustauschVerzeichnis = os.getcwd()
        self.kuerzeltSignoGdt = configIni["GDT"]["kuerzelsignogdt"]
        self.kuerzeltPraxisEdv= configIni["GDT"]["kuerzelpraxisedv"]
        self.gdtImportdateiLoeschen = configIni["GDT"]["importdateiloeschen"] == "True"
        self.aktuelleZeichensatznummer = int(configIni["GDT"]["zeichensatz"]) - 1

        self.setWindowTitle("GDT-Einstellungen")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        dialogLayoutV = QVBoxLayout()
        groupboxLayoutG = QGridLayout()
        # Groupbox GDT-IDs
        groupboxGdtIds = QGroupBox("GDT-IDs (8 Zeichen)")
        groupboxGdtIds.setStyleSheet("font-weight:bold")
        labelSignoGdtId = QLabel("SignoGDT:")
        labelSignoGdtId.setStyleSheet("font-weight:normal")
        labelPraxisEdvId = QLabel("Praxis-EDV:")
        labelPraxisEdvId.setStyleSheet("font-weight:normal")
        self.lineEditSignoGdtId = QLineEdit(self.idSignoGdt)
        self.lineEditSignoGdtId.setStyleSheet("font-weight:normal")
        self.lineEditSignoGdtId.setEnabled(False)
        self.lineEditPraxisEdvId = QLineEdit(self.idPraxisEdv)
        self.lineEditPraxisEdvId.setStyleSheet("font-weight:normal")
        groupboxLayoutG.addWidget(labelSignoGdtId, 0, 0)
        groupboxLayoutG.addWidget(self.lineEditSignoGdtId, 0, 1)
        groupboxLayoutG.addWidget(labelPraxisEdvId, 0, 2)
        groupboxLayoutG.addWidget(self.lineEditPraxisEdvId, 0, 3)
        groupboxGdtIds.setLayout(groupboxLayoutG)
        # Groupbox Austauschverzeichnis
        groupboxLayoutG = QGridLayout()
        groupboxAustauschverzeichniss = QGroupBox("Austauschverzeichnis")
        groupboxAustauschverzeichniss.setStyleSheet("font-weight:bold")
        self.lineEditImport = QLineEdit(self.gdtAustauschVerzeichnis)
        self.lineEditImport.setStyleSheet("font-weight:normal")
        buttonDurchsuchenImport = QPushButton("Durchsuchen")
        buttonDurchsuchenImport.setStyleSheet("font-weight:normal")
        buttonDurchsuchenImport.clicked.connect(self.durchsuchenImport) # type:ignore
        self.checkBoxImportdateiLoeschen = QCheckBox("Importdatei nach dem Import löschen")
        self.checkBoxImportdateiLoeschen.setStyleSheet("font-weight:normal")
        self.checkBoxImportdateiLoeschen.setChecked(self.gdtImportdateiLoeschen)
        groupboxLayoutG.addWidget(self.lineEditImport, 0, 0)
        groupboxLayoutG.addWidget(buttonDurchsuchenImport, 0, 1)
        groupboxLayoutG.addWidget(self.checkBoxImportdateiLoeschen, 1, 0)
        groupboxAustauschverzeichniss.setLayout(groupboxLayoutG)
        # Groupbox Kuerzel
        groupboxLayoutG = QGridLayout()
        groupboxKuerzel = QGroupBox("Kürzel für Austauschdateien (4 Zeichen)")
        groupboxKuerzel.setStyleSheet("font-weight:bold")
        labelSignoGdtKuerzel = QLabel("SignoGDT:")
        labelSignoGdtKuerzel.setStyleSheet("font-weight:normal")
        labelPraxisEdvKuerzel = QLabel("Praxis-EDV:")
        labelPraxisEdvKuerzel.setStyleSheet("font-weight:normal")
        self.lineEditSignoGdtKuerzel = QLineEdit(self.kuerzeltSignoGdt)
        self.lineEditSignoGdtKuerzel.textChanged.connect(self.kuerzelGeaendert) # type:ignore
        self.lineEditSignoGdtKuerzel.setStyleSheet("font-weight:normal")
        self.lineEditSignoGdtKuerzel.setEnabled(False)
        self.lineEditPraxisEdvKuerzel = QLineEdit(self.kuerzeltPraxisEdv)
        self.lineEditPraxisEdvKuerzel.textChanged.connect(self.kuerzelGeaendert) # type:ignore
        self.lineEditPraxisEdvKuerzel.setStyleSheet("font-weight:normal")
        self.labelImportDateiname = QLabel("Import-Dateiname: " + self.lineEditSignoGdtKuerzel.text() + self.lineEditPraxisEdvKuerzel.text() + ".gdt")
        self.labelImportDateiname.setStyleSheet("font-weight:normal")
        self.labelExportDateiname = QLabel("Export-Dateiname: " + self.lineEditPraxisEdvKuerzel.text() + self.lineEditSignoGdtKuerzel.text() + ".gdt")
        self.labelExportDateiname.setStyleSheet("font-weight:normal")
        groupboxLayoutG.addWidget(labelSignoGdtKuerzel, 0, 0)
        groupboxLayoutG.addWidget(self.lineEditSignoGdtKuerzel, 0, 1)
        groupboxLayoutG.addWidget(labelPraxisEdvKuerzel, 0, 2)
        groupboxLayoutG.addWidget(self.lineEditPraxisEdvKuerzel, 0, 3)
        groupboxLayoutG.addWidget(self.labelImportDateiname, 1, 0, 1, 4)
        groupboxLayoutG.addWidget(self.labelExportDateiname, 2, 0, 1, 4)
        groupboxKuerzel.setLayout(groupboxLayoutG)
        # Groupbox Zeichensatz
        groupboxLayoutZeichensatz = QVBoxLayout()
        groupboxZeichensatz = QGroupBox("Zeichensatz")
        groupboxZeichensatz.setStyleSheet("font-weight:bold")
        self.combobxZeichensatz = QComboBox()
        for zs in zeichensatz:
            self.combobxZeichensatz.addItem(zs)
        self.combobxZeichensatz.setStyleSheet("font-weight:normal")
        self.combobxZeichensatz.setCurrentIndex(self.aktuelleZeichensatznummer)
        self.combobxZeichensatz.currentIndexChanged.connect(self.zeichensatzGewechselt) # type:ignore
        groupboxLayoutZeichensatz.addWidget(self.combobxZeichensatz)
        groupboxZeichensatz.setLayout(groupboxLayoutZeichensatz)

        dialogLayoutV.addWidget(groupboxGdtIds)
        dialogLayoutV.addWidget(groupboxAustauschverzeichniss)
        dialogLayoutV.addWidget(groupboxKuerzel)
        dialogLayoutV.addWidget(groupboxZeichensatz)
        dialogLayoutV.addWidget(self.buttonBox)
        dialogLayoutV.setContentsMargins(10, 10, 10, 10)
        dialogLayoutV.setSpacing(20)
        self.setLayout(dialogLayoutV)

    def kuerzelGeaendert(self):
        kuerzelSignoGdt = self.lineEditSignoGdtKuerzel.text()
        kuerzelPraxisEdv = self.lineEditPraxisEdvKuerzel.text()
        self.labelImportDateiname.setText("Import-Dateiname: " + kuerzelSignoGdt + kuerzelPraxisEdv + ".gdt")
        self.labelExportDateiname.setText("Export-Dateiname: " + kuerzelPraxisEdv + kuerzelSignoGdt + ".gdt")

    def durchsuchenImport(self):
        fd = QFileDialog(self)
        fd.setFileMode(QFileDialog.FileMode.Directory)
        fd.setWindowTitle("GDT-Austauschverzeichnis")
        fd.setDirectory(self.gdtAustauschVerzeichnis)
        fd.setModal(True)
        fd.setLabelText(QFileDialog.DialogLabel.Accept, "Ok")
        fd.setLabelText(QFileDialog.DialogLabel.Reject, "Abbrechen")
        if fd.exec() == 1:
            self.lineEditImport.setText(fd.directory().path())
            self.gdtAustauschVerzeichnis = fd.directory().path()

    def zeichensatzGewechselt(self):
        self.aktuelleZeichensatznummer = self.combobxZeichensatz.currentIndex()

    def accept(self):
        if len(self.lineEditPraxisEdvId.text()) != 8 and len(self.lineEditPraxisEdvId.text()) != 0:
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis", "Die GDT-ID muss aus acht Zeichen bestehen.", QMessageBox.StandardButton.Ok)
            mb.exec()
            self.lineEditPraxisEdvId.setFocus()
            self.lineEditPraxisEdvId.selectAll()
        elif len(self.lineEditPraxisEdvKuerzel.text()) != 4:
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von SignoGDT", "Das Kürzel für Austauschdateien muss aus vier Zeichen bestehen.", QMessageBox.StandardButton.Ok)
            mb.exec()
            self.lineEditPraxisEdvKuerzel.setFocus()
            self.lineEditPraxisEdvKuerzel.selectAll()
        else:
            self.done(1)