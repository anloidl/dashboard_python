Voraussetzungen: 
- Python 3.9 oder höher
- Alle verwendeten Module sind aus der Python-Standardbibliothek. Es ist keine zusätzliche Installation von Modulen erforderlich.

Github-Link:
https://github.com/anloidl/dashboard_python

Start des Dashboards:
- Variante A - Starten über Terminal: "python main.py"
- Variante B - Starten über JupyterLab: Datei main.ipynb ausführen

Projektstruktur:
- main.py bzw. main.ipynb: Start-Skript mit main()
- business/: Enthält die Geschäftslogik (Entities und DashboardService)
- gui/: Enthält die GUI-Komponenten
- data/: Enthält die Datenverwaltung (speichern und laden aus den csv-Dateien)
- resources/: Enthält die csv-Dateien

Ablauf:
- Beim ersten Start wird die Initialisierungslogik durchlaufen und es werden Studenten, Module, Studiengang usw. erzeugt
- Diese Objekte werden anschließend in den csv-Dateien gespeichert
- Alle Änderungen die in Folge übers Dashboard vorgenommen werden, werden in den csv-Dateien gespeichert

Funktionen des Dashboards:
- Anlegen neuer Module
- Noten zu Modulen eintragen
- Status von Modulen ändern
- Tracken der Lernzeit
- Semesterauswahl
- Zielverfolgung: ECTS gesamt, ECTS im ausgewählten Semester, Aktive Lernzeit, Notendurchschnitt
