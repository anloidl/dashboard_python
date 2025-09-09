import csv
import os
import json
from typing import List, Dict, Union, Any
from datetime import date
from enum import Enum

class DatenVerwaltung:
    def __init__(self, daten_ordner: str = "resources"):
        self.__daten_ordner = daten_ordner
        os.makedirs(daten_ordner, exist_ok=True)

    def __dateipfad(self, dateiname: str) -> str:
        return os.path.join(self.__daten_ordner, f"{dateiname}.csv")

    def __serialize_value(self, value: Any) -> Union[str, int, float, bool, None, dict[str, Any], list[Any]]:
        """Wandelt Objekte, Enums, Dicts und einfache Typen rekursiv in eine JSON-kompatible Struktur um."""
        if isinstance(value, (str, int, float, bool)) or value is None: # einfache Typen
            return value
        elif isinstance(value, date): # Date
            return value.isoformat()
        elif isinstance(value, Enum): # Enum
            return value.value
        elif hasattr(value, "to_dict") and callable(value.to_dict): # Hat eine to_dict-Methode → als Dict serialisieren
            return self.__serialize_value(value.to_dict())
        elif isinstance(value, list): # Liste
            return [self.__serialize_value(v) for v in value]
        elif isinstance(value, dict): # Dictionary
            return {k: self.__serialize_value(v) for k, v in value.items()}
        else:
            return str(value)

    def __lade_objekte_von_csv(self, name: str, cls: type[Any]) -> list[Any]:
        """Lädt Objekte einer Klasse aus einer CSV-Datei.
        Erwartet, dass die Klasse eine from_dict-Methode hat."""
        objects = []
        filename = self.__dateipfad(name)
        with open(filename, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                parsed_row = {}
                for key, value in row.items():
                    if not value:  
                        parsed_row[key] = None
                    else:
                        # Prüfen ob JSON (für Listen, Dicts, verschachtelte Objekte)
                        try:
                            parsed_value = json.loads(value)
                            parsed_row[key] = parsed_value
                        except (json.JSONDecodeError, TypeError):
                            parsed_row[key] = value  # normaler String/Zahl   
                # Jetzt mit from_dict ein Objekt bauen
                obj = cls.from_dict(parsed_row)
                objects.append(obj)
        return objects

    def __speichere_objekte_in_csv(self, name: str, objects: list[Any]) -> None:
        """Speichert eine Liste von Objekten mit to_dict() in CSV."""
        if not objects:
            return
        # Feldnamen aus der ersten Instanz ableiten
        fieldnames = list(self.__serialize_value(objects[0].to_dict()).keys())
        filename = self.__dateipfad(name)
        # Schreiben
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for obj in objects:
                row_dict = self.__serialize_value(obj.to_dict())
                # Listen / Dicts als JSON-Strings speichern
                for key, value in row_dict.items():
                    if isinstance(value, (list, dict)):
                        row_dict[key] = json.dumps(value, ensure_ascii=False)
                writer.writerow(row_dict)

     # öffentliche Methoden (API für außen)
    def lade(self, name: str, cls: type[Any]) -> list[Any]:
        """Lädt eine Liste von Objekten aus CSV."""
        return self.__lade_objekte_von_csv(name, cls)

    def speichere(self, name: str, objects: list[Any]) -> None:
        """Speichert eine Liste von Objekten in CSV."""
        self.__speichere_objekte_in_csv(name, objects)
