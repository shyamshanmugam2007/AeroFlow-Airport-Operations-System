"""
AeroFlow – Airport Operations Control
Configuration, UI Constants, Color Palette, and Styling Definitions.
"""

import os
import tempfile

# Ensure Matplotlib config cache is writable in temporary directory
os.environ['MPLCONFIGDIR'] = os.path.join(tempfile.gettempdir(), 'aeroflow_matplotlib')

# Application Meta
APP_TITLE = "AeroFlow – Airport Operations Control"
APP_SUBTITLE = "Airport Flight & Gate Allocation Management System"
APP_VERSION = "2.1 (Validated In-Memory Edition)"

# Color Palette (Airport Dark Dashboard)
COLOR_BG = "#0B1120"             # Main background
COLOR_SIDEBAR = "#111827"        # Sidebar background
COLOR_SIDEBAR_ACTIVE = "#1E293B" # Active nav item
COLOR_SIDEBAR_HOVER = "#1E293B"  # Hover nav item
COLOR_CARD = "#172033"           # Cards and panels
COLOR_CARD_ALT = "#1E293B"       # Card variant
COLOR_CARD_BORDER = "#1E2A42"    # Subtle borders
COLOR_CARD_HOVER = "#233352"

# Accents
COLOR_PRIMARY = "#38BDF8"        # Sky blue primary accent
COLOR_PRIMARY_HOVER = "#0284C7"  # Primary hover
COLOR_SECONDARY = "#2563EB"      # Blue secondary accent
COLOR_SECONDARY_HOVER = "#1D4ED8"# Secondary hover

# Status and Indicator Colors
COLOR_SUCCESS = "#22C55E"        # Green (Arrived / Available)
COLOR_WARNING = "#F59E0B"        # Amber (Boarding)
COLOR_ERROR = "#EF4444"          # Red (Delayed / Conflict)
COLOR_PURPLE = "#8B5CF6"         # Departed
COLOR_MUTED = "#64748B"          # Cancelled / Inactive

# Typography Colors
COLOR_TEXT_PRIMARY = "#F8FAFC"   # Crisp White
COLOR_TEXT_SECONDARY = "#94A3B8" # Muted Slate
COLOR_TEXT_MUTED = "#64748B"     # Dark Slate

# Table Colors
COLOR_TABLE_HEADER = "#1E293B"
COLOR_TABLE_ROW = "#172033"
COLOR_TABLE_ROW_ALT = "#121A2B"
COLOR_TABLE_ROW_HOVER = "#1E2A42"

# Typography Fonts
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 20, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 13)
FONT_SECTION = (FONT_FAMILY, 15, "bold")
FONT_CARD_TITLE = (FONT_FAMILY, 11, "bold")
FONT_CARD_VALUE = (FONT_FAMILY, 24, "bold")
FONT_BODY = (FONT_FAMILY, 12)
FONT_BODY_BOLD = (FONT_FAMILY, 12, "bold")
FONT_SMALL = (FONT_FAMILY, 10)
FONT_SMALL_BOLD = (FONT_FAMILY, 10, "bold")
FONT_BADGE = (FONT_FAMILY, 10, "bold")

# Flight Status Definitions & Styles
FLIGHT_STATUSES = [
    "Scheduled",
    "Boarding",
    "Departed",
    "Arrived",
    "Delayed",
    "Cancelled"
]

STATUS_COLORS = {
    "Scheduled": {"bg": "#0C4A6E", "fg": "#38BDF8", "border": "#0284C7"},
    "Boarding": {"bg": "#78350F", "fg": "#FCD34D", "border": "#D97706"},
    "Departed": {"bg": "#1E3A8A", "fg": "#93C5FD", "border": "#2563EB"},
    "Arrived": {"bg": "#064E3B", "fg": "#6EE7B7", "border": "#059669"},
    "Delayed": {"bg": "#7F1D1D", "fg": "#FCA5A5", "border": "#DC2626"},
    "Cancelled": {"bg": "#334155", "fg": "#94A3B8", "border": "#475569"}
}

# Flight Types
FLIGHT_TYPES = ["Arrival", "Departure"]

# Gates
GATES_LIST = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]

# Airline presets
POPULAR_AIRLINES = [
    "AeroFlow Airways",
    "SkyJet International",
    "Apex Aviation",
    "Oceanic Express",
    "Starlight Air",
    "Aurora Airways",
    "Pacific Vista Airlines",
    "Horizon Air",
    "Delta Shuttle",
    "Global Wings"
]

# Popular Hubs
POPULAR_AIRPORTS = [
    "JFK - New York",
    "LHR - London Heathrow",
    "DXB - Dubai International",
    "SIN - Singapore Changi",
    "HND - Tokyo Haneda",
    "CDG - Paris Charles de Gaulle",
    "FRA - Frankfurt",
    "SYD - Sydney Kingsford",
    "LAX - Los Angeles",
    "ORD - Chicago O'Hare"
]

