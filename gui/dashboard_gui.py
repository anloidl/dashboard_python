import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import re
from business.dashboard_service import DashboardService

class StudentDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Studenten-Dashboard - Angewandte KI")
        self.root.geometry("800x800")
        self.root.configure(bg='#f5f5f5')
        self.__selected_semester = tk.StringVar()
        self.__selected_semester.set("Kein Semester gewählt - alle Module werden angezeigt")
        self.__ds = DashboardService()
        self.__student_data = self.__ds.get_student_daten()
        self.__studienziele = self.__ds.get_studienziele()
        self.__create_styles()
        self.__create_widgets()

    def __create_styles(self):
        """Konfiguriert die ttk-Stile"""
        self.__style = ttk.Style()
        # Konfiguriere Main Frame Style
        self.__style.configure('Card.TFrame', background='white', relief='flat', borderwidth=1)
        # Konfiguriere Button Style
        self.__style.configure('Primary.TButton', background='#007bff', foreground='white', padding=(12, 6))
        # Konfiguriere Treeview Style
        self.__style.configure("Custom.Treeview", background="white", foreground="#495057", 
                               fieldbackground="white", borderwidth=0, rowheight=25)
        self.__style.configure("Custom.Treeview.Heading", background="#f8f9fa", foreground="#495057", font=('Arial', 9, 'bold'))
    
    def __create_widgets(self):
        """Erstellt alle Dashboard Widgets"""
        # Main Container mit Scrollbar
        canvas = tk.Canvas(self.root, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.__scrollable_frame = ttk.Frame(canvas)
        
        self.__scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.__scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack Canvas und Scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind Mousewheel to Canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Container mit Padding
        container = ttk.Frame(self.__scrollable_frame, padding="20")
        container.pack(fill="both", expand=True)
        
        self.__create_header_section(container)
        self.__create_goals_section(container)
        self.__create_modules_section(container)
    
    def __create_header_section(self, parent):
        """Erstellt die Sektion für die allgemeinen Daten"""
        # Sektion Title
        title_label = tk.Label(parent, text="Allgemeine Daten", font=('Arial', 14, 'bold'), bg='#f5f5f5', fg='#333')
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Header Frame
        header_frame = tk.Frame(parent, bg='white', relief='flat', bd=1)
        header_frame.pack(fill="x", pady=(0, 20))
        
        header_content = tk.Frame(header_frame, bg='white')
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Student Info Grid
        info_frame = tk.Frame(header_content, bg='white')
        info_frame.pack(fill="x")
        
        # Linke Spalte - Studenten Details
        left_frame = tk.Frame(info_frame, bg='white')
        left_frame.pack(side="left", fill="both", expand=True)
        
        name_label = tk.Label(left_frame, text=f"Name: {self.__student_data.name}", 
                             font=('Arial', 10), bg='white', fg='#333', anchor="w")
        name_label.pack(anchor="w", pady=2)
        
        matrikel_label = tk.Label(left_frame, text=f"Matrikelnummer: {self.__student_data.studiengang.titel}", 
                                 font=('Arial', 10), bg='white', fg='#333', anchor="w")
        matrikel_label = tk.Label(left_frame, text=f"Matrikelnummer: {self.__student_data.einschreibung.matrikelnummer}", 
                                 font=('Arial', 10), bg='white', fg='#333', anchor="w")
        matrikel_label.pack(anchor="w", pady=2)
        
        # Rechte Spalte - Studien Info
        right_frame = tk.Frame(info_frame, bg='white')
        right_frame.pack(side="right", fill="both", expand=True)
        
        studiengang_label = tk.Label(right_frame, text=f"Studiengang: {self.__student_data.studiengang.titel}", 
                                    font=('Arial', 10), bg='white', fg='#333', anchor="e")
        studiengang_label.pack(anchor="e", pady=2)
        
        beginn_label = tk.Label(right_frame, text=f"Studienbeginn: {self.__student_data.einschreibung.einschreibungsdatum}", 
                               font=('Arial', 10), bg='white', fg='#333', anchor="e")
        beginn_label.pack(anchor="e", pady=2)
        
        abschluss_label = tk.Label(right_frame, text=f"Geplanter Abschluss: {self.__student_data.einschreibung.geplanter_abschluss}", 
                                  font=('Arial', 10), bg='white', fg='#333', anchor="e")
        abschluss_label.pack(anchor="e", pady=2)
    
    def __create_goals_section(self, parent):
        """Erstellt die Ziele-Sektion"""
        # Sektion Title
        title_label = tk.Label(parent, text="Ziele", font=('Arial', 14, 'bold'), bg='#f5f5f5', fg='#333')
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Ziele Container
        goals_container = tk.Frame(parent, bg='#f5f5f5')
        goals_container.pack(fill="x", pady=(0, 20))
        
        # Ziel 1: ECTS Studienfortschritt gesamt
        self.__label_ects_gesamt = self.__create_goal_card(goals_container, "ECTS-Punkte gesamt:", "", "green")
        # Ziel 2: ECTS Studienfortschritt im ausgewählten Semester
        self.__label_ects_semester = self.__create_goal_card(goals_container, f"ECTS-Punkte im ausgewählten Semester:", "", "green")
        # Ziel 3: Lernzeit mit Button zum Tracken
        self.__label_lernzeit = self.__create_goal_card(goals_container, "Aktive Lernzeit in dieser Woche:", "", "red")    
        track_button = self.__create_button(self.__label_lernzeit.master, "Lernzeit tracken", self.__zeige_dialog_lernzeit_tracken, "#007bff")
        track_button.pack(side="left", padx=(15, 0))
        # Ziel 4: Durchschnittsnote
        self.__label_note = self.__create_goal_card(goals_container, "Notendurchschnitt:", "","red")
        
        # Initial befüllen
        self.__update_goals_section()
    
    def __create_goal_card(self, parent, title, value, color_type):
        """Erstellt den Bereich für ein Ziel"""
        card_frame = tk.Frame(parent, bg='white', relief='flat', bd=1)
        card_frame.pack(fill="x", pady=4)
        
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Frame für horizontale Anordnung
        row_frame = tk.Frame(content_frame, bg='white')
        row_frame.pack(fill="x")
        
        title_label = tk.Label(row_frame, text=title, font=('Arial', 9, 'bold'), bg='white', fg='#2c3e50', anchor="w")
        title_label.pack(side="left")
        
        color = "#28a745" if color_type == "green" else "#dc3545"
        value_label = tk.Label(row_frame, text=value, font=('Arial', 9, 'bold'), bg='white', fg=color, anchor="w")
        value_label.pack(side="left", padx=(10,0)) # Abstand zwischen Label und Wert
        
        return value_label

    def __update_goals_section(self):
        """Aktualisiert die Ziel-Labels mit aktuellen Werten"""
        studienziele = self.__ds.aktualisiere_studienziele(self.__selected_semester.get())
        # Zieltypen
        for ziel in studienziele:
            if ziel.typ.value == "Erreichte ECTS Punkte gesamt":
                self.__label_ects_gesamt.config(
                    text=f"{ziel.aktueller_wert} / {int(ziel.ziel_wert)} ECTS "
                         f"({int(ziel.aktueller_wert / ziel.ziel_wert * 100)}%)",
                    fg="#28a745" if ziel.status else "#dc3545"
                )
            elif ziel.typ.value == "Erreichte ECTS Punkte Semester":
                self.__label_ects_semester.config(
                    text=f"{ziel.aktueller_wert} / {int(ziel.ziel_wert)} ECTS "
                         f"({int(ziel.aktueller_wert / ziel.ziel_wert * 100)}%)",
                    fg="#28a745" if ziel.status else "#dc3545"
                )
            elif ziel.typ.value == "Anzahl der Lernstunden":
                self.__label_lernzeit.config(
                    text=f"{ziel.aktueller_wert} / {ziel.ziel_wert} Stunden "
                         f"({int(ziel.aktueller_wert / ziel.ziel_wert * 100)}%)",
                    fg="#28a745" if ziel.status else "#dc3545"
                )
            elif ziel.typ.value == "Notendurchschnitt":
                self.__label_note.config(
                    text=f"{ziel.aktueller_wert} / {ziel.ziel_wert}",
                    fg="#28a745" if ziel.status else "#dc3545"
                )
    
    def __create_modules_section(self, parent):
        """Erstellt die Module-Sektion"""
        # Sektion title
        title_label = tk.Label(parent, text="Module", font=('Arial', 14, 'bold'), bg='#f5f5f5', fg='#333')
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Module Frame
        module_frame = tk.Frame(parent, bg='white', relief='flat', bd=1)
        module_frame.pack(fill="both", expand=True)
        module_content = tk.Frame(module_frame, bg='white')
        module_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Buttons für neues Modul, Note anlegen und Status ändern
        button_frame = tk.Frame(module_content, bg='white')
        button_frame.pack(fill="x", pady=(0, 15))

        btn1 = self.__create_button(button_frame, "Semester auswählen", self.__waehle_semester, "#007bff")
        btn1.pack(side="left", padx=(0, 10))
        
        btn2 = self.__create_button(button_frame, "Neues Modul anlegen", self.__zeige_dialog_neues_modul, "#007bff")
        btn2.pack(side="left", padx=(0, 10))
        
        btn3 = self.__create_button(button_frame, "Note zu einem Modul eintragen", self.__zeige_dialog_note_modul, "#007bff")
        btn3.pack(side="left", padx=(0, 10))
        
        btn4 = self.__create_button(button_frame, "Status zu einem Modul ändern", self.__zeige_dialog_status_modul, "#007bff")
        btn4.pack(side="left")

        # Label für aktuelles Semester
        self.__label_aktuelles_semester = tk.Label(module_content, text=f"Aktuell ausgewähltes Semester: {self.__selected_semester.get()}",
                                                font=('Arial', 9), bg='white', fg='#333')
        self.__label_aktuelles_semester.pack(anchor="w", pady=(5, 10))
        
        # Modul Tabelle
        self.__create_modules_table(module_content)
    
    def __create_modules_table(self, parent):
        """Erstellt die Modul-Tabelle"""
        # Erstelle Treeview mit Scrollbar
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill="both", expand=True)
        
        # Treeview
        columns = ("modulname", "ects", "status", "note")
        self.__tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview", height=8)
        
        # Konfiguriere Spalten
        self.__tree.heading("modulname", text="Modulname")
        self.__tree.heading("ects", text="ECTS")
        self.__tree.heading("status", text="Status")
        self.__tree.heading("note", text="Note")
        
        # Konfiguriere Spaltenbreiten
        self.__tree.column("modulname", width=300, anchor="w")
        self.__tree.column("ects", width=60, anchor="center")
        self.__tree.column("status", width=120, anchor="center")
        self.__tree.column("note", width=60, anchor="center")
        
        # Scrollbar hinzufügen
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.__tree.yview)
        self.__tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Pack Treeview und Scrollbar
        self.__tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        
        # Befülle Tabelle
        self.__populate_modules_table()
        
        # Konfiguriere Farben der Zeilen
        self.__tree.tag_configure('evenrow', background='#f8f9fa')
        self.__tree.tag_configure('oddrow', background='white')

    def __populate_modules_table(self):
        """Befüllt die Modul-Tabelle mit Modulen aus dem aktuell ausgewählten Semester oder allen Semestern"""
        # Tabelle leeren
        for row in self.__tree.get_children():
            self.__tree.delete(row)
    
        # Alle Module aus Service laden
        alle_module = self.__ds.get_module()
    
        akt_semester_id = self.__selected_semester.get()
    
        if akt_semester_id.startswith("Kein Semester"):
            module_liste = alle_module
        else:
            # Semester-Objekt aus student_data
            semester_obj = next(
                (s for s in self.__student_data.studiengang.semester_liste
                 if str(s.semester_id) == str(akt_semester_id)),
                None
            )
            if semester_obj:
                semester_modul_ids = [m.modul_id for m in semester_obj.module]
                module_liste = [m for m in alle_module if m.modul_id in semester_modul_ids]     
    
        # Module in Tabelle einfügen
        for i, module in enumerate(module_liste):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            note = (module.pruefungsleistungen[-1].note
                if module.pruefungsleistungen and module.pruefungsleistungen[-1].note is not None
                else "-"
            )
            self.__tree.insert("", "end", values=(module.titel, module.ects_punkte, module.status.value, note), tags=(tag,))
    
    def __zeige_dialog_lernzeit_tracken(self):
        """Dialog zum Hinzufügen einer Lernzeit"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Lernzeit eintragen")
        dialog.geometry("400x200")
        dialog.grab_set()  # macht das Fenster modal
    
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=10, pady=10, fill="x")

        # Aktuelle Kalenderwoche oben als Label
        aktuelle_kw = date.today().isocalendar()[1]
        label_kw = tk.Label(form_frame, text=f"Die aktuelle Kalenderwoche lautet: {aktuelle_kw}", font=('Arial', 9), anchor="w")
        label_kw.pack(fill="x", pady=(0, 10))

        entry_kw = self.__create_row(form_frame, "Kalenderwoche (z.B. KW 26):", 25)
        entry_time = self.__create_row(form_frame, "Lernzeit (Stunden):", 25)
    
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill="x", padx=10, pady=(10, 15))
    
        def save_learning_time():
            try:
                kw_input = entry_kw.get().strip()
                stunden = float(entry_time.get().strip())
    
                if not kw_input or stunden <= 0:
                    messagebox.showerror("Fehler", "Bitte gültige Daten eingeben!")
                    return

                # Ziffern extrahieren (es soll immer im Format "KW 35" gespeichert werden, egal ob "KW35", "35", "KW-35", "35.")
                match = re.search(r"\d+", kw_input)
                if match:
                    kw_number = int(match.group(0))  # auf int konvertieren, um führende Nullen etc. zu normalisieren
                    kw_formatiert = f"KW {kw_number}"
    
                # über den Service buchen
                self.__ds.buche_lernzeit(kw_formatiert, stunden)

                messagebox.showinfo("Erfolg", f"{stunden} Stunden Lernzeit für KW {kw_number} gespeichert.")
    
                # Ziele aktualisieren
                self.__update_goals_section()
    
                dialog.destroy()
    
            except ValueError:
                messagebox.showerror("Fehler", "Lernzeit muss eine Zahl sein!")
    
        save_button = self.__create_button(button_frame, "Speichern", save_learning_time, "#28a745")
        save_button.pack(side="left")      
    
    def __zeige_dialog_neues_modul(self):
        """Dialog zum Hinzufügen eines neuen Moduls"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Neues Modul anlegen")
        dialog.geometry("400x250")
        dialog.grab_set()  # macht das Fenster modal
    
        # Container-Frame für das Formular
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=10, pady=10, fill="x")
    
        entry_id = self.__create_row(form_frame, "Modul-ID:", 15)
        entry_titel = self.__create_row(form_frame, "Titel:", 15)
        entry_ects = self.__create_row(form_frame, "ECTS-Punkte:", 15)
    
        # Frame für den Button, damit er immer sichtbar ist
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill="x", padx=10, pady=(10, 15))
    
        def save_module():
            try:
                modul_id = entry_id.get().strip()
                titel = entry_titel.get().strip()
                ects = int(entry_ects.get().strip())
    
                if not modul_id or not titel:
                    messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen!")
                    return
    
                self.__ds.erstelle_neues_modul(modul_id, titel, ects)

                messagebox.showinfo("Erfolg", f"Modul {modul_id} erfolgreich angelegt.")
    
                # Tabelle aktualisieren
                for row in self.__tree.get_children():
                    self.__tree.delete(row)
                self.__populate_modules_table()

                # Ziele aktualisieren
                self.__update_goals_section()
    
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Fehler", "ECTS-Punkte müssen eine Zahl sein!")
    
        save_button = self.__create_button(button_frame, "Speichern", save_module, "#28a745")
        save_button.pack(side="left")

    def __zeige_dialog_note_modul(self):
        """Dialog zum Hinzufügen einer Note zu einem Modul"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Note hinzufügen")
        dialog.geometry("400x300")
        dialog.grab_set()  # modal
    
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=10, pady=10, fill="x")
    
        # Zeile mit Label + Combobox für Module (nur aktive Module)
        row_frame = tk.Frame(form_frame)
        row_frame.pack(fill="x", pady=5)
        label = tk.Label(row_frame, text="Modul:", width=15, anchor="w")
        label.pack(side="left")
    
        aktive_module = self.__ds.get_module_status_aktiv()
        module_names = [f"{m.modul_id} - {m.titel}" for m in aktive_module]
    
        module_combo = ttk.Combobox(row_frame, values=module_names, state="readonly")
        module_combo.pack(side="left", fill="x", expand=True)

        entry_leistung_id = self.__create_row(form_frame, "Leistung-ID:", 15)
        entry_note = self.__create_row(form_frame, "Note:", 15)
        entry_versuch = self.__create_row(form_frame, "Versuch:", 15)
    
        # Button-Frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill="x", padx=10, pady=(10, 15))
    
        def save_grade():
            try:
                auswahl = module_combo.get()
                if not auswahl:
                    messagebox.showerror("Fehler", "Bitte ein Modul auswählen!")
                    return
    
                # Modul-ID aus der Combobox extrahieren (vor dem " - ")
                modul_id = auswahl.split(" - ")[0]
    
                leistung_id = entry_leistung_id.get().strip()
                note = float(entry_note.get().strip())
                versuch = int(entry_versuch.get().strip())
    
                if not leistung_id or not note:
                    messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen!")
                    return
    
                self.__ds.erstelle_pruefungsleistung(leistung_id, note, date.today(), versuch, modul_id)

                messagebox.showinfo("Erfolg", f"Prüfungsleistung {leistung_id} erfolgreich angelegt.")
    
                # Tabelle neu laden
                self.__populate_modules_table()

                # Ziele aktualisieren
                self.__update_goals_section()
    
                dialog.destroy()
    
            except ValueError:
                messagebox.showerror("Fehler", "Bitte gültige Werte eingeben!")

        save_button = self.__create_button(button_frame, "Speichern", save_grade, "#28a745")
        save_button.pack(side="left")
    
    def __zeige_dialog_status_modul(self):
        """Dialog zum Ändern des Modul-Status"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Modulstatus ändern")
        dialog.geometry("450x200")
        dialog.grab_set()  # macht das Fenster modal
    
        # Container-Frame für das Formular
        form_frame = tk.Frame(dialog)
        form_frame.pack(padx=10, pady=10, fill="x")
    
        # Modul-Auswahl
        row_modul = tk.Frame(form_frame)
        row_modul.pack(fill="x", pady=5)
        tk.Label(row_modul, text="Modul:", width=15, anchor="w").pack(side="left")
        module_namen = []
        for sem in self.__student_data.studiengang.semester_liste:
            if sem.module:
                module_namen.extend([f"{m.modul_id} - {m.titel}" for m in sem.module])
        combo_modul = ttk.Combobox(row_modul, values=module_namen, state="readonly")
        combo_modul.pack(side="left", fill="x", expand=True)
    
        # Status-Auswahl
        row_status = tk.Frame(form_frame)
        row_status.pack(fill="x", pady=5)
        tk.Label(row_status, text="Neuer Status:", width=15, anchor="w").pack(side="left")
        status_werte = self.__ds.get_modul_status_optionen()
        combo_status = ttk.Combobox(row_status, values=status_werte, state="readonly")
        combo_status.pack(side="left", fill="x", expand=True)
    
        # Frame für den Button
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill="x", padx=10, pady=(10, 15))
    
        def save_status():
            try:
                selected_index = combo_modul.current()
                new_status_value = combo_status.get()
    
                if selected_index == -1 or not new_status_value:
                    messagebox.showerror("Fehler", "Bitte Modul und neuen Status auswählen!")
                    return
    
                # Modul-Objekt auswählen und Status setzen
                auswahl = combo_modul.get()
                modul_id = auswahl.split(" - ")[0]
                
                # Speichern
                self.__ds.aendere_modul_status(modul_id, new_status_value)

                messagebox.showinfo("Erfolg", f"Status zum Modul {modul_id} erfolgreich geändert.")
                
                # Tabelle aktualisieren
                self.__populate_modules_table()

                # Ziele aktualisieren
                self.__update_goals_section()
    
                dialog.destroy()
    
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
    
        save_button = self.__create_button(button_frame, "Speichern", save_status, "#28a745")
        save_button.pack(side="left")

    def __waehle_semester(self):
        """Dialog zum Auswählen des aktuellen Semesters"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Semester auswählen")
        dialog.geometry("400x200")
        dialog.grab_set()  # macht das Fenster modal
    
        frame = tk.Frame(dialog)
        frame.pack(padx=10, pady=10, fill="x")
    
        # Label
        tk.Label(frame, text="Wähle das aktuelle Semester:", font=('Arial', 9)).pack(anchor="w", pady=(0,5))
    
        # Dropdown mit Semester-Auswahl
        semester_options = [sem.semester_id for sem in self.__student_data.studiengang.semester_liste]
        self.__selected_semester = tk.StringVar()
        semester_combo = ttk.Combobox(frame, textvariable=self.__selected_semester, values=semester_options, state="readonly", width=15)
        semester_combo.pack(anchor="w")
        semester_combo.current(0)  # Standardwert

        # Frame für den Button
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill="x", padx=10, pady=(10, 15))
    
        # Speichern-Button
        def save_semester():
            chosen = self.__selected_semester.get()
            # Hier könntest du die Auswahl im Service speichern
            messagebox.showinfo("Semester ausgewählt", f"Das Semester {chosen} wurde ausgewählt.")

            # Label aktualisieren
            self.__label_aktuelles_semester.config(text=f"Aktuelles Semester: {chosen}")
                
            # Tabelle aktualisieren
            for row in self.__tree.get_children():
                self.__tree.delete(row)
            self.__populate_modules_table()

            # Ziele aktualisieren
            self.__update_goals_section()
            
            dialog.destroy()
    
        save_button = self.__create_button(button_frame, "Speichern", save_semester, "#28a745")
        save_button.pack(side="left")

    def __create_row(self, parent, label_text: str, entry_width: int = 20):
        """Hilfsfunktion zum Erstellen von Label+Entry nebeneinander"""
        row_frame = tk.Frame(parent)
        row_frame.pack(fill="x", pady=5)
        label = tk.Label(row_frame, text=label_text, width=entry_width, anchor="w")
        label.pack(side="left")
        entry = tk.Entry(row_frame)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def __create_button(self, parent, text, command, color="#28a745"):
        """Hilfsfunktion für das Erzeugen eines Buttons"""
        return tk.Button(parent, text=text, command=command, bg=color, fg="white",
            font=('Arial', 9, 'bold'), relief='flat', padx=3, pady=3)
    

