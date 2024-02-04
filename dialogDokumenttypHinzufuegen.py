import configparser, os
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QCheckBox
)

class DokumenttypHinzufuegen(QDialog):
    def __init__(self, dokumenttypen:list):
        super().__init__()
        self.setMinimumWidth(400)
        self.dokumenttypen = dokumenttypen

        self.setWindowTitle("Dokumenttyp hinzufügen")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        dialogLayoutV = QVBoxLayout()
        labelName = QLabel("Name:")
        self.lineEditName = QLineEdit()

        dialogLayoutV.addWidget(labelName)
        dialogLayoutV.addWidget(self.lineEditName)
        dialogLayoutV.addWidget(self.buttonBox)
        dialogLayoutV.setSpacing(20)
        self.setLayout(dialogLayoutV)

        self.lineEditName.setFocus()

    def accept(self):
        # Name auf Eindeutigkeit prüfen
        doppelt = False
        for dokument in self.dokumenttypen:
            if self.lineEditName.text() == dokument.name:
                mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von SignoGDT", "Ein Dokumenttyp mit dem angegebenen Namen existiert bereits.", QMessageBox.StandardButton.Ok)
                mb.exec()
                self.lineEditName.setFocus()
                self.lineEditName.selectAll()
                break
        self.done(1)