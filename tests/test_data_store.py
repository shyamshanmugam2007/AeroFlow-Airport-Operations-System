import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path

from data_store import DataStore


class DataStoreValidationTests(unittest.TestCase):
    def setUp(self):
        self.store = DataStore()
        self.today = date.today().isoformat()

    def flight(self, **overrides):
        data = {
            "flight_number": "TST-900", "airline": "Test Air",
            "origin": "AAA - Alpha", "destination": "BBB - Beta",
            "flight_type": "Arrival", "date": self.today,
            "start_time": "09:00", "end_time": "10:00",
            "gate": "Unassigned", "status": "Scheduled",
        }
        data.update(overrides)
        return data

    def test_valid_zero_padded_time(self):
        ok, _, _ = self.store.add_flight(self.flight())
        self.assertTrue(ok)

    def test_non_zero_padded_time_rejected(self):
        ok, message, _ = self.store.add_flight(self.flight(start_time="9:00"))
        self.assertFalse(ok)
        self.assertIn("HH:MM", message)

    def test_chronologically_invalid_interval_rejected(self):
        ok, _, _ = self.store.add_flight(self.flight(start_time="10:00", end_time="09:30"))
        self.assertFalse(ok)

    def test_overnight_interval_rejected_with_explanation(self):
        ok, message, _ = self.store.add_flight(self.flight(start_time="23:00", end_time="01:00"))
        self.assertFalse(ok)
        self.assertIn("Overnight", message)

    def test_invalid_gate_rejected(self):
        ok, message, _ = self.store.add_flight(self.flight(gate="G99"))
        self.assertFalse(ok)
        self.assertIn("Invalid gate", message)

    def test_invalid_status_rejected(self):
        ok, message, _ = self.store.add_flight(self.flight(status="Flying"))
        self.assertFalse(ok)
        self.assertIn("Invalid status", message)

    def test_invalid_flight_type_rejected(self):
        ok, message, _ = self.store.add_flight(self.flight(flight_type="Cargo"))
        self.assertFalse(ok)
        self.assertIn("Invalid flight type", message)

    def test_duplicate_flight_number_on_same_date_rejected(self):
        ok, _, _ = self.store.add_flight(self.flight())
        self.assertTrue(ok)
        ok, message, _ = self.store.add_flight(self.flight(gate="Unassigned"))
        self.assertFalse(ok)
        self.assertIn("already scheduled", message)

    def test_update_rejects_invalid_values(self):
        flight_id = next(iter(self.store.flights))
        original = self.store.get_flight(flight_id).copy()
        update = {key: original[key] for key in (
            "flight_number", "airline", "origin", "destination", "flight_type",
            "date", "start_time", "end_time", "gate", "status"
        )}
        update["gate"] = "G99"
        ok, message = self.store.update_flight(flight_id, update)
        self.assertFalse(ok)
        self.assertIn("Invalid gate", message)

    def test_invalid_status_update_rejected(self):
        flight_id = next(iter(self.store.flights))
        ok, message = self.store.update_flight_status(flight_id, "Flying")
        self.assertFalse(ok)
        self.assertIn("Invalid status", message)

    def test_adjacent_gate_allocations_are_allowed(self):
        ok, _, _ = self.store.add_flight(self.flight(gate="G8", start_time="00:00", end_time="01:00"))
        self.assertTrue(ok)
        ok, _, _ = self.store.add_flight(self.flight(
            flight_number="TST-901", gate="G8", start_time="01:00", end_time="02:00"))
        self.assertTrue(ok)

    def test_overlapping_gate_allocation_rejected(self):
        ok, _, _ = self.store.add_flight(self.flight(gate="G8"))
        self.assertTrue(ok)
        ok, message, _ = self.store.add_flight(self.flight(
            flight_number="TST-901", gate="G8", start_time="09:30", end_time="10:30"))
        self.assertFalse(ok)
        self.assertIn("Gate Conflict", message)

    def test_assign_unknown_gate_rejected(self):
        flight_id = next(iter(self.store.flights))
        ok, message, _ = self.store.assign_gate(flight_id, "G99")
        self.assertFalse(ok)
        self.assertIn("Invalid gate", message)

    def test_cancelled_flight_releases_gate(self):
        flight_id = next(iter(self.store.flights))
        ok, _ = self.store.update_flight_status(flight_id, "Cancelled")
        self.assertTrue(ok)
        self.assertEqual(self.store.flights[flight_id]["gate"], "Unassigned")

    def test_csv_formula_injection_is_neutralized(self):
        ok, _, flight_id = self.store.add_flight(self.flight(
            flight_number="=1+1", gate="Unassigned"))
        self.assertTrue(ok)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "export.csv"
            ok, _ = self.store.export_to_csv(str(path))
            self.assertTrue(ok)
            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))
            row = next(r for r in rows[1:] if r[0] == str(flight_id))
            self.assertEqual(row[1], "'=1+1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
