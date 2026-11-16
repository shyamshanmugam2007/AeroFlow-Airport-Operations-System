"""
AeroFlow – In-Memory Data Store & Conflict Detection Engine
Manages flights, gates, conflict calculations, and CSV export using pure Python data structures.
"""

from datetime import datetime, date, time
import csv
import re
from typing import List, Dict, Any, Optional, Tuple
import config


class DataStore:
    @staticmethod
    def _parse_time(value: str) -> time:
        """Parse a strict 24-hour HH:MM value into a comparable time object."""
        if not isinstance(value, str) or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
            raise ValueError("Time must use zero-padded 24-hour HH:MM format.")
        return datetime.strptime(value, "%H:%M").time()

    @staticmethod
    def _validate_allowed_values(gate: str, status: str, flight_type: str) -> Optional[str]:
        if gate not in ["Unassigned", *config.GATES_LIST]:
            return f"Invalid gate '{gate}'. Choose a configured gate or Unassigned."
        if status not in config.FLIGHT_STATUSES:
            return f"Invalid status '{status}'. Allowed statuses: {', '.join(config.FLIGHT_STATUSES)}."
        if flight_type not in config.FLIGHT_TYPES:
            return f"Invalid flight type '{flight_type}'. Allowed types: {', '.join(config.FLIGHT_TYPES)}."
        return None

    def __init__(self):
        self._next_flight_id = 1
        self.flights: Dict[int, Dict[str, Any]] = {}
        self.gates: List[Dict[str, Any]] = []
        
        self._init_gates()
        self._init_sample_data()

    def _init_gates(self):
        terminals = {
            "G1": "Terminal 1", "G2": "Terminal 1", "G3": "Terminal 1",
            "G4": "Terminal 2", "G5": "Terminal 2", "G6": "Terminal 2",
            "G7": "Terminal 3", "G8": "Terminal 3"
        }
        self.gates = [
            {"gate_id": gid, "terminal": terminals.get(gid, "Terminal 1")}
            for gid in config.GATES_LIST
        ]

    def _init_sample_data(self):
        """Seeds 14 realistic sample flights with fictional details for demonstrations."""
        today_str = date.today().isoformat()

        samples = [
            ("AF-101", "AeroFlow Airways", "SIN - Singapore Changi", "JFK - New York", "Arrival", today_str, "08:00", "09:30", "G1", "Arrived"),
            ("SK-204", "SkyJet International", "JFK - New York", "LHR - London Heathrow", "Departure", today_str, "09:45", "11:15", "G1", "Departed"),
            ("AP-305", "Apex Aviation", "DXB - Dubai International", "JFK - New York", "Arrival", today_str, "10:00", "11:30", "G2", "Boarding"),
            ("OE-410", "Oceanic Express", "JFK - New York", "HND - Tokyo Haneda", "Departure", today_str, "11:00", "12:45", "G3", "Scheduled"),
            ("SA-502", "Starlight Air", "CDG - Paris Charles de Gaulle", "JFK - New York", "Arrival", today_str, "12:15", "13:45", "G4", "Delayed"),
            ("AA-618", "Aurora Airways", "JFK - New York", "FRA - Frankfurt", "Departure", today_str, "13:30", "15:00", "G5", "Scheduled"),
            ("PV-722", "Pacific Vista Airlines", "SYD - Sydney Kingsford", "JFK - New York", "Arrival", today_str, "14:00", "15:45", "G6", "Scheduled"),
            ("HZ-830", "Horizon Air", "JFK - New York", "ORD - Chicago O'Hare", "Departure", today_str, "15:15", "16:30", "Unassigned", "Scheduled"),
            ("GW-901", "Global Wings", "LAX - Los Angeles", "JFK - New York", "Arrival", today_str, "16:00", "17:30", "Unassigned", "Scheduled"),
            ("AF-108", "AeroFlow Airways", "JFK - New York", "SIN - Singapore Changi", "Departure", today_str, "17:00", "18:30", "Unassigned", "Scheduled"),
            ("SK-215", "SkyJet International", "LHR - London Heathrow", "JFK - New York", "Arrival", today_str, "18:15", "19:45", "Unassigned", "Scheduled"),
            ("AP-320", "Apex Aviation", "JFK - New York", "DXB - Dubai International", "Departure", today_str, "19:30", "21:00", "Unassigned", "Scheduled"),
            ("DS-441", "Delta Shuttle", "BOS - Boston Logan", "JFK - New York", "Arrival", today_str, "20:00", "21:15", "Unassigned", "Cancelled"),
            ("OE-490", "Oceanic Express", "JFK - New York", "SYD - Sydney Kingsford", "Departure", today_str, "21:30", "23:00", "Unassigned", "Scheduled"),
        ]

        for s in samples:
            self.add_flight({
                "flight_number": s[0],
                "airline": s[1],
                "origin": s[2],
                "destination": s[3],
                "flight_type": s[4],
                "date": s[5],
                "start_time": s[6],
                "end_time": s[7],
                "gate": s[8],
                "status": s[9]
            }, allow_unassigned_gate_on_cancelled=True)

    # ==========================================================
    # FLIGHT CRUD OPERATIONS
    # ==========================================================

    def add_flight(self, data: Dict[str, Any], allow_unassigned_gate_on_cancelled: bool = False) -> Tuple[bool, str, Optional[int]]:
        """Adds a flight with comprehensive field, duplicate, and time validation."""
        f_num = data.get("flight_number", "").strip().upper()
        airline = data.get("airline", "").strip()
        origin = data.get("origin", "").strip()
        dest = data.get("destination", "").strip()
        f_type = data.get("flight_type", "Arrival")
        f_date = data.get("date", "").strip()
        start = data.get("start_time", "").strip()
        end = data.get("end_time", "").strip()
        gate = data.get("gate", "Unassigned").strip()
        status = data.get("status", "Scheduled")

        # 1. Mandatory checks
        if not f_num or not airline or not origin or not dest or not f_date or not start or not end:
            return False, "All fields are required.", None

        if origin.upper() == dest.upper():
            return False, "Origin and Destination cannot be the same airport.", None

        # 2. Date and Time Format validation
        try:
            datetime.strptime(f_date, "%Y-%m-%d")
        except ValueError:
            return False, "Date must follow YYYY-MM-DD format (e.g. 2026-11-16).", None

        try:
            start_value = self._parse_time(start)
            end_value = self._parse_time(end)
        except ValueError:
            return False, "Times must use zero-padded 24-hour HH:MM format (e.g. 09:30, 14:15).", None

        if start_value >= end_value:
            return False, "End time must be later than start time. Overnight flights are not supported in this version.", None

        invalid = self._validate_allowed_values(gate, status, f_type)
        if invalid:
            return False, invalid, None

        # 3. Duplicate flight number prevention on the same date
        for existing in self.flights.values():
            if existing["flight_number"].upper() == f_num and existing["date"] == f_date:
                return False, f"Flight '{f_num}' is already scheduled for date {f_date}.", None

        # 4. Cancelled flights must not occupy gates
        if status == "Cancelled" and gate != "Unassigned":
            gate = "Unassigned"

        # 5. Gate Conflict check if gate is assigned
        if gate and gate != "Unassigned":
            has_conflict, conf_flight = self.check_gate_conflict(gate, f_date, start, end)
            if has_conflict:
                sugg = self.suggest_available_gates(f_date, start, end)
                sugg_str = ", ".join(sugg) if sugg else "None available"
                return False, (
                    f"Gate Conflict at {gate}!\n"
                    f"Overlaps with Flight {conf_flight['flight_number']} ({conf_flight['airline']}) "
                    f"allocated {conf_flight['start_time']} - {conf_flight['end_time']}.\n\n"
                    f"Suggested Available Gates: {sugg_str}"
                ), None

        new_id = self._next_flight_id
        self._next_flight_id += 1

        self.flights[new_id] = {
            "id": new_id,
            "flight_number": f_num,
            "airline": airline,
            "origin": origin,
            "destination": dest,
            "flight_type": f_type,
            "date": f_date,
            "start_time": start,
            "end_time": end,
            "gate": gate,
            "status": status,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return True, f"Flight {f_num} successfully registered.", new_id

    def update_flight(self, flight_id: int, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Updates an existing flight record with conflict exclusion for its own slot."""
        if flight_id not in self.flights:
            return False, "Flight record not found."

        f_num = data.get("flight_number", "").strip().upper()
        airline = data.get("airline", "").strip()
        origin = data.get("origin", "").strip()
        dest = data.get("destination", "").strip()
        f_type = data.get("flight_type", "Arrival")
        f_date = data.get("date", "").strip()
        start = data.get("start_time", "").strip()
        end = data.get("end_time", "").strip()
        gate = data.get("gate", "Unassigned").strip()
        status = data.get("status", "Scheduled")

        if not f_num or not airline or not origin or not dest or not f_date or not start or not end:
            return False, "All fields are required."

        if origin.upper() == dest.upper():
            return False, "Origin and Destination cannot be identical."

        try:
            datetime.strptime(f_date, "%Y-%m-%d")
            start_value = self._parse_time(start)
            end_value = self._parse_time(end)
        except ValueError:
            return False, "Invalid date or time. Use YYYY-MM-DD and zero-padded HH:MM."

        if start_value >= end_value:
            return False, "End time must be later than start time. Overnight flights are not supported in this version."

        invalid = self._validate_allowed_values(gate, status, f_type)
        if invalid:
            return False, invalid

        # Duplicate check excluding self
        for fid, existing in self.flights.items():
            if fid != flight_id and existing["flight_number"].upper() == f_num and existing["date"] == f_date:
                return False, f"Flight '{f_num}' already exists on date {f_date}."

        # Cancelled flights must not occupy gates
        if status == "Cancelled":
            gate = "Unassigned"

        # Gate conflict check excluding self
        if gate and gate != "Unassigned":
            has_conflict, conf_flight = self.check_gate_conflict(gate, f_date, start, end, exclude_flight_id=flight_id)
            if has_conflict:
                sugg = self.suggest_available_gates(f_date, start, end, exclude_flight_id=flight_id)
                sugg_str = ", ".join(sugg) if sugg else "None available"
                return False, (
                    f"Gate Conflict at {gate}!\n"
                    f"Overlaps with Flight {conf_flight['flight_number']} ({conf_flight['airline']}) "
                    f"allocated {conf_flight['start_time']} - {conf_flight['end_time']}.\n\n"
                    f"Suggested Available Gates: {sugg_str}"
                )

        self.flights[flight_id].update({
            "flight_number": f_num,
            "airline": airline,
            "origin": origin,
            "destination": dest,
            "flight_type": f_type,
            "date": f_date,
            "start_time": start,
            "end_time": end,
            "gate": gate,
            "status": status,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return True, f"Flight {f_num} updated successfully."

    def delete_flight(self, flight_id: int) -> Tuple[bool, str]:
        """Removes a flight from memory."""
        if flight_id in self.flights:
            f_num = self.flights[flight_id]["flight_number"]
            del self.flights[flight_id]
            return True, f"Flight {f_num} deleted successfully."
        return False, "Flight does not exist."

    def get_flight(self, flight_id: int) -> Optional[Dict[str, Any]]:
        return self.flights.get(flight_id)

    def get_all_flights(self) -> List[Dict[str, Any]]:
        """Returns all flights sorted by date and start time."""
        return sorted(list(self.flights.values()), key=lambda x: (x["date"], x["start_time"]), reverse=True)

    def update_flight_status(self, flight_id: int, new_status: str) -> Tuple[bool, str]:
        """Updates flight status and releases gate if marked Cancelled."""
        if flight_id not in self.flights:
            return False, "Flight not found."
        
        if new_status not in config.FLIGHT_STATUSES:
            return False, f"Invalid status '{new_status}'. Allowed statuses: {', '.join(config.FLIGHT_STATUSES)}."

        fl = self.flights[flight_id]
        fl["status"] = new_status
        if new_status == "Cancelled" and fl["gate"] != "Unassigned":
            fl["gate"] = "Unassigned"
            return True, f"Flight {fl['flight_number']} marked Cancelled. Gate released."
        return True, f"Flight {fl['flight_number']} status changed to {new_status}."

    # ==========================================================
    # GATE CONFLICT DETECTION & ALLOCATION LOGIC
    # Conflict condition: new_start < existing_end AND new_end > existing_start
    # ==========================================================

    def check_gate_conflict(
        self,
        gate: str,
        f_date: str,
        start_time: str,
        end_time: str,
        exclude_flight_id: Optional[int] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Determines if an allocation overlaps with an existing allocation on the same gate and date.
        Cancelled flights DO NOT occupy gates and are ignored.
        Consecutive slots (e.g. 10:00-11:30 and 11:30-13:00) DO NOT conflict.
        """
        for fid, f in self.flights.items():
            if exclude_flight_id is not None and fid == exclude_flight_id:
                continue
            if f["status"] == "Cancelled":
                continue
            if f["gate"] == gate and f["date"] == f_date:
                # Interval overlap condition
                new_start = self._parse_time(start_time)
                new_end = self._parse_time(end_time)
                existing_start = self._parse_time(f["start_time"])
                existing_end = self._parse_time(f["end_time"])
                if new_start < existing_end and new_end > existing_start:
                    return True, f
        return False, None

    def suggest_available_gates(
        self,
        f_date: str,
        start_time: str,
        end_time: str,
        exclude_flight_id: Optional[int] = None
    ) -> List[str]:
        """Returns all gates from G1-G8 that have no time conflict for the given window."""
        available = []
        for gid in config.GATES_LIST:
            has_conf, _ = self.check_gate_conflict(gid, f_date, start_time, end_time, exclude_flight_id)
            if not has_conf:
                available.append(gid)
        return available

    def assign_gate(self, flight_id: int, gate: str) -> Tuple[bool, str, List[str]]:
        """Assigns a gate to a flight after evaluating conflicts."""
        if flight_id not in self.flights:
            return False, "Flight not found.", []

        fl = self.flights[flight_id]

        if fl["status"] == "Cancelled":
            return False, "Cannot allocate gate to a Cancelled flight.", []

        if gate not in ["Unassigned", *config.GATES_LIST]:
            return False, f"Invalid gate '{gate}'. Choose a configured gate or Unassigned.", []

        if gate == "Unassigned":
            fl["gate"] = "Unassigned"
            return True, f"Gate for flight {fl['flight_number']} released.", []

        has_conflict, conf_fl = self.check_gate_conflict(
            gate=gate,
            f_date=fl["date"],
            start_time=fl["start_time"],
            end_time=fl["end_time"],
            exclude_flight_id=flight_id
        )

        if has_conflict:
            sugg = self.suggest_available_gates(fl["date"], fl["start_time"], fl["end_time"], exclude_flight_id=flight_id)
            msg = (
                f"Allocation Conflict at {gate}!\n"
                f"Overlaps with Flight {conf_fl['flight_number']} ({conf_fl['airline']}) "
                f"scheduled {conf_fl['start_time']} - {conf_fl['end_time']}."
            )
            return False, msg, sugg

        fl["gate"] = gate
        return True, f"Gate {gate} successfully allocated to Flight {fl['flight_number']}.", []

    def release_gate(self, flight_id: int) -> Tuple[bool, str]:
        """Releases the gate assignment for a given flight."""
        if flight_id in self.flights:
            fl = self.flights[flight_id]
            fl["gate"] = "Unassigned"
            return True, f"Gate for flight {fl['flight_number']} has been released."
        return False, "Flight not found."

    # ==========================================================
    # GATE CARD & AVAILABILITY STATUS
    # ==========================================================

    def get_gate_card_data(self) -> List[Dict[str, Any]]:
        """Return current occupancy only; future bookings never count as occupied."""
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        now_time = now.time().replace(second=0, microsecond=0)
        results = []
        for gate in self.gates:
            gid = gate["gate_id"]
            today_flights = [
                f for f in self.flights.values()
                if f["gate"] == gid and f["date"] == today_str and f["status"] != "Cancelled"
            ]
            today_flights.sort(key=lambda f: self._parse_time(f["start_time"]))
            active = next((f for f in today_flights
                           if self._parse_time(f["start_time"]) <= now_time < self._parse_time(f["end_time"])), None)
            next_flight = next((f for f in today_flights
                                if self._parse_time(f["start_time"]) > now_time), None)
            selected = active or next_flight
            is_occupied = active is not None
            if selected:
                results.append({
                    "gate_id": gid, "terminal": gate["terminal"],
                    "status": "Occupied" if is_occupied else "Available",
                    "flight_number": selected["flight_number"],
                    "airline": selected["airline"] if is_occupied else f"Upcoming: {selected['airline']}",
                    "time_window": f"{selected['start_time']} - {selected['end_time']}",
                    "route": f"{selected['origin'].split(' - ')[0]} ➔ {selected['destination'].split(' - ')[0]}",
                    "flight_status": selected["status"] if is_occupied else "Upcoming",
                    "flight_id": selected["id"], "all_today_flights": today_flights
                })
            else:
                results.append({
                    "gate_id": gid, "terminal": gate["terminal"], "status": "Available",
                    "flight_number": "None", "airline": "No active allocation",
                    "time_window": "--:-- - --:--", "route": "Ready for assignment",
                    "flight_status": "Available", "flight_id": None, "all_today_flights": today_flights
                })
        return results

    # ==========================================================
    # DASHBOARD & ANALYTICS DATA
    # ==========================================================

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Calculates dynamic stats from in-memory records."""
        total = len(self.flights)
        arrivals = sum(1 for f in self.flights.values() if f["flight_type"] == "Arrival")
        departures = sum(1 for f in self.flights.values() if f["flight_type"] == "Departure")
        delayed = sum(1 for f in self.flights.values() if f["status"] == "Delayed")
        cancelled = sum(1 for f in self.flights.values() if f["status"] == "Cancelled")

        gate_cards = self.get_gate_card_data()
        occupied_gates = sum(1 for g in gate_cards if g["status"] == "Occupied")
        available_gates = len(gate_cards) - occupied_gates

        status_counts = {}
        for st in config.FLIGHT_STATUSES:
            status_counts[st] = sum(1 for f in self.flights.values() if f["status"] == st)

        recent = sorted(list(self.flights.values()), key=lambda x: (x["date"], x["start_time"]), reverse=True)[:6]

        return {
            "total_flights": total,
            "arrivals": arrivals,
            "departures": departures,
            "delayed_flights": delayed,
            "cancelled_flights": cancelled,
            "available_gates": available_gates,
            "occupied_gates": occupied_gates,
            "total_gates": len(config.GATES_LIST),
            "status_counts": status_counts,
            "recent_flights": recent,
            "gate_cards": gate_cards
        }

    # ==========================================================
    # SEARCH & FILTER
    # ==========================================================

    def filter_flights(
        self,
        flight_number: str = "",
        airline: str = "All",
        origin: str = "",
        destination: str = "",
        flight_type: str = "All",
        status: str = "All",
        date_str: str = ""
    ) -> List[Dict[str, Any]]:
        """Filters in-memory flight records according to multiple parameters."""
        results = []
        for f in self.flights.values():
            if flight_number and flight_number.upper() not in f["flight_number"].upper():
                continue
            if airline != "All" and f["airline"] != airline:
                continue
            if origin and origin.lower() not in f["origin"].lower():
                continue
            if destination and destination.lower() not in f["destination"].lower():
                continue
            if flight_type != "All" and f["flight_type"] != flight_type:
                continue
            if status != "All" and f["status"] != status:
                continue
            if date_str and f["date"] != date_str.strip():
                continue
            results.append(f)

        return sorted(results, key=lambda x: (x["date"], x["start_time"]), reverse=True)

    # ==========================================================
    # CSV EXPORT
    # ==========================================================

    def export_to_csv(self, file_path: str) -> Tuple[bool, str]:
        """Exports all in-memory flight records into a standard CSV file."""
        try:
            fields = [
                "ID", "Flight Number", "Airline", "Origin", "Destination",
                "Flight Type", "Date", "Start Time", "End Time", "Gate", "Status"
            ]
            all_fl = self.get_all_flights()
            with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(fields)
                def safe_cell(value):
                    value = str(value)
                    first = value.lstrip(" \t\r\n")[:1]
                    return "'" + value if first in ("=", "+", "-", "@") else value
                for f in all_fl:
                    writer.writerow([
                        f["id"], *[safe_cell(f[key]) for key in (
                            "flight_number", "airline", "origin", "destination", "flight_type",
                            "date", "start_time", "end_time", "gate", "status"
                        )]
                    ])
            return True, f"Successfully exported {len(all_fl)} flight records to {file_path}"
        except Exception as e:
            return False, f"Failed to export CSV: {str(e)}"
