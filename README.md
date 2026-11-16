# AeroFlow – Airport Flight and Gate Allocation System

AeroFlow is a Python desktop **airport-operations simulation**. It demonstrates flight registration, flight status updates, gate assignment, same-day gate conflict detection, gate suggestions, multi-criteria search, dashboard summaries, charts and CSV export.

> **Important scope note:** This version is still an in-memory coursework prototype. It does not connect to live airline/airport systems and does not use SQL or another persistent database. Changes made during a session are lost when the application closes. CSV export creates a snapshot; it is not automatic persistence.

## Requirements

- Windows 10/11 (recommended for the submitted desktop GUI)
- Python 3.10–3.13 (test on the exact Python version installed on your machine)
- Packages listed in `requirements.txt`

## Folder structure

```text
AeroFlow/
├── main.py
├── config.py
├── data_store.py
├── requirements.txt
├── README.md
├── modules/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── flights.py
│   ├── gates.py
│   ├── status.py
│   ├── search.py
│   └── reports.py
└── tests/
    └── test_data_store.py
```

## Install and run (Windows PowerShell)

```powershell
cd path\to\AeroFlow
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

If PowerShell blocks activation, use `cmd.exe` and run `.venv\Scripts\activate.bat`.

## Run the automated data-layer tests

```powershell
python -m unittest discover -s tests -v
```

The tests cover strict time validation, chronological intervals, overnight-flight rejection, allowed gate/status/type values, gate overlap and adjacent intervals, cancellation/release, and CSV formula-injection mitigation.

## Corrections in this version

1. Time inputs require zero-padded `HH:MM`; comparisons use parsed `datetime.time` values rather than lexical string ordering.
2. End times must be later than start times. Overnight flights are explicitly unsupported rather than silently mis-scheduled.
3. Gate IDs, flight types and statuses are validated in the data layer, not just by UI dropdowns.
4. Status updates reject unknown statuses; cancellation releases the assigned gate.
5. Gate cards count a gate as occupied only during the half-open interval `start <= now < end`. A future booking is displayed as upcoming while the gate remains currently available.
6. Reports distinguish current gate occupancy from time-based utilisation. Per-gate percentages are described as assignment share, not utilisation.
7. Selecting an unassigned flight resets the gate selector instead of retaining the prior flight's gate.
8. The clock label correctly says local time; it does not claim to show UTC.
9. CSV export prefixes potentially executable spreadsheet formula values with an apostrophe.
10. Added automated data-layer tests.

## Known limitations / items to verify on your machine

- No SQL database or persistence is implemented. If your faculty requires a database, add SQLite or the specifically required DBMS as a separate project enhancement and test data persistence after restarting the app.
- Same-day schedules only; overnight flights are rejected.
- The app uses fictional demonstration flight records. It is not an operational airport control system.
- The automated tests exercise the data layer, not the complete CustomTkinter GUI. Install the dependencies and launch `python main.py` on the target Windows machine to verify all screens, dialogs, fonts and callbacks.
- No live flight feeds, airport system integration, authentication or role-based access control are included.

## Suggested demonstration

1. Open Flight Management and add a flight.
2. Allocate it to a gate.
3. Try to add another flight with an overlapping time on the same gate and show the conflict message.
4. Try an adjacent slot to show that back-to-back allocations are allowed.
5. Cancel a flight and show that its gate is released.
6. Search/filter flights, view dashboard and reports, then export a CSV snapshot.

Describe the system honestly as a desktop simulation with an in-memory data store and CSV export.
