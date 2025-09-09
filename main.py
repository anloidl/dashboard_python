import tkinter as tk
from datetime import date
import json
import os

from gui.dashboard_gui import StudentDashboard
from business.entities import Student, Studiengang, Semester, Studienziel, Zieltyp, Modul, ModulStatus
from business.dashboard_service import DashboardService
from data.daten_verwaltung import DatenVerwaltung

def csv_existieren(*filenamen) -> bool:
    """Prüft, ob alle angegebenen CSV-Dateien existieren."""
    return all(os.path.exists(f"resources/{name}.csv") for name in filenamen)


def main():
    dv = DatenVerwaltung()

    # Dateien, die geprüft werden sollen
    erforderliche_dateien = ["module", "semester", "studiengang", "student", "studienziele"]

    if not csv_existieren(*erforderliche_dateien):
        # Initialisierung nur beim ersten Start
        # Module speichern
        modul_mathematik = Modul("Modul_1", "Mathematik für KI", 5, ModulStatus.AKTIV)
        modul_python = Modul("Modul_2", "Programmieren in Python", 5, ModulStatus.ABGESCHLOSSEN)
        modul_machine_learning = Modul("Modul_3", "Machine Learning Grundlagen", 5, ModulStatus.OFFEN)
        modul_datenstrukturen = Modul("Modul_4", "Datenstrukturen & Algorithmen", 5, ModulStatus.OFFEN)
        modul_statistik = Modul("Modul_5", "Statistik für Data Science", 5, ModulStatus.OFFEN)
        modul_deep_learning = Modul("Modul_6", "Deep Learning", 5, ModulStatus.OFFEN)
        dv.speichere("module", [modul_mathematik, modul_python, modul_machine_learning, modul_datenstrukturen, 
                                modul_statistik, modul_deep_learning])

        # Semester anlegen
        semester_1 = Semester("2025SS", 1, [modul_mathematik, modul_python])
        semester_2 = Semester("2025WS", 2, [modul_machine_learning, modul_datenstrukturen])
        semester_3 = Semester("2026SS", 3, [modul_statistik, modul_deep_learning])
    
        dv.speichere("semester", [semester_1, semester_2, semester_3])
    
        # Studenten anlegen und in Studiengang immatrikulieren
        student = Student("1", "Andreas Loidl", "andreas.loidl@gmail.com", date(1981,8,13), json.dumps({"KW 35": [2, 1]}))
        studiengang = Studiengang("AI_1", "Angewandte Künstliche Intelligenz", 6, 180, [semester_1, semester_2, semester_3])
        student.immatrikulieren(studiengang)
        dv.speichere("studiengang", [studiengang])
        dv.speichere("student", [student])

        # Studienziele speichern
        studienziel_ects_gesamt = Studienziel("Ziel_ECTS_Gesamt", Zieltyp.ECTS_GESAMT, 180.0, 0.0, False)
        studienziel_ects_semester = Studienziel("Ziel_ECTS_Semester", Zieltyp.ECTS_SEMESTER, 30.0, 0.0, False)
        studienziel_notenschnitt = Studienziel("Ziel_Notenschnitt", Zieltyp.NOTENSCHNITT, 2.0, 5.0, False)
        studienziel_lernstunden = Studienziel("Ziel_Lernstunden", Zieltyp.LERNZEIT, 4.0, 0.0, False)
        dv.speichere("studienziele", [studienziel_ects_gesamt, studienziel_ects_semester,
                                                      studienziel_notenschnitt, studienziel_lernstunden])


    ds = DashboardService()
    
    # Dashboard starten
    root = tk.Tk()
    app = StudentDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()