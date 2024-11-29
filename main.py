import sys, configparser, os, datetime, shutil, logger, time, subprocess, re, atexit
import xml.etree.ElementTree as ElementTree
import gdt, class_dokumenttyp, class_smlDatei
## Nur mit Lizenz
import gdttoolsL
## /Nur mit Lizenz
import dialogEinstellungenGdt, dialogEinstellungenGdt, dialogEinstellungenLanrLizenzschluessel, dialogUeberSignoGdt, dialogEinstellungenAllgemein, dialogDokumenttypHinzufuegen, dialogWarten, dialogEula, dialogDokumenttypAuswaehlen
from PySide6.QtCore import Qt, QTranslator, QLibraryInfo,QFileSystemWatcher
from PySide6.QtGui import QFont, QAction, QIcon, QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QAbstractItemView,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QLabel, 
    QDialogButtonBox,
    QComboBox,
    QMessageBox, 
    QListWidget,
    QLineEdit,
    QSystemTrayIcon,
    QDialog
)
import requests

basedir = os.path.dirname(__file__)
reGdtFeldkennung = r"^\d{4}$"
variablenInhalte = ["ID (FK 3000)", "Vorname (FK 3102)", "Nachname (FK 3101)", "Geburtsdatum (FK 3103)", "Straße (FK 3107)", "Wohnort (FK 3106)", "Körpergröße (FK 3122)", "Körpergewicht (FK 3123)", "E-Mail-Adresse (FK 3619)", "Telefonnummer fest (FK 3626)", "Telefonnummer mobil (FK 3618)"]
datumsfeldkennungen = ["3103"]

def versionVeraltet(versionAktuell:str, versionVergleich:str):
    """
    Vergleicht zwei Versionen im Format x.x.x
    Parameter:
        versionAktuell:str
        versionVergleich:str
    Rückgabe:
        True, wenn versionAktuell veraltet
    """
    versionVeraltet= False
    hunderterBase = int(versionVergleich.split(".")[0])
    zehnerBase = int(versionVergleich.split(".")[1])
    einserBase = int(versionVergleich.split(".")[2])
    hunderter = int(versionAktuell.split(".")[0])
    zehner = int(versionAktuell.split(".")[1])
    einser = int(versionAktuell.split(".")[2])
    if hunderterBase > hunderter:
        versionVeraltet = True
    elif hunderterBase == hunderter:
        if zehnerBase >zehner:
            versionVeraltet = True
        elif zehnerBase == zehner:
            if einserBase > einser:
                versionVeraltet = True
    return versionVeraltet

# Sicherstellen, dass Icon in Windows angezeigt wird
try:
    from ctypes import windll # type: ignore
    mayappid = "gdttools.signogdt"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(mayappid)
except ImportError:
    pass

