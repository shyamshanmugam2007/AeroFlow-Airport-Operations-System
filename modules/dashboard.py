"""
AeroFlow – Dashboard Module
Displays high-level KPI cards, embedded Matplotlib analytics, gate occupancy, and recent flights.
"""

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime, date
import config


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color=config.COLOR_BG)
        self.app_controller = app_controller
        self.data_store = app_controller.data_store

        self.canvas_widget = None
        self.fig = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_kpi_cards()
        self._build_main_scrollable()
        self.refresh_data()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        title_lbl = ctk.CTkLabel(
            title_box,
            text="Airport Operations Dashboard",
            font=config.FONT_TITLE,
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_box,
            text="Live overview of active flights, terminal gates, and schedule statuses",
            font=config.FONT_SUBTITLE,
            text_color=config.COLOR_TEXT_SECONDARY
        )
        subtitle_lbl.pack(anchor="w")

        btn_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_box.grid(row=0, column=1, sticky="e")

        add_btn = ctk.CTkButton(
            btn_box,
            text="+ Register Flight",
            font=config.FONT_BODY_BOLD,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_HOVER,
            text_color="#0B1120",
            height=34,
            command=lambda: self.app_controller.views["flights"].open_add_dialog()
        )
        add_btn.pack(side="left", padx=6)

        refresh_btn = ctk.CTkButton(
            btn_box,
            text="↻ Refresh",
            font=config.FONT_BODY,
            fg_color=config.COLOR_CARD,
            hover_color=config.COLOR_CARD_HOVER,
            text_color=config.COLOR_PRIMARY,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER,
            width=85,
            height=34,
            command=self.refresh_data
        )
        refresh_btn.pack(side="left")

    def _build_kpi_cards(self):
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 14))
        for col in range(6):
            self.cards_frame.grid_columnconfigure(col, weight=1, uniform="kpi")

        self.kpi_widgets = {}

        card_defs = [
            ("total_flights", "Total Flights", "✈", config.COLOR_PRIMARY),
            ("arrivals", "Arrivals", "🛬", config.COLOR_SUCCESS),
            ("departures", "Departures", "🛫", config.COLOR_SECONDARY),
            ("delayed_flights", "Delayed", "⚠", config.COLOR_ERROR),
            ("available_gates", "Available Gates", "🚪", config.COLOR_SUCCESS),
            ("occupied_gates", "Occupied Gates", "⛶", config.COLOR_WARNING),
        ]

        for i, (key, label, icon, accent) in enumerate(card_defs):
            card = ctk.CTkFrame(
                self.cards_frame,
                fg_color=config.COLOR_CARD,
                corner_radius=10,
                border_width=1,
                border_color=config.COLOR_CARD_BORDER
            )
            card.grid(row=0, column=i, sticky="nsew", padx=4, pady=2)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(10, 2))

            icon_lbl = ctk.CTkLabel(top_row, text=icon, font=(config.FONT_FAMILY, 14), text_color=accent)
            icon_lbl.pack(side="left")

            title_lbl = ctk.CTkLabel(top_row, text=label, font=config.FONT_CARD_TITLE, text_color=config.COLOR_TEXT_SECONDARY)
            title_lbl.pack(side="left", padx=6)

            val_lbl = ctk.CTkLabel(card, text="0", font=config.FONT_CARD_VALUE, text_color=config.COLOR_TEXT_PRIMARY)
            val_lbl.pack(anchor="w", padx=14, pady=(2, 8))

            self.kpi_widgets[key] = val_lbl

    def _build_main_scrollable(self):
        # Outer scrollable frame to ensure all contents fit perfectly on any screen size
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 16))
        self.main_scroll.grid_columnconfigure(0, weight=1)

        # 1. Gate Occupancy Overview (Cards for G1-G8)
        self._build_gate_occupancy_section()

        # 2. Charts Section (Status Distribution & Arrivals vs Departures)
        self._build_charts_section()

        # 3. Recent Flights Table Section
        self._build_recent_flights_section()

    def _build_gate_occupancy_section(self):
        gate_sec = ctk.CTkFrame(
            self.main_scroll,
            fg_color=config.COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        gate_sec.pack(fill="x", pady=(0, 14))
        gate_sec.grid_columnconfigure(0, weight=1)

        # Section Header
        hdr = ctk.CTkFrame(gate_sec, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 8))
        hdr.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(hdr, text="Terminal Gates Occupancy (G1 – G8)", font=config.FONT_SECTION, text_color=config.COLOR_TEXT_PRIMARY)
        lbl.grid(row=0, column=0, sticky="w")

        manage_gates_btn = ctk.CTkButton(
            hdr,
            text="Manage Gate Allocations →",
            font=config.FONT_SMALL_BOLD,
            fg_color="transparent",
            hover_color=config.COLOR_SIDEBAR_ACTIVE,
            text_color=config.COLOR_PRIMARY,
            height=26,
            command=lambda: self.app_controller.show_view("gates")
        )
        manage_gates_btn.grid(row=0, column=1, sticky="e")

        # Container for 8 Gate mini-cards
        self.gate_cards_grid = ctk.CTkFrame(gate_sec, fg_color="transparent")
        self.gate_cards_grid.pack(fill="x", padx=16, pady=(0, 14))
        for col in range(8):
            self.gate_cards_grid.grid_columnconfigure(col, weight=1, uniform="gate_col")

    def _build_charts_section(self):
        chart_sec = ctk.CTkFrame(
            self.main_scroll,
            fg_color=config.COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        chart_sec.pack(fill="x", pady=(0, 14))

        hdr = ctk.CTkFrame(chart_sec, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 6))

        lbl = ctk.CTkLabel(hdr, text="Operations & Flight Distribution Analytics", font=config.FONT_SECTION, text_color=config.COLOR_TEXT_PRIMARY)
        lbl.pack(side="left")

        self.chart_container = ctk.CTkFrame(chart_sec, fg_color="#121A2B", corner_radius=8)
        self.chart_container.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def _build_recent_flights_section(self):
        table_sec = ctk.CTkFrame(
            self.main_scroll,
            fg_color=config.COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        table_sec.pack(fill="x", pady=(0, 10))

        hdr = ctk.CTkFrame(table_sec, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 8))
        hdr.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(hdr, text="Recent Flight Schedules", font=config.FONT_SECTION, text_color=config.COLOR_TEXT_PRIMARY)
        lbl.grid(row=0, column=0, sticky="w")

        all_fl_btn = ctk.CTkButton(
            hdr,
            text="Open Flight Registry →",
            font=config.FONT_SMALL_BOLD,
            fg_color="transparent",
            hover_color=config.COLOR_SIDEBAR_ACTIVE,
            text_color=config.COLOR_PRIMARY,
            height=26,
            command=lambda: self.app_controller.show_view("flights")
        )
        all_fl_btn.grid(row=0, column=1, sticky="e")

        self.recent_table_container = ctk.CTkFrame(table_sec, fg_color="transparent")
        self.recent_table_container.pack(fill="x", padx=16, pady=(0, 14))

    def refresh_data(self):
        """Re-calculates dynamic statistics and re-renders cards, charts, and table."""
        metrics = self.data_store.get_dashboard_metrics()

        # Update KPI values
        for key in ["total_flights", "arrivals", "departures", "delayed_flights", "available_gates", "occupied_gates"]:
            if key in self.kpi_widgets:
                self.kpi_widgets[key].configure(text=str(metrics.get(key, 0)))

        # Update Gate Mini-Cards
        self._render_gate_cards(metrics["gate_cards"])

        # Update Embedded Matplotlib Charts
        self._render_charts(metrics)

        # Update Recent Flights
        self._render_recent_table(metrics["recent_flights"])

    def _render_gate_cards(self, gate_cards):
        for w in self.gate_cards_grid.winfo_children():
            w.destroy()

        for col_idx, g in enumerate(gate_cards):
            is_occ = g["status"] == "Occupied"
            card_border = config.COLOR_WARNING if is_occ else config.COLOR_SUCCESS
            badge_bg = "#78350F" if is_occ else "#064E3B"
            badge_fg = "#FCD34D" if is_occ else "#6EE7B7"

            card = ctk.CTkFrame(
                self.gate_cards_grid,
                fg_color=config.COLOR_CARD_ALT,
                corner_radius=8,
                border_width=1,
                border_color=card_border
            )
            card.grid(row=0, column=col_idx, padx=3, pady=4, sticky="nsew")

            # Gate Name
            ctk.CTkLabel(card, text=g["gate_id"], font=(config.FONT_FAMILY, 14, "bold"), text_color=config.COLOR_TEXT_PRIMARY).pack(pady=(6, 2))

            # Status pill
            badge = ctk.CTkFrame(card, fg_color=badge_bg, corner_radius=10)
            badge.pack(padx=4, pady=2)
            ctk.CTkLabel(badge, text=g["status"], font=config.FONT_BADGE, text_color=badge_fg).pack(padx=6, pady=1)

            # Flight text
            fl_text = g["flight_number"]
            ctk.CTkLabel(card, text=fl_text, font=config.FONT_SMALL_BOLD, text_color=config.COLOR_PRIMARY if is_occ else config.COLOR_TEXT_MUTED).pack(pady=(2, 6))

    def _render_charts(self, metrics):
        # Clear existing canvas if present
        if self.canvas_widget:
            self.canvas_widget.destroy()
            if self.fig:
                plt.close(self.fig)

        status_counts = metrics["status_counts"]
        total = metrics["total_flights"] or 1

        # Create Matplotlib Figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 3.2), facecolor="#121A2B")
        self.fig = fig
        fig.subplots_adjust(left=0.08, right=0.92, top=0.88, bottom=0.15, wspace=0.35)

        # 1. Donut Chart - Flight Status Distribution
        labels = []
        sizes = []
        colors = []
        color_map = {
            "Scheduled": "#38BDF8",
            "Boarding": "#F59E0B",
            "Departed": "#2563EB",
            "Arrived": "#22C55E",
            "Delayed": "#EF4444",
            "Cancelled": "#64748B"
        }

        for st in config.FLIGHT_STATUSES:
            cnt = status_counts.get(st, 0)
            if cnt > 0:
                labels.append(f"{st} ({cnt})")
                sizes.append(cnt)
                colors.append(color_map.get(st, "#38BDF8"))

        if not sizes:
            sizes = [1]
            labels = ["No Data"]
            colors = ["#334155"]

        wedges, texts, autotexts = ax1.pie(
            sizes,
            labels=labels,
            autopct="%1.0f%%" if sum(sizes) > 0 and labels[0] != "No Data" else "",
            colors=colors,
            startangle=140,
            pctdistance=0.75,
            textprops={"color": "#94A3B8", "fontsize": 8}
        )
        for at in autotexts:
            at.set_color("#FFFFFF")
            at.set_fontsize(8)
            at.set_weight("bold")

        # Centre white circle to make donut
        centre_circle = plt.Circle((0, 0), 0.55, fc="#121A2B")
        ax1.add_artist(centre_circle)
        ax1.set_title("Flight Status Distribution", color="#F8FAFC", fontsize=10, fontweight="bold", pad=8)

        # 2. Bar Chart - Arrivals vs Departures
        arr_cnt = metrics["arrivals"]
        dep_cnt = metrics["departures"]
        categories = ["Arrivals", "Departures"]
        bar_counts = [arr_cnt, dep_cnt]
        bar_colors = ["#22C55E", "#2563EB"]

        bars = ax2.bar(categories, bar_counts, color=bar_colors, width=0.45, edgecolor="#1E2A42", linewidth=1)
        ax2.set_facecolor("#121A2B")
        ax2.tick_params(colors="#94A3B8", labelsize=9)
        ax2.spines["bottom"].set_color("#1E2A42")
        ax2.spines["left"].set_color("#1E2A42")
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.set_title("Arrivals vs Departures", color="#F8FAFC", fontsize=10, fontweight="bold", pad=8)
        ax2.yaxis.grid(True, linestyle="--", alpha=0.3, color="#334155")

        # Value labels above bars
        for b in bars:
            h = b.get_height()
            ax2.annotate(f"{h}",
                         xy=(b.get_x() + b.get_width() / 2, h),
                         xytext=(0, 3),
                         textcoords="offset points",
                         ha="center", va="bottom",
                         color="#F8FAFC", fontsize=9, fontweight="bold")

        # Mount into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=4, pady=4)

    def _render_recent_table(self, recent_flights):
        for w in self.recent_table_container.winfo_children():
            w.destroy()

        if not recent_flights:
            ctk.CTkLabel(
                self.recent_table_container,
                text="No flights registered.",
                font=config.FONT_BODY,
                text_color=config.COLOR_TEXT_MUTED
            ).pack(pady=20)
            return

        # Header Row
        th = ctk.CTkFrame(self.recent_table_container, fg_color=config.COLOR_TABLE_HEADER, corner_radius=6, height=32)
        th.pack(fill="x", pady=(0, 4))
        th.grid_columnconfigure(0, weight=2)
        th.grid_columnconfigure(1, weight=3)
        th.grid_columnconfigure(2, weight=3)
        th.grid_columnconfigure(3, weight=1)
        th.grid_columnconfigure(4, weight=2)
        th.grid_columnconfigure(5, weight=1)
        th.grid_columnconfigure(6, weight=2)

        cols = ["Flight #", "Airline", "Route", "Type", "Time Slot", "Gate", "Status"]
        for c, name in enumerate(cols):
            ctk.CTkLabel(
                th, text=name, font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY
            ).grid(row=0, column=c, padx=8, pady=6, sticky="w" if c < 6 else "ew")

        # Data Rows
        for idx, fl in enumerate(recent_flights):
            bg = config.COLOR_TABLE_ROW if idx % 2 == 0 else config.COLOR_TABLE_ROW_ALT
            row = ctk.CTkFrame(self.recent_table_container, fg_color=bg, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(0, weight=2)
            row.grid_columnconfigure(1, weight=3)
            row.grid_columnconfigure(2, weight=3)
            row.grid_columnconfigure(3, weight=1)
            row.grid_columnconfigure(4, weight=2)
            row.grid_columnconfigure(5, weight=1)
            row.grid_columnconfigure(6, weight=2)

            # Flight #
            ctk.CTkLabel(row, text=fl["flight_number"], font=config.FONT_BODY_BOLD, text_color=config.COLOR_PRIMARY).grid(row=0, column=0, padx=8, pady=7, sticky="w")

            # Airline
            ctk.CTkLabel(row, text=fl["airline"], font=config.FONT_BODY, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=1, padx=8, pady=7, sticky="w")

            # Route
            origin_c = fl["origin"].split(" - ")[0]
            dest_c = fl["destination"].split(" - ")[0]
            ctk.CTkLabel(row, text=f"{origin_c} ➔ {dest_c}", font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=2, padx=8, pady=7, sticky="w")

            # Type
            type_col = config.COLOR_SUCCESS if fl["flight_type"] == "Arrival" else config.COLOR_SECONDARY
            ctk.CTkLabel(row, text=fl["flight_type"], font=config.FONT_SMALL_BOLD, text_color=type_col).grid(row=0, column=3, padx=8, pady=7, sticky="w")

            # Time Slot
            time_slot = f"{fl['start_time']} - {fl['end_time']}"
            ctk.CTkLabel(row, text=time_slot, font=config.FONT_SMALL, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=4, padx=8, pady=7, sticky="w")

            # Gate
            gate_val = fl.get("gate", "Unassigned")
            gate_col = config.COLOR_PRIMARY if gate_val != "Unassigned" else config.COLOR_TEXT_MUTED
            ctk.CTkLabel(row, text=gate_val, font=config.FONT_SMALL_BOLD, text_color=gate_col).grid(row=0, column=5, padx=8, pady=7, sticky="w")

            # Status Badge
            st_color = config.STATUS_COLORS.get(fl["status"], {"bg": config.COLOR_CARD, "fg": config.COLOR_TEXT_PRIMARY})
            badge = ctk.CTkFrame(row, fg_color=st_color["bg"], corner_radius=12)
            badge.grid(row=0, column=6, padx=8, pady=5)
            ctk.CTkLabel(badge, text=fl["status"], font=config.FONT_BADGE, text_color=st_color["fg"]).pack(padx=8, pady=2)
