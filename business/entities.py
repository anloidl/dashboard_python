from datetime import date
from enum import Enum

class Status(Enum):
    GEPLANT = "geplant"
    AKTIV = "aktiv"
    ABGESCHLOSSEN = "abgeschlossen"

class ModulStatus(Enum):
    OFFEN = "offen"
    AKTIV = "aktiv"
    ABGESCHLOSSEN = "abgeschlossen"

class Zieltyp(Enum):
    ECTS_GESAMT = "Erreichte ECTS Punkte gesamt"
    ECTS_SEMESTER = "Erreichte ECTS Punkte Semester"
    NOTENSCHNITT = "Notendurchschnitt"
    LERNZEIT = "Anzahl der Lernstunden"


class Einschreibung:
    """Repräsentiert die Einschreibung eines Studenten."""
    def __init__(self, matrikelnummer: str, status: Enum, einschreibungsdatum=date(2025,1,1), geplanter_abschluss=date(2025,1,1)):
        self.__matrikelnummer = matrikelnummer
        self.__status = status
        self.__einschreibungsdatum = date(2025,3,17)
        self.__geplanter_abschluss = date(2028,3,17)

    @property
    def matrikelnummer(self): return self.__matrikelnummer
    @property
    def status(self): return self.__status
    @property
    def einschreibungsdatum(self): return self.__einschreibungsdatum
    @property
    def geplanter_abschluss(self): return self.__geplanter_abschluss

    @status.setter
    def status(self, value: Status): self.__status = value

    def to_dict(self):
        return {
            "matrikelnummer" : self.__matrikelnummer,
            "status" : self.__status.value if self.__status else None,   # Enum als String
            "einschreibungsdatum" : self.__einschreibungsdatum.isoformat() if self.__einschreibungsdatum else None,
            "geplanter_abschluss" : self.__geplanter_abschluss.isoformat() if self.__geplanter_abschluss else None,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            matrikelnummer = data.get("matrikelnummer"),
            status = Status(data.get("status")) if data.get("status") else None,
            einschreibungsdatum = date.fromisoformat(data["einschreibungsdatum"]) if data.get("einschreibungsdatum") else None,
            geplanter_abschluss = date.fromisoformat(data["geplanter_abschluss"]) if data.get("geplanter_abschluss") else None,
        )


class Pruefungsleistung:
    """Repräsentiert eine Prüfungsleistung in einem Modul."""
    def __init__(self, leistung_id: str, note: float, datum: date=date(2025,1,1), versuch: int=0, modul_id: str=""):
        self.__leistung_id = leistung_id
        self.__note = note
        self.__datum = datum
        self.__versuch = versuch
        self.__modul_id = modul_id

    @property
    def leistung_id(self): return self.__leistung_id
    @property
    def note(self): return self.__note
    @property
    def datum(self): return self.__datum
    @property
    def versuch(self): return self.__versuch
    @property
    def modul_id(self): return self.__modul_id

    @note.setter
    def note(self, value: float): self.__note = value

    @datum.setter
    def datum(self, value: date): self.__datum = value

    @versuch.setter
    def versuch(self, value: int): self.__versuch = value

    

    def to_dict(self):
        return {
            "leistung_id" : self.__leistung_id,
            "note" : self.__note,
            "datum" : self.__datum.isoformat() if self.__datum else None,
            "versuch" : self.__versuch,
            "modul_id" : self.__modul_id
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            leistung_id = data.get("leistung_id"),
            note = data.get("note"),
            datum = date.fromisoformat(data["datum"]) if data.get("datum") else None,
            versuch = data.get("versuch"),
            modul_id = data.get("modul_id"),
        )


class Modul:
    """Repräsentiert ein Studienmodul."""
    def __init__(self, modul_id: str, titel: str, ects_punkte: int, status: ModulStatus = ModulStatus.OFFEN, pruefungsleistungen: list=None):
        self.__modul_id = modul_id
        self.__titel = titel
        self.__ects_punkte = ects_punkte
        self.__status = status
        self.__pruefungsleistungen = pruefungsleistungen if pruefungsleistungen else []

    @property
    def modul_id(self): return self.__modul_id
    @property
    def titel(self): return self.__titel
    @property
    def ects_punkte(self): return self.__ects_punkte
    @property
    def status(self): return self.__status
    @property
    def pruefungsleistungen(self): return self.__pruefungsleistungen

    @status.setter
    def status(self, value: ModulStatus): self.__status = value

    def to_dict(self):
        return {
            "modul_id" : self.__modul_id,
            "titel" : self.__titel,
            "ects_punkte" : self.__ects_punkte,
            "status" : self.__status.value if self.__status else None,   # Enum als String
            "pruefungsleistungen" : [pl.to_dict() if hasattr(pl, "to_dict") else pl for pl in self.__pruefungsleistungen]
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            modul_id = data.get("modul_id"),
            titel = data.get("titel"),
            ects_punkte = data.get("ects_punkte"),
            status = ModulStatus(data.get("status")) if data.get("status") else None,  # String → Enum,
            pruefungsleistungen=[Pruefungsleistung.from_dict(pl) for pl in data.get("pruefungsleistungen", [])]
        )

    def add_pruefungsleistung(self, leistung: Pruefungsleistung):
        self.__pruefungsleistungen.append(leistung)


