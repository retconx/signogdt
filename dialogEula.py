from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QTextEdit, 
    QScrollBar
)
from PySide6.QtGui import Qt, QDesktopServices

class Eula(QDialog):
    def __init__(self, neueVersion=""):
        super().__init__()

        self.setWindowTitle("Endnutzer-Lizenzvereinbarung (EULA)")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.accepted.connect(self.accept)

        dialogLayoutV = QVBoxLayout()
        labelAktualisiert = QLabel("SignoGDT wurde erfolgreich auf Version " + neueVersion + " aktualisiert.")
        labelBestaetigung = QLabel("Bitte bestätigen Sie, dass Sie die folgende Lizenzvereinbarung gelesen haben und dieser zustimmen.")
        text = ""
        self.textEditEula = QTextEdit()
        self.textEditEula.setReadOnly(True)
        with open("eula.txt", "r", encoding="utf_8") as f:  
            for zeile in f:
                text += zeile
        self.textEditEula.setText(text)
        self.textEditEula.setFixedHeight(300)
        self.textEditEula.verticalScrollBar().setRange(0,105)
        self.textEditEula.verticalScrollBar().valueChanged.connect(self.scrollBarChanged)

        self.checkBoxZustimmung = QCheckBox("Gelesen und zugestimmt")
        self.checkBoxZustimmung.setEnabled(False)
        if neueVersion != "":
            dialogLayoutV.addWidget(labelAktualisiert)
            dialogLayoutV.addSpacing(10)
        dialogLayoutV.addWidget(labelBestaetigung, alignment=Qt.AlignmentFlag.AlignCenter)
        dialogLayoutV.addSpacing(10)
        dialogLayoutV.addWidget(self.textEditEula)
        dialogLayoutV.addSpacing(10)
        dialogLayoutV.addWidget(self.checkBoxZustimmung, alignment=Qt.AlignmentFlag.AlignCenter)
        dialogLayoutV.addSpacing(10)
        dialogLayoutV.addWidget(self.buttonBox, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(dialogLayoutV)
    
    def scrollBarChanged(self, d):
       if d == 1722:
           self.checkBoxZustimmung.setEnabled(True)
