"""
AeroFlow – Flight Management Module
Provides interactive flight registry, validation, addition, modification, and deletion.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, date
import config


class FlightsView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color=config.COLOR_BG)
        self.app_controller = app_controller
        self.data_store = app_controller.data_store

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_toolbar()
        self._build_table_container()
        self.refresh_flights()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 8))
        header_frame.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        title_lbl = ctk.CTkLabel(
            title_box,
            text="Flight Management & Schedules",
            font=config.FONT_TITLE,
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_box,
            text="Register new flights, modify existing schedules, and monitor gate connections",
            font=config.FONT_SUBTITLE,
            text_color=config.COLOR_TEXT_SECONDARY
        )
        subtitle_lbl.pack(anchor="w")

        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Register New Flight",
            font=config.FONT_BODY_BOLD,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_HOVER,
            text_color="#0B1120",
            height=38,
            command=self.open_add_dialog
        )
        add_btn.grid(row=0, column=1, sticky="e")

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_CARD,
            corner_radius=8,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        toolbar.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        toolbar.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)
        inner.grid_columnconfigure(0, weight=1)

        # Search bar
        self.search_entry = ctk.CTkEntry(
            inner,
            placeholder_text="🔍 Search by Flight #, Airline, Origin, or Destination...",
            font=config.FONT_BODY,
            height=36,
            fg_color=config.COLOR_BG,
            border_color=config.COLOR_CARD_BORDER,
            text_color=config.COLOR_TEXT_PRIMARY
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_flights_local())

        # Type filter dropdown
        self.type_filter = ctk.CTkOptionMenu(
            inner,
            values=["All Types", "Arrival", "Departure"],
            font=config.FONT_BODY,
            fg_color=config.COLOR_CARD_ALT,
            button_color=config.COLOR_CARD_HOVER,
            height=36,
            width=120,
            command=lambda v: self.filter_flights_local()
        )
        self.type_filter.grid(row=0, column=1, padx=(0, 10))

        # Status filter dropdown
        self.status_filter = ctk.CTkOptionMenu(
            inner,
            values=["All Statuses"] + config.FLIGHT_STATUSES,
            font=config.FONT_BODY,
            fg_color=config.COLOR_CARD_ALT,
            button_color=config.COLOR_CARD_HOVER,
            height=36,
            width=140,
            command=lambda v: self.filter_flights_local()
        )
        self.status_filter.grid(row=0, column=2, padx=(0, 10))

        # Clear button
        clear_btn = ctk.CTkButton(
            inner,
            text="Reset",
            font=config.FONT_BODY,
            fg_color="transparent",
            hover_color=config.COLOR_CARD_HOVER,
            text_color=config.COLOR_TEXT_SECONDARY,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER,
            width=70,
            height=36,
            command=self.reset_filters
        )
        clear_btn.grid(row=0, column=3)

    def _build_table_container(self):
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

        # Column Headers Frame
        self.th_frame = ctk.CTkFrame(container, fg_color=config.COLOR_TABLE_HEADER, height=38, corner_radius=6)
        self.th_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        self._setup_column_weights(self.th_frame)

        cols = [
            ("ID", 0, "w"),
            ("Flight #", 1, "w"),
            ("Airline", 2, "w"),
            ("Route", 3, "w"),
            ("Type", 4, "w"),
            ("Date", 5, "w"),
            ("Time Window", 6, "w"),
            ("Gate", 7, "w"),
            ("Status", 8, "ew"),
            ("Actions", 9, "ew")
        ]

        for title, col_idx, anchor in cols:
            lbl = ctk.CTkLabel(
                self.th_frame,
                text=title,
                font=config.FONT_SMALL_BOLD,
                text_color=config.COLOR_TEXT_SECONDARY
            )
            lbl.grid(row=0, column=col_idx, padx=6, pady=8, sticky=anchor)

        # Scrollable Rows Container
        self.scroll_table = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.scroll_table.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.scroll_table.grid_columnconfigure(0, weight=1)

        # Status footer count
        self.count_lbl = ctk.CTkLabel(
            container,
            text="Displaying 0 flights",
            font=config.FONT_SMALL,
            text_color=config.COLOR_TEXT_MUTED
        )
        self.count_lbl.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 10))

    def _setup_column_weights(self, frame):
        frame.grid_columnconfigure(0, weight=1, minsize=40)   # ID
        frame.grid_columnconfigure(1, weight=2, minsize=80)   # Flight #
        frame.grid_columnconfigure(2, weight=3, minsize=140)  # Airline
        frame.grid_columnconfigure(3, weight=4, minsize=160)  # Route
        frame.grid_columnconfigure(4, weight=2, minsize=80)   # Type
        frame.grid_columnconfigure(5, weight=2, minsize=85)   # Date
        frame.grid_columnconfigure(6, weight=2, minsize=100)  # Time Window
        frame.grid_columnconfigure(7, weight=2, minsize=65)   # Gate
        frame.grid_columnconfigure(8, weight=2, minsize=100)  # Status
        frame.grid_columnconfigure(9, weight=3, minsize=130)  # Actions

    def refresh_flights(self):
        """Loads all flights from the data store and refreshes table."""
        self.all_flights = self.data_store.get_all_flights()
        self.filter_flights_local()

    def filter_flights_local(self):
        query = self.search_entry.get().strip().lower()
        type_val = self.type_filter.get()
        status_val = self.status_filter.get()

        filtered = []
        for f in self.all_flights:
            if type_val != "All Types" and f["flight_type"] != type_val:
                continue
            if status_val != "All Statuses" and f["status"] != status_val:
                continue
            if query:
                match = (
                    query in f["flight_number"].lower() or
                    query in f["airline"].lower() or
                    query in f["origin"].lower() or
                    query in f["destination"].lower()
                )
                if not match:
                    continue
            filtered.append(f)

        self._render_rows(filtered)

    def reset_filters(self):
        self.search_entry.delete(0, "end")
        self.type_filter.set("All Types")
        self.status_filter.set("All Statuses")
        self.filter_flights_local()

    def _render_rows(self, flights_list):
        for w in self.scroll_table.winfo_children():
            w.destroy()

        self.count_lbl.configure(text=f"Displaying {len(flights_list)} of {len(self.all_flights)} flights")

        if not flights_list:
            empty = ctk.CTkLabel(
                self.scroll_table,
                text="No flight records matching the selected filter criteria.",
                font=config.FONT_BODY,
                text_color=config.COLOR_TEXT_MUTED
            )
            empty.pack(pady=40)
            return

        for idx, fl in enumerate(flights_list):
            bg = config.COLOR_TABLE_ROW if idx % 2 == 0 else config.COLOR_TABLE_ROW_ALT
            row = ctk.CTkFrame(self.scroll_table, fg_color=bg, corner_radius=6)
            row.pack(fill="x", pady=2)
            self._setup_column_weights(row)

            # ID
            ctk.CTkLabel(row, text=str(fl["id"]), font=config.FONT_SMALL, text_color=config.COLOR_TEXT_MUTED).grid(row=0, column=0, padx=6, pady=8, sticky="w")

            # Flight #
            ctk.CTkLabel(row, text=fl["flight_number"], font=config.FONT_BODY_BOLD, text_color=config.COLOR_PRIMARY).grid(row=0, column=1, padx=6, pady=8, sticky="w")

            # Airline
            ctk.CTkLabel(row, text=fl["airline"], font=config.FONT_BODY, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=2, padx=6, pady=8, sticky="w")

            # Route
            origin_code = fl["origin"].split(" - ")[0]
            dest_code = fl["destination"].split(" - ")[0]
            ctk.CTkLabel(row, text=f"{origin_code} ➔ {dest_code}", font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=3, padx=6, pady=8, sticky="w")

            # Type
            type_color = config.COLOR_SUCCESS if fl["flight_type"] == "Arrival" else config.COLOR_SECONDARY
            ctk.CTkLabel(row, text=fl["flight_type"], font=config.FONT_SMALL_BOLD, text_color=type_color).grid(row=0, column=4, padx=6, pady=8, sticky="w")

            # Date
            ctk.CTkLabel(row, text=fl["date"], font=config.FONT_SMALL, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=5, padx=6, pady=8, sticky="w")

            # Time Window
            time_str = f"{fl['start_time']} - {fl['end_time']}"
            ctk.CTkLabel(row, text=time_str, font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=6, padx=6, pady=8, sticky="w")

            # Gate
            gate_str = fl.get("gate", "Unassigned")
            gate_col = config.COLOR_PRIMARY if gate_str != "Unassigned" else config.COLOR_TEXT_MUTED
            ctk.CTkLabel(row, text=gate_str, font=config.FONT_SMALL_BOLD, text_color=gate_col).grid(row=0, column=7, padx=6, pady=8, sticky="w")

            # Status Badge
            st_info = config.STATUS_COLORS.get(fl["status"], {"bg": config.COLOR_CARD, "fg": config.COLOR_TEXT_PRIMARY})
            badge = ctk.CTkFrame(row, fg_color=st_info["bg"], corner_radius=12)
            badge.grid(row=0, column=8, padx=6, pady=6)
            ctk.CTkLabel(badge, text=fl["status"], font=config.FONT_BADGE, text_color=st_info["fg"]).pack(padx=8, pady=2)

            # Action Buttons
            act_frame = ctk.CTkFrame(row, fg_color="transparent")
            act_frame.grid(row=0, column=9, padx=6, pady=6)

            edit_btn = ctk.CTkButton(
                act_frame,
                text="✎ Edit",
                width=55,
                height=26,
                font=config.FONT_SMALL_BOLD,
                fg_color=config.COLOR_CARD_ALT,
                hover_color=config.COLOR_CARD_HOVER,
                text_color=config.COLOR_PRIMARY,
                command=lambda f_id=fl["id"]: self.open_edit_dialog(f_id)
            )
            edit_btn.pack(side="left", padx=2)

            del_btn = ctk.CTkButton(
                act_frame,
                text="🗑",
                width=32,
                height=26,
                font=config.FONT_SMALL_BOLD,
                fg_color="#3A1C20",
                hover_color="#552228",
                text_color=config.COLOR_ERROR,
                command=lambda f_id=fl["id"], fn=fl["flight_number"]: self.confirm_delete_flight(f_id, fn)
            )
            del_btn.pack(side="left", padx=2)

    def open_add_dialog(self):
        FlightFormDialog(self, title="Register New Flight", on_save=self._on_flight_saved)

    def open_edit_dialog(self, flight_id):
        flight = self.data_store.get_flight(flight_id)
        if flight:
            FlightFormDialog(self, title=f"Edit Flight {flight['flight_number']}", flight=flight, on_save=self._on_flight_saved)

    def _on_flight_saved(self):
        self.refresh_flights()
        self.app_controller.refresh_all_views()

    def confirm_delete_flight(self, flight_id, flight_number):
        ans = messagebox.askyesno(
            "Confirm Flight Deletion",
            f"Are you sure you want to remove flight '{flight_number}' from the system?",
            parent=self
        )
        if ans:
            ok, msg = self.data_store.delete_flight(flight_id)
            if ok:
                messagebox.showinfo("Deleted", msg, parent=self)
                self.refresh_flights()
                self.app_controller.refresh_all_views()
            else:
                messagebox.showerror("Error", msg, parent=self)


class FlightFormDialog(ctk.CTkToplevel):
    """Modal dialog for creating and modifying flight records with strict validation."""
    def __init__(self, parent_view, title="Flight Form", flight=None, on_save=None):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.data_store = parent_view.data_store
        self.flight = flight
        self.on_save = on_save

        self.title(title)
        self.geometry("560x680")
        self.resizable(False, False)
        self.configure(fg_color=config.COLOR_SIDEBAR)

        # Modal behaviour
        self.transient(parent_view)
        self.grab_set()

        self._build_form()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 560) // 2
        y = (self.winfo_screenheight() - 680) // 2
        self.geometry(f"+{x}+{y}")

    def _build_form(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 10))

        title_text = "Edit Flight Details" if self.flight else "Register New Flight"
        ctk.CTkLabel(hdr, text=title_text, font=config.FONT_TITLE, text_color=config.COLOR_TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(
            hdr, 
            text="All fields marked with (*) are required. Overlap conflict checks are automatically enforced.",
            font=config.FONT_SMALL, 
            text_color=config.COLOR_TEXT_SECONDARY
        ).pack(anchor="w")

        # Scrollable form container
        form_scroll = ctk.CTkScrollableFrame(self, fg_color=config.COLOR_CARD, corner_radius=10)
        form_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # 1. Flight Number & Airline
        self._add_label(form_scroll, "Flight Number (*): e.g. AF-102")
        self.entry_flight_number = ctk.CTkEntry(form_scroll, font=config.FONT_BODY, height=36)
        self.entry_flight_number.pack(fill="x", pady=(0, 10))

        self._add_label(form_scroll, "Airline (*):")
        self.combo_airline = ctk.CTkComboBox(form_scroll, values=config.POPULAR_AIRLINES, font=config.FONT_BODY, height=36)
        self.combo_airline.pack(fill="x", pady=(0, 10))

        # 2. Flight Type
        self._add_label(form_scroll, "Flight Type (*):")
        self.combo_type = ctk.CTkOptionMenu(form_scroll, values=config.FLIGHT_TYPES, font=config.FONT_BODY, height=36)
        self.combo_type.pack(fill="x", pady=(0, 10))

        # 3. Origin & Destination
        self._add_label(form_scroll, "Origin Airport (*):")
        self.combo_origin = ctk.CTkComboBox(form_scroll, values=config.POPULAR_AIRPORTS, font=config.FONT_BODY, height=36)
        self.combo_origin.pack(fill="x", pady=(0, 10))

        self._add_label(form_scroll, "Destination Airport (*):")
        self.combo_dest = ctk.CTkComboBox(form_scroll, values=config.POPULAR_AIRPORTS, font=config.FONT_BODY, height=36)
        self.combo_dest.pack(fill="x", pady=(0, 10))

        # 4. Schedule Date & Times
        time_row = ctk.CTkFrame(form_scroll, fg_color="transparent")
        time_row.pack(fill="x", pady=(0, 10))
        time_row.grid_columnconfigure((0, 1, 2), weight=1)

        # Date
        ctk.CTkLabel(time_row, text="Date (YYYY-MM-DD)*", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        self.entry_date = ctk.CTkEntry(time_row, font=config.FONT_BODY, height=36)
        self.entry_date.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(4, 0))

        # Start Time
        ctk.CTkLabel(time_row, text="Start (HH:MM)*", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=1, sticky="w")
        self.entry_start_time = ctk.CTkEntry(time_row, font=config.FONT_BODY, height=36)
        self.entry_start_time.grid(row=1, column=1, sticky="ew", padx=3, pady=(4, 0))

        # End Time
        ctk.CTkLabel(time_row, text="End (HH:MM)*", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=2, sticky="w")
        self.entry_end_time = ctk.CTkEntry(time_row, font=config.FONT_BODY, height=36)
        self.entry_end_time.grid(row=1, column=2, sticky="ew", padx=(6, 0), pady=(4, 0))

        # 5. Gate Allocation
        self._add_label(form_scroll, "Gate Assignment:")
        gate_names = ["Unassigned"] + config.GATES_LIST
        self.combo_gate = ctk.CTkOptionMenu(form_scroll, values=gate_names, font=config.FONT_BODY, height=36)
        self.combo_gate.pack(fill="x", pady=(0, 10))

        # 6. Flight Status
        self._add_label(form_scroll, "Flight Status (*):")
        self.combo_status = ctk.CTkOptionMenu(form_scroll, values=config.FLIGHT_STATUSES, font=config.FONT_BODY, height=36)
        self.combo_status.pack(fill="x", pady=(0, 10))

        # Error display banner
        self.error_lbl = ctk.CTkLabel(form_scroll, text="", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_ERROR, wraplength=480)
        self.error_lbl.pack(pady=4)

        # Footer Buttons
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill="x", padx=24, pady=(0, 20))
        btn_box.grid_columnconfigure((0, 1), weight=1)

        cancel_btn = ctk.CTkButton(
            btn_box,
            text="Cancel",
            font=config.FONT_BODY,
            fg_color=config.COLOR_CARD_ALT,
            hover_color=config.COLOR_CARD_HOVER,
            text_color=config.COLOR_TEXT_PRIMARY,
            height=38,
            command=self.destroy
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        save_btn = ctk.CTkButton(
            btn_box,
            text="Save Flight",
            font=config.FONT_BODY_BOLD,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_HOVER,
            text_color="#0B1120",
            height=38,
            command=self.save_flight
        )
        save_btn.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        # Prefill if editing
        if self.flight:
            self.entry_flight_number.insert(0, self.flight["flight_number"])
            self.combo_airline.set(self.flight["airline"])
            self.combo_type.set(self.flight["flight_type"])
            self.combo_origin.set(self.flight["origin"])
            self.combo_dest.set(self.flight["destination"])
            self.entry_date.insert(0, self.flight["date"])
            self.entry_start_time.insert(0, self.flight["start_time"])
            self.entry_end_time.insert(0, self.flight["end_time"])
            self.combo_gate.set(self.flight.get("gate", "Unassigned"))
            self.combo_status.set(self.flight["status"])
        else:
            # Default values for new flight
            self.entry_date.insert(0, date.today().isoformat())
            self.entry_start_time.insert(0, "10:00")
            self.entry_end_time.insert(0, "11:30")
            self.combo_gate.set("Unassigned")
            self.combo_status.set("Scheduled")

    def _add_label(self, parent, text):
        lbl = ctk.CTkLabel(parent, text=text, font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY)
        lbl.pack(anchor="w", pady=(4, 2))

    def save_flight(self):
        f_num = self.entry_flight_number.get().strip().upper()
        airline = self.combo_airline.get().strip()
        f_type = self.combo_type.get()
        origin = self.combo_origin.get().strip()
        dest = self.combo_dest.get().strip()
        f_date = self.entry_date.get().strip()
        start = self.entry_start_time.get().strip()
        end = self.entry_end_time.get().strip()
        gate = self.combo_gate.get()
        status = self.combo_status.get()

        data = {
            "flight_number": f_num,
            "airline": airline,
            "origin": origin,
            "destination": dest,
            "flight_type": f_type,
            "date": f_date,
            "start_time": start,
            "end_time": end,
            "gate": gate,
            "status": status
        }

        if self.flight:
            ok, msg = self.data_store.update_flight(self.flight["id"], data)
        else:
            ok, msg, _ = self.data_store.add_flight(data)

        if ok:
            messagebox.showinfo("Success", msg, parent=self)
            if self.on_save:
                self.on_save()
            self.destroy()
        else:
            self.error_lbl.configure(text=f"⚠ {msg}")
