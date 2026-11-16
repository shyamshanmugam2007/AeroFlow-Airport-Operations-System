"""
AeroFlow – Search & Filtering Module
Provides deep multi-criteria search by flight number, airline, route, type, date, and status.
"""

import customtkinter as ctk
from datetime import date
import config


class SearchView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color=config.COLOR_BG)
        self.app_controller = app_controller
        self.data_store = app_controller.data_store

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_filters_card()
        self._build_results_table_container()
        self.execute_search()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 8))
        header_frame.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        title_lbl = ctk.CTkLabel(
            title_box,
            text="Flight Search & Query Engine",
            font=config.FONT_TITLE,
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_box,
            text="Query active flights across multiple criteria with instant matching and tabular export",
            font=config.FONT_SUBTITLE,
            text_color=config.COLOR_TEXT_SECONDARY
        )
        subtitle_lbl.pack(anchor="w")

    def _build_filters_card(self):
        filter_card = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        filter_card.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 14))

        # Grid of filter inputs
        grid_frame = ctk.CTkFrame(filter_card, fg_color="transparent")
        grid_frame.pack(fill="x", padx=16, pady=14)
        for c in range(4):
            grid_frame.grid_columnconfigure(c, weight=1)

        # Row 1: Flight Number, Airline, Origin, Destination
        # 1. Flight Number
        ctk.CTkLabel(grid_frame, text="Flight Number:", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=0, sticky="w", padx=6)
        self.entry_flight_num = ctk.CTkEntry(grid_frame, placeholder_text="e.g. AF-101", font=config.FONT_BODY, height=34)
        self.entry_flight_num.grid(row=1, column=0, sticky="ew", padx=6, pady=(2, 8))
        self.entry_flight_num.bind("<KeyRelease>", lambda e: self.execute_search())

        # 2. Airline
        ctk.CTkLabel(grid_frame, text="Airline:", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=1, sticky="w", padx=6)
        self.combo_airline = ctk.CTkOptionMenu(
            grid_frame,
            values=["All"] + config.POPULAR_AIRLINES,
            font=config.FONT_BODY,
            height=34,
            command=lambda v: self.execute_search()
        )
        self.combo_airline.grid(row=1, column=1, sticky="ew", padx=6, pady=(2, 8))

        # 3. Origin
        ctk.CTkLabel(grid_frame, text="Origin Airport:", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=2, sticky="w", padx=6)
        self.entry_origin = ctk.CTkEntry(grid_frame, placeholder_text="e.g. SIN, JFK", font=config.FONT_BODY, height=34)
        self.entry_origin.grid(row=1, column=2, sticky="ew", padx=6, pady=(2, 8))
        self.entry_origin.bind("<KeyRelease>", lambda e: self.execute_search())

        # 4. Destination
        ctk.CTkLabel(grid_frame, text="Destination Airport:", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=3, sticky="w", padx=6)
        self.entry_dest = ctk.CTkEntry(grid_frame, placeholder_text="e.g. LHR, DXB", font=config.FONT_BODY, height=34)
        self.entry_dest.grid(row=1, column=3, sticky="ew", padx=6, pady=(2, 8))
        self.entry_dest.bind("<KeyRelease>", lambda e: self.execute_search())

        # Row 2: Flight Type, Status, Date, Actions
        # 5. Flight Type
        ctk.CTkLabel(grid_frame, text="Flight Type:", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=2, column=0, sticky="w", padx=6)
        self.combo_type = ctk.CTkOptionMenu(
            grid_frame,
            values=["All", "Arrival", "Departure"],
            font=config.FONT_BODY,
            height=34,
            command=lambda v: self.execute_search()
        )
        self.combo_type.grid(row=3, column=0, sticky="ew", padx=6, pady=(2, 4))

        # 6. Status
        ctk.CTkLabel(grid_frame, text="Flight Status:", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=2, column=1, sticky="w", padx=6)
        self.combo_status = ctk.CTkOptionMenu(
            grid_frame,
            values=["All"] + config.FLIGHT_STATUSES,
            font=config.FONT_BODY,
            height=34,
            command=lambda v: self.execute_search()
        )
        self.combo_status.grid(row=3, column=1, sticky="ew", padx=6, pady=(2, 4))

        # 7. Date
        ctk.CTkLabel(grid_frame, text="Scheduled Date (YYYY-MM-DD):", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=2, column=2, sticky="w", padx=6)
        self.entry_date = ctk.CTkEntry(grid_frame, placeholder_text="Leave blank for all dates", font=config.FONT_BODY, height=34)
        self.entry_date.grid(row=3, column=2, sticky="ew", padx=6, pady=(2, 4))
        self.entry_date.bind("<KeyRelease>", lambda e: self.execute_search())

        # 8. Reset Button
        btn_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=3, sticky="ew", padx=6, pady=(2, 4))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        search_btn = ctk.CTkButton(
            btn_frame,
            text="Search",
            font=config.FONT_BODY_BOLD,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_HOVER,
            text_color="#0B1120",
            height=34,
            command=self.execute_search
        )
        search_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        reset_btn = ctk.CTkButton(
            btn_frame,
            text="Clear Filters",
            font=config.FONT_BODY,
            fg_color=config.COLOR_CARD_ALT,
            hover_color=config.COLOR_CARD_HOVER,
            text_color=config.COLOR_TEXT_PRIMARY,
            height=34,
            command=self.clear_filters
        )
        reset_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")

    def _build_results_table_container(self):
        container = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        container.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Header Row
        th = ctk.CTkFrame(container, fg_color=config.COLOR_TABLE_HEADER, height=36, corner_radius=6)
        th.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        self._setup_weights(th)

        cols = ["Flight #", "Airline", "Origin", "Destination", "Type", "Date", "Time Slot", "Gate", "Status"]
        for c, name in enumerate(cols):
            ctk.CTkLabel(th, text=name, font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(
                row=0, column=c, padx=6, pady=8, sticky="w" if c < 8 else "ew"
            )

        # Scrollable rows
        self.scroll_table = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.scroll_table.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))
        self.scroll_table.grid_columnconfigure(0, weight=1)

        # Footer match count
        self.count_lbl = ctk.CTkLabel(
            container,
            text="Query Results: 0 matching flights found",
            font=config.FONT_SMALL,
            text_color=config.COLOR_TEXT_MUTED
        )
        self.count_lbl.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 10))

    def _setup_weights(self, frame):
        frame.grid_columnconfigure(0, weight=2, minsize=80)   # Flight #
        frame.grid_columnconfigure(1, weight=3, minsize=140)  # Airline
        frame.grid_columnconfigure(2, weight=3, minsize=140)  # Origin
        frame.grid_columnconfigure(3, weight=3, minsize=140)  # Destination
        frame.grid_columnconfigure(4, weight=1, minsize=75)   # Type
        frame.grid_columnconfigure(5, weight=2, minsize=85)   # Date
        frame.grid_columnconfigure(6, weight=2, minsize=90)   # Time Slot
        frame.grid_columnconfigure(7, weight=1, minsize=65)   # Gate
        frame.grid_columnconfigure(8, weight=2, minsize=100)  # Status

    def clear_filters(self):
        self.entry_flight_num.delete(0, "end")
        self.combo_airline.set("All")
        self.entry_origin.delete(0, "end")
        self.entry_dest.delete(0, "end")
        self.combo_type.set("All")
        self.combo_status.set("All")
        self.entry_date.delete(0, "end")
        self.execute_search()

    def execute_search(self):
        f_num = self.entry_flight_num.get().strip()
        airline = self.combo_airline.get()
        origin = self.entry_origin.get().strip()
        dest = self.entry_dest.get().strip()
        f_type = self.combo_type.get()
        status = self.combo_status.get()
        f_date = self.entry_date.get().strip()

        results = self.data_store.filter_flights(
            flight_number=f_num,
            airline=airline,
            origin=origin,
            destination=dest,
            flight_type=f_type,
            status=status,
            date_str=f_date
        )

        self._render_results(results)

    def _render_results(self, results):
        for w in self.scroll_table.winfo_children():
            w.destroy()

        self.count_lbl.configure(text=f"Query Results: {len(results)} matching flights found")

        if not results:
            ctk.CTkLabel(
                self.scroll_table,
                text="No flights matching the query parameters.",
                font=config.FONT_BODY,
                text_color=config.COLOR_TEXT_MUTED
            ).pack(pady=40)
            return

        for idx, fl in enumerate(results):
            bg = config.COLOR_TABLE_ROW if idx % 2 == 0 else config.COLOR_TABLE_ROW_ALT
            row = ctk.CTkFrame(self.scroll_table, fg_color=bg, corner_radius=6)
            row.pack(fill="x", pady=2)
            self._setup_weights(row)

            # Flight #
            ctk.CTkLabel(row, text=fl["flight_number"], font=config.FONT_BODY_BOLD, text_color=config.COLOR_PRIMARY).grid(row=0, column=0, padx=6, pady=8, sticky="w")

            # Airline
            ctk.CTkLabel(row, text=fl["airline"], font=config.FONT_BODY, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=1, padx=6, pady=8, sticky="w")

            # Origin
            ctk.CTkLabel(row, text=fl["origin"], font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=2, padx=6, pady=8, sticky="w")

            # Destination
            ctk.CTkLabel(row, text=fl["destination"], font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=3, padx=6, pady=8, sticky="w")

            # Type
            type_col = config.COLOR_SUCCESS if fl["flight_type"] == "Arrival" else config.COLOR_SECONDARY
            ctk.CTkLabel(row, text=fl["flight_type"], font=config.FONT_SMALL_BOLD, text_color=type_col).grid(row=0, column=4, padx=6, pady=8, sticky="w")

            # Date
            ctk.CTkLabel(row, text=fl["date"], font=config.FONT_SMALL, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=5, padx=6, pady=8, sticky="w")

            # Time Slot
            ctk.CTkLabel(row, text=f"{fl['start_time']} - {fl['end_time']}", font=config.FONT_SMALL, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=6, padx=6, pady=8, sticky="w")

            # Gate
            gate_val = fl.get("gate", "Unassigned")
            gate_col = config.COLOR_PRIMARY if gate_val != "Unassigned" else config.COLOR_TEXT_MUTED
            ctk.CTkLabel(row, text=gate_val, font=config.FONT_SMALL_BOLD, text_color=gate_col).grid(row=0, column=7, padx=6, pady=8, sticky="w")

            # Status Badge
            st_color = config.STATUS_COLORS.get(fl["status"], {"bg": config.COLOR_CARD, "fg": config.COLOR_TEXT_PRIMARY})
            badge = ctk.CTkFrame(row, fg_color=st_color["bg"], corner_radius=12)
            badge.grid(row=0, column=8, padx=6, pady=6)
            ctk.CTkLabel(badge, text=fl["status"], font=config.FONT_BADGE, text_color=st_color["fg"]).pack(padx=8, pady=2)
