"""
AeroFlow – Reports & Analytics Module
Provides statistical metrics, embedded Matplotlib visualizations, and CSV export.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import date
import config


class ReportsView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color=config.COLOR_BG)
        self.app_controller = app_controller
        self.data_store = app_controller.data_store

        self.canvas_widget = None
        self.fig = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_main_scrollable()
        self.refresh_reports()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        title_lbl = ctk.CTkLabel(
            title_box,
            text="Airport Analytics & Operations Reports",
            font=config.FONT_TITLE,
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_box,
            text="Current gate occupancy, flight assignment distribution, and CSV reporting",
            font=config.FONT_SUBTITLE,
            text_color=config.COLOR_TEXT_SECONDARY
        )
        subtitle_lbl.pack(anchor="w")

        btn_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_box.grid(row=0, column=1, sticky="e")

        export_btn = ctk.CTkButton(
            btn_box,
            text="📥 Export Flights CSV",
            font=config.FONT_BODY_BOLD,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_HOVER,
            text_color="#0B1120",
            height=36,
            command=self.export_csv
        )
        export_btn.pack(side="left", padx=6)

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
            height=36,
            command=self.refresh_reports
        )
        refresh_btn.pack(side="left")

    def _build_main_scrollable(self):
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        self.main_scroll.grid_columnconfigure(0, weight=1)

        # 1. Summary KPI Cards
        self._build_kpi_cards()

        # 2. Charts Container (Matplotlib)
        self._build_charts_section()

        # 3. Gate Utilisation Detailed Breakdown Table
        self._build_gate_utilisation_table()

    def _build_kpi_cards(self):
        cards_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 14))
        for col in range(6):
            cards_frame.grid_columnconfigure(col, weight=1, uniform="rep_kpi")

        self.kpi_widgets = {}

        card_defs = [
            ("total_flights", "Total Flights", "✈", config.COLOR_PRIMARY),
            ("arrivals", "Arrivals", "🛬", config.COLOR_SUCCESS),
            ("departures", "Departures", "🛫", config.COLOR_SECONDARY),
            ("delayed_flights", "Delayed", "⚠", config.COLOR_ERROR),
            ("cancelled_flights", "Cancelled", "✕", config.COLOR_MUTED),
            ("gate_utilisation", "Current Gate Occupancy", "📈", config.COLOR_WARNING),
        ]

        for i, (key, label, icon, accent) in enumerate(card_defs):
            card = ctk.CTkFrame(
                cards_frame,
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

    def _build_charts_section(self):
        chart_card = ctk.CTkFrame(
            self.main_scroll,
            fg_color=config.COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        chart_card.pack(fill="x", pady=(0, 14))

        hdr = ctk.CTkFrame(chart_card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 6))

        lbl = ctk.CTkLabel(
            hdr,
            text="Visual Analytics: Flight Assignments & Status Distribution",
            font=config.FONT_SECTION,
            text_color=config.COLOR_TEXT_PRIMARY
        )
        lbl.pack(side="left")

        self.chart_container = ctk.CTkFrame(chart_card, fg_color="#121A2B", corner_radius=8)
        self.chart_container.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def _build_gate_utilisation_table(self):
        table_card = ctk.CTkFrame(
            self.main_scroll,
            fg_color=config.COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        table_card.pack(fill="x", pady=(0, 10))

        hdr = ctk.CTkFrame(table_card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 8))

        lbl = ctk.CTkLabel(
            hdr,
            text="Gate Assignment Share & Terminal Overview",
            font=config.FONT_SECTION,
            text_color=config.COLOR_TEXT_PRIMARY
        )
        lbl.pack(side="left")

        # Table Header
        th = ctk.CTkFrame(table_card, fg_color=config.COLOR_TABLE_HEADER, corner_radius=6, height=34)
        th.pack(fill="x", padx=16, pady=(0, 4))
        th.grid_columnconfigure(0, weight=1) # Gate
        th.grid_columnconfigure(1, weight=2) # Terminal
        th.grid_columnconfigure(2, weight=2) # Flights Allocated
        th.grid_columnconfigure(3, weight=2) # Assignment share
        th.grid_columnconfigure(4, weight=3) # Current State / Assignment

        for c, name in enumerate(["Gate ID", "Terminal Location", "Total Scheduled Flights", "Assignment Share", "Operational Status"]):
            ctk.CTkLabel(th, text=name, font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(
                row=0, column=c, padx=8, pady=7, sticky="w" if c < 4 else "ew"
            )

        self.utilisation_table_container = ctk.CTkFrame(table_card, fg_color="transparent")
        self.utilisation_table_container.pack(fill="x", padx=16, pady=(0, 14))

    def refresh_reports(self):
        """Calculates dynamic report metrics from the in-memory data store."""
        metrics = self.data_store.get_dashboard_metrics()
        all_flights = self.data_store.get_all_flights()
        total_fl = len(all_flights)

        # Current occupancy ratio (not time-based utilisation).
        gate_cards = self.data_store.get_gate_card_data()
        occupied_cnt = sum(1 for g in gate_cards if g["status"] == "Occupied")
        total_gates = len(gate_cards) or 1
        utilisation_pct = round((occupied_cnt / total_gates) * 100)

        # Update KPI Cards
        self.kpi_widgets["total_flights"].configure(text=str(total_fl))
        self.kpi_widgets["arrivals"].configure(text=str(metrics["arrivals"]))
        self.kpi_widgets["departures"].configure(text=str(metrics["departures"]))
        self.kpi_widgets["delayed_flights"].configure(text=str(metrics["delayed_flights"]))
        self.kpi_widgets["cancelled_flights"].configure(text=str(metrics["cancelled_flights"]))
        self.kpi_widgets["gate_utilisation"].configure(text=f"{utilisation_pct}%")

        # Render Embedded Matplotlib Visuals
        self._render_charts(all_flights, metrics, gate_cards)

        # Render Utilisation Table
        self._render_utilisation_table(gate_cards, all_flights)

    def _render_charts(self, all_flights, metrics, gate_cards):
        if self.canvas_widget:
            self.canvas_widget.destroy()
            if self.fig:
                plt.close(self.fig)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 3.4), facecolor="#121A2B")
        self.fig = fig
        fig.subplots_adjust(left=0.08, right=0.92, top=0.86, bottom=0.18, wspace=0.35)

        # 1. Gate Assignment Count: Flights per Gate (G1 to G8)
        gate_counts = {gid: 0 for gid in config.GATES_LIST}
        for f in all_flights:
            g = f.get("gate", "Unassigned")
            if g in gate_counts and f["status"] != "Cancelled":
                gate_counts[g] += 1

        gates = list(gate_counts.keys())
        counts = list(gate_counts.values())
        bar_colors = ["#38BDF8" if c > 0 else "#334155" for c in counts]

        bars = ax1.bar(gates, counts, color=bar_colors, width=0.55, edgecolor="#1E2A42")
        ax1.set_facecolor("#121A2B")
        ax1.tick_params(colors="#94A3B8", labelsize=8)
        ax1.spines["bottom"].set_color("#1E2A42")
        ax1.spines["left"].set_color("#1E2A42")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.set_title("Flights Allocated per Gate", color="#F8FAFC", fontsize=10, fontweight="bold", pad=8)
        ax1.yaxis.grid(True, linestyle="--", alpha=0.3, color="#334155")

        for b in bars:
            h = b.get_height()
            ax1.annotate(f"{h}",
                         xy=(b.get_x() + b.get_width() / 2, h),
                         xytext=(0, 2),
                         textcoords="offset points",
                         ha="center", va="bottom",
                         color="#F8FAFC", fontsize=8, fontweight="bold")

        # 2. Status Distribution Donut Chart
        status_counts = metrics["status_counts"]
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
            labels = ["No Flights"]
            colors = ["#334155"]

        ax2.pie(
            sizes,
            labels=labels,
            autopct="%1.0f%%" if sum(sizes) > 0 and labels[0] != "No Flights" else "",
            colors=colors,
            startangle=140,
            pctdistance=0.75,
            textprops={"color": "#94A3B8", "fontsize": 8}
        )
        centre_circle = plt.Circle((0, 0), 0.55, fc="#121A2B")
        ax2.add_artist(centre_circle)
        ax2.set_title("Flight Status Distribution", color="#F8FAFC", fontsize=10, fontweight="bold", pad=8)

        # Mount into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=4, pady=4)

    def _render_utilisation_table(self, gate_cards, all_flights):
        for w in self.utilisation_table_container.winfo_children():
            w.destroy()

        # Count flights assigned to each gate
        gate_flight_map = {g["gate_id"]: [] for g in gate_cards}
        for f in all_flights:
            g = f.get("gate", "Unassigned")
            if g in gate_flight_map and f["status"] != "Cancelled":
                gate_flight_map[g].append(f)

        total_scheduled = sum(len(fls) for fls in gate_flight_map.values()) or 1

        for idx, g in enumerate(gate_cards):
            gid = g["gate_id"]
            term = g["terminal"]
            fls = gate_flight_map.get(gid, [])
            count = len(fls)
            pct = int((count / total_scheduled) * 100)

            bg = config.COLOR_TABLE_ROW if idx % 2 == 0 else config.COLOR_TABLE_ROW_ALT
            row = ctk.CTkFrame(self.utilisation_table_container, fg_color=bg, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=2)
            row.grid_columnconfigure(2, weight=2)
            row.grid_columnconfigure(3, weight=2)
            row.grid_columnconfigure(4, weight=3)

            # Gate ID
            ctk.CTkLabel(row, text=gid, font=config.FONT_BODY_BOLD, text_color=config.COLOR_PRIMARY).grid(row=0, column=0, padx=8, pady=7, sticky="w")

            # Terminal
            ctk.CTkLabel(row, text=term, font=config.FONT_BODY, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=1, padx=8, pady=7, sticky="w")

            # Count
            ctk.CTkLabel(row, text=f"{count} flights", font=config.FONT_BODY_BOLD, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=2, padx=8, pady=7, sticky="w")

            # Share of all assigned flights (not time-based gate utilisation).
            ctk.CTkLabel(row, text=f"{pct}% of assigned flights", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_WARNING if pct > 15 else config.COLOR_TEXT_SECONDARY).grid(row=0, column=3, padx=8, pady=7, sticky="w")

            # Operational Status
            is_occ = g["status"] == "Occupied"
            st_text = f"Occupied by {g['flight_number']}" if is_occ else "Available / Clear"
            st_col = config.COLOR_WARNING if is_occ else config.COLOR_SUCCESS
            ctk.CTkLabel(row, text=st_text, font=config.FONT_SMALL_BOLD, text_color=st_col).grid(row=0, column=4, padx=8, pady=7, sticky="ew")

    def export_csv(self):
        default_filename = f"aeroflow_flights_export_{date.today().isoformat()}.csv"
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Export Flights Data to CSV",
            initialfile=default_filename,
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        ok, msg = self.data_store.export_to_csv(file_path)
        if ok:
            messagebox.showinfo("Export Successful", msg, parent=self)
        else:
            messagebox.showerror("Export Failed", msg, parent=self)