class MainWindow(QMainWindow):
    # Mainwindow zentrieren
    def resizeEvent(self, e):
        mainwindowBreite = e.size().width()
        mainwindowHoehe = e.size().height()
        ag = self.screen().availableGeometry()
        screenBreite = ag.size().width()
        screenHoehe = ag.size().height()
        left = screenBreite / 2 - mainwindowBreite / 2
        top = screenHoehe / 2 - mainwindowHoehe / 2
        self.setGeometry(left, top, mainwindowBreite, mainwindowHoehe)

    def closeEvent(self, e):
        if self.ungesicherteAenderungen:
            mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von SignoGDT", "Es liegen möglicherweise ungesicherte Änderungen vor.\nSoll SignoGDT dennoch geschlossen werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            mb.setDefaultButton(QMessageBox.StandardButton.Yes)
            mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
            mb.button(QMessageBox.StandardButton.No).setText("Nein")
            if mb.exec() == QMessageBox.StandardButton.No:
                e.ignore()

    def __init__(self):
        super().__init__()
        # Prüfen, ob dokumenttypen.xml existiert
        if os.path.exists(os.path.join(updateSafePath, "dokumenttypen.xml")):
            logger.logger.info("dokumenttypen.xml in " + updateSafePath + " exisitert")
        else:
            rootElement = ElementTree.Element("root")
            et = ElementTree.ElementTree(rootElement)
            ElementTree.indent(et)
            try:
                et.write(os.path.join(updateSafePath, "dokumenttypen.xml"), "utf-8", True)
                logger.logger.info("dokumenttypen.xml in " + updateSafePath + " erzeugt")
            except Exception as e:
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Fehler beim Erzeugen der dokumenttypen.xml in " + updateSafePath + ": " + str(e), QMessageBox.StandardButton.Ok)
                mb.exec()

        # Nachträglich hinzufefügte Options
        # 1.0.2
        global ci_eulagelesen
        ci_eulagelesen = False
        if configIni.has_option("Allgemein", "eulagelesen"):
            ci_eulagelesen = configIni["Allgemein"]["eulagelesen"] == "True"
        # 1.4.0
        self.autoupdate = True
        self.updaterpfad = ""
        if configIni.has_option("Allgemein", "autoupdate"):
            self.autoupdate = configIni["Allgemein"]["autoupdate"] == "True"
        if configIni.has_option("Allgemein", "updaterpfad"):
            self.updaterpfad = configIni["Allgemein"]["updaterpfad"]
        # /Nachträglich hinzufefügte Options

        ## Nur mit Lizenz
        # Prüfen, ob Lizenzschlüssel unverschlüsselt
        global ci_lizenzschluessel, ci_version
        if len(ci_lizenzschluessel) == 29:
            logger.logger.info("Lizenzschlüssel unverschlüsselt")
            configIni["Erweiterungen"]["lizenzschluessel"] = gdttoolsL.GdtToolsLizenzschluessel.krypt(ci_lizenzschluessel)
            with open(os.path.join(ci_pfad, "config.ini"), "w") as configfile:
                    configIni.write(configfile)
        else:
            ci_lizenzschluessel = gdttoolsL.GdtToolsLizenzschluessel.dekrypt(ci_lizenzschluessel)
        ## /Nur mit Lizenz

        # Prüfen, ob EULA gelesen
        if not ci_eulagelesen:
            de = dialogEula.Eula()
            de.exec()
            if de.checkBoxZustimmung.isChecked():
                ci_eulagelesen = True
                configIni["Allgemein"]["eulagelesen"] = "True"
                with open(os.path.join(ci_pfad, "config.ini"), "w") as configfile:
                    configIni.write(configfile)
                logger.logger.info("EULA zugestimmt")
            else:
                mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von SignoGDT", "Ohne einmalige Zustimmung der Lizenzvereinbarung kann SignoGDT nicht gestartet werden.", QMessageBox.StandardButton.Ok)
                mb.exec()
                sys.exit()
            
        # Grundeinstellungen bei erstem Start
        if ersterStart:
            logger.logger.info("Erster Start")
            mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von SignoGDT", "Vermutlich starten Sie SignoGDT das erste Mal auf diesem PC.\nMöchten Sie jetzt die Grundeinstellungen vornehmen?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            mb.setDefaultButton(QMessageBox.StandardButton.Yes)
            if mb.exec() == QMessageBox.StandardButton.Yes:
                ## Nur mit Lizenz
                self.einstellungenLanrLizenzschluessel(False, False)
                ## /Nur mit Lizenz
                self.einstellungenGdt(False, False)
                self.einstellungenAllgemein(False, False)
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Die Ersteinrichtung ist abgeschlossen. SignoGDT wird beendet.", QMessageBox.StandardButton.Ok)
                mb.exec()
                sys.exit()

        # Version vergleichen und gegebenenfalls aktualisieren
        configIniBase = configparser.ConfigParser()
        try:
            configIniBase.read(os.path.join(basedir, "config.ini"))
            if versionVeraltet(ci_version, configIniBase["Allgemein"]["version"]):
                # Version aktualisieren
                configIni["Allgemein"]["version"] = configIniBase["Allgemein"]["version"]
                configIni["Allgemein"]["releasedatum"] = configIniBase["Allgemein"]["releasedatum"] 
                # config.ini aktualisieren
                # 1.2.2 -> 1.3.0 ["Allgemein"]["autoupdate"] und ["Allgemein"]["updaterpfad"] hinzufügen
                if not configIni.has_option("Allgemein", "autoupdate"):
                    configIni["Allgemein"]["autoupdate"] = "True"
                if not configIni.has_option("Allgemein", "updaterpfad"):
                    configIni["Allgemein"]["updaterpfad"] = ""
                # /config.ini aktualisieren

                with open(os.path.join(ci_pfad, "config.ini"), "w") as configfile:
                    configIni.write(configfile)
                ci_version = configIni["Allgemein"]["version"]
                logger.logger.info("Version auf " + ci_version + " aktualisiert")
                # Prüfen, ob EULA gelesen
                de = dialogEula.Eula(ci_version)
                de.exec()
                ci_eulagelesen = de.checkBoxZustimmung.isChecked()
                configIni["Allgemein"]["eulagelesen"] = str(ci_eulagelesen)
                with open(os.path.join(ci_pfad, "config.ini"), "w") as configfile:
                    configIni.write(configfile)
                if ci_eulagelesen:
                    logger.logger.info("EULA zugestimmt")
                else:
                    logger.logger.info("EULA nicht zugestimmt")
                    mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von SignoGDT", "Ohne  Zustimmung zur Lizenzvereinbarung kann SignoGDT nicht gestartet werden.", QMessageBox.StandardButton.Ok)
                    mb.exec()
                    sys.exit()
        except SystemExit:
            sys.exit()
        except:
            logger.logger.error("Problem beim Aktualisieren auf Version " + configIniBase["Allgemein"]["version"])
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Problem beim Aktualisieren auf Version " + configIniBase["Allgemein"]["version"], QMessageBox.StandardButton.Ok)
            mb.exec()

        self.addOnsFreigeschaltet = True
        
        ## Nur mit Lizenz
        # Add-Ons freigeschaltet?
        self.addOnsFreigeschaltet = gdttoolsL.GdtToolsLizenzschluessel.lizenzErteilt(ci_lizenzschluessel, ci_lanr, gdttoolsL.SoftwareId.SIGNOGDT) or gdttoolsL.GdtToolsLizenzschluessel.lizenzErteilt(ci_lizenzschluessel, ci_lanr, gdttoolsL.SoftwareId.SIGNOGDTPSEUDO)
        ## Nur mit Lizenz
        
        jahr = datetime.datetime.now().year
        copyrightJahre = "2024"
        if jahr > 2024:
            copyrightJahre = "2024-" + str(jahr)
        self.setWindowTitle("SignoGDT V" + ci_version + " (\u00a9 Fabian Treusch - GDT-Tools " + copyrightJahre + ")")
        self.fontNormal = QFont()
        self.fontNormal.setBold(False)
        self.fontBold = QFont()
        self.fontBold.setBold(True)
        self.ungesicherteAenderungen = False

        # Dokumenttypen laden
        try:
            tree = ElementTree.parse(os.path.join(updateSafePath, "dokumenttypen.xml"))
            logger.logger.info("dokumenttypen.xml geladen")
            dokumenttypenRoot = tree.getroot()
        except Exception as e:
            logger.logger.critical("Fehler beim Laden der dokumenttypen.xml: " + str(e))
            mb = QMessageBox(QMessageBox.Icon.Critical, "Hinweis von SignoGDT", "Fehler beim Laden der dokumenttypen.xml: " + str(e) + ". SignoGDT kann nicht gestartet werden.", QMessageBox.StandardButton.Ok)
            mb.exec()
            sys.exit()

        self.widget = QWidget()
        self.widget.installEventFilter(self)

        ## Formularaufbau
        mainLayoutV = QVBoxLayout()
        mainLayoutH = QHBoxLayout()
        layoutSpalte1V = QVBoxLayout()
        layoutSpalte2V = QVBoxLayout()
        layoutSpalte2G = QGridLayout()
        self.labelPseudolizenz = QLabel("+++ Pseudolizenz für Test-/ Präsentationszwecke +++")
        self.labelPseudolizenz.setStyleSheet("color:rgb(200,0,0);font-style:italic")
        # Dokumenttypen
        labelDokumenttypen = QLabel("Dokumenttypen:")
        self.pushButtonDokumenttypHinzufuegen = QPushButton("Neu...")
        self.pushButtonDokumenttypHinzufuegen.setToolTip("Dokumenttyp hinzufügen")
        self.pushButtonDokumenttypHinzufuegen.clicked.connect(self.pushButtonDokumenttypHinzufuegenClicked)
        self.listWidgetDokumenttypen = QListWidget()
        self.listWidgetDokumenttypen.currentItemChanged.connect(self.aktualisiereFormular)
        self.listWidgetDokumenttypen.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked | QAbstractItemView.EditTrigger.DoubleClicked)
        self.dokumenttypen = class_dokumenttyp.getAlleDokumenttypen(os.path.join(updateSafePath, "dokumenttypen.xml"))
        i = 0
        for dokumenttyp in self.dokumenttypen:
            self.listWidgetDokumenttypen.addItem(dokumenttyp.getName())
            self.listWidgetDokumenttypen.item(i).setFlags(self.listWidgetDokumenttypen.item(i).flags() | Qt.ItemFlag.ItemIsEditable)
            i += 1
        self.listWidgetDokumenttypen.itemChanged.connect(self.listWidgetDokumenttypenItemChanged)
        layoutSpalte1V.addWidget(labelDokumenttypen)
        layoutSpalte1V.addWidget(self.pushButtonDokumenttypHinzufuegen)
        layoutSpalte1V.addWidget(self.listWidgetDokumenttypen)
        # Dateipfade, Variablen
        labelDateipfade = QLabel("Dateipfade:")
        layoutSpalte2G.addWidget(labelDateipfade, 1, 0, 1, 2)
        self.lineEditDateipfade = []
        self.pushButtonDateipfadSuchen = []
        labelVariable = QLabel("Variablen:")
        self.comboBoxVariableninhalte = QComboBox()
        self.comboBoxVariableninhalte.addItems(variablenInhalte)
        self.comboBoxVariableninhalte.currentIndexChanged.connect(self.comboBoxVariableninhalteChanged)
        layoutSpalte2G.addWidget(labelVariable, 0, 2, 1, 2)
        layoutSpalte2G.addWidget(self.comboBoxVariableninhalte, 1, 2, 1, 3)
        labelVariablenNr = []
        self.lineEditVariable = []
        self.pushButtonVariableEinfuegen = []
        for i in range(10):
            self.lineEditDateipfade.append(QLineEdit())
            self.lineEditDateipfade[i].setMinimumWidth(300)
            self.lineEditDateipfade[i].editingFinished.connect(lambda dateipfadNr=i: self.lineEditDateipfadeEditingFinished(dateipfadNr))
            self.pushButtonDateipfadSuchen.append(QPushButton("..."))
            self.pushButtonDateipfadSuchen[i].setToolTip("Dateipfad auswählen")
            self.pushButtonDateipfadSuchen[i].clicked.connect(lambda checked=False, variablenNr=i: self.pushButtonDateipfadSuchenClicked(checked, variablenNr))
            labelVariablenNr.append(QLabel(str(i + 1)))
            self.lineEditVariable.append(QLineEdit())
            self.lineEditVariable[i].setMinimumWidth(200)
            self.lineEditVariable[i].editingFinished.connect(lambda variablennNr=i: self.lineEditVariableEditingFinished(variablennNr))
            self.pushButtonVariableEinfuegen.append(QPushButton("\u2380"))
            self.pushButtonVariableEinfuegen[i].setToolTip("Variable für " + self.comboBoxVariableninhalte.currentText() + " einfügen")
            self.pushButtonVariableEinfuegen[i].clicked.connect(lambda checked=False, variablenNr=i: self.pushButtonVariableEinfuegenClicked(checked, variablenNr))
            layoutSpalte2G.addWidget(self.lineEditDateipfade[i], i + 2, 0)
            layoutSpalte2G.addWidget(self.pushButtonDateipfadSuchen[i], i + 2, 1)
            layoutSpalte2G.addWidget(labelVariablenNr[i], i + 2, 2)
            layoutSpalte2G.addWidget(self.lineEditVariable[i], i + 2, 3)
            layoutSpalte2G.addWidget(self.pushButtonVariableEinfuegen[i], i + 2, 4)
        layoutSpalte2V.addLayout(layoutSpalte2G)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Schließen")
        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.buttonBox.rejected.connect(self.reject) # type: ignore

        mainLayoutH.addLayout(layoutSpalte1V)
        mainLayoutH.addLayout(layoutSpalte2V)
        ## Nur mit Lizenz
        if self.addOnsFreigeschaltet and gdttoolsL.GdtToolsLizenzschluessel.getSoftwareId(ci_lizenzschluessel) == gdttoolsL.SoftwareId.SIGNOGDTPSEUDO:
            mainLayoutV.addWidget(self.labelPseudolizenz, alignment=Qt.AlignmentFlag.AlignCenter)
        ## /Nur mit Lizenz
        mainLayoutV.addLayout(mainLayoutH)
        mainLayoutV.addWidget(self.buttonBox)
        ## Nur mit Lizenz
        if self.addOnsFreigeschaltet:
            gueltigeLizenztage = gdttoolsL.GdtToolsLizenzschluessel.nochTageGueltig(ci_lizenzschluessel)
            if gueltigeLizenztage  > 0 and gueltigeLizenztage <= 30:
                labelLizenzLaeuftAus = QLabel("Die genutzte Lizenz ist noch " + str(gueltigeLizenztage) + " Tage gültig.")
                labelLizenzLaeuftAus.setStyleSheet("color:rgb(200,0,0)")
                mainLayoutV.addWidget(labelLizenzLaeuftAus, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText("Keine gültige Lizenz")
        ## /Nur mit Lizenz
        self.widget.setLayout(mainLayoutV)
        self.setCentralWidget(self.widget)

        self.listWidgetDokumenttypen.setCurrentRow(0)
        self.aktualisiereFormular()

        # Menü
        menubar = self.menuBar()
        anwendungMenu = menubar.addMenu("")
        aboutAction = QAction(self)
        aboutAction.setMenuRole(QAction.MenuRole.AboutRole)
        aboutAction.triggered.connect(self.ueberSignoGdt) # type: ignore
        updateAction = QAction("Auf Update prüfen", self)
        updateAction.setMenuRole(QAction.MenuRole.ApplicationSpecificRole)
        updateAction.triggered.connect(self.updatePruefung) # type: ignore
        einstellungenMenu = menubar.addMenu("Einstellungen")
        einstellungenAllgemeinAction = QAction("Allgemeine Einstellungen", self)
        einstellungenAllgemeinAction.triggered.connect(lambda checked = False, neustartfrage = True: self.einstellungenAllgemein(checked, neustartfrage))
        einstellungenGdtAction = QAction("GDT-Einstellungen", self)
        einstellungenGdtAction.triggered.connect(lambda checked = False, neustartfrage = True: self.einstellungenGdt(checked, neustartfrage))
        ## Nur mit Lizenz
        einstellungenErweiterungenAction = QAction("LANR/Lizenzschlüssel", self)
        einstellungenErweiterungenAction.triggered.connect(lambda checked = False, neustartfrage = True: self.einstellungenLanrLizenzschluessel(checked, neustartfrage))
        ## /Nur mit Lizenz
        hilfeMenu = menubar.addMenu("Hilfe")
        hilfeWikiAction = QAction("SignoGDT Wiki", self)
        hilfeWikiAction.triggered.connect(self.signogdtWiki) 
        hilfeUpdateAction = QAction("Auf Update prüfen", self)
        hilfeUpdateAction.triggered.connect(self.updatePruefung) 
        hilfeAutoUpdateAction = QAction("Automatisch auf Update prüfen", self)
        hilfeAutoUpdateAction.setCheckable(True)
        hilfeAutoUpdateAction.setChecked(self.autoupdate)
        hilfeAutoUpdateAction.triggered.connect(self.autoUpdatePruefung)
        hilfeUeberAction = QAction("Über SignoGDT", self)
        hilfeUeberAction.setMenuRole(QAction.MenuRole.NoRole)
        hilfeUeberAction.triggered.connect(self.ueberSignoGdt) 
        hilfeEulaAction = QAction("Lizenzvereinbarung (EULA)", self)
        hilfeEulaAction.triggered.connect(self.eula) 
        hilfeLogExportieren = QAction("Log-Verzeichnis exportieren", self)
        hilfeLogExportieren.triggered.connect(self.logExportieren) 
        
        anwendungMenu.addAction(aboutAction)
        anwendungMenu.addAction(updateAction)
        einstellungenMenu.addAction(einstellungenAllgemeinAction)
        einstellungenMenu.addAction(einstellungenGdtAction)
        ## Nur mit Lizenz
        einstellungenMenu.addAction(einstellungenErweiterungenAction)
        ## /Nur mit Lizenz
        hilfeMenu.addAction(hilfeWikiAction)
        hilfeMenu.addSeparator()
        hilfeMenu.addAction(hilfeUpdateAction)
        hilfeMenu.addAction(hilfeAutoUpdateAction)
        hilfeMenu.addSeparator()
        hilfeMenu.addAction(hilfeUeberAction)
        hilfeMenu.addAction(hilfeEulaAction)
        hilfeMenu.addSeparator()
        hilfeMenu.addAction(hilfeLogExportieren)
        
        # Updateprüfung auf Github
        if self.autoupdate:
            try:
                self.updatePruefung(meldungNurWennUpdateVerfuegbar=True)
            except Exception as e:
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Updateprüfung nicht möglich.\nBitte überprüfen Sie Ihre Internetverbindung.", QMessageBox.StandardButton.Ok)
                mb.exec()
                logger.logger.warning("Updateprüfung nicht möglich: " + str(e))

    # def updatePruefung(self, meldungNurWennUpdateVerfuegbar = False):
    #     response = requests.get("https://api.github.com/repos/retconx/signogdt/releases/latest")
    #     githubRelaseTag = response.json()["tag_name"]
    #     latestVersion = githubRelaseTag[1:] # ohne v
    #     if versionVeraltet(ci_version, latestVersion):
    #         mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Die aktuellere SignoGDT-Version " + latestVersion + " ist auf <a href='https://github.com/retconx/signogdt/releases'>Github</a> verfügbar.", QMessageBox.StandardButton.Ok)
    #         mb.setTextFormat(Qt.TextFormat.RichText)
    #         mb.exec()
    #     elif not meldungNurWennUpdateVerfuegbar:
    #         mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Sie nutzen die aktuelle SignoGDT-Version.", QMessageBox.StandardButton.Ok)
    #         mb.exec()

    def updatePruefung(self, meldungNurWennUpdateVerfuegbar = False):
        logger.logger.info("Updateprüfung")
        response = requests.get("https://api.github.com/repos/retconx/signogdt/releases/latest")
        githubRelaseTag = response.json()["tag_name"]
        latestVersion = githubRelaseTag[1:] # ohne v
        if versionVeraltet(ci_version, latestVersion):
            logger.logger.info("Bisher: " + ci_version + ", neu: " + latestVersion)
            if os.path.exists(self.updaterpfad):
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von SignoGDT", "Die aktuellere SignoGDT-Version " + latestVersion + " ist auf Github verfügbar.\nSoll der GDT-Tools Updater geladen werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    logger.logger.info("Updater wird geladen")
                    atexit.register(self.updaterLaden)
                    sys.exit()
            else:
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Die aktuellere SignoGDT-Version " + latestVersion + " ist auf <a href='https://github.com/retconx/signogdt/releases'>Github</a> verfügbar.<br />Bitte beachten Sie auch die Möglichkeit, den Updateprozess mit dem <a href='https://github.com/retconx/gdttoolsupdater/wiki'>GDT-Tools Updater</a> zu automatisieren.", QMessageBox.StandardButton.Ok)
                mb.setTextFormat(Qt.TextFormat.RichText)
                mb.exec()
        elif not meldungNurWennUpdateVerfuegbar:
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Sie nutzen die aktuelle SignoGDT-Version.", QMessageBox.StandardButton.Ok)
            mb.exec()

    def updaterLaden(self):
        sex = sys.executable
        programmverzeichnis = ""
        logger.logger.info("sys.executable: " + sex)
        if "win32" in sys.platform:
            programmverzeichnis = sex[:sex.rfind("signogdt.exe")]
        elif "darwin" in sys.platform:
            programmverzeichnis = sex[:sex.find("SignoGDT.app")]
        elif "win32" in sys.platform:
            programmverzeichnis = sex[:sex.rfind("signogdt")]
        logger.logger.info("Programmverzeichnis: " + programmverzeichnis)
        try:
            if "win32" in sys.platform:
                subprocess.Popen([self.updaterpfad, "signogdt", ci_version, programmverzeichnis], creationflags=subprocess.DETACHED_PROCESS) # type: ignore
            elif "darwin" in sys.platform:
                subprocess.Popen(["open", "-a", self.updaterpfad, "--args", "signogdt", ci_version, programmverzeichnis])
            elif "linux" in sys.platform:
                subprocess.Popen([self.updaterpfad, "signogdt", ci_version, programmverzeichnis])
        except Exception as e:
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Der GDT-Tools Updater konnte nicht gestartet werden", QMessageBox.StandardButton.Ok)
            logger.logger.error("Fehler beim Starten des GDT-Tools Updaters: " + str(e))
            mb.exec()

    def autoUpdatePruefung(self, checked):
        self.autoupdate = checked
        configIni["Allgemein"]["autoupdate"] = str(checked)
        with open(os.path.join(ci_pfad, "config.ini"), "w") as configfile:
            configIni.write(configfile)

    def ueberSignoGdt(self):
        de = dialogUeberSignoGdt.UeberSignoGdt()
        de.exec()

    def eula(self):
        QDesktopServices.openUrl("https://gdttools.de/Lizenzvereinbarung_SignoGDT.pdf")

    def logExportieren(self):
        if (os.path.exists(os.path.join(basedir, "log"))):
            downloadPath = ""
            if sys.platform == "win32":
                downloadPath = os.path.expanduser("~\\Downloads")
            else:
                downloadPath = os.path.expanduser("~/Downloads")
            try:
                if shutil.copytree(os.path.join(basedir, "log"), os.path.join(downloadPath, "Log_SignoGDT"), dirs_exist_ok=True):
                    shutil.make_archive(os.path.join(downloadPath, "Log_SignoGDT"), "zip", root_dir=os.path.join(downloadPath, "Log_SignoGDT"))
                    shutil.rmtree(os.path.join(downloadPath, "Log_SignoGDT"))
                    mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Das Log-Verzeichnis wurde in den Ordner " + downloadPath + " kopiert.", QMessageBox.StandardButton.Ok)
                    mb.exec()
            except Exception as e:
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Problem beim Download des Log-Verzeichnisses: " + str(e), QMessageBox.StandardButton.Ok)
                mb.exec()
        else:
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Das Log-Verzeichnis wurde nicht gefunden.", QMessageBox.StandardButton.Ok)
            mb.exec() 

    def einstellungenAllgemein(self, checked, neustartfrage):
        de = dialogEinstellungenAllgemein.EinstellungenAllgemein(ci_pfad)
        if de.exec() == 1:
            configIni["Allgemein"]["signosignpfad"] = de.lineEditSignoSignPfad.text()
            configIni["Allgemein"]["deleteafteropen"] = str(de.checkBoxDeleteAfterOpen.isChecked())
            configIni["Allgemein"]["signosignarchivverzeichnis"] = de.lineEditArchivverzeichnis.text()
            configIni["Allgemein"]["signosignarchivierungsname"] = de.lineEditArchivierungsname.text()
            configIni["Allgemein"]["backupverzeichnis"] = de.lineEditBackupverzeichnis.text()
            configIni["Allgemein"]["updaterpfad"] = de.lineEditUpdaterPfad.text()
            configIni["Allgemein"]["autoupdate"] = str(de.checkBoxAutoUpdate.isChecked())

            with open(os.path.join(ci_pfad, "config.ini"), "w") as configfile:
                configIni.write(configfile)
            if neustartfrage:
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von SignoGDT", "Damit die Einstellungsänderungen wirksam werden, sollte SignoGDT neu gestartet werden.\nSoll SignoGDT jetzt neu gestartet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    if re.search("python", sys.executable, flags=re.IGNORECASE) != None:
                        os.execl(sys.executable, __file__, *sys.argv)
                    else: 
                        os.execl(sys.executable, *sys.argv)


    def einstellungenGdt(self, checked, neustartfrage):
        de = dialogEinstellungenGdt.EinstellungenGdt(ci_pfad)
        if de.exec() == 1:
            configIni["GDT"]["idsignogdt"] = de.lineEditSignoGdtId.text()
            configIni["GDT"]["idpraxisedv"] = de.lineEditPraxisEdvId.text()
            configIni["GDT"]["austauschverzeichnis"] = de.lineEditImport.text()
            configIni["GDT"]["importdateiloeschen"] = str(de.checkBoxImportdateiLoeschen.isChecked())
            configIni["GDT"]["kuerzelsignogdt"] = de.lineEditSignoGdtKuerzel.text()
            configIni["GDT"]["kuerzelpraxisedv"] = de.lineEditPraxisEdvKuerzel.text()
            configIni["GDT"]["zeichensatz"] = str(de.aktuelleZeichensatznummer + 1)
            with open(os.path.join(ci_pfad, "config.ini"), "w") as configfile:
                configIni.write(configfile)
            if neustartfrage:
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von SignoGDT", "Damit die Einstellungsänderungen wirksam werden, sollte SignoGDT neu gestartet werden.\nSoll SignoGDT jetzt neu gestartet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    if re.search("python", sys.executable, flags=re.IGNORECASE) != None:
                        os.execl(sys.executable, __file__, *sys.argv)
                    else: 
                        os.execl(sys.executable, *sys.argv)

    ## Nur mit Lizenz
    def einstellungenLanrLizenzschluessel(self, checked, neustartfrage):
        de = dialogEinstellungenLanrLizenzschluessel.EinstellungenProgrammerweiterungen(ci_pfad)
        if de.exec() == 1:
            configIni["Erweiterungen"]["lanr"] = de.lineEditLanr.text()
            configIni["Erweiterungen"]["lizenzschluessel"] = gdttoolsL.GdtToolsLizenzschluessel.krypt(de.lineEditLizenzschluessel.text())
            with open(os.path.join(ci_pfad, "config.ini"), "w") as configfile:
                configIni.write(configfile)
            if neustartfrage:
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von SignoGDT", "Damit die Einstellungsänderungen wirksam werden, sollte SignoGDT neu gestartet werden.\nSoll SignoGDT jetzt neu gestartet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    if re.search("python", sys.executable, flags=re.IGNORECASE) != None:
                        os.execl(sys.executable, __file__, *sys.argv)
                    else: 
                        os.execl(sys.executable, *sys.argv)
    ## /Nur mit Lizenz
    
    def signogdtWiki(self, link):
        QDesktopServices.openUrl("https://github.com/retconx/signogdt/wiki")
                
    def gdtToolsLinkGeklickt(self, link):
        QDesktopServices.openUrl(link)

    def pushButtonDokumenttypHinzufuegenClicked(self):
        ddh = dialogDokumenttypHinzufuegen.DokumenttypHinzufuegen(self.dokumenttypen)
        if ddh.exec() == 1 and ddh.lineEditName.text().strip() != "":
            self.listWidgetDokumenttypen.addItem(ddh.lineEditName.text())
            dokumenttypNummer = self.listWidgetDokumenttypen.count() - 1
            self.listWidgetDokumenttypen.setCurrentRow(dokumenttypNummer)
            self.dokumenttypen.append(class_dokumenttyp.Dokumenttyp(ddh.lineEditName.text(), [], []))
            self.aktualisiereFormular()
            self.listWidgetDokumenttypen.item(dokumenttypNummer).setFlags(self.listWidgetDokumenttypen.item(dokumenttypNummer).flags() | Qt.ItemFlag.ItemIsEditable)

    def comboBoxVariableninhalteChanged(self):
        for i in range(10):
            self.pushButtonVariableEinfuegen[i].setToolTip("Variable für " + self.comboBoxVariableninhalte.currentText() + " einfügen")

    def pushButtonDateipfadSuchenClicked(self, checked, dateipfadNr:int):
        fd = QFileDialog(self)
        fd.setFileMode(QFileDialog.FileMode.ExistingFile)
        fd.setWindowTitle("Dateipfad auswählen")
        fd.setModal(True)
        fd.setViewMode(QFileDialog.ViewMode.Detail)
        fd.setNameFilters(["PDF-Dateien (*.pdf)"])
        fd.setLabelText(QFileDialog.DialogLabel.Accept, "Ok")
        fd.setLabelText(QFileDialog.DialogLabel.Reject, "Abbrechen")
        if fd.exec() == 1:
            self.lineEditDateipfade[dateipfadNr].setText(os.path.abspath(fd.selectedFiles()[0]))
            self.lineEditDateipfade[dateipfadNr].setToolTip(os.path.abspath(fd.selectedFiles()[0]))
            self.lineEditDateipfadeEditingFinished(dateipfadNr)

    def pushButtonVariableEinfuegenClicked(self, checked, variablenNr:int):
        cursorPosition = self.lineEditVariable[variablenNr].cursorPosition()
        textVorCursor = self.lineEditVariable[variablenNr].text()[:cursorPosition]
        textNachCursor = self.lineEditVariable[variablenNr].text()[cursorPosition:]
        neuerText = textVorCursor + "${" + self.comboBoxVariableninhalte.currentText()[-5:-1] + "}" + textNachCursor
        self.lineEditVariable[variablenNr].setText(neuerText)
        self.lineEditVariable[variablenNr].setCursorPosition(cursorPosition + 7)
        self.lineEditVariableEditingFinished(variablenNr)

    # Formular abhängig vom ausgewählten Dokumenttyp neu ausfüllen
    def aktualisiereFormular(self):
        for i in range(10):
            self.lineEditDateipfade[i].setText("")
            self.lineEditVariable[i].setText("")
        if self.listWidgetDokumenttypen.count() > 0:
            dokumenttypName = self.listWidgetDokumenttypen.currentItem().text()
            gesuchterDokumenttyp = None
            gesuchterDokumenttypNummer = 0
            for dokumenttyp in self.dokumenttypen:
                if dokumenttyp.name == dokumenttypName:
                    gesuchterDokumenttyp = class_dokumenttyp.Dokumenttyp(dokumenttyp.name, dokumenttyp.getDateipfade().copy(), dokumenttyp.getVariablen().copy())
                    break
                gesuchterDokumenttypNummer += 1
            if gesuchterDokumenttyp != None:
                i = 0
                for dateipfad in gesuchterDokumenttyp.getDateipfade():
                    if dateipfad != "None":
                        self.lineEditDateipfade[i].setText(dateipfad)
                    i += 1
                nr = 0
                for variable in gesuchterDokumenttyp.getVariablen():
                    if variable != "None":
                        self.lineEditVariable[nr].setText(variable)
                    nr += 1
            else:
                logger.logger.error("Fehler in def aktualisiereFormular: Dokumenttyp " + dokumenttypName + " nicht in self.dokumenttypen gefunden")

    # Änderung der Dokumenttypen
    def listWidgetDokumenttypenItemChanged(self, item):
        currentRow = self.listWidgetDokumenttypen.currentRow()
        i = 0
        doppelt = False
        for dokumenttyp in self.dokumenttypen:
            if item.text() == dokumenttyp.getName() and i != currentRow:
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Die Dokumenttypbezeichnung muss eindeutig sein.", QMessageBox.StandardButton.Ok)
                mb.exec()
                self.listWidgetDokumenttypen.item(currentRow).setText(self.dokumenttypen[currentRow].getName())
                doppelt = True
                break
            i += 1
        if not doppelt:
            if item.text().strip() == "":
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von SignoGDT", "Soll der Dokumenttyp " + self.dokumenttypen[currentRow].getName() + " wirklich entfernt werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.No)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    self.listWidgetDokumenttypen.takeItem(currentRow)
                    self.dokumenttypen.pop(currentRow)
                    if self.listWidgetDokumenttypen.count() > 0:
                        if self.listWidgetDokumenttypen.count() == 1:
                            self.listWidgetDokumenttypen.setCurrentRow(0)
                        else:
                            self.listWidgetDokumenttypen.setCurrentRow(currentRow)
                    self.aktualisiereFormular()
                else:
                    self.listWidgetDokumenttypen.item(currentRow).setText(self.dokumenttypen[currentRow].getName())
            else:
                self.dokumenttypen[currentRow].name = item.text()

    def lineEditDateipfadeEditingFinished(self, dateipfadNr:int):
        if self.listWidgetDokumenttypen.count() > 0:
            dokumenttypIndex = self.listWidgetDokumenttypen.currentRow()
            if dateipfadNr < len(self.dokumenttypen[dokumenttypIndex].dateipfade):
                self.dokumenttypen[dokumenttypIndex].dateipfade[dateipfadNr] = self.lineEditDateipfade[dateipfadNr].text()
                self.ungesicherteAenderungen = True
            else:
                self.dokumenttypen[dokumenttypIndex].dateipfade.append(self.lineEditDateipfade[dateipfadNr].text())
            self.ungesicherteAenderungen = True
                                                                       
    def lineEditVariableEditingFinished(self, variablenNr:int):
        if self.listWidgetDokumenttypen.count() > 0:
            dokumenttypIndex = self.listWidgetDokumenttypen.currentRow()
            if variablenNr < len(self.dokumenttypen[dokumenttypIndex].variablen):
                self.dokumenttypen[dokumenttypIndex].variablen[variablenNr] = self.lineEditVariable[variablenNr].text()
            else:
                self.dokumenttypen[dokumenttypIndex].variablen.append(self.lineEditVariable[variablenNr].text())
            self.ungesicherteAenderungen = True
    
    def accept(self):
        if len(self.dokumenttypen) > 0:
            for i in range(len(self.dokumenttypen[self.listWidgetDokumenttypen.currentRow()].dateipfade)):
                self.lineEditDateipfadeEditingFinished(i)
            # for i in range(len(self.dokumenttypen[self.listWidgetDokumenttypen.currentRow()].variablen)):
            #     self.lineEditVariableEditingFinished(i)
            for i in range(10):
                self.lineEditVariableEditingFinished(i)
            rootElement = ElementTree.Element("root")
            for dokumenttyp in self.dokumenttypen:
                rootElement.append(dokumenttyp.getXml())
            et = ElementTree.ElementTree(rootElement)
            ElementTree.indent(et)
            try:
                et.write(os.path.join(ci_pfad, "dokumenttypen.xml"), "utf-8", True)
                logger.logger.info("dokumenttypen.xml erfolgreich gespeichert")
            except Exception as e:
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Fehler beim Speichern der Dokumenttypen: " + str(e), QMessageBox.StandardButton.Ok)
                mb.exec()
                logger.logger.error("Fehler beim Speichern der dokumenttypen.xml: " + str(e))
        sys.exit() 
        

    def reject(self):
        if self.ungesicherteAenderungen:
            mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von SignoGDT", "Es liegen möglicherweise ungesicherte Änderungen vor.\nSoll SignoGDT dennoch geschlossen werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            mb.setDefaultButton(QMessageBox.StandardButton.No)
            mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
            mb.button(QMessageBox.StandardButton.No).setText("Nein")
            if mb.exec() == QMessageBox.StandardButton.Yes:
                sys.exit()
        else:
            sys.exit()

