import xml.etree.ElementTree as ElementTree
import os, sys

basedir = os.path.dirname(__file__)

class SmlFehlerException(Exception):
    def __init__(self, meldung):
        self.meldung = meldung
    def __str__(self):
        return "SML-Fehler: " + self.meldung
    
class Values:
    def __init__(self, docType:str, variablenListe:list):
        self.docType = docType
        self.variablenListe = variablenListe

class Open:
    def __init__(self, filenameListe:list, values:Values):
        self.filenameListe = filenameListe
        self.values = values

        self.openElement = ElementTree.Element("Open")
        for filename in self.filenameListe:
            fileElement = ElementTree.Element("File")
            fileElement.text = filename
            self.openElement.append(fileElement)
        valuesElement = ElementTree.Element("Values")
        docTypeElement = ElementTree.Element("DocType")
        docTypeElement.text = values.docType
        valuesElement.append(docTypeElement)
        variablennummer = 1
        for variable in values.variablenListe:
            variableElement = ElementTree.Element("Variable" + str(variablennummer))
            variableElement.text = variable 
            valuesElement.append(variableElement)
            variablennummer += 1
        self.openElement.append(valuesElement)
    
    def getXml(self):
        return self.openElement

class SmlDatei:
    def __init__(self, openElementListe:list, deleteAfterOpen:bool):
        self.openElementListe = openElementListe
        self.deleteAfterOpen = deleteAfterOpen

        self.signotecElement = ElementTree.Element("signotec")
        for openelement in self.openElementListe:
            self.signotecElement.append(openelement)
        daoElement = ElementTree.Element("DeleteAfterOpen")
        daoElement.text = str(deleteAfterOpen)
        self.signotecElement.append(daoElement)
    
    def speichern(self, dateipfad:str):
        if dateipfad[-4:].lower() == ".sml":
            et = ElementTree.ElementTree(self.signotecElement)
            ElementTree.indent(et)
            try:
                et.write(dateipfad, "utf-8", True)
            except Exception as e:
                raise SmlFehlerException("Fehler beim Speichern der SML-Datei: " + str(e))
        else:
            raise SmlFehlerException("Dateiname endet nicht auf \".sml\"")