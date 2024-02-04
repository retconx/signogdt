import  os, subprocess
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QSystemTrayIcon
)

class Warten(QDialog):
    def __init__(self):
        super().__init__()

        dialogLayoutV = QVBoxLayout()
        self.setWindowTitle("Warten auf Dokument...")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.rejected.connect(self.reject)
        self.setWindowFlag(self.buttonBox.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        label = QLabel("SignoGDT wartet auf das unterzeichnete Dokument.")

        dialogLayoutV.addWidget(label)
        dialogLayoutV.addWidget(self.buttonBox)
        self.setLayout(dialogLayoutV)
        self.show()