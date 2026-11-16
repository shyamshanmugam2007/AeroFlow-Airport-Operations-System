"""
AeroFlow – Gate Allocation Module
Manages terminal gate assignments, conflict detection, automatic gate suggestion, and releases.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, date
import config


class GatesView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color=config.COLOR_BG)
        self.app_controller = app_controller
        self.data_store = app_controller.data_store

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_main_content()
        self.refresh_gates()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        title_lbl = ctk.CTkLabel(
            title_box,
            text="Gate Allocation & Ramp Control",
            font=config.FONT_TITLE,
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_box,
            text="Manage ramp positions, monitor time overlaps, and allocate aircraft to terminal gates",
            font=config.FONT_SUBTITLE,
            text_color=config.COLOR_TEXT_SECONDARY
        )
        subtitle_lbl.pack(anchor="w")

        # Stats summary pill
        self.summary_pill = ctk.CTkLabel(
            header_frame,
            text="Loading Gates...",
            font=config.FONT_BODY_BOLD,
            text_color=config.COLOR_PRIMARY
        )
        self.summary_pill.grid(row=0, column=1, sticky="e")

    def _build_main_content(self):
        self.scroll_content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        self.scroll_content.grid_columnconfigure(0, weight=1)

        # 1. Interactive Gate Allocation Tool
        self._build_allocation_control_panel()

        # 2. Visual Gate Cards Grid (G1 - G8)
        self._build_visual_cards_section()

        # 3. Comprehensive Master Gate Schedule Table
        self._build_schedule_table_section()

    def _build_allocation_control_panel(self):
        panel = ctk.CTkFrame(
            self.scroll_content,
            fg_color=config.COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        panel.pack(fill="x", pady=(0, 16))

        hdr = ctk.CTkFrame(panel, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(
            hdr,
            text="Interactive Gate Allocation & Reassignment",
            font=config.FONT_SECTION,
            text_color=config.COLOR_TEXT_PRIMARY
        ).pack(anchor="w")
        ctk.CTkLabel(
            hdr,
            text="Select a flight to evaluate real-time conflict conditions: new_start < existing_end AND new_end > existing_start",
            font=config.FONT_SMALL,
            text_color=config.COLOR_TEXT_SECONDARY
        ).pack(anchor="w")

        # Form controls
        ctrl_frame = ctk.CTkFrame(panel, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=16, pady=(4, 14))
        ctrl_frame.grid_columnconfigure(0, weight=3) # Flight dropdown
        ctrl_frame.grid_columnconfigure(1, weight=1) # Gate dropdown
        ctrl_frame.grid_columnconfigure(2, weight=1) # Suggest Button
        ctrl_frame.grid_columnconfigure(3, weight=1) # Assign Button
        ctrl_frame.grid_columnconfigure(4, weight=1) # Release Button

        # Flight Selector
        ctk.CTkLabel(ctrl_frame, text="Select Flight:", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=0, sticky="w", padx=4)
        self.flight_combobox = ctk.CTkComboBox(
            ctrl_frame,
            values=["Loading flights..."],
            font=config.FONT_BODY,
            height=36,
            command=self._on_flight_selected
        )
        self.flight_combobox.grid(row=1, column=0, sticky="ew", padx=4, pady=(2, 0))

        # Gate Selector
        ctk.CTkLabel(ctrl_frame, text="Assign Gate:", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=1, sticky="w", padx=4)
        self.gate_combobox = ctk.CTkOptionMenu(
            ctrl_frame,
            values=config.GATES_LIST,
            font=config.FONT_BODY,
            height=36
        )
        self.gate_combobox.grid(row=1, column=1, sticky="ew", padx=4, pady=(2, 0))

        # Suggest Gate Button
        self.suggest_btn = ctk.CTkButton(
            ctrl_frame,
            text="⚡ Suggest Gates",
            font=config.FONT_BODY_BOLD,
            fg_color=config.COLOR_SECONDARY,
            hover_color=config.COLOR_SECONDARY_HOVER,
            text_color=config.COLOR_TEXT_PRIMARY,
            height=36,
            command=self.suggest_gates_for_selected
        )
        self.suggest_btn.grid(row=1, column=2, sticky="ew", padx=4, pady=(2, 0))

        # Assign Button
        self.assign_btn = ctk.CTkButton(
            ctrl_frame,
            text="✓ Allocate Gate",
            font=config.FONT_BODY_BOLD,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_HOVER,
            text_color="#0B1120",
            height=36,
            command=self.allocate_gate_selected
        )
        self.assign_btn.grid(row=1, column=3, sticky="ew", padx=4, pady=(2, 0))

        # Release Button
        self.release_btn = ctk.CTkButton(
            ctrl_frame,
            text="✕ Release Gate",
            font=config.FONT_BODY,
            fg_color="#3A1C20",
            hover_color="#552228",
            text_color=config.COLOR_ERROR,
            height=36,
            command=self.release_gate_selected
        )
        self.release_btn.grid(row=1, column=4, sticky="ew", padx=4, pady=(2, 0))

        # Status / Feedback label
        self.feedback_lbl = ctk.CTkLabel(
            panel,
            text="",
            font=config.FONT_SMALL_BOLD,
            text_color=config.COLOR_PRIMARY
        )
        self.feedback_lbl.pack(anchor="w", padx=20, pady=(0, 10))

    def _build_visual_cards_section(self):
        sec = ctk.CTkFrame(
            self.scroll_content,
            fg_color=config.COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        sec.pack(fill="x", pady=(0, 16))

        hdr = ctk.CTkFrame(sec, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(
            hdr,
            text="Airport Terminal Gates Status (G1 – G8)",
            font=config.FONT_SECTION,
            text_color=config.COLOR_TEXT_PRIMARY
        ).pack(side="left")

        # 4x2 Grid for 8 Gates
        self.cards_grid = ctk.CTkFrame(sec, fg_color="transparent")
        self.cards_grid.pack(fill="x", padx=16, pady=(0, 16))
        for col in range(4):
            self.cards_grid.grid_columnconfigure(col, weight=1, uniform="gate_card")

    def _build_schedule_table_section(self):
        sec = ctk.CTkFrame(
            self.scroll_content,
            fg_color=config.COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        sec.pack(fill="x", pady=(0, 16))

        hdr = ctk.CTkFrame(sec, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(
            hdr,
            text="Master Gate Occupancy & Daily Schedule",
            font=config.FONT_SECTION,
            text_color=config.COLOR_TEXT_PRIMARY
        ).pack(side="left")

        # Table Header
        th = ctk.CTkFrame(sec, fg_color=config.COLOR_TABLE_HEADER, corner_radius=6, height=34)
        th.pack(fill="x", padx=16, pady=(0, 4))
        th.grid_columnconfigure(0, weight=1) # Gate
        th.grid_columnconfigure(1, weight=1) # Terminal
        th.grid_columnconfigure(2, weight=2) # Flight #
        th.grid_columnconfigure(3, weight=3) # Airline
        th.grid_columnconfigure(4, weight=3) # Route
        th.grid_columnconfigure(5, weight=2) # Date
        th.grid_columnconfigure(6, weight=2) # Time Window
        th.grid_columnconfigure(7, weight=2) # Status
        th.grid_columnconfigure(8, weight=1) # Action

        cols = ["Gate", "Terminal", "Flight #", "Airline", "Route", "Date", "Time Slot", "Status", "Release"]
        for c, name in enumerate(cols):
            ctk.CTkLabel(th, text=name, font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(
                row=0, column=c, padx=6, pady=7, sticky="w" if c < 7 else "ew"
            )

        self.schedule_table_container = ctk.CTkFrame(sec, fg_color="transparent")
        self.schedule_table_container.pack(fill="x", padx=16, pady=(0, 14))

    def refresh_gates(self):
        """Refreshes all cards, dropdowns, and schedule rows."""
        gate_cards = self.data_store.get_gate_card_data()
        avail_cnt = sum(1 for g in gate_cards if g["status"] == "Available")
        occ_cnt = len(gate_cards) - avail_cnt
        self.summary_pill.configure(
            text=f"Total Gates: {len(gate_cards)}   |   Available: {avail_cnt}   |   Occupied: {occ_cnt}"
        )

        self._render_gate_cards(gate_cards)
        self._populate_flight_selector()
        self._render_master_schedule()

    def _render_gate_cards(self, gate_cards):
        for w in self.cards_grid.winfo_children():
            w.destroy()

        for idx, g in enumerate(gate_cards):
            r = idx // 4
            c = idx % 4
            is_occ = g["status"] == "Occupied"
            border_col = config.COLOR_WARNING if is_occ else config.COLOR_SUCCESS
            badge_bg = "#78350F" if is_occ else "#064E3B"
            badge_fg = "#FCD34D" if is_occ else "#6EE7B7"

            card = ctk.CTkFrame(
                self.cards_grid,
                fg_color=config.COLOR_CARD_ALT,
                corner_radius=10,
                border_width=1,
                border_color=border_col
            )
            card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")

            # Header row inside card
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(10, 4))
            top.grid_columnconfigure(0, weight=1)

            # Gate name & Terminal
            gate_name_lbl = ctk.CTkLabel(
                top,
                text=g["gate_id"],
                font=(config.FONT_FAMILY, 16, "bold"),
                text_color=config.COLOR_TEXT_PRIMARY
            )
            gate_name_lbl.grid(row=0, column=0, sticky="w")

            term_lbl = ctk.CTkLabel(
                top,
                text=g["terminal"],
                font=config.FONT_SMALL,
                text_color=config.COLOR_TEXT_SECONDARY
            )
            term_lbl.grid(row=1, column=0, sticky="w")

            # Status Badge
            badge = ctk.CTkFrame(top, fg_color=badge_bg, corner_radius=12)
            badge.grid(row=0, column=1, rowspan=2, sticky="e")
            ctk.CTkLabel(badge, text=g["status"], font=config.FONT_BADGE, text_color=badge_fg).pack(padx=8, pady=2)

            # Divider
            ctk.CTkFrame(card, height=1, fg_color=config.COLOR_CARD_BORDER).pack(fill="x", padx=10, pady=4)

            # Flight info
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=12, pady=4)

            if is_occ:
                # Flight number & airline
                ctk.CTkLabel(
                    info_frame,
                    text=f"{g['flight_number']} – {g['airline']}",
                    font=config.FONT_BODY_BOLD,
                    text_color=config.COLOR_PRIMARY
                ).pack(anchor="w")

                # Route
                ctk.CTkLabel(
                    info_frame,
                    text=f"Route: {g['route']}",
                    font=config.FONT_SMALL,
                    text_color=config.COLOR_TEXT_SECONDARY
                ).pack(anchor="w", pady=1)

                # Time Window
                ctk.CTkLabel(
                    info_frame,
                    text=f"Slot: {g['time_window']}",
                    font=config.FONT_SMALL_BOLD,
                    text_color=config.COLOR_WARNING
                ).pack(anchor="w", pady=1)
            else:
                ctk.CTkLabel(
                    info_frame,
                    text="No Active Allocation",
                    font=config.FONT_BODY_BOLD,
                    text_color=config.COLOR_TEXT_MUTED
                ).pack(anchor="w")
                ctk.CTkLabel(
                    info_frame,
                    text="Gate is clear and ready for flight assignment.",
                    font=config.FONT_SMALL,
                    text_color=config.COLOR_TEXT_SECONDARY,
                    wraplength=190
                ).pack(anchor="w", pady=2)

            # Card actions
            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(fill="x", padx=10, pady=(6, 10))

            if is_occ and g["flight_id"]:
                rel_btn = ctk.CTkButton(
                    btn_row,
                    text="Release",
                    font=config.FONT_SMALL_BOLD,
                    fg_color="#3A1C20",
                    hover_color="#552228",
                    text_color=config.COLOR_ERROR,
                    height=26,
                    command=lambda fid=g["flight_id"]: self.release_gate_by_id(fid)
                )
                rel_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

            sched_btn = ctk.CTkButton(
                btn_row,
                text="Schedule",
                font=config.FONT_SMALL_BOLD,
                fg_color=config.COLOR_CARD,
                hover_color=config.COLOR_CARD_BORDER,
                text_color=config.COLOR_TEXT_PRIMARY,
                border_width=1,
                border_color=config.COLOR_CARD_BORDER,
                height=26,
                command=lambda gid=g["gate_id"], t=g["terminal"]: self.show_gate_schedule_dialog(gid, t)
            )
            sched_btn.pack(side="left", fill="x", expand=True)

    def _populate_flight_selector(self):
        all_flights = self.data_store.get_all_flights()
        # Filter out Cancelled flights since they cannot occupy gates
        valid_flights = [f for f in all_flights if f["status"] != "Cancelled"]

        self.flight_options_map = {}
        options = []
        for f in valid_flights:
            orig = f["origin"].split(" - ")[0]
            dest = f["destination"].split(" - ")[0]
            display = f"{f['flight_number']} ({f['airline']}) | {orig}➔{dest} | {f['date']} {f['start_time']}-{f['end_time']} | Gate: {f.get('gate', 'Unassigned')}"
            options.append(display)
            self.flight_options_map[display] = f

        if options:
            self.flight_combobox.configure(values=options)
            if not self.flight_combobox.get() or self.flight_combobox.get() not in options:
                self.flight_combobox.set(options[0])
                self._on_flight_selected(options[0])
        else:
            self.flight_combobox.configure(values=["No eligible flights"])
            self.flight_combobox.set("No eligible flights")

    def _on_flight_selected(self, choice):
        flight = self.flight_options_map.get(choice)
        if flight:
            current_gate = flight.get("gate", "Unassigned")
            self.gate_combobox.set(current_gate if current_gate in config.GATES_LIST else "Unassigned")
            self.feedback_lbl.configure(
                text=f"Selected {flight['flight_number']} scheduled on {flight['date']} ({flight['start_time']} - {flight['end_time']}). Current Gate: {current_gate}",
                text_color=config.COLOR_TEXT_PRIMARY
            )

    def suggest_gates_for_selected(self):
        choice = self.flight_combobox.get()
        flight = self.flight_options_map.get(choice)
        if not flight:
            messagebox.showwarning("Select Flight", "Please select a valid flight first.", parent=self)
            return

        available = self.data_store.suggest_available_gates(
            f_date=flight["date"],
            start_time=flight["start_time"],
            end_time=flight["end_time"],
            exclude_flight_id=flight["id"]
        )

        if available:
            self.gate_combobox.set(available[0])
            avail_str = ", ".join(available)
            msg = f"✓ Available conflict-free gates for {flight['flight_number']} ({flight['start_time']} - {flight['end_time']}): {avail_str}"
            self.feedback_lbl.configure(text=msg, text_color=config.COLOR_SUCCESS)
            messagebox.showinfo("Available Gates", msg, parent=self)
        else:
            msg = f"⚠ No airport gates are free for {flight['flight_number']} between {flight['start_time']} and {flight['end_time']} on {flight['date']}!"
            self.feedback_lbl.configure(text=msg, text_color=config.COLOR_ERROR)
            messagebox.showwarning("No Gates Available", msg, parent=self)

    def allocate_gate_selected(self):
        choice = self.flight_combobox.get()
        flight = self.flight_options_map.get(choice)
        if not flight:
            messagebox.showwarning("Select Flight", "Please select a valid flight first.", parent=self)
            return

        target_gate = self.gate_combobox.get()
        ok, msg, suggested = self.data_store.assign_gate(flight["id"], target_gate)

        if ok:
            messagebox.showinfo("Allocation Successful", msg, parent=self)
            self.feedback_lbl.configure(text=f"✓ {msg}", text_color=config.COLOR_SUCCESS)
            self.refresh_gates()
            self.app_controller.refresh_all_views()
        else:
            sugg_str = ", ".join(suggested) if suggested else "None"
            full_msg = f"{msg}\n\nSuggested alternative gates: {sugg_str}"
            messagebox.showerror("Gate Allocation Conflict", full_msg, parent=self)
            self.feedback_lbl.configure(text=f"⚠ Conflict at {target_gate}! Suggested: {sugg_str}", text_color=config.COLOR_ERROR)
            if suggested:
                self.gate_combobox.set(suggested[0])

    def release_gate_selected(self):
        choice = self.flight_combobox.get()
        flight = self.flight_options_map.get(choice)
        if not flight:
            messagebox.showwarning("Select Flight", "Please select a flight to release.", parent=self)
            return

        self.release_gate_by_id(flight["id"])

    def release_gate_by_id(self, flight_id):
        ok, msg = self.data_store.release_gate(flight_id)
        if ok:
            messagebox.showinfo("Gate Released", msg, parent=self)
            self.feedback_lbl.configure(text=f"✓ {msg}", text_color=config.COLOR_SUCCESS)
            self.refresh_gates()
            self.app_controller.refresh_all_views()
        else:
            messagebox.showerror("Error", msg, parent=self)

    def _render_master_schedule(self):
        for w in self.schedule_table_container.winfo_children():
            w.destroy()

        all_flights = self.data_store.get_all_flights()
        # Find all flights assigned to a gate
        allocated = [f for f in all_flights if f.get("gate", "Unassigned") != "Unassigned"]
        # Sort by Gate name, then date, then start_time
        allocated.sort(key=lambda x: (x["gate"], x["date"], x["start_time"]))

        if not allocated:
            ctk.CTkLabel(
                self.schedule_table_container,
                text="No active gate assignments. Use the panel above to allocate gates.",
                font=config.FONT_BODY,
                text_color=config.COLOR_TEXT_MUTED
            ).pack(pady=20)
            return

        for idx, fl in enumerate(allocated):
            bg = config.COLOR_TABLE_ROW if idx % 2 == 0 else config.COLOR_TABLE_ROW_ALT
            row = ctk.CTkFrame(self.schedule_table_container, fg_color=bg, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=2)
            row.grid_columnconfigure(3, weight=3)
            row.grid_columnconfigure(4, weight=3)
            row.grid_columnconfigure(5, weight=2)
            row.grid_columnconfigure(6, weight=2)
            row.grid_columnconfigure(7, weight=2)
            row.grid_columnconfigure(8, weight=1)

            # Gate
            ctk.CTkLabel(row, text=fl["gate"], font=config.FONT_BODY_BOLD, text_color=config.COLOR_PRIMARY).grid(row=0, column=0, padx=6, pady=7, sticky="w")

            # Terminal
            term = "Terminal 1" if fl["gate"] in ["G1", "G2", "G3"] else ("Terminal 2" if fl["gate"] in ["G4", "G5", "G6"] else "Terminal 3")
            ctk.CTkLabel(row, text=term, font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=1, padx=6, pady=7, sticky="w")

            # Flight Number
            ctk.CTkLabel(row, text=fl["flight_number"], font=config.FONT_BODY_BOLD, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=2, padx=6, pady=7, sticky="w")

            # Airline
            ctk.CTkLabel(row, text=fl["airline"], font=config.FONT_BODY, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=3, padx=6, pady=7, sticky="w")

            # Route
            orig = fl["origin"].split(" - ")[0]
            dest = fl["destination"].split(" - ")[0]
            ctk.CTkLabel(row, text=f"{orig} ➔ {dest}", font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=4, padx=6, pady=7, sticky="w")

            # Date
            ctk.CTkLabel(row, text=fl["date"], font=config.FONT_SMALL, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=5, padx=6, pady=7, sticky="w")

            # Slot
            slot_str = f"{fl['start_time']} - {fl['end_time']}"
            ctk.CTkLabel(row, text=slot_str, font=config.FONT_SMALL_BOLD, text_color=config.COLOR_WARNING).grid(row=0, column=6, padx=6, pady=7, sticky="w")

            # Status Badge
            st_color = config.STATUS_COLORS.get(fl["status"], {"bg": config.COLOR_CARD, "fg": config.COLOR_TEXT_PRIMARY})
            badge = ctk.CTkFrame(row, fg_color=st_color["bg"], corner_radius=12)
            badge.grid(row=0, column=7, padx=6, pady=5)
            ctk.CTkLabel(badge, text=fl["status"], font=config.FONT_BADGE, text_color=st_color["fg"]).pack(padx=8, pady=2)

            # Release action
            rel_btn = ctk.CTkButton(
                row,
                text="Release",
                font=config.FONT_SMALL_BOLD,
                width=65,
                height=26,
                fg_color="#3A1C20",
                hover_color="#552228",
                text_color=config.COLOR_ERROR,
                command=lambda fid=fl["id"]: self.release_gate_by_id(fid)
            )
            rel_btn.grid(row=0, column=8, padx=6, pady=5)

    def show_gate_schedule_dialog(self, gate_id, terminal):
        """Displays dialog showing all scheduled allocations for the given gate."""
        GateScheduleDialog(self, gate_id=gate_id, terminal=terminal, data_store=self.data_store)


class GateScheduleDialog(ctk.CTkToplevel):
    def __init__(self, parent_view, gate_id, terminal, data_store):
        super().__init__(parent_view)
        self.title(f"Schedule for Gate {gate_id} ({terminal})")
        self.geometry("620x460")
        self.resizable(False, False)
        self.configure(fg_color=config.COLOR_SIDEBAR)

        self.transient(parent_view)
        self.grab_set()

        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 620) // 2
        y = (self.winfo_screenheight() - 460) // 2
        self.geometry(f"+{x}+{y}")

        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(16, 10))
        ctk.CTkLabel(hdr, text=f"Gate {gate_id} – Allocation Timeline", font=config.FONT_TITLE, text_color=config.COLOR_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(hdr, text=f"Ramp Location: {terminal}. Allocations are checked against conflict condition.", font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY).pack(anchor="w")

        # Table container
        table_scroll = ctk.CTkScrollableFrame(self, fg_color=config.COLOR_CARD, corner_radius=10)
        table_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Query all flights for this gate
        gate_flights = [f for f in data_store.get_all_flights() if f.get("gate") == gate_id and f["status"] != "Cancelled"]
        gate_flights.sort(key=lambda x: (x["date"], x["start_time"]))

        if not gate_flights:
            ctk.CTkLabel(
                table_scroll,
                text=f"No flight allocations recorded for Gate {gate_id}.",
                font=config.FONT_BODY,
                text_color=config.COLOR_TEXT_MUTED
            ).pack(pady=40)
        else:
            # Header
            th = ctk.CTkFrame(table_scroll, fg_color=config.COLOR_TABLE_HEADER, corner_radius=6)
            th.pack(fill="x", pady=(0, 4))
            th.grid_columnconfigure(0, weight=2)
            th.grid_columnconfigure(1, weight=3)
            th.grid_columnconfigure(2, weight=2)
            th.grid_columnconfigure(3, weight=2)
            th.grid_columnconfigure(4, weight=2)

            for c, name in enumerate(["Flight", "Airline", "Date", "Slot", "Status"]):
                ctk.CTkLabel(th, text=name, font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=c, padx=6, pady=6, sticky="w")

            for idx, fl in enumerate(gate_flights):
                bg = config.COLOR_TABLE_ROW if idx % 2 == 0 else config.COLOR_TABLE_ROW_ALT
                r = ctk.CTkFrame(table_scroll, fg_color=bg, corner_radius=6)
                r.pack(fill="x", pady=2)
                r.grid_columnconfigure(0, weight=2)
                r.grid_columnconfigure(1, weight=3)
                r.grid_columnconfigure(2, weight=2)
                r.grid_columnconfigure(3, weight=2)
                r.grid_columnconfigure(4, weight=2)

                ctk.CTkLabel(r, text=fl["flight_number"], font=config.FONT_BODY_BOLD, text_color=config.COLOR_PRIMARY).grid(row=0, column=0, padx=6, pady=6, sticky="w")
                ctk.CTkLabel(r, text=fl["airline"], font=config.FONT_BODY, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=1, padx=6, pady=6, sticky="w")
                ctk.CTkLabel(r, text=fl["date"], font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=2, padx=6, pady=6, sticky="w")
                ctk.CTkLabel(r, text=f"{fl['start_time']} - {fl['end_time']}", font=config.FONT_SMALL_BOLD, text_color=config.COLOR_WARNING).grid(row=0, column=3, padx=6, pady=6, sticky="w")
                ctk.CTkLabel(r, text=fl["status"], font=config.FONT_BADGE, text_color=config.STATUS_COLORS.get(fl["status"], {}).get("fg", "#FFFFFF")).grid(row=0, column=4, padx=6, pady=6, sticky="w")

        # Close button
        ctk.CTkButton(
            self,
            text="Close Window",
            font=config.FONT_BODY,
            fg_color=config.COLOR_CARD_ALT,
            hover_color=config.COLOR_CARD_HOVER,
            text_color=config.COLOR_TEXT_PRIMARY,
            height=34,
            command=self.destroy
        ).pack(pady=(0, 16))
