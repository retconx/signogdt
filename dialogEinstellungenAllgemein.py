import configparser, os, sys
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QCheckBox,
    QGroupBox, 
    QMessageBox
)

class EinstellungenAllgemein(QDialog):
    def __init__(self, configPath):
        super().__init__()
        self.setMinimumWidth(500)
        self.fontNormal = QFont()
        self.fontNormal.setBold(False)
        self.fontBold = QFont()
        self.fontBold.setBold(True)

        #config.ini lesen
        configIni = configparser.ConfigParser()
        configIni.read(os.path.join(configPath, "config.ini"))
        self.signoSignPfad = configIni["Allgemein"]["signosignpfad"]
        self.signoSignArchivverzeichnis= configIni["Allgemein"]["signosignarchivverzeichnis"]
        self.signoSignArchivierungsname = configIni["Allgemein"]["signosignarchivierungsname"]
        self.deleteAfterOpen = configIni["Allgemein"]["deleteafteropen"] == "True"
        self.backupverzeichnis = configIni["Allgemein"]["backupverzeichnis"]
        self.autoupdate = configIni["Allgemein"]["autoupdate"] == "True"
        self.updaterpfad = configIni["Allgemein"]["updaterpfad"]
        self.setWindowTitle("Allgemeine Einstellungen")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        dialogLayoutV = QVBoxLayout()
        dialogLayoutGroupboxSignoSignG = QGridLayout()
        dialogLayoutGroupboxSignoGdtG = QGridLayout()
        # GroupBox signoSign/2
        groupBoxSignoSign = QGroupBox("signoSign/2")
        groupBoxSignoSign.setFont(self.fontBold)
        groupBoxSignoSign.setLayout(dialogLayoutGroupboxSignoSignG)
        labelSignoSignPfad = QLabel("Programmpfad (signosign.exe):")
        labelSignoSignPfad.setFont(self.fontNormal)
        self.lineEditSignoSignPfad = QLineEdit(self.signoSignPfad)
        self.lineEditSignoSignPfad.setToolTip(self.signoSignPfad)
        self.lineEditSignoSignPfad.setFont(self.fontNormal)
        self.pushButtonSignoSignPfadDurchsuchen = QPushButton("...")
        self.pushButtonSignoSignPfadDurchsuchen.setFont(self.fontNormal)
        self.pushButtonSignoSignPfadDurchsuchen.clicked.connect(self.pushButtonSignoSignPfadDurchsuchenClicked)
        labelArchivverzeichnis = QLabel("Archivverzeichnis:")
        labelArchivverzeichnis.setFont(self.fontNormal)
        self.lineEditArchivverzeichnis = QLineEdit(self.signoSignArchivverzeichnis)
        self.lineEditArchivverzeichnis.setToolTip(self.signoSignArchivverzeichnis)
        self.lineEditArchivverzeichnis.setFont(self.fontNormal)
        self.pushButtonSignoSignArchivverzeichnisDurchsuchen = QPushButton("...")
        self.pushButtonSignoSignArchivverzeichnisDurchsuchen.setFont(self.fontNormal)
        self.pushButtonSignoSignArchivverzeichnisDurchsuchen.clicked.connect(self.pushButtonSignoSignArchivverzeichnisDurchsuchenClicked)
        labelArchivierungsname = QLabel("Archivierungsname (ohne .pdf):")
        labelArchivierungsname.setFont(self.fontNormal)
        self.lineEditArchivierungsname = QLineEdit(self.signoSignArchivierungsname)
        self.lineEditArchivierungsname.setFont(self.fontNormal)
        dialogLayoutGroupboxSignoSignG.addWidget(labelSignoSignPfad, 0, 0, 1, 2)
        dialogLayoutGroupboxSignoSignG.addWidget(self.lineEditSignoSignPfad, 1, 0, 1, 1)
        dialogLayoutGroupboxSignoSignG.addWidget(self.pushButtonSignoSignPfadDurchsuchen, 1, 1, 1, 1)
        dialogLayoutGroupboxSignoSignG.addWidget(labelArchivverzeichnis, 2, 0, 1, 2)
        dialogLayoutGroupboxSignoSignG.addWidget(self.lineEditArchivverzeichnis, 3, 0, 1, 1)
        dialogLayoutGroupboxSignoSignG.addWidget(self.pushButtonSignoSignArchivverzeichnisDurchsuchen, 3, 1, 1, 1)
        dialogLayoutGroupboxSignoSignG.addWidget(labelArchivierungsname, 4, 0, 1, 2)
        dialogLayoutGroupboxSignoSignG.addWidget(self.lineEditArchivierungsname, 5, 0, 1, 2)

        # GroupBox SignoGDT
        groupBoxSignoGdt = QGroupBox("SignoGDT")
        groupBoxSignoGdt.setFont(self.fontBold)
        groupBoxSignoGdt.setLayout(dialogLayoutGroupboxSignoGdtG)
        labelBackupverzeichnis = QLabel("Backup-Verzeichnis:")
        labelBackupverzeichnis.setFont(self.fontNormal)
        self.lineEditBackupverzeichnis = QLineEdit(self.backupverzeichnis)
        self.lineEditBackupverzeichnis.setToolTip(self.backupverzeichnis)
        self.lineEditBackupverzeichnis.setFont(self.fontNormal)
        self.pushButtonBackupverzeichnisDurchsuchen = QPushButton("...")
        self.pushButtonBackupverzeichnisDurchsuchen.setFont(self.fontNormal)
        self.pushButtonBackupverzeichnisDurchsuchen.clicked.connect(self.pushButtonBackupverzeichnisDurchsuchenClicked)
        self.checkBoxDeleteAfterOpen = QCheckBox("SML-Datei nach Einlesen löschen")
        self.checkBoxDeleteAfterOpen.setChecked(self.deleteAfterOpen)
        self.checkBoxDeleteAfterOpen.setFont(self.fontNormal)
        dialogLayoutGroupboxSignoGdtG.addWidget(labelBackupverzeichnis, 0, 0, 1, 2)
        dialogLayoutGroupboxSignoGdtG.addWidget(self.lineEditBackupverzeichnis, 1, 0, 1, 1)
        dialogLayoutGroupboxSignoGdtG.addWidget(self.pushButtonBackupverzeichnisDurchsuchen, 1, 1, 1, 1)
        dialogLayoutGroupboxSignoGdtG.addWidget(self.checkBoxDeleteAfterOpen)

        # GroupBox Updates
        groupBoxUpdatesLayoutG = QGridLayout()
        groupBoxUpdates = QGroupBox("Updates")
        groupBoxUpdates.setFont(self.fontBold)
        labelUpdaterPfad = QLabel("Updater-Pfad")
        labelUpdaterPfad.setFont(self.fontNormal)
        self.lineEditUpdaterPfad= QLineEdit(self.updaterpfad)
        self.lineEditUpdaterPfad.setFont(self.fontNormal)
        self.lineEditUpdaterPfad.setToolTip(self.updaterpfad)
        if not os.path.exists(self.updaterpfad):
            self.lineEditUpdaterPfad.setStyleSheet("background:rgb(255,200,200)")
        self.pushButtonUpdaterPfad = QPushButton("...")
        self.pushButtonUpdaterPfad.setFont(self.fontNormal)
        self.pushButtonUpdaterPfad.setToolTip("Pfad zum GDT-Tools Updater auswählen")
        self.pushButtonUpdaterPfad.clicked.connect(self.pushButtonUpdaterPfadClicked)
        self.checkBoxAutoUpdate = QCheckBox("Automatisch auf Update prüfen")
        self.checkBoxAutoUpdate.setFont(self.fontNormal)
        self.checkBoxAutoUpdate.setChecked(self.autoupdate)
        groupBoxUpdatesLayoutG.addWidget(labelUpdaterPfad, 0, 0)
        groupBoxUpdatesLayoutG.addWidget(self.lineEditUpdaterPfad, 0, 1)
        groupBoxUpdatesLayoutG.addWidget(self.pushButtonUpdaterPfad, 0, 2)
        groupBoxUpdatesLayoutG.addWidget(self.checkBoxAutoUpdate, 1, 0)
        groupBoxUpdates.setLayout(groupBoxUpdatesLayoutG)

        dialogLayoutV.addWidget(groupBoxSignoSign)
        dialogLayoutV.addWidget(groupBoxSignoGdt)
        dialogLayoutV.addWidget(groupBoxUpdates)
        dialogLayoutV.addWidget(self.buttonBox)
        dialogLayoutV.setSpacing(20)
        self.setLayout(dialogLayoutV)

    def pushButtonSignoSignPfadDurchsuchenClicked(self):
        fd = QFileDialog(self)
        fd.setFileMode(QFileDialog.FileMode.ExistingFile)
        fd.setWindowTitle("Pfad zu signoSign/2")
        fd.setDirectory(self.signoSignPfad)
        fd.setModal(True)
        fd.setViewMode(QFileDialog.ViewMode.Detail)
        fd.setNameFilters(["exe-Dateien (*.exe)"])
        fd.setLabelText(QFileDialog.DialogLabel.Accept, "Ok")
        fd.setLabelText(QFileDialog.DialogLabel.Reject, "Abbrechen")
        if fd.exec() == 1:
            self.lineEditSignoSignPfad.setText(os.path.abspath(fd.selectedFiles()[0]))
            self.lineEditSignoSignPfad.setToolTip(os.path.abspath(fd.selectedFiles()[0]))
            self.signoSignPfad = os.path.abspath(fd.selectedFiles()[0])

    def pushButtonSignoSignArchivverzeichnisDurchsuchenClicked(self):
        fd = QFileDialog(self)
        fd.setFileMode(QFileDialog.FileMode.Directory)
        fd.setWindowTitle("signoSign/2-Archivverzeichnis")
        fd.setDirectory(self.signoSignArchivverzeichnis)
        fd.setModal(True)
        fd.setLabelText(QFileDialog.DialogLabel.Accept, "Ok")
        fd.setLabelText(QFileDialog.DialogLabel.Reject, "Abbrechen")
        if fd.exec() == 1:
            self.lineEditArchivverzeichnis.setText(os.path.abspath(fd.directory().path()))
            self.lineEditArchivverzeichnis.setToolTip(os.path.abspath(fd.directory().path()))
            self.signoSignArchivverzeichnis = os.path.abspath(fd.directory().path())

    def pushButtonBackupverzeichnisDurchsuchenClicked(self):
        fd = QFileDialog(self)
        fd.setFileMode(QFileDialog.FileMode.Directory)
        fd.setWindowTitle("Backup-Verzeichnis")
        fd.setDirectory(self.backupverzeichnis)
        fd.setModal(True)
        fd.setLabelText(QFileDialog.DialogLabel.Accept, "Ok")
        fd.setLabelText(QFileDialog.DialogLabel.Reject, "Abbrechen")
        if fd.exec() == 1:
            self.lineEditBackupverzeichnis.setText(os.path.abspath(fd.directory().path()))
            self.lineEditBackupverzeichnis.setToolTip(os.path.abspath(fd.directory().path()))
            self.backupverzeichnis = os.path.abspath(fd.directory().path())
    
    def pushButtonUpdaterPfadClicked(self):
        fd = QFileDialog(self)
        fd.setFileMode(QFileDialog.FileMode.ExistingFile)
        if os.path.exists(self.lineEditUpdaterPfad.text()):
            fd.setDirectory(os.path.dirname(self.lineEditUpdaterPfad.text()))
        fd.setWindowTitle("Updater-Pfad auswählen")
        fd.setModal(True)
        if "win32" in sys.platform:
            fd.setNameFilters(["exe-Dateien (*.exe)"])
        elif "darwin" in sys.platform:
            fd.setNameFilters(["app-Bundles (*.app)"])
        fd.setLabelText(QFileDialog.DialogLabel.Accept, "Auswählen")
        fd.setLabelText(QFileDialog.DialogLabel.Reject, "Abbrechen")
        if fd.exec() == 1:
            self.lineEditUpdaterPfad.setText(os.path.abspath(fd.selectedFiles()[0]))
            self.lineEditUpdaterPfad.setToolTip(os.path.abspath(fd.selectedFiles()[0]))
            self.lineEditUpdaterPfad.setStyleSheet("background:rgb(255,255,255)")

    def accept(self):
        if self.lineEditArchivierungsname.text()[-4:] == ".pdf":
            self.lineEditArchivierungsname.setText(self.lineEditArchivierungsname.text()[:-4])
        self.done(1)