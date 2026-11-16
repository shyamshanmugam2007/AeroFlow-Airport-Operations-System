"""
AeroFlow – Airport Operations Control
Main Application Entry Point.
Provides desktop window orchestration, dark theme layout, fixed sidebar, and live view routing.
"""

import customtkinter as ctk
from datetime import datetime, date
import sys
import os

# Ensure local imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from data_store import DataStore
from modules.dashboard import DashboardView
from modules.flights import FlightsView
from modules.gates import GatesView
from modules.status import StatusView
from modules.search import SearchView
from modules.reports import ReportsView


class AeroFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Window settings
        self.title(config.APP_TITLE)
        self.geometry("1280x820")
        self.minsize(1080, 680)
        self.configure(fg_color=config.COLOR_BG)

        # In-Memory Data Store Initialization
        self.data_store = DataStore()

        # Grid configuration: Column 0 = Sidebar, Column 1 = Main Workspace
        self.grid_columnconfigure(0, weight=0, minsize=240)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Active view tracker
        self.current_view_name = "dashboard"
        self.views = {}
        self.nav_buttons = {}

        # Build UI layout
        self._build_sidebar()
        self._build_workspace()
        self._init_views()

        # Start live clock
        self._update_clock()

        # Display default view
        self.show_view("dashboard")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_SIDEBAR,
            corner_radius=0,
            border_width=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1) # Spacer push to bottom

        # Brand / Logo Header
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 20))

        logo_title = ctk.CTkLabel(
            logo_frame,
            text="✈ AeroFlow",
            font=(config.FONT_FAMILY, 22, "bold"),
            text_color=config.COLOR_PRIMARY
        )
        logo_title.pack(anchor="w")

        logo_sub = ctk.CTkLabel(
            logo_frame,
            text="Airport Operations Control",
            font=config.FONT_SMALL,
            text_color=config.COLOR_TEXT_SECONDARY
        )
        logo_sub.pack(anchor="w", pady=(2, 0))

        # Divider
        ctk.CTkFrame(self.sidebar, height=1, fg_color=config.COLOR_CARD_BORDER).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))

        # Navigation Items
        nav_items = [
            ("dashboard", "📊  Dashboard", 2),
            ("flights", "✈  Flight Management", 3),
            ("gates", "⛶  Gate Allocation", 4),
            ("status", "⏱  Flight Status", 5),
            ("search", "🔍  Search Flights", 6),
            ("reports", "📈  Reports & Analytics", 7),
        ]

        for key, label, row_idx in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=config.FONT_BODY_BOLD,
                fg_color="transparent",
                hover_color=config.COLOR_SIDEBAR_HOVER,
                text_color=config.COLOR_TEXT_SECONDARY,
                anchor="w",
                height=42,
                corner_radius=8,
                command=lambda k=key: self.show_view(k)
            )
            btn.grid(row=row_idx, column=0, sticky="ew", padx=14, pady=3)
            self.nav_buttons[key] = btn

        # Bottom System Info & Exit Button
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.grid(row=9, column=0, sticky="ew", padx=16, pady=20)

        # Status indicator pill
        status_box = ctk.CTkFrame(bottom_frame, fg_color=config.COLOR_CARD, corner_radius=8, border_width=1, border_color=config.COLOR_CARD_BORDER)
        status_box.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            status_box,
            text="● In-Memory Store Active",
            font=config.FONT_SMALL_BOLD,
            text_color=config.COLOR_SUCCESS
        ).pack(anchor="w", padx=10, pady=(6, 2))

        ctk.CTkLabel(
            status_box,
            text="RAM Engine  |  8 Terminal Gates",
            font=config.FONT_SMALL,
            text_color=config.COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=10, pady=(0, 6))

        # Exit application button
        exit_btn = ctk.CTkButton(
            bottom_frame,
            text="✕ Exit Application",
            font=config.FONT_BODY,
            fg_color="#2A1619",
            hover_color="#451E22",
            text_color=config.COLOR_ERROR,
            height=36,
            corner_radius=8,
            command=self.quit
        )
        exit_btn.pack(fill="x")

    def _build_workspace(self):
        self.workspace = ctk.CTkFrame(self, fg_color=config.COLOR_BG, corner_radius=0)
        self.workspace.grid(row=0, column=1, sticky="nsew")
        self.workspace.grid_rowconfigure(1, weight=1)
        self.workspace.grid_columnconfigure(0, weight=1)

        # Top Header Bar
        top_bar = ctk.CTkFrame(
            self.workspace,
            fg_color=config.COLOR_SIDEBAR,
            height=54,
            corner_radius=0
        )
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        # Left side: Current section breadcrumb
        self.header_title = ctk.CTkLabel(
            top_bar,
            text="Airport Operations Overview",
            font=config.FONT_SECTION,
            text_color=config.COLOR_TEXT_PRIMARY
        )
        self.header_title.grid(row=0, column=0, sticky="w", padx=24, pady=12)

        # Right side: Live Date and Clock
        right_header = ctk.CTkFrame(top_bar, fg_color="transparent")
        right_header.grid(row=0, column=1, sticky="e", padx=24, pady=10)

        self.clock_lbl = ctk.CTkLabel(
            right_header,
            text="--:--:--",
            font=(config.FONT_FAMILY, 13, "bold"),
            text_color=config.COLOR_PRIMARY
        )
        self.clock_lbl.pack(side="right", padx=(8, 0))

        self.date_lbl = ctk.CTkLabel(
            right_header,
            text="Loading date...",
            font=config.FONT_SMALL,
            text_color=config.COLOR_TEXT_SECONDARY
        )
        self.date_lbl.pack(side="right")

        # Main View Display Area
        self.view_container = ctk.CTkFrame(self.workspace, fg_color=config.COLOR_BG, corner_radius=0)
        self.view_container.grid(row=1, column=0, sticky="nsew")
        self.view_container.grid_rowconfigure(0, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)

    def _init_views(self):
        """Initializes all view modules into the view container."""
        self.views["dashboard"] = DashboardView(self.view_container, self)
        self.views["flights"] = FlightsView(self.view_container, self)
        self.views["gates"] = GatesView(self.view_container, self)
        self.views["status"] = StatusView(self.view_container, self)
        self.views["search"] = SearchView(self.view_container, self)
        self.views["reports"] = ReportsView(self.view_container, self)

    def show_view(self, view_name: str):
        """Switches active view and updates sidebar highlights."""
        if view_name not in self.views:
            return

        self.current_view_name = view_name

        # Update sidebar button appearances
        for key, btn in self.nav_buttons.items():
            if key == view_name:
                btn.configure(
                    fg_color=config.COLOR_SIDEBAR_ACTIVE,
                    text_color=config.COLOR_PRIMARY
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=config.COLOR_TEXT_SECONDARY
                )

        # Header title update
        titles = {
            "dashboard": "Airport Operations Dashboard",
            "flights": "Flight Registry & Management",
            "gates": "Gate Allocation & Ramp Control",
            "status": "Flight Status & Operations State",
            "search": "Flight Search & Parameter Filtering",
            "reports": "Airport Analytics & CSV Reporting"
        }
        self.header_title.configure(text=titles.get(view_name, "Operations Control"))

        # Raise active view
        view = self.views[view_name]
        view.tkraise()
        view.grid(row=0, column=0, sticky="nsew")

        # Refresh the active view's data
        if hasattr(view, "refresh_data"):
            view.refresh_data()
        elif hasattr(view, "refresh_flights"):
            view.refresh_flights()
        elif hasattr(view, "refresh_gates"):
            view.refresh_gates()
        elif hasattr(view, "refresh_status_view"):
            view.refresh_status_view()
        elif hasattr(view, "execute_search"):
            view.execute_search()
        elif hasattr(view, "refresh_reports"):
            view.refresh_reports()

    def refresh_all_views(self):
        """Refreshes all view caches so UI remains synchronized across tabs."""
        if "dashboard" in self.views:
            self.views["dashboard"].refresh_data()
        if "flights" in self.views:
            self.views["flights"].refresh_flights()
        if "gates" in self.views:
            self.views["gates"].refresh_gates()
        if "status" in self.views:
            self.views["status"].refresh_status_view()
        if "search" in self.views:
            self.views["search"].execute_search()
        if "reports" in self.views:
            self.views["reports"].refresh_reports()

    def _update_clock(self):
        try:
            if not self.winfo_exists():
                return
            now = datetime.now()
            self.date_lbl.configure(text=now.strftime("%A, %d %B %Y  |  "))
            self.clock_lbl.configure(text=now.strftime("%H:%M:%S Local Time"))
            self._clock_job = self.after(1000, self._update_clock)
        except Exception:
            pass


def main():
    app = AeroFlowApp()
    app.mainloop()


if __name__ == "__main__":
    main()
