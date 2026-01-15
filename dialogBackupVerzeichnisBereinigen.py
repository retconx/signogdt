import  os, subprocess
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QLabel
)

class BackupVerzeichnisBereinigen(QDialog):
    def __init__(self):
        super().__init__()

        dialogLayoutV = QVBoxLayout()
        self.setWindowTitle("SignoGDT")
        self.buttonBox = QDialogButtonBox()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.CustomizeWindowHint, True)
        self.setWindowFlag(Qt. WindowType.WindowCloseButtonHint, False)
        self.setFixedWidth(300)
        self.setFixedHeight(80)
        label = QLabel("Das Backup-Verzeichnis wird bereinigt...")

        dialogLayoutV.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)
        dialogLayoutV.addWidget(self.buttonBox)
        self.setLayout(dialogLayoutV)
        self.show()