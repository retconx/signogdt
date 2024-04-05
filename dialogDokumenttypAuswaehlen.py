import os
import class_dokumenttyp
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QComboBox,
    QLabel,
    QCheckBox,
    QTextEdit, 
    QScrollBar
)
from PySide6.QtGui import Qt

basedir = os.path.dirname(__file__)

class DokumenttypAuswaehlen(QDialog):
    def __init__(self, updateSafePath:str):
        super().__init__()

        self.setWindowTitle("SignoGDT Dokumenttyp-Auswahl")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        labelTitel = QLabel("Bitte wählen Sie den gewünschten Dokumenttyp:")

        dokumenttypen = class_dokumenttyp.getAlleDokumenttypen(os.path.join(updateSafePath, "dokumenttypen.xml"))
        dialogLayoutV = QVBoxLayout()
        self.comboBoxDokumenttypen = QComboBox()
        for dt in dokumenttypen:
            self.comboBoxDokumenttypen.addItem(dt.getName())
        self.comboBoxDokumenttypen.addItems(dokumenttypen)
        dialogLayoutV.addWidget(labelTitel)
        dialogLayoutV.addWidget(self.comboBoxDokumenttypen)
        dialogLayoutV.addWidget(self.buttonBox, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(dialogLayoutV)
