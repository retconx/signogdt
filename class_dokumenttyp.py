from enum import Enum
import re, os
import xml.etree.ElementTree as ElementTree

reTTMMJJJJ = r"^\d{8}$"

class DokumenttypFehlerException(Exception):
    def __init__(self, meldung):
        self.Meldung = meldung
    def __str__(self):
        return "Dokumenttyp-Fehler: " + self.Meldung

class Dokumenttyp:
    def __init__(self, name:str, gdtid:str, dateipfade:list, variablen:list):
        self.name = name
        self.gdtid = gdtid
        self.dateipfade = dateipfade
        self.variablen = variablen

    def getXml(self):
        dokumenttypElement = ElementTree.Element("dokumenttyp")
        dokumenttypElement.set("name", self.name)
        dokumenttypElement.set("gdtid", self.gdtid)
        dateipfadeElement = ElementTree.Element("dateipfade")
        for dateipfad in self.dateipfade:
            if dateipfad != "":
                dateipfadElement = ElementTree.Element("dateipfad")
                dateipfadElement.text = dateipfad
                dateipfadeElement.append(dateipfadElement)
        dokumenttypElement.append(dateipfadeElement)
        variablenElement = ElementTree.Element("variablen")
        for variable in self.variablen:
            variableElement = ElementTree.Element("variable")
            variableElement.text = variable
            variablenElement.append(variableElement)
        dokumenttypElement.append(variablenElement)
        return dokumenttypElement

    def getName(self):
        """
        Gibt den Namen des Dokumenttyps zurück
        Return:
            Name:str
        """
        return self.name
    
    def getGdtId(self):
        """
        Gibt die GDT-ID des Dokumenttyps zurück
        Return:
            gdtid:str
        """
        return self.gdtid
    
    def getDateipfade(self):
        """
        Gib eine Liste der Dateipfade zurück
        Return:
            Dateipfade:String-Liste
        """
        return self.dateipfade
    
    def getVariablen(self):
        """
        Gib eine Liste der Variablen zurück
        Return:
            Variablen:Variable-Liste
        """
        return self.variablen
@staticmethod
def getAlleDokumenttypen(pfad:str):
    """
    Gibt alle Dokumenttypen der dokumenttypen.xml zurück
    Parameter:
        pfad:str Pfad zur dokumenttypen.xml
    Rückgabe:
        Dokumenttypen: Dokumenttyp-Liste
    """
    dokumenttypen = []
    dateipfade = []
    variablen = []
    if os.path.exists(pfad):
        tree = ElementTree.parse(pfad)
        dokumenttypenRoot = tree.getroot()
        for dokumenttypElement in dokumenttypenRoot:
            name = str(dokumenttypElement.get("name"))
            gdtid = str(dokumenttypElement.get("gdtid"))
            dateipfade.clear()
            dateipfadeElement = dokumenttypElement.find("dateipfade")
            for dateipfadElement in dateipfadeElement.findall("dateipfad"): # type: ignore
                inhalt = str(dateipfadElement.text)
                if inhalt == "None":
                    inhalt = ""
                dateipfade.append(inhalt)
            variablen.clear()
            variablenElement = dokumenttypElement.find("variablen")
            for variableElement in variablenElement.findall("variable"): # type: ignore
                inhalt = str(variableElement.text)
                if inhalt == "None":
                    inhalt = ""
                variablen.append(inhalt)
            dokumenttypen.append(Dokumenttyp(name, gdtid, dateipfade.copy(), variablen.copy()))
        return dokumenttypen
    else:
        raise DokumenttypFehlerException(pfad + " existiert nicht")