def fswDirectoryChanged(pfad, patId:str, wartenDialog:QDialog, fsw:QFileSystemWatcher):
    logger.logger.info("Innerhalb directoryChanged (Pat-Id: " + patId + ")")
    files = os.listdir(ci_signoSignArchivverzeichnis)
    for file in files:
        logger.logger.info("Name in files: " + file)
        if file == ci_signoSignArchivierungsname + ".pdf":
            logger.logger.info("PDF-Datei " + file + " gefunden")
            backup = shutil.copy(os.path.join(ci_signoSignArchivverzeichnis, ci_signoSignArchivierungsname + ".pdf"), os.path.join(ci_backupverzeichnis, datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S_") + ci_signoSignArchivierungsname + ".pdf"))
            logger.logger.info("PDF-Datei nach " + backup + " kopiert")
            kopieFuerPvs = shutil.copy(os.path.join(ci_signoSignArchivverzeichnis, ci_signoSignArchivierungsname + ".pdf"), os.path.join(updateSafePath, ci_signoSignArchivierungsname + ".pdf"))
            logger.logger.info("PDF-Datei für PVS-Import nach " + kopieFuerPvs + " kopiert")
            wartenDialog.close()
            logger.logger.info("Warten-Dialog geschlossen")
            # GDT-Datei für PVS erzeugen
            gd = gdt.GdtDatei()
            sh = gdt.SatzHeader(gdt.Satzart.DATEN_EINER_UNTERSUCHUNG_UEBERMITTELN_6310, ci_idPraxisEdv, ci_idSignoGdt, ci_zeichensatz, "2.10", "Fabian Treusch - GDT-Tools", "SignoGDT", ci_version, patId)
            gd.erzeugeGdtDatei(sh.getSatzheader())
            gd.addZeile("6302", "signosign_" + datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S"))
            gd.addZeile("6303", "pdf")
            gd.addZeile("6304", "Unterzeichnetes Dokument (" + dokumenttypName + ")")
            gd.addZeile("6305", os.path.join(updateSafePath, ci_signoSignArchivierungsname + ".pdf"))
            gd.addZeile("6227", "Unterzeichnet: " + datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%Y %H:%M:%S"))
            gdtDateiname = ci_kuerzelPraxisEdv + ci_kuerzelSignoGdt + ".gdt"
            if gd.speichern(os.path.join(ci_austauschVerzeichnis, gdtDateiname), ci_zeichensatz):
                logger.logger.info("GDT-Datei " + os.path.join(ci_austauschVerzeichnis, gdtDateiname) + " gespeichert")
            else:
                logger.logger.error("Fehler beim Speichern der GDT-Datei " + os.path.join(ci_austauschVerzeichnis, gdtDateiname))
            fsw.removePath(ci_signoSignArchivverzeichnis)
            logger.logger.info("Archivverzeichnis " + ci_signoSignArchivverzeichnis + " vom FileSystemWatcher entfernt")
            os.unlink(os.path.join(ci_signoSignArchivverzeichnis, ci_signoSignArchivierungsname + ".pdf"))
            logger.logger.info("PDF-Datei " + os.path.join(ci_signoSignArchivverzeichnis, ci_signoSignArchivierungsname + ".pdf") + " gelöscht")
            sys.exit()
        else:
            logger.logger.info("Dateiname " + file + " entspricht nicht dem signoSign-Archivierungsname " + ci_signoSignArchivierungsname + ".pdf")   

app = QApplication(sys.argv)
app.setWindowIcon(QIcon(os.path.join(basedir, "icons", "program.png")))
# config.ini lesen
ersterStart = False
updateSafePath = ""
if sys.platform == "win32":
    logger.logger.info("Plattform: win32")
    updateSafePath = os.path.expanduser("~\\appdata\\local\\signogdt")
else:
    logger.logger.info("Plattform: nicht win32")
    updateSafePath = os.path.expanduser("~/.config/signogdt")
ci_pfad = updateSafePath
configIni = configparser.ConfigParser()
if os.path.exists(os.path.join(updateSafePath, "config.ini")):
    logger.logger.info("config.ini in " + updateSafePath + " exisitert")
elif os.path.exists(os.path.join(basedir, "config.ini")):
    logger.logger.info("config.ini in " + updateSafePath + " exisitert nicht")
    try:
        if (not os.path.exists(updateSafePath)):
            logger.logger.info(updateSafePath + " exisitert nicht")
            os.makedirs(updateSafePath, 0o777)
            logger.logger.info(updateSafePath + "erzeugt")
        shutil.copy(os.path.join(basedir, "config.ini"), updateSafePath)
        logger.logger.info("config.ini von " + basedir + " nach " + updateSafePath + " kopiert")
        ersterStart = True
    except:
        logger.logger.error("Problem beim Kopieren der config.ini von " + basedir + " nach " + updateSafePath)
        mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von SignoGDT", "Problem beim Kopieren der Konfigurationsdatei. SignoGDT wird mit Standardeinstellungen gestartet.", QMessageBox.StandardButton.Ok)
        mb.exec()
        ci_pfad = basedir
else:
    logger.logger.critical("config.ini fehlt")
    mb = QMessageBox(QMessageBox.Icon.Critical, "Hinweis von SignoGDT", "Die Konfigurationsdatei config.ini fehlt. SignoGDT kann nicht gestartet werden.", QMessageBox.StandardButton.Ok)
    mb.exec()
    sys.exit()

def getDokumenttypAusArgs():
    """
    Gibt das Argument, das nicht debug oder patidxxx ist, zurück, falls vorhanden
    Return:
        Dokumenttyp oder "", falls nicht vorhanden: str
    """
    dokumenttyp = ""
    for arg in sys.argv[1:]:
        if re.match("^debug$", arg, True) == None and re.match("^patid\\d+$", arg, False) == None:
            dokumenttyp = arg
            break
    return dokumenttyp

def getPatIdAusArgs():
    """
    Gibt xxx aus patidxxx zurück, falls vorhanden
    Return:
        PatId oder "", falls nicht vorhanden: str
    """
    patId = ""
    for arg in sys.argv[1:]:
        if re.match("^patid\\d+$", arg, False) != None:
            patId = arg[5:]
            break
    return patId

configIni.read(os.path.join(ci_pfad, "config.ini"))
ci_version = configIni["Allgemein"]["version"]
ci_releasedatum = configIni["Allgemein"]["releasedatum"]
ci_signoSignPfad = configIni["Allgemein"]["signosignpfad"]
ci_signoSignArchivverzeichnis = configIni["Allgemein"]["signosignarchivverzeichnis"]
ci_signoSignArchivierungsname = configIni["Allgemein"]["signosignarchivierungsname"]
ci_deleteafteropen = configIni["Allgemein"]["deleteafteropen"] == "True"
ci_backupverzeichnis = configIni["Allgemein"]["backupverzeichnis"]
ci_idSignoGdt = configIni["GDT"]["idsignogdt"]
ci_idPraxisEdv = configIni["GDT"]["idpraxisedv"]
ci_kuerzelSignoGdt = configIni["GDT"]["kuerzelsignogdt"]
ci_kuerzelPraxisEdv = configIni["GDT"]["kuerzelpraxisedv"]
ci_austauschVerzeichnis = configIni["GDT"]["austauschverzeichnis"]
ci_importDateiLoeschen = configIni["GDT"]["importdateiloeschen"] == "True"
z = configIni["GDT"]["zeichensatz"]
ci_zeichensatz = gdt.GdtZeichensatz.IBM_CP437
if z == "1":
    ci_zeichensatz = gdt.GdtZeichensatz.BIT_7
elif z == "3":
    ci_zeichensatz = gdt.GdtZeichensatz.ANSI_CP1252
ci_lanr = configIni["Erweiterungen"]["lanr"]
ci_lizenzschluessel = gdttoolsL.GdtToolsLizenzschluessel.dekrypt(configIni["Erweiterungen"]["lizenzschluessel"])
dokumenttypName = ""

# Programmstart mit Dokumenttyp als Argument?
if getDokumenttypAusArgs() != "":
    patId = getPatIdAusArgs()
    tray = QSystemTrayIcon(app)
    icon = QIcon(os.path.join(os.path.dirname(__file__), "icons/program.png"))
    tray.setIcon(icon)
    tray.show()
    if gdttoolsL.GdtToolsLizenzschluessel.lizenzErteilt(ci_lizenzschluessel, ci_lanr, gdttoolsL.SoftwareId.SIGNOGDT) or (gdttoolsL.GdtToolsLizenzschluessel.lizenzErteilt(ci_lizenzschluessel, ci_lanr, gdttoolsL.SoftwareId.SIGNOGDTPSEUDO) and patId != ""):
        gesuchterDokumenttypname = getDokumenttypAusArgs()
        if gesuchterDokumenttypname == "auswahl":
            dda = dialogDokumenttypAuswaehlen.DokumenttypAuswaehlen(updateSafePath)
            if dda.exec() == 1:
                gesuchterDokumenttypname = dda.comboBoxDokumenttypen.currentText()
            else:
                tray.hide()
                sys.exit()
        logger.logger.info("Start mit Dokumenttyp " + gesuchterDokumenttypname)
        if patId != "":
            logger.logger.info("PatId " + patId + " als Startargument übergeben")
        gdtDateiname = ci_kuerzelSignoGdt + ci_kuerzelPraxisEdv + ".gdt"
        if os.path.exists(os.path.join(updateSafePath, "config.ini")):
            # GDT-Datei von PVS laden
            gd = gdt.GdtDatei()
            try:
                gd.laden(os.path.join(ci_austauschVerzeichnis, gdtDateiname), ci_zeichensatz)
                logger.logger.info("GDT-Datei (Pat-Id: " + str(gd.getInhalt("3000")) + ") " + os.path.join(ci_austauschVerzeichnis, gdtDateiname) + " geladen")
                # Pseudolizenz-Check
                pseudoLizenzcheckOk = True
                if patId != "" and patId != gd.getInhalt("3000"):
                    pseudoLizenzcheckOk = False
                elif patId == "":
                    patId = gd.getInhalt("3000")
                if ci_importDateiLoeschen:
                    os.unlink(os.path.join(ci_austauschVerzeichnis, gdtDateiname))
                    logger.logger.info("GDT-Importdatei " + os.path.join(ci_austauschVerzeichnis, gdtDateiname) + " gelöscht")
                if pseudoLizenzcheckOk:
                    verfuegbareVariablen = {}
                    for inhalt in variablenInhalte:
                        feldkennung = inhalt[-5:-1]
                        if gd.getInhalt(feldkennung) != None:
                            verfuegbareVariablen[feldkennung] = gd.getInhalt(feldkennung)
                    dokumenttypen = class_dokumenttyp.getAlleDokumenttypen(os.path.join(updateSafePath, "dokumenttypen.xml"))
                    for dokumenttyp in dokumenttypen:
                        if dokumenttyp.name == gesuchterDokumenttypname:
                            dokumenttypName = dokumenttyp.getName()
                            logger.logger.info("Argument " + dokumenttypName + " in dokumenttypen.xml gefunden")
                            variablenErsetzt = []
                            for var in dokumenttyp.getVariablen():
                                tempVariableErsetzt = var
                                for verfuegbareVariable in verfuegbareVariablen:
                                    if verfuegbareVariable in datumsfeldkennungen:
                                        tempVariableErsetzt = tempVariableErsetzt.replace("${" + verfuegbareVariable + "}", verfuegbareVariablen[verfuegbareVariable][:2] + "." + verfuegbareVariablen[verfuegbareVariable][2:4] + "." + verfuegbareVariablen[verfuegbareVariable][4:])
                                    else:
                                        tempVariableErsetzt = tempVariableErsetzt.replace("${" + verfuegbareVariable + "}", verfuegbareVariablen[verfuegbareVariable])
                                variablenErsetzt.append(tempVariableErsetzt)
                            values = class_smlDatei.Values(dokumenttyp.name, variablenErsetzt)
                            op = class_smlDatei.Open(dokumenttyp.getDateipfade(), values)
                            openElement = op.getXml()
                            sd = class_smlDatei.SmlDatei([op.getXml()], ci_deleteafteropen)
                            try:
                                # signogdt.sml speichern
                                sd.speichern(os.path.join(updateSafePath,"signogdt.sml"))
                                logger.logger.info("signogdt.sml erfolgreich gespeichert")
                                time.sleep(2)
                                # Archivverzeichnisüberwachung starten
                                fsw = QFileSystemWatcher()
                                logger.logger.info("FileSystemWatcher instanziert")
                                if fsw.addPath(ci_signoSignArchivverzeichnis):
                                    logger.logger.info("Archivverzeichnis " + ci_signoSignArchivverzeichnis + " dem FileSystemWatcher hinzugefügt")
                                    # signoSign/2 starten
                                    try:
                                        tray.showMessage("SignoGDT", "SignoSign/2 mit Dokumenttyp " + gesuchterDokumenttypname + " wird geladen", QSystemTrayIcon.MessageIcon.Information)
                                        subprocess.run([ci_signoSignPfad, os.path.join(updateSafePath, "signogdt.sml")], check=True)
                                        dw = dialogWarten.Warten() # für manuellen Abbruch
                                        logger.logger.info("Warten-Dialog instanziert")
                                        fsw.directoryChanged.connect(lambda pfad, patId = str(patId), dw = dw, fsw = fsw: fswDirectoryChanged(pfad, patId, dw, fsw))
                                        dw.exec() # Manuell abgebrochen
                                        logger.logger.info("Über Warten-Dialog manuell abgebrochen")
                                        fsw.removePath(ci_signoSignArchivverzeichnis)
                                        logger.logger.info("Archivverzeichnis " + ci_signoSignArchivverzeichnis + " vom FileSystemWatcher entfernt")
                                    except subprocess.CalledProcessError as e:
                                        logger.logger.error("CalledProcessError beim Startversuch von signoSign: " + str(e))
                                    except Exception as e:
                                        logger.logger.error("Unbehandelter Fehler nach signoSign/2 starten: " + str(e))
                                else:
                                    logger.logger.error("Problem beim Hinzufügen des Archivverzeichnisses " + ci_signoSignArchivverzeichnis + " zum FileSystemWatcher")
                            except Exception as e:
                                logger.logger.error("Fehler beim Speichern der signogdt.sml: " + str(e)) 
                            sys.exit()
                    logger.logger.warning("Dokumenttyp " + gesuchterDokumenttypname + " als Startargument nicht gefunden")
                    sys.exit()
                else: # Pseudocheck False
                    tray.showMessage("SignoGDT", "Falsche PatId übergeben", QSystemTrayIcon.MessageIcon.Warning)
                    logger.logger.error("Mit Pseudolizenz übergebene PatId " + str(patId) + " stimmt nicht mit PatId der geladenen GDT-Datei überein")
            except Exception as e:
                tray.showMessage("SignoGDT", "Fehler beim Laden der GDT-Datei", QSystemTrayIcon.MessageIcon.Warning)
                logger.logger.error("Fehler beim Laden der GDT-Datei " + os.path.join(ci_austauschVerzeichnis, gdtDateiname) + ": " + str(e))
            sys.exit()
        else:
            tray.showMessage("SignoGDT", "config.ini nicht gefunden", QSystemTrayIcon.MessageIcon.Critical)
            logger.logger.error("config.ini exisitert nicht")
            sys.exit()
    elif gdttoolsL.GdtToolsLizenzschluessel.lizenzErteilt(ci_lizenzschluessel, ci_lanr, gdttoolsL.SoftwareId.SIGNOGDTPSEUDO) and patId == "":
        tray.showMessage("SignoGDT", "Pseudolizenz ohne PatId-Übergabe", QSystemTrayIcon.MessageIcon.Warning)
        sys.exit()
    else:
        tray.showMessage("SignoGDT", "Ungültige LANR-/ Lizenzschlüsselkombination", QSystemTrayIcon.MessageIcon.Warning)
        sys.exit()
else:
    qt = QTranslator()
    filename = "qtbase_de"
    directory = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    qt.load(filename, directory)
    app.installTranslator(qt)
    window = MainWindow()
    window.show()
    app.exec()