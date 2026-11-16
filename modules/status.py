"""
AeroFlow – Flight Status Management Module
Allows instant flight status updates, color-coded badges, and sensible transition checks.
"""

import customtkinter as ctk
from tkinter import messagebox
import config


class StatusView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color=config.COLOR_BG)
        self.app_controller = app_controller
        self.data_store = app_controller.data_store

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_status_counter_bar()
        self._build_table_container()
        self.refresh_status_view()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 8))
        header_frame.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        title_lbl = ctk.CTkLabel(
            title_box,
            text="Flight Operations Status Control",
            font=config.FONT_TITLE,
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_box,
            text="Update operational flight states in real time. Changes immediately sync with Gate Allocation and Dashboard.",
            font=config.FONT_SUBTITLE,
            text_color=config.COLOR_TEXT_SECONDARY
        )
        subtitle_lbl.pack(anchor="w")

    def _build_status_counter_bar(self):
        self.counter_bar = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_CARD,
            corner_radius=8,
            border_width=1,
            border_color=config.COLOR_CARD_BORDER
        )
        self.counter_bar.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 14))
        for c in range(6):
            self.counter_bar.grid_columnconfigure(c, weight=1, uniform="status_col")

        self.counter_labels = {}
        for idx, st in enumerate(config.FLIGHT_STATUSES):
            col_info = config.STATUS_COLORS.get(st, {"fg": "#FFFFFF", "bg": "#1E293B"})
            pill = ctk.CTkFrame(self.counter_bar, fg_color="transparent")
            pill.grid(row=0, column=idx, padx=6, pady=8)

            ctk.CTkLabel(pill, text=st, font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).pack()
            val_lbl = ctk.CTkLabel(pill, text="0", font=config.FONT_CARD_TITLE, text_color=col_info["fg"])
            val_lbl.pack()
            self.counter_labels[st] = val_lbl

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

        # Header
        th = ctk.CTkFrame(container, fg_color=config.COLOR_TABLE_HEADER, height=36, corner_radius=6)
        th.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        self._setup_weights(th)

        cols = ["Flight #", "Airline", "Route", "Type", "Time Slot", "Gate", "Current Status", "Update Status Action"]
        for c, name in enumerate(cols):
            ctk.CTkLabel(th, text=name, font=config.FONT_SMALL_BOLD, text_color=config.COLOR_TEXT_SECONDARY).grid(
                row=0, column=c, padx=6, pady=8, sticky="w" if c < 6 else "ew"
            )

        # Scrollable table rows
        self.scroll_table = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.scroll_table.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.scroll_table.grid_columnconfigure(0, weight=1)

    def _setup_weights(self, frame):
        frame.grid_columnconfigure(0, weight=2, minsize=80)   # Flight #
        frame.grid_columnconfigure(1, weight=3, minsize=140)  # Airline
        frame.grid_columnconfigure(2, weight=3, minsize=150)  # Route
        frame.grid_columnconfigure(3, weight=1, minsize=70)   # Type
        frame.grid_columnconfigure(4, weight=2, minsize=90)   # Time Slot
        frame.grid_columnconfigure(5, weight=1, minsize=65)   # Gate
        frame.grid_columnconfigure(6, weight=2, minsize=110)  # Current Status
        frame.grid_columnconfigure(7, weight=3, minsize=160)  # Update Action

    def refresh_status_view(self):
        """Re-reads flights and renders status counts and interactive row selectors."""
        flights = self.data_store.get_all_flights()

        # Update counter bar
        counts = {st: 0 for st in config.FLIGHT_STATUSES}
        for f in flights:
            st = f.get("status", "Scheduled")
            if st in counts:
                counts[st] += 1

        for st, count in counts.items():
            if st in self.counter_labels:
                self.counter_labels[st].configure(text=str(count))

        # Clear rows
        for w in self.scroll_table.winfo_children():
            w.destroy()

        if not flights:
            ctk.CTkLabel(
                self.scroll_table,
                text="No flight records available.",
                font=config.FONT_BODY,
                text_color=config.COLOR_TEXT_MUTED
            ).pack(pady=40)
            return

        for idx, fl in enumerate(flights):
            bg = config.COLOR_TABLE_ROW if idx % 2 == 0 else config.COLOR_TABLE_ROW_ALT
            row = ctk.CTkFrame(self.scroll_table, fg_color=bg, corner_radius=6)
            row.pack(fill="x", pady=2)
            self._setup_weights(row)

            # Flight Number
            ctk.CTkLabel(row, text=fl["flight_number"], font=config.FONT_BODY_BOLD, text_color=config.COLOR_PRIMARY).grid(row=0, column=0, padx=6, pady=8, sticky="w")

            # Airline
            ctk.CTkLabel(row, text=fl["airline"], font=config.FONT_BODY, text_color=config.COLOR_TEXT_PRIMARY).grid(row=0, column=1, padx=6, pady=8, sticky="w")

            # Route
            orig = fl["origin"].split(" - ")[0]
            dest = fl["destination"].split(" - ")[0]
            ctk.CTkLabel(row, text=f"{orig} ➔ {dest}", font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=2, padx=6, pady=8, sticky="w")

            # Type
            type_col = config.COLOR_SUCCESS if fl["flight_type"] == "Arrival" else config.COLOR_SECONDARY
            ctk.CTkLabel(row, text=fl["flight_type"], font=config.FONT_SMALL_BOLD, text_color=type_col).grid(row=0, column=3, padx=6, pady=8, sticky="w")

            # Time Slot
            ctk.CTkLabel(row, text=f"{fl['start_time']} - {fl['end_time']}", font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY).grid(row=0, column=4, padx=6, pady=8, sticky="w")

            # Gate
            gate_val = fl.get("gate", "Unassigned")
            gate_col = config.COLOR_PRIMARY if gate_val != "Unassigned" else config.COLOR_TEXT_MUTED
            ctk.CTkLabel(row, text=gate_val, font=config.FONT_SMALL_BOLD, text_color=gate_col).grid(row=0, column=5, padx=6, pady=8, sticky="w")

            # Status Badge
            st_color = config.STATUS_COLORS.get(fl["status"], {"bg": config.COLOR_CARD, "fg": config.COLOR_TEXT_PRIMARY})
            badge = ctk.CTkFrame(row, fg_color=st_color["bg"], corner_radius=12)
            badge.grid(row=0, column=6, padx=6, pady=6)
            ctk.CTkLabel(badge, text=fl["status"], font=config.FONT_BADGE, text_color=st_color["fg"]).pack(padx=8, pady=2)

            # Update Action: Quick OptionMenu
            action_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_frame.grid(row=0, column=7, padx=6, pady=6)

            status_menu = ctk.CTkOptionMenu(
                action_frame,
                values=config.FLIGHT_STATUSES,
                font=config.FONT_SMALL_BOLD,
                width=120,
                height=26,
                fg_color=config.COLOR_CARD_ALT,
                button_color=config.COLOR_CARD_HOVER,
                command=lambda new_st, fid=fl["id"], cur_st=fl["status"], fn=fl["flight_number"]: self.on_status_change_requested(fid, fn, cur_st, new_st)
            )
            status_menu.set(fl["status"])
            status_menu.pack(side="left")

    def on_status_change_requested(self, flight_id, flight_number, current_status, new_status):
        if current_status == new_status:
            return

        # Check for nonsensical transitions and request confirmation
        unusual = False
        warning_text = ""

        if current_status == "Departed" and new_status in ["Scheduled", "Boarding"]:
            unusual = True
            warning_text = f"Flight {flight_number} has already Departed. Moving it back to '{new_status}' is unusual."
        elif current_status == "Arrived" and new_status in ["Scheduled", "Boarding", "Delayed"]:
            unusual = True
            warning_text = f"Flight {flight_number} has already Arrived. Moving it back to '{new_status}' is unusual."
        elif current_status == "Cancelled" and new_status in ["Departed", "Arrived"]:
            unusual = True
            warning_text = f"Flight {flight_number} was marked Cancelled. Setting status to '{new_status}' requires confirmation."
        elif new_status == "Cancelled":
            warning_text = f"Marking Flight {flight_number} as 'Cancelled' will automatically release its assigned gate ramp position."

        if unusual or new_status == "Cancelled":
            ans = messagebox.askyesno(
                "Confirm Status Transition",
                f"{warning_text}\n\nDo you want to proceed with setting status to '{new_status}'?",
                parent=self
            )
            if not ans:
                self.refresh_status_view()
                return

        ok, msg = self.data_store.update_flight_status(flight_id, new_status)
        if ok:
            messagebox.showinfo("Status Updated", msg, parent=self)
            self.refresh_status_view()
            self.app_controller.refresh_all_views()
        else:
            messagebox.showerror("Error", msg, parent=self)
            self.refresh_status_view()
