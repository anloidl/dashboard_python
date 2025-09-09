from business.entities import Student, Studiengang, Status, Studienziel, Zieltyp, Modul, ModulStatus, Pruefungsleistung, Semester
from data.daten_verwaltung import DatenVerwaltung
from datetime import date
import json

class DashboardService:
    """Koordiniert die Geschäftslogik zwischen GUI und Datenverwaltung."""
    def __init__(self):
        self.__dv = DatenVerwaltung()
        self.__student_data = self.__dv.lade("student", Student)[0]
        self.__studienziele = self.__dv.lade("studienziele", Studienziel)
        self.__module = [m for sem in self.__student_data.studiengang.semester_liste for m in sem.module]

    def get_student_daten(self) -> Student:
        """Gibt das Student-Objekt zurück."""
        return self.__student_data

    def get_studienziele(self) -> list[Studienziel]:
        """Gibt die Studienziele zurück"""
        return self.__studienziele

    def get_module(self) -> list[Modul]:
        """Gibt alle Module aus allen Semestern zurück (flach)"""
        alle_module = []
        for semester in self.__student_data.studiengang.semester_liste:
            alle_module.extend(semester.module)
        return alle_module

    def erstelle_neues_modul(self, modul_id: str, titel: str, ects_punkte: int) -> list[Modul]:
        """Erstellt ein neues Modul und speichert es in CSV."""
        neues_modul = Modul(modul_id, titel, ects_punkte)
        # Neues Modul anlegen (aktuell wird jedes neue Modul immer im ersten Semester angelegt)
        self.__student_data.studiengang.semester_liste[0].module.append(neues_modul)
        # Flache Liste aktualisieren
        self.__module = [m for sem in self.__student_data.studiengang.semester_liste for m in sem.module]
        self.__dv.speichere("student", [self.__student_data])
        return self.__module

    def get_module_semester(self, semester_nummer: int) -> list[Modul]:
        """Gibt die Module des angegebenen Semesters an die GUI zurück"""
        return self.__student_data.studiengang.get_module_semester(semester_nummer)

    def get_modul_status_optionen(self) -> list[str]:
        """Gibt alle Modulstatus als Strings an die GUI zurück"""
        return [status.name.lower() for status in ModulStatus]

    def get_module_status_aktiv(self) -> list[Modul]:
        """Gibt alle Module die nicht den Status 'offen' besitzen zurück"""
        return [m for m in self.get_module() if m.status != ModulStatus.OFFEN]
    
    def aendere_modul_status(self, modul_id: str, neuer_status: str) -> list[Modul]:
        """Ändert den Status eines Moduls und speichert diesen in CSV."""
        modul = None
        for semester in self.__student_data.studiengang.semester_liste:
            modul = next((m for m in semester.module if m.modul_id == modul_id), None)
            if modul:
                modul.status = ModulStatus(neuer_status)
                break
        if not modul:
            raise ValueError(f"Kein Modul mit ID '{modul_id}' gefunden!")    
        # Flache Liste aktualisieren
        self.__module = [m for sem in self.__student_data.studiengang.semester_liste for m in sem.module]
        self.__dv.speichere("student", [self.__student_data])
        return self.__module

    def erstelle_pruefungsleistung(self, leistung_id: str, note: float, datum: date, versuch: int, modul_id: str) -> list[Modul]:
        """Erstellt eine neue Prüfungsleistung und speichert diese in CSV."""
        neue_leistung = Pruefungsleistung(leistung_id, note, datum, versuch, modul_id)
        modul = None
        for semester in self.__student_data.studiengang.semester_liste:
            modul = next((m for m in semester.module if m.modul_id == modul_id), None)
            if modul:
                modul.add_pruefungsleistung(neue_leistung)
                break  
        if not modul:
            raise ValueError(f"Kein Modul mit ID '{modul_id}' gefunden!")    
        # Flache Liste aktualisieren
        self.__module = [m for sem in self.__student_data.studiengang.semester_liste for m in sem.module]
        # Student speichern
        self.__dv.speichere("student", [self.__student_data])
        return self.__module

    def berechne_durchschnittsnote(self) -> float:
        """Berechnet die Durchschnittsnote aller aktiven und abgeschlossenen Module.
        Liefert None, wenn keine Noten vorhanden sind."""
        noten = []
        # Flache Liste aktualisieren
        self.__module = [m for sem in self.__student_data.studiengang.semester_liste for m in sem.module]
        for modul in self.__module:
            if modul.status != ModulStatus.OFFEN and modul.pruefungsleistungen:
                # letzte Prüfungsleistung
                letzte_leistung = modul.pruefungsleistungen[-1]
                if letzte_leistung.note is not None:
                    noten.append(letzte_leistung.note)  
        if not noten:
            return 0.0   
        return round(sum(noten) / len(noten), 2)

    def berechne_studienfortschritt(self, semester_id: str = None) -> int:
        """Berechnet die Summe der ECTS-Punkte aller aktiven und abgeschlossenen Module.
        Liefert 0, wenn keine Module abgeschlossen sind."""
        ects_summe = 0
        for semester in self.__student_data.studiengang.semester_liste:
            if semester_id is None or str(semester.semester_id) == str(semester_id):
                for modul in semester.module:
                    if modul.status == ModulStatus.ABGESCHLOSSEN:
                        ects_summe += modul.ects_punkte
        return ects_summe

    def berechne_studienfortschritt_semester(self, semester_id: str) -> int:
        """Berechnet die Summe der ECTS-Punkte eines bestimmten Semesters."""
        ects_summe = 0
        for semester in self.__student_data.studiengang.semester_liste:
            if str(semester.semester_id) == str(semester_id):
                for modul in semester.module:
                    if modul.status == ModulStatus.ABGESCHLOSSEN:
                        ects_summe += modul.ects_punkte
        return ects_summe

    def berechne_lernzeit_aktuelle_woche(self) -> int:
        """Summiert die Lernzeiten des Studenten in Stunden für die aktuelle Kalenderwoche.
        Gibt 0 zurück, wenn keine Lernzeiten vorhanden sind."""
        student = self.__student_data
        # Lernzeiten aus JSON laden
        lernzeiten = json.loads(student.lernzeiten) if isinstance(student.lernzeiten, str) else student.lernzeiten
        lernzeiten = lernzeiten or {}
        # Aktuelle Kalenderwoche ermitteln
        aktuelle_kw = f"KW {date.today().isocalendar()[1]}"
        # Stunden aufsummieren
        return sum(lernzeiten.get(aktuelle_kw, []))

    def buche_lernzeit(self, kw: str, minuten: int) -> Student:
        """Fügt dem Studenten eine Lernzeit hinzu und speichert sie in CSV"""
        if not hasattr(self.__student_data, "lernzeiten") or self.__student_data.lernzeiten is None:
            self.__student_data.lernzeiten = {}
        elif isinstance(self.__student_data.lernzeiten, str):
            self.__student_data.lernzeiten = json.loads(self.__student_data.lernzeiten)
        if kw not in self.__student_data.lernzeiten:
            self.__student_data.lernzeiten[kw] = []
        self.__student_data.lernzeiten[kw].append(minuten)
        # nur für die Speicherung konvertieren
        daten = self.__student_data
        daten.lernzeiten = json.dumps(self.__student_data.lernzeiten)
        # Student mit neuen Daten abspeichern
        self.__dv.speichere("student", [daten])
        return self.__student_data

    def aktualisiere_studienziele(self, aktuelles_semester: str = None):
        """Berechnet die aktuellen Werte und setzt den Status der Ziele"""
        for ziel in self.__studienziele:
            if ziel.typ == Zieltyp.ECTS_GESAMT: 
                ziel.aktueller_wert = self.berechne_studienfortschritt()
                ziel.status = ziel.aktueller_wert >= ziel.ziel_wert
            elif ziel.typ == Zieltyp.ECTS_SEMESTER: 
                ziel.aktueller_wert = self.berechne_studienfortschritt_semester(aktuelles_semester)
                ziel.status = ziel.aktueller_wert >= ziel.ziel_wert
            elif ziel.typ == Zieltyp.LERNZEIT:
                ziel.aktueller_wert = self.berechne_lernzeit_aktuelle_woche()
                ziel.status = ziel.aktueller_wert >= ziel.ziel_wert
            elif ziel.typ == Zieltyp.NOTENSCHNITT:
                ziel.aktueller_wert = self.berechne_durchschnittsnote()
                ziel.status = ziel.aktueller_wert <= ziel.ziel_wert
        return self.__studienziele
        