class Student:
    """Repräsentiert einen Studenten."""
    def __init__(self, student_id: str, name: str, email: str, geburtsdatum: date, lernzeiten={}, studiengang=None, einschreibung=None):
        self.__student_id = student_id
        self.__name = name
        self.__email = email
        self.__geburtsdatum = geburtsdatum
        self.__lernzeiten = lernzeiten
        self.__studiengang = studiengang
        self.__einschreibung = einschreibung

    @property
    def student_id(self): return self.__student_id
    @property
    def name(self): return self.__name
    @property
    def email(self): return self.__email
    @property
    def geburtsdatum(self): return self.__geburtsdatum
    @property
    def lernzeiten(self): return self.__lernzeiten
    @property
    def studiengang(self): return self.__studiengang
    @property
    def einschreibung(self): return self.__einschreibung

    @lernzeiten.setter
    def lernzeiten(self, value): self.__lernzeiten = value

    @studiengang.setter
    def studiengang(self, value): self.__studiengang = value

    @einschreibung.setter
    def einschreibung(self, value): self.__einschreibung = value

    def to_dict(self):
        return {
            "student_id" : self.__student_id,
            "name" : self.__name,
            "email" : self.__email,
            "geburtsdatum" : self.__geburtsdatum.isoformat() if self.__geburtsdatum else None,
            "lernzeiten" : self.__lernzeiten,
            "studiengang" : self.__studiengang.to_dict() if self.__studiengang else None,
            "einschreibung" : self.__einschreibung.to_dict() if self.__einschreibung else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            student_id = data.get("student_id"),
            name = data.get("name"),
            email = data.get("email"),
            geburtsdatum = date.fromisoformat(data["geburtsdatum"]) if data.get("geburtsdatum") else None,
            lernzeiten = data.get("lernzeiten"),
            studiengang = Studiengang.from_dict(data["studiengang"]) if data.get("studiengang") else None,
            einschreibung = Einschreibung.from_dict(data["einschreibung"]) if data.get("einschreibung") else None,
        )

    def immatrikulieren(self, studiengang):
        self.__studiengang = studiengang
        self.__einschreibung = Einschreibung("14128675", Status.AKTIV)


class Studiengang:
    """Repräsentiert einen Studiengang."""
    def __init__(self, studiengang_id: str, titel: str, dauer: int, ects_gesamt: int, semester_liste: list = None):
        self.__studiengang_id = studiengang_id
        self.__titel = titel
        self.__dauer = dauer # Anzahl der Semester
        self.__ects_gesamt = ects_gesamt
        self.__semester_liste = semester_liste if semester_liste else []

    @property
    def studiengang_id(self): return self.__studiengang_id
    @property
    def titel(self): return self.__titel
    @property
    def dauer(self): return self.__dauer
    @property
    def ects_gesamt(self): return self.__ects_gesamt
    @property
    def semester_liste(self): return self.__semester_liste

    @semester_liste.setter
    def semester_liste(self, value): self.__semester_liste = value

    def to_dict(self):
        return {
            "studiengang_id" : self.__studiengang_id,
            "titel" : self.__titel,
            "dauer" : self.__dauer,
            "ects_gesamt" : self.__ects_gesamt,
            "semester_liste" : [sem.to_dict() if hasattr(sem, "to_dict") else sem for sem in self.__semester_liste]
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            studiengang_id = data.get("studiengang_id"),
            titel = data.get("titel"),
            dauer = data.get("dauer"),
            ects_gesamt = data.get("ects_gesamt"),
            semester_liste = [Semester.from_dict(sem) for sem in data.get("semester_liste", [])]
        )

    def get_module_semester(self, semester_nummer: int) -> list[Modul]:
        """Gibt die Module für das angegebene Semester zurück."""
        for sem in self.__semester_liste:
            if sem.nummer == semester_nummer:
                return sem.module
        return []


class Semester:
    """Repräsentiert ein Semester innerhalb eines Studiengangs."""
    def __init__(self, semester_id: str, nummer: int, module: list):
        self.__semester_id = semester_id
        self.__nummer = nummer
        self.__module = module if module else []

    @property
    def semester_id(self): return self.__semester_id
    @property
    def nummer(self): return self.__nummer
    @property
    def module(self): return self.__module

    def to_dict(self):
        return {
            "semester_id" : self.__semester_id,
            "nummer" : self.__nummer,
            "module" : [m.to_dict() if hasattr(m, "to_dict") else m for m in self.__module]
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            semester_id = data.get("semester_id"),
            nummer = data.get("nummer"),
            module = [Modul.from_dict(m) for m in data.get("module", [])]
        )


class Studienziel:
    """Definiert das Studienziel eines Studenten."""
    def __init__(self, ziel_id: str, typ: Enum, ziel_wert: float, aktueller_wert: float, status: bool):
        self.__ziel_id = ziel_id
        self.__typ = typ
        self.__ziel_wert = ziel_wert
        self.__aktueller_wert = aktueller_wert
        self.__status = False

    @property
    def ziel_id(self): return self.__ziel_id
    @property
    def typ(self): return self.__typ
    @property
    def ziel_wert(self): return self.__ziel_wert
    @property
    def aktueller_wert(self): return self.__aktueller_wert
    @property
    def status(self): return self.__status

    @aktueller_wert.setter
    def aktueller_wert(self, wert: float):
        self.__aktueller_wert = wert

    @status.setter
    def status(self, wert: bool):
        self.__status = wert

    def to_dict(self):
        return {
            "ziel_id" : self.__ziel_id,
            "typ" : self.__typ.value if self.__typ else None,   # Enum als String
            "ziel_wert" : self.__ziel_wert,
            "aktueller_wert" : self.__aktueller_wert,
            "status" : self.__status
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            ziel_id = data.get("ziel_id"),
            typ = Zieltyp(data.get("typ")) if data.get("typ") else None,  # String → Enum
            ziel_wert = data.get("ziel_wert"),
            aktueller_wert = data.get("aktueller_wert"),
            status = data.get("status")
        )
        