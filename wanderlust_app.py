# ============================================================
# Wanderlust Travel Planning & Booking Application
# Developer: Shohjahon Asrorov  |  RMIT University 2026
# Assessment Task 3A - Python Tkinter GUI Application
#
# Functional Requirements implemented:
#   FR01 - User Registration & Login
#   FR02 - Destination Search & Filtering
#   FR04 - Itinerary Builder
#   FR05 - Cost Estimation (running total)
#   FR06 - Save & Retrieve Itineraries
#   FR07 - Payment Processing (simulated)
#   FR08 - Export Trip Summary (.txt)
#   FR10 - Travel Companion Discovery Feed
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import re
import json
import os
from datetime import datetime, date


# ============================================================
# COLOUR CONSTANTS (Design 2: Immersive Wanderlust)
# ============================================================
NAVY     = "#1A2B4A"
TEAL     = "#00B4D8"
WHITE    = "#FFFFFF"
LIGHT_BG = "#F0F4F8"
DARK_TXT = "#1A2B4A"
MID_GREY = "#6B7280"
ERROR_RED= "#DC2626"
SUCCESS  = "#16A34A"
CARD_BG  = "#FFFFFF"
ACCENT   = "#0077B6"

FONT_H1   = ("Arial", 22, "bold")
FONT_H2   = ("Arial", 16, "bold")
FONT_H3   = ("Arial", 13, "bold")
FONT_BODY = ("Arial", 12)
FONT_SM   = ("Arial", 10)
FONT_LABEL= ("Arial", 11)


# ============================================================
# DATABASE INITIALISATION
# ============================================================

def init_database():
    """
    Create SQLite database tables if they do not already exist.
    Tables: users, itineraries, companion_posts
    """
    conn = sqlite3.connect("wanderlust.db")
    cur  = conn.cursor()

    # --- Users (FR01) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name     TEXT    NOT NULL,
            last_name      TEXT    NOT NULL,
            email          TEXT    UNIQUE NOT NULL,
            password_hash  TEXT    NOT NULL,
            user_role      TEXT    NOT NULL DEFAULT 'Traveller',
            account_created TEXT   NOT NULL
        )
    """)

    # --- Itineraries (FR06) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS itineraries (
            itinerary_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            itinerary_name TEXT    NOT NULL,
            destination    TEXT    NOT NULL,
            departure_date TEXT,
            return_date    TEXT,
            items_json     TEXT,
            total_cost     REAL    DEFAULT 0.0,
            saved_at       TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # --- Companion Posts (FR10) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS companion_posts (
            post_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            poster_name    TEXT    NOT NULL,
            destination    TEXT    NOT NULL,
            departure_date TEXT,
            return_date    TEXT,
            budget_min     REAL,
            budget_max     REAL,
            travel_style   TEXT,
            bio            TEXT,
            posted_at      TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# MOCK TRAVEL DATA  (simulates external API, FR02 / FR03)
# ============================================================

MOCK_DESTINATIONS = [
    {
        "name": "Bali, Indonesia",
        "type": "Beach",
        "style": "Relaxation",
        "description": "Tropical paradise with rice terraces, temples and surf beaches.",
        "flights": [
            {"airline": "Garuda Indonesia", "price": 680,  "duration": "6h 20m", "departs": "07:00"},
            {"airline": "AirAsia",          "price": 520,  "duration": "7h 05m", "departs": "22:30"},
        ],
        "hotels": [
            {"name": "Alaya Resort Ubud",   "price_night": 185, "rating": 4.8, "location": "Ubud"},
            {"name": "W Bali – Seminyak",   "price_night": 310, "rating": 4.9, "location": "Seminyak"},
            {"name": "Kuta Beach Hostel",   "price_night":  45, "rating": 3.9, "location": "Kuta"},
        ],
    },
    {
        "name": "Tokyo, Japan",
        "type": "City",
        "style": "Cultural",
        "description": "A seamless blend of ancient temples and neon-lit skyscrapers.",
        "flights": [
            {"airline": "Japan Airlines",  "price": 1140, "duration": "9h 50m", "departs": "10:15"},
            {"airline": "Qantas",          "price": 1380, "duration": "9h 45m", "departs": "14:30"},
        ],
        "hotels": [
            {"name": "Park Hyatt Tokyo",         "price_night": 520, "rating": 4.9, "location": "Shinjuku"},
            {"name": "Dormy Inn Asakusa",        "price_night": 130, "rating": 4.5, "location": "Asakusa"},
            {"name": "Shibuya Stream Excel Hotel","price_night":210, "rating": 4.6, "location": "Shibuya"},
        ],
    },
    {
        "name": "Paris, France",
        "type": "City",
        "style": "Cultural",
        "description": "The City of Light — world-class art, cuisine and the Eiffel Tower.",
        "flights": [
            {"airline": "Air France",  "price": 1750, "duration": "22h 10m", "departs": "08:00"},
            {"airline": "Singapore Airlines", "price": 1490, "duration": "23h 30m", "departs": "21:45"},
        ],
        "hotels": [
            {"name": "Le Marais Boutique Hotel", "price_night": 220, "rating": 4.7, "location": "Le Marais"},
            {"name": "Hotel Eiffel Blomet",      "price_night": 175, "rating": 4.4, "location": "15th arr."},
            {"name": "Generator Paris Hostel",   "price_night":  55, "rating": 4.0, "location": "10th arr."},
        ],
    },
    {
        "name": "Bangkok, Thailand",
        "type": "City",
        "style": "Adventure",
        "description": "Street food, golden temples, and vibrant nightlife in South-East Asia.",
        "flights": [
            {"airline": "Thai Airways",  "price": 590,  "duration": "8h 15m", "departs": "09:00"},
            {"airline": "Scoot",         "price": 380,  "duration": "9h 40m", "departs": "23:55"},
        ],
        "hotels": [
            {"name": "Capella Bangkok",     "price_night": 480, "rating": 5.0, "location": "Riverside"},
            {"name": "Ibis Bangkok Siam",   "price_night":  90, "rating": 4.2, "location": "Siam"},
            {"name": "Lub*d Silom Hostel",  "price_night":  35, "rating": 4.3, "location": "Silom"},
        ],
    },
    {
        "name": "Queenstown, NZ",
        "type": "Mountain",
        "style": "Adventure",
        "description": "The adventure capital of the world with bungee jumping and skiing.",
        "flights": [
            {"airline": "Air New Zealand", "price": 420,  "duration": "3h 30m", "departs": "06:45"},
            {"airline": "Jetstar",         "price": 310,  "duration": "3h 45m", "departs": "18:00"},
        ],
        "hotels": [
            {"name": "Eichardt's Private Hotel","price_night": 395, "rating": 4.9, "location": "Lakefront"},
            {"name": "Novotel Queenstown",       "price_night": 210, "rating": 4.5, "location": "Central"},
            {"name": "Base Queenstown Hostel",   "price_night":  42, "rating": 4.1, "location": "Central"},
        ],
    },
    {
        "name": "Maldives",
        "type": "Beach",
        "style": "Relaxation",
        "description": "Crystal-clear lagoons and overwater bungalows in the Indian Ocean.",
        "flights": [
            {"airline": "Maldivian",  "price": 1950, "duration": "11h 00m", "departs": "07:30"},
            {"airline": "Emirates",   "price": 1650, "duration": "13h 20m", "departs": "14:00"},
        ],
        "hotels": [
            {"name": "Gili Lankanfushi",   "price_night": 1200, "rating": 5.0, "location": "North Malé"},
            {"name": "Centara Grand",       "price_night": 650,  "rating": 4.8, "location": "South Malé"},
            {"name": "Adaaran Select Meedhupparu","price_night":320,"rating":4.4,"location":"Raa Atoll"},
        ],
    },
]

MOCK_COMPANION_POSTS = [
    {"poster": "Liam T.", "destination": "Bali, Indonesia",  "dates": "15 Jul – 28 Jul",
     "budget": "$1,500 AUD", "style": "Relaxation", "bio": "28, Melbourne. Love yoga and sunsets. Looking for a chill travel buddy!"},
    {"poster": "Aisha M.", "destination": "Tokyo, Japan",    "dates": "01 Sep – 14 Sep",
     "budget": "$3,200 AUD", "style": "Cultural",   "bio": "25, Sydney. Huge anime and ramen fan. First trip to Japan!"},
    {"poster": "Carlos R.","destination": "Queenstown, NZ",  "dates": "10 Aug – 17 Aug",
     "budget": "$2,000 AUD", "style": "Adventure",  "bio": "32, Brisbane. Skydiving + bungee jumping planned — need a brave companion!"},
    {"poster": "Sophie K.","destination": "Bangkok, Thailand","dates": "20 Jun – 30 Jun",
     "budget": "$1,200 AUD", "style": "Adventure",  "bio": "27, Perth. Street food obsessed and temple hopper. Join me!"},
]


# ============================================================
# HELPER / VALIDATION FUNCTIONS
# ============================================================

def hash_password(plain_text: str) -> str:
    """Return SHA-256 hash of plain-text password (NFR05 — no plain-text storage)."""
    return hashlib.sha256(plain_text.encode()).hexdigest()


def validate_email(email: str) -> bool:
    """Return True if email matches standard format using regex (FR01)."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_password(password: str) -> bool:
    """
    Return True if password is ≥ 8 characters AND contains
    at least one digit and one special character (FR01 / NFR05).
    """
    has_length  = len(password) >= 8
    has_digit   = bool(re.search(r"\d",        password))
    has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password))
    return has_length and has_digit and has_special


def validate_card_number(card: str) -> bool:
    """Return True if card number is exactly 16 digits (FR07)."""
    return bool(re.fullmatch(r"\d{16}", card.replace(" ", "")))


def validate_expiry(expiry: str) -> bool:
    """
    Return True if expiry is in MM/YY format and is not in the past (FR07).
    """
    if not re.fullmatch(r"\d{2}/\d{2}", expiry):
        return False
    month, year = int(expiry[:2]), int("20" + expiry[3:])
    today = date.today()
    if month < 1 or month > 12:
        return False
    return (year, month) >= (today.year, today.month)


def validate_cvv(cvv: str) -> bool:
    """Return True if CVV is exactly 3 digits (FR07)."""
    return bool(re.fullmatch(r"\d{3}", cvv))


def validate_date_not_past(date_str: str) -> bool:
    """Return True if date string (DD/MM/YYYY) is today or in the future (FR02)."""
    try:
        d = datetime.strptime(date_str, "%d/%m/%Y").date()
        return d >= date.today()
    except ValueError:
        return False


def validate_date_after(date_str: str, other_str: str) -> bool:
    """Return True if date_str is strictly after other_str (FR02)."""
    try:
        d1 = datetime.strptime(date_str, "%d/%m/%Y").date()
        d2 = datetime.strptime(other_str, "%d/%m/%Y").date()
        return d1 > d2
    except ValueError:
        return False


def generate_booking_ref() -> str:
    """Generate a unique alphanumeric booking reference (FR07)."""
    import random, string
    return "WL-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


# ============================================================
# MAIN APPLICATION CLASS
# ============================================================

class WanderlustApp(tk.Tk):
    """
    Root application window. Manages frame switching and shared state.
    Uses a dictionary of frame instances to navigate between screens.
    """

    def __init__(self):
        super().__init__()
        self.title("Wanderlust Travel App")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=LIGHT_BG)
        self.resizable(True, True)

        # Shared session state
        self.current_user    = None   # dict with user data after login
        self.itinerary_items = []     # list of dicts added to current itinerary
        self.search_results  = []     # last search results from mock API
        self.selected_dest   = None   # destination dict currently being viewed

        # Container that holds all frames
        container = tk.Frame(self, bg=LIGHT_BG)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initialise all frames
        self.frames = {}
        for FrameClass in (
            LoginRegisterFrame,
            HomeFrame,
            SearchFrame,
            ItineraryFrame,
            PaymentFrame,
            SavedTripsFrame,
            CompanionFrame,
        ):
            frame = FrameClass(container, self)
            self.frames[FrameClass] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginRegisterFrame)

    # -------------------------------------------------------
    def show_frame(self, frame_class):
        """Raise the requested frame to the top and call its on_show hook."""
        frame = self.frames[frame_class]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    # -------------------------------------------------------
    def logout(self):
        """Clear session state and return to login screen (NFR05)."""
        self.current_user    = None
        self.itinerary_items = []
        self.search_results  = []
        self.selected_dest   = None
        self.show_frame(LoginRegisterFrame)


# ============================================================
# REUSABLE UI WIDGETS
# ============================================================

def make_header(parent, app, title: str, show_nav: bool = True):
    """
    Build the navy top-bar header with title and optional nav buttons.
    Returns the header frame.
    """
    hdr = tk.Frame(parent, bg=NAVY, pady=12)
    hdr.pack(fill="x", side="top")

    tk.Label(hdr, text="✈  Wanderlust", font=("Arial", 14, "bold"),
             fg=TEAL, bg=NAVY).pack(side="left", padx=16)

    tk.Label(hdr, text=title, font=FONT_H2, fg=WHITE, bg=NAVY).pack(side="left", padx=20)

    if show_nav and app.current_user:
        nav_frame = tk.Frame(hdr, bg=NAVY)
        nav_frame.pack(side="right", padx=12)

        btns = [
            ("🏠 Home",      HomeFrame),
            ("🔍 Search",    SearchFrame),
            ("📋 Itinerary", ItineraryFrame),
            ("💾 Saved",     SavedTripsFrame),
            ("👥 Companions",CompanionFrame),
        ]
        for label, frame_class in btns:
            tk.Button(nav_frame, text=label, font=FONT_SM,
                      bg=NAVY, fg=WHITE, bd=0, cursor="hand2",
                      activebackground=ACCENT, activeforeground=WHITE,
                      command=lambda fc=frame_class: app.show_frame(fc)
                      ).pack(side="left", padx=6)

        tk.Button(nav_frame, text="⏻ Logout", font=FONT_SM,
                  bg=ERROR_RED, fg=WHITE, bd=0, cursor="hand2",
                  padx=8, pady=2,
                  command=app.logout).pack(side="left", padx=10)
    return hdr


def styled_button(parent, text, command, bg=TEAL, fg=WHITE,
                  font=FONT_BODY, width=None, pady=8, padx=16):
    """Return a consistently styled button widget."""
    kwargs = dict(text=text, command=command, bg=bg, fg=fg,
                  font=font, relief="flat", cursor="hand2",
                  activebackground=ACCENT, activeforeground=WHITE,
                  pady=pady, padx=padx)
    if width:
        kwargs["width"] = width
    return tk.Button(parent, **kwargs)


def labeled_entry(parent, label_text, row, show="", width=30):
    """
    Create a label + entry pair on a grid layout.
    Returns the Entry widget.
    """
    tk.Label(parent, text=label_text, font=FONT_LABEL,
             bg=WHITE, fg=DARK_TXT, anchor="w").grid(
        row=row, column=0, sticky="w", pady=4, padx=(0, 12))
    ent = tk.Entry(parent, font=FONT_BODY, width=width, show=show,
                   relief="solid", bd=1, bg="#F9FAFB")
    ent.grid(row=row, column=1, sticky="ew", pady=4)
    return ent


# ============================================================
# FRAME 1 — LOGIN / REGISTER  (FR01)
# ============================================================

class LoginRegisterFrame(tk.Frame):
    """
    Login and registration screen with tabbed interface.
    Validates all inputs against SRS FR01 rules before submission.
    """

    def __init__(self, parent, app: WanderlustApp):
        super().__init__(parent, bg=LIGHT_BG)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # ---- Header (no nav — not logged in yet) ----
        make_header(self, self.app, "Welcome", show_nav=False)

        # ---- Centre card ----
        card = tk.Frame(self, bg=WHITE, padx=40, pady=30,
                        relief="solid", bd=1)
        card.place(relx=0.5, rely=0.52, anchor="center")

        tk.Label(card, text="Wanderlust Travel", font=FONT_H1,
                 fg=NAVY, bg=WHITE).grid(row=0, column=0, columnspan=2, pady=(0, 4))
        tk.Label(card, text="Plan. Book. Explore.", font=FONT_BODY,
                 fg=MID_GREY, bg=WHITE).grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # ---- Tab buttons ----
        tab_frame = tk.Frame(card, bg=WHITE)
        tab_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        self.active_tab = tk.StringVar(value="login")

        self.btn_tab_login = tk.Button(
            tab_frame, text="Login", font=FONT_H3, width=12,
            relief="flat", cursor="hand2",
            command=lambda: self._switch_tab("login"))
        self.btn_tab_login.pack(side="left")

        self.btn_tab_reg = tk.Button(
            tab_frame, text="Register", font=FONT_H3, width=12,
            relief="flat", cursor="hand2",
            command=lambda: self._switch_tab("register"))
        self.btn_tab_reg.pack(side="left", padx=(8, 0))

        # ---- Stacked form panels ----
        self.login_panel    = self._build_login_panel(card)
        self.register_panel = self._build_register_panel(card)

        self._switch_tab("login")

    # -------------------------------------------------------
    def _switch_tab(self, tab: str):
        """Show the correct form panel and update tab styling."""
        self.active_tab.set(tab)
        if tab == "login":
            self.login_panel.grid(row=3, column=0, columnspan=2)
            self.register_panel.grid_remove()
            self.btn_tab_login.config(bg=NAVY, fg=WHITE)
            self.btn_tab_reg.config(bg=LIGHT_BG, fg=DARK_TXT)
        else:
            self.register_panel.grid(row=3, column=0, columnspan=2)
            self.login_panel.grid_remove()
            self.btn_tab_reg.config(bg=NAVY, fg=WHITE)
            self.btn_tab_login.config(bg=LIGHT_BG, fg=DARK_TXT)

    # -------------------------------------------------------
    def _build_login_panel(self, parent) -> tk.Frame:
        """Build the login form with email, password and error label."""
        panel = tk.Frame(parent, bg=WHITE)

        self.lbl_login_error = tk.Label(panel, text="", font=FONT_SM,
                                        fg=ERROR_RED, bg=WHITE)
        self.lbl_login_error.grid(row=0, column=0, columnspan=2, pady=(0, 4))

        self.ent_login_email    = labeled_entry(panel, "Email Address", 1)
        self.ent_login_password = labeled_entry(panel, "Password",      2, show="●")

        panel.columnconfigure(1, weight=1)

        styled_button(panel, "Login", self._do_login, width=20).grid(
            row=3, column=0, columnspan=2, pady=(16, 0))
        return panel

    # -------------------------------------------------------
    def _build_register_panel(self, parent) -> tk.Frame:
        """Build the registration form with all FR01 fields."""
        panel = tk.Frame(parent, bg=WHITE)

        self.lbl_reg_error = tk.Label(panel, text="", font=FONT_SM,
                                      fg=ERROR_RED, bg=WHITE, wraplength=380)
        self.lbl_reg_error.grid(row=0, column=0, columnspan=2, pady=(0, 4))

        self.ent_reg_fname    = labeled_entry(panel, "First Name",     1)
        self.ent_reg_lname    = labeled_entry(panel, "Last Name",      2)
        self.ent_reg_email    = labeled_entry(panel, "Email Address",  3)
        self.ent_reg_password = labeled_entry(panel, "Password",       4, show="●")
        self.ent_reg_confirm  = labeled_entry(panel, "Confirm Password",5, show="●")

        tk.Label(panel, text="Account Type", font=FONT_LABEL,
                 bg=WHITE, fg=DARK_TXT, anchor="w").grid(
            row=6, column=0, sticky="w", pady=4, padx=(0, 12))
        self.ddl_role = ttk.Combobox(panel, values=["Traveller", "Agent"],
                                     state="readonly", width=28, font=FONT_BODY)
        self.ddl_role.set("Traveller")
        self.ddl_role.grid(row=6, column=1, sticky="ew", pady=4)

        # Password hint
        tk.Label(panel,
                 text="Min 8 chars, must include a number and special character",
                 font=("Arial", 9), fg=MID_GREY, bg=WHITE).grid(
            row=7, column=0, columnspan=2, sticky="w")

        panel.columnconfigure(1, weight=1)
        styled_button(panel, "Create Account", self._do_register, width=20).grid(
            row=8, column=0, columnspan=2, pady=(16, 0))
        return panel

    # -------------------------------------------------------
    def _do_login(self):
        """
        Validate login credentials against database.
        Displays error message on failure (FR01 error handling).
        """
        email    = self.ent_login_email.get().strip().lower()
        password = self.ent_login_password.get()

        # Existence check (NFR04)
        if not email or not password:
            self.lbl_login_error.config(text="Email and password cannot be empty.")
            return

        # Email format check (FR01)
        if not validate_email(email):
            self.lbl_login_error.config(text="Please enter a valid email address.")
            return

        # Database credential check (FR01)
        conn = sqlite3.connect("wanderlust.db")
        cur  = conn.cursor()
        cur.execute(
            "SELECT user_id, first_name, last_name, email, user_role "
            "FROM users WHERE email=? AND password_hash=?",
            (email, hash_password(password))
        )
        row = cur.fetchone()
        conn.close()

        if row is None:
            self.lbl_login_error.config(text="Incorrect email or password.")
            return

        # Store session data
        self.app.current_user = {
            "user_id":    row[0],
            "first_name": row[1],
            "last_name":  row[2],
            "email":      row[3],
            "user_role":  row[4],
        }
        self.lbl_login_error.config(text="")
        self.ent_login_password.delete(0, "end")
        self.app.show_frame(HomeFrame)

    # -------------------------------------------------------
    def _do_register(self):
        """
        Validate all registration fields and create a new user account.
        All checks align with FR01 and NFR05.
        """
        fname    = self.ent_reg_fname.get().strip()
        lname    = self.ent_reg_lname.get().strip()
        email    = self.ent_reg_email.get().strip().lower()
        password = self.ent_reg_password.get()
        confirm  = self.ent_reg_confirm.get()
        role     = self.ddl_role.get()

        # --- Existence checks ---
        if not all([fname, lname, email, password, confirm]):
            self.lbl_reg_error.config(text="All fields are required.")
            return

        # --- Name format: letters only ---
        if not re.fullmatch(r"[A-Za-z\- ']+", fname) or \
           not re.fullmatch(r"[A-Za-z\- ']+", lname):
            self.lbl_reg_error.config(text="Names must contain letters only.")
            return

        # --- Email format check ---
        if not validate_email(email):
            self.lbl_reg_error.config(text="Please enter a valid email address.")
            return

        # --- Password strength check ---
        if not validate_password(password):
            self.lbl_reg_error.config(
                text="Password must be ≥ 8 characters and include a number "
                     "and a special character (e.g. !, @, #).")
            return

        # --- Password confirmation ---
        if password != confirm:
            self.lbl_reg_error.config(text="Passwords do not match.")
            return

        # --- Duplicate email check ---
        conn = sqlite3.connect("wanderlust.db")
        cur  = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE email=?", (email,))
        if cur.fetchone():
            self.lbl_reg_error.config(
                text="An account with this email already exists.")
            conn.close()
            return

        # --- Insert new user ---
        created_at = datetime.now().strftime("%d/%m/%Y %H:%M")
        cur.execute(
            "INSERT INTO users (first_name,last_name,email,password_hash,"
            "user_role,account_created) VALUES (?,?,?,?,?,?)",
            (fname, lname, email, hash_password(password), role, created_at)
        )
        conn.commit()
        user_id = cur.lastrowid
        conn.close()

        # Auto-login after registration
        self.app.current_user = {
            "user_id":    user_id,
            "first_name": fname,
            "last_name":  lname,
            "email":      email,
            "user_role":  role,
        }
        self.lbl_reg_error.config(text="")
        self.app.show_frame(HomeFrame)


# ============================================================
# FRAME 2 — HOME / DASHBOARD
# ============================================================

class HomeFrame(tk.Frame):
    """
    Main dashboard shown after login.
    Displays personalised welcome and quick-action tiles.
    """

    def __init__(self, parent, app: WanderlustApp):
        super().__init__(parent, bg=LIGHT_BG)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.hdr = make_header(self, self.app, "Dashboard")

        # Welcome banner
        self.lbl_welcome = tk.Label(self, text="", font=FONT_H1,
                                    fg=NAVY, bg=LIGHT_BG)
        self.lbl_welcome.pack(pady=(24, 4))
        tk.Label(self, text="Where would you like to go today?",
                 font=FONT_BODY, fg=MID_GREY, bg=LIGHT_BG).pack()

        # Quick-action tiles
        tiles_frame = tk.Frame(self, bg=LIGHT_BG)
        tiles_frame.pack(pady=30)

        tiles = [
            ("🔍\nSearch\nDestinations",  SearchFrame,    TEAL),
            ("📋\nItinerary\nBuilder",     ItineraryFrame, ACCENT),
            ("💾\nSaved\nTrips",           SavedTripsFrame,"#0A7558"),
            ("👥\nTravel\nCompanions",     CompanionFrame, "#7B3FA0"),
        ]
        for label, fc, color in tiles:
            btn = tk.Button(
                tiles_frame, text=label, font=("Arial", 13, "bold"),
                width=14, height=5, bg=color, fg=WHITE,
                relief="flat", cursor="hand2",
                activebackground=NAVY, activeforeground=WHITE,
                command=lambda f=fc: self.app.show_frame(f))
            btn.pack(side="left", padx=12)

        # Itinerary summary strip
        self.lbl_itin = tk.Label(self, text="", font=FONT_BODY,
                                 fg=NAVY, bg=LIGHT_BG)
        self.lbl_itin.pack(pady=8)

    def on_show(self):
        """Refresh personalised labels whenever this screen becomes visible."""
        user = self.app.current_user
        if user:
            name = user["first_name"]
            role = user["user_role"]
            self.lbl_welcome.config(
                text=f"Welcome back, {name}!  ({role} account)")
        n    = len(self.app.itinerary_items)
        cost = sum(i["price"] for i in self.app.itinerary_items)
        if n:
            self.lbl_itin.config(
                text=f"Current itinerary: {n} item(s)  |  "
                     f"Estimated total: ${cost:,.2f} AUD")
        else:
            self.lbl_itin.config(text="Your itinerary is empty — start by searching for a destination.")


# ============================================================
# FRAME 3 — DESTINATION SEARCH  (FR02 / FR03)
# ============================================================

class SearchFrame(tk.Frame):
    """
    Destination search screen.
    Accepts text + date + budget inputs, filters mock API data,
    and displays results as selectable cards.
    """

    def __init__(self, parent, app: WanderlustApp):
        super().__init__(parent, bg=LIGHT_BG)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        make_header(self, self.app, "Search Destinations")

        content = tk.Frame(self, bg=LIGHT_BG)
        content.pack(fill="both", expand=True, padx=30, pady=16)

        # ---- Left: search form ----
        form_card = tk.Frame(content, bg=WHITE, padx=20, pady=20,
                             relief="solid", bd=1)
        form_card.pack(side="left", fill="y", padx=(0, 20))

        tk.Label(form_card, text="Find Your Destination", font=FONT_H3,
                 fg=NAVY, bg=WHITE).grid(row=0, column=0, columnspan=2,
                                         sticky="w", pady=(0, 12))

        self.lbl_search_err = tk.Label(form_card, text="", font=FONT_SM,
                                       fg=ERROR_RED, bg=WHITE, wraplength=280)
        self.lbl_search_err.grid(row=1, column=0, columnspan=2)

        self.ent_dest      = labeled_entry(form_card, "Destination",       2, width=26)
        self.ent_depart    = labeled_entry(form_card, "Depart (DD/MM/YYYY)",3, width=26)
        self.ent_return    = labeled_entry(form_card, "Return (DD/MM/YYYY)",4, width=26)
        self.ent_budget    = labeled_entry(form_card, "Max Budget (AUD)",   5, width=26)

        tk.Label(form_card, text="Destination Type",
                 font=FONT_LABEL, bg=WHITE, fg=DARK_TXT, anchor="w").grid(
            row=6, column=0, sticky="w", pady=4)
        self.ddl_type = ttk.Combobox(
            form_card, values=["Any", "Beach", "City", "Mountain"],
            state="readonly", width=24, font=FONT_BODY)
        self.ddl_type.set("Any")
        self.ddl_type.grid(row=6, column=1, sticky="ew", pady=4)

        tk.Label(form_card, text="Travel Style",
                 font=FONT_LABEL, bg=WHITE, fg=DARK_TXT, anchor="w").grid(
            row=7, column=0, sticky="w", pady=4)
        self.ddl_style = ttk.Combobox(
            form_card, values=["Any", "Adventure", "Relaxation", "Cultural"],
            state="readonly", width=24, font=FONT_BODY)
        self.ddl_style.set("Any")
        self.ddl_style.grid(row=7, column=1, sticky="ew", pady=4)

        form_card.columnconfigure(1, weight=1)
        styled_button(form_card, "🔍  Search", self._do_search).grid(
            row=8, column=0, columnspan=2, pady=(16, 0), sticky="ew")

        # ---- Right: results panel ----
        results_frame = tk.Frame(content, bg=LIGHT_BG)
        results_frame.pack(side="left", fill="both", expand=True)

        tk.Label(results_frame, text="Results", font=FONT_H3,
                 fg=NAVY, bg=LIGHT_BG).pack(anchor="w")

        self.lbl_api_status = tk.Label(results_frame, text="Enter search details above.",
                                       font=FONT_BODY, fg=MID_GREY, bg=LIGHT_BG)
        self.lbl_api_status.pack(pady=8, anchor="w")

        # Scrollable result cards
        canvas = tk.Canvas(results_frame, bg=LIGHT_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical",
                                  command=canvas.yview)
        self.results_inner = tk.Frame(canvas, bg=LIGHT_BG)
        self.results_inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.results_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

    # -------------------------------------------------------
    def _do_search(self):
        """
        Validate search inputs and filter MOCK_DESTINATIONS.
        Simulates FR02 / FR03 behaviour without a live API.
        """
        dest   = self.ent_dest.get().strip()
        depart = self.ent_depart.get().strip()
        ret    = self.ent_return.get().strip()
        budget = self.ent_budget.get().strip()
        dtype  = self.ddl_type.get()
        dstyle = self.ddl_style.get()

        # Existence check (NFR04)
        if not dest:
            self.lbl_search_err.config(text="Please enter a destination.")
            return

        # Date validation (FR02)
        if depart and not validate_date_not_past(depart):
            self.lbl_search_err.config(
                text="Departure date must be today or in the future.")
            return
        if depart and ret and not validate_date_after(ret, depart):
            self.lbl_search_err.config(
                text="Return date must be after the departure date.")
            return

        # Budget: must be numeric and positive (FR02)
        budget_val = None
        if budget:
            try:
                budget_val = float(budget)
                if budget_val <= 0:
                    raise ValueError
            except ValueError:
                self.lbl_search_err.config(
                    text="Budget must be a positive number.")
                return

        self.lbl_search_err.config(text="")

        # Filter mock destinations (simulates FR03 API response)
        results = []
        for d in MOCK_DESTINATIONS:
            name_match  = dest.lower() in d["name"].lower()
            type_match  = (dtype  == "Any") or (d["type"]  == dtype)
            style_match = (dstyle == "Any") or (d["style"] == dstyle)
            if name_match or (type_match and style_match):
                results.append(d)

        self.app.search_results  = results
        self.app.itinerary_items  # preserved

        # Render result cards
        for widget in self.results_inner.winfo_children():
            widget.destroy()

        if not results:
            self.lbl_api_status.config(
                text="No destinations found matching your search. Try broader filters.")
            return

        self.lbl_api_status.config(
            text=f"{len(results)} destination(s) found:")

        for dest_data in results:
            self._make_result_card(self.results_inner, dest_data)

    # -------------------------------------------------------
    def _make_result_card(self, parent, dest: dict):
        """Build a card widget for one destination result."""
        card = tk.Frame(parent, bg=WHITE, padx=16, pady=12,
                        relief="solid", bd=1)
        card.pack(fill="x", pady=6, padx=4)

        header_row = tk.Frame(card, bg=WHITE)
        header_row.pack(fill="x")

        tk.Label(header_row, text=dest["name"], font=FONT_H3,
                 fg=NAVY, bg=WHITE).pack(side="left")

        badge_txt = f"  {dest['type']}  |  {dest['style']}  "
        tk.Label(header_row, text=badge_txt, font=FONT_SM,
                 bg=TEAL, fg=WHITE, padx=4).pack(side="right")

        tk.Label(card, text=dest["description"], font=FONT_BODY,
                 fg=MID_GREY, bg=WHITE, wraplength=480,
                 justify="left").pack(anchor="w", pady=(4, 8))

        # Cheapest flight price
        min_flight = min(dest["flights"], key=lambda f: f["price"])
        tk.Label(card, text=f"✈  Flights from  ${min_flight['price']:,} AUD",
                 font=FONT_BODY, fg=SUCCESS, bg=WHITE).pack(anchor="w")

        # View details button
        styled_button(card, "View Details & Add to Itinerary",
                      lambda d=dest: self._view_details(d),
                      bg=ACCENT, pady=6).pack(anchor="e", pady=(8, 0))

    # -------------------------------------------------------
    def _view_details(self, dest: dict):
        """Store selected destination and navigate to itinerary builder."""
        self.app.selected_dest = dest
        self.app.show_frame(ItineraryFrame)


# ============================================================
# FRAME 4 — ITINERARY BUILDER  (FR04 / FR05)
# ============================================================

class ItineraryFrame(tk.Frame):
    """
    Itinerary builder screen.
    Displays flights and hotels for the selected destination.
    Users can add/remove items and see a live running cost total (FR05).
    """

    def __init__(self, parent, app: WanderlustApp):
        super().__init__(parent, bg=LIGHT_BG)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        make_header(self, self.app, "Itinerary Builder")

        content = tk.Frame(self, bg=LIGHT_BG)
        content.pack(fill="both", expand=True, padx=24, pady=12)

        # ---- Left: destination options ----
        left = tk.Frame(content, bg=LIGHT_BG, width=480)
        left.pack(side="left", fill="both", padx=(0, 16))

        self.lbl_dest_title = tk.Label(left, text="Select a destination to begin.",
                                       font=FONT_H3, fg=NAVY, bg=LIGHT_BG, anchor="w")
        self.lbl_dest_title.pack(anchor="w", pady=(0, 8))

        # Flights section
        tk.Label(left, text="✈  Available Flights", font=FONT_H3,
                 fg=ACCENT, bg=LIGHT_BG).pack(anchor="w", pady=(8, 4))
        self.flights_frame = tk.Frame(left, bg=LIGHT_BG)
        self.flights_frame.pack(fill="x")

        # Hotels section
        tk.Label(left, text="🏨  Available Hotels", font=FONT_H3,
                 fg=ACCENT, bg=LIGHT_BG).pack(anchor="w", pady=(16, 4))
        self.hotels_frame = tk.Frame(left, bg=LIGHT_BG)
        self.hotels_frame.pack(fill="x")

        # ---- Right: current itinerary ----
        right = tk.Frame(content, bg=WHITE, padx=16, pady=16,
                         relief="solid", bd=1)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="📋  Current Itinerary",
                 font=FONT_H3, fg=NAVY, bg=WHITE).pack(anchor="w")

        self.itin_listbox = tk.Listbox(right, font=FONT_BODY,
                                       height=10, relief="solid", bd=1,
                                       selectbackground=TEAL)
        self.itin_listbox.pack(fill="both", expand=True, pady=(8, 0))

        styled_button(right, "✕  Remove Selected",
                      self._remove_item, bg=ERROR_RED, pady=6).pack(
            fill="x", pady=(8, 0))

        # Running total (FR05)
        self.lbl_total = tk.Label(right, text="Estimated Total:  $0.00 AUD",
                                  font=FONT_H2, fg=NAVY, bg=WHITE)
        self.lbl_total.pack(pady=(12, 8))

        tk.Label(right, text="* Estimate based on per-person costs.",
                 font=FONT_SM, fg=MID_GREY, bg=WHITE).pack()

        btn_row = tk.Frame(right, bg=WHITE)
        btn_row.pack(fill="x", pady=(12, 0))
        styled_button(btn_row, "💳  Proceed to Payment",
                      lambda: self.app.show_frame(PaymentFrame),
                      bg=SUCCESS, pady=8).pack(side="left", fill="x", expand=True, padx=(0, 6))
        styled_button(btn_row, "💾  Save Itinerary",
                      self._save_itinerary,
                      bg=ACCENT, pady=8).pack(side="left", fill="x", expand=True)

    # -------------------------------------------------------
    def on_show(self):
        """Refresh when frame becomes visible — rebuild options for selected destination."""
        self._refresh_destination_options()
        self._refresh_itinerary_list()

    def _refresh_destination_options(self):
        """Populate flight and hotel option cards from the selected destination."""
        dest = self.app.selected_dest
        for frame in (self.flights_frame, self.hotels_frame):
            for w in frame.winfo_children():
                w.destroy()

        if not dest:
            self.lbl_dest_title.config(
                text="← Go to Search to select a destination.")
            return

        self.lbl_dest_title.config(text=f"Destination: {dest['name']}")

        for flight in dest["flights"]:
            self._make_option_card(
                self.flights_frame,
                title=f"{flight['airline']}",
                detail=f"Departs {flight['departs']}  •  {flight['duration']}",
                price=flight["price"],
                item_type="Flight",
                item_name=f"{flight['airline']} to {dest['name']}",
            )

        nights_label = "(per night)"
        for hotel in dest["hotels"]:
            self._make_option_card(
                self.hotels_frame,
                title=hotel["name"],
                detail=f"{hotel['location']}  •  ★ {hotel['rating']}",
                price=hotel["price_night"],
                item_type="Hotel",
                item_name=f"{hotel['name']}, {dest['name']}",
                extra_label=nights_label,
            )

    def _make_option_card(self, parent, title, detail, price,
                          item_type, item_name, extra_label=""):
        """Create a compact card for a flight or hotel option with an Add button."""
        card = tk.Frame(parent, bg=WHITE, padx=10, pady=8, relief="solid", bd=1)
        card.pack(fill="x", pady=3)

        info = tk.Frame(card, bg=WHITE)
        info.pack(side="left", fill="x", expand=True)

        tk.Label(info, text=title, font=("Arial", 11, "bold"),
                 fg=DARK_TXT, bg=WHITE).pack(anchor="w")
        tk.Label(info, text=detail, font=FONT_SM,
                 fg=MID_GREY, bg=WHITE).pack(anchor="w")

        price_txt = f"${price:,} AUD {extra_label}"
        tk.Label(card, text=price_txt, font=("Arial", 11, "bold"),
                 fg=SUCCESS, bg=WHITE).pack(side="right", padx=(8, 6))

        styled_button(card, "+ Add",
                      lambda n=item_name, t=item_type, p=price:
                          self._add_item(n, t, p),
                      bg=TEAL, pady=4, padx=8).pack(side="right")

    # -------------------------------------------------------
    def _add_item(self, name: str, item_type: str, price: float):
        """Add an item to the itinerary and update the running total (FR04 / FR05)."""
        self.app.itinerary_items.append({
            "name":  name,
            "type":  item_type,
            "price": price,
        })
        self._refresh_itinerary_list()

    def _remove_item(self):
        """Remove the selected item from the itinerary (FR04)."""
        sel = self.itin_listbox.curselection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select an item to remove.")
            return
        idx = sel[0]
        self.app.itinerary_items.pop(idx)
        self._refresh_itinerary_list()

    def _refresh_itinerary_list(self):
        """Redraw the listbox and update the live running total (FR05)."""
        self.itin_listbox.delete(0, "end")
        total = 0.0
        for item in self.app.itinerary_items:
            self.itin_listbox.insert(
                "end", f"  [{item['type']}]  {item['name']}  —  ${item['price']:,} AUD")
            total += item["price"]
        # Live running total update (FR05)
        self.lbl_total.config(text=f"Estimated Total:  ${total:,.2f} AUD")

    # -------------------------------------------------------
    def _save_itinerary(self):
        """
        Prompt for itinerary name and persist to database (FR06).
        Requires user to be logged in.
        """
        if not self.app.current_user:
            messagebox.showwarning("Not Logged In",
                                   "Please log in to save your itinerary.")
            self.app.show_frame(LoginRegisterFrame)
            return
        if not self.app.itinerary_items:
            messagebox.showinfo("Empty Itinerary",
                                "Add at least one item before saving.")
            return

        dest_name = self.app.selected_dest["name"] if self.app.selected_dest else "My Trip"

        # Popup to name the itinerary
        popup = tk.Toplevel(self)
        popup.title("Save Itinerary")
        popup.geometry("360x160")
        popup.configure(bg=WHITE)
        popup.grab_set()

        tk.Label(popup, text="Name your itinerary:", font=FONT_BODY,
                 bg=WHITE, fg=DARK_TXT).pack(pady=(20, 6))
        ent_name = tk.Entry(popup, font=FONT_BODY, width=30,
                            relief="solid", bd=1)
        ent_name.insert(0, f"Trip to {dest_name}")
        ent_name.pack()

        def do_save():
            itin_name = ent_name.get().strip()
            if not itin_name:
                return
            conn = sqlite3.connect("wanderlust.db")
            cur  = conn.cursor()
            total = sum(i["price"] for i in self.app.itinerary_items)
            cur.execute(
                "INSERT INTO itineraries "
                "(user_id,itinerary_name,destination,items_json,total_cost,saved_at) "
                "VALUES (?,?,?,?,?,?)",
                (
                    self.app.current_user["user_id"],
                    itin_name,
                    dest_name,
                    json.dumps(self.app.itinerary_items),
                    total,
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                )
            )
            conn.commit()
            conn.close()
            popup.destroy()
            messagebox.showinfo("Saved", f'"{itin_name}" saved successfully!')

        styled_button(popup, "Save", do_save, pady=6).pack(pady=12)


# ============================================================
# FRAME 5 — PAYMENT  (FR07)
# ============================================================

class PaymentFrame(tk.Frame):
    """
    Payment screen.
    Validates card number (16 digits), expiry (MM/YY, not past),
    CVV (3 digits), and cardholder name before processing (FR07).
    """

    def __init__(self, parent, app: WanderlustApp):
        super().__init__(parent, bg=LIGHT_BG)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        make_header(self, self.app, "Payment")

        # Centre card
        card = tk.Frame(self, bg=WHITE, padx=40, pady=30,
                        relief="solid", bd=1)
        card.place(relx=0.5, rely=0.54, anchor="center")

        tk.Label(card, text="💳  Secure Payment", font=FONT_H2,
                 fg=NAVY, bg=WHITE).grid(row=0, column=0, columnspan=2, pady=(0, 6))

        self.lbl_order_total = tk.Label(card, text="", font=FONT_H3,
                                        fg=ACCENT, bg=WHITE)
        self.lbl_order_total.grid(row=1, column=0, columnspan=2, pady=(0, 16))

        self.lbl_pay_error = tk.Label(card, text="", font=FONT_SM,
                                      fg=ERROR_RED, bg=WHITE, wraplength=380)
        self.lbl_pay_error.grid(row=2, column=0, columnspan=2)

        # Payment fields (FR07)
        self.ent_card_holder = labeled_entry(card, "Cardholder Name",   3, width=30)
        self.ent_card_number = labeled_entry(card, "Card Number (16 digits)", 4, width=30)
        self.ent_expiry      = labeled_entry(card, "Expiry (MM/YY)",    5, width=30)
        self.ent_cvv         = labeled_entry(card, "CVV",               6, width=30, show="●")

        card.columnconfigure(1, weight=1)

        tk.Label(card, text="🔒  Your payment details are not stored.",
                 font=FONT_SM, fg=MID_GREY, bg=WHITE).grid(
            row=7, column=0, columnspan=2, pady=(8, 0))

        styled_button(card, "Confirm & Pay", self._do_payment,
                      bg=SUCCESS, width=22).grid(
            row=8, column=0, columnspan=2, pady=(16, 0))
        styled_button(card, "← Back to Itinerary",
                      lambda: self.app.show_frame(ItineraryFrame),
                      bg=MID_GREY, width=22).grid(
            row=9, column=0, columnspan=2, pady=(8, 0))

    def on_show(self):
        total = sum(i["price"] for i in self.app.itinerary_items)
        self.lbl_order_total.config(text=f"Order Total:  ${total:,.2f} AUD")

    # -------------------------------------------------------
    def _do_payment(self):
        """
        Validate all payment fields before confirming booking (FR07).
        Card details are validated but NOT stored (NFR05 / FR07 spec).
        """
        holder = self.ent_card_holder.get().strip()
        number = self.ent_card_number.get().strip()
        expiry = self.ent_expiry.get().strip()
        cvv    = self.ent_cvv.get().strip()

        # Existence check
        if not all([holder, number, expiry, cvv]):
            self.lbl_pay_error.config(
                text="All payment fields are required.")
            return

        # Cardholder name: letters and spaces only
        if not re.fullmatch(r"[A-Za-z\s]+", holder):
            self.lbl_pay_error.config(
                text="Cardholder name must contain letters only.")
            return

        # Card number: exactly 16 digits (FR07)
        if not validate_card_number(number):
            self.lbl_pay_error.config(
                text="Card number must be exactly 16 digits.")
            return

        # Expiry: MM/YY format and not expired (FR07)
        if not validate_expiry(expiry):
            self.lbl_pay_error.config(
                text="Expiry must be in MM/YY format and not be in the past.")
            return

        # CVV: 3 digits (FR07)
        if not validate_cvv(cvv):
            self.lbl_pay_error.config(
                text="CVV must be exactly 3 digits.")
            return

        # All checks passed — generate booking reference
        booking_ref = generate_booking_ref()
        total       = sum(i["price"] for i in self.app.itinerary_items)

        # Clear sensitive fields immediately (NFR05 — no data retention)
        self.ent_card_number.delete(0, "end")
        self.ent_cvv.delete(0, "end")
        self.lbl_pay_error.config(text="")

        # Show confirmation dialog
        msg = (
            f"✅  Booking Confirmed!\n\n"
            f"Booking Reference:  {booking_ref}\n"
            f"Total Charged:  ${total:,.2f} AUD\n\n"
            f"A confirmation summary has been generated.\n"
            f"Would you like to export your trip summary?"
        )
        export = messagebox.askyesno("Booking Confirmed!", msg)
        if export:
            self._export_summary(booking_ref, total)

        self.app.show_frame(HomeFrame)

    # -------------------------------------------------------
    def _export_summary(self, ref: str, total: float):
        """
        Generate and save a plain-text trip summary file (FR08).
        Filename format: LastName_BookingRef.txt
        """
        user     = self.app.current_user
        dest     = self.app.selected_dest
        lastname = user["last_name"] if user else "Guest"
        filename = f"{lastname}_{ref}.txt"
        filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)

        # Build summary content
        lines = [
            "=" * 50,
            "   WANDERLUST TRAVEL — TRIP SUMMARY",
            "=" * 50,
            f"Booking Reference : {ref}",
            f"Traveller         : {user['first_name']} {user['last_name']}",
            f"Email             : {user['email']}",
            f"Date Exported     : {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "",
            f"Destination: {dest['name'] if dest else 'N/A'}",
            "",
            "--- ITINERARY ITEMS ---",
        ]
        for item in self.app.itinerary_items:
            lines.append(f"  [{item['type']}]  {item['name']}  —  ${item['price']:,} AUD")
        lines += [
            "",
            f"TOTAL ESTIMATED COST:  ${total:,.2f} AUD",
            "=" * 50,
            "Thank you for booking with Wanderlust Travel.",
            "=" * 50,
        ]

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Export Successful",
                                f"Trip summary saved to:\n{filepath}")
        except OSError:
            # Fall back to working directory if Desktop not writable
            fallback = os.path.join(os.getcwd(), filename)
            with open(fallback, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Export Successful",
                                f"Trip summary saved to:\n{fallback}")


# ============================================================
# FRAME 6 — SAVED TRIPS  (FR06)
# ============================================================

class SavedTripsFrame(tk.Frame):
    """
    Saved trips screen.
    Fetches all itineraries for the logged-in user from the database
    and allows them to reload a trip into the itinerary builder (FR06).
    """

    def __init__(self, parent, app: WanderlustApp):
        super().__init__(parent, bg=LIGHT_BG)
        self.app  = app
        self._rows = []     # list of fetched database rows
        self._build_ui()

    def _build_ui(self):
        make_header(self, self.app, "Saved Trips")

        content = tk.Frame(self, bg=LIGHT_BG)
        content.pack(fill="both", expand=True, padx=30, pady=16)

        tk.Label(content, text="Your Saved Itineraries",
                 font=FONT_H2, fg=NAVY, bg=LIGHT_BG).pack(anchor="w")

        self.lbl_none = tk.Label(content, text="No saved trips found.",
                                 font=FONT_BODY, fg=MID_GREY, bg=LIGHT_BG)
        self.lbl_none.pack(pady=20)

        # Table headers
        header_frame = tk.Frame(content, bg=NAVY)
        header_frame.pack(fill="x", pady=(12, 0))
        for col, width in [("Trip Name", 24), ("Destination", 20),
                           ("Saved On", 18), ("Total (AUD)", 14), ("", 14)]:
            tk.Label(header_frame, text=col, font=("Arial", 11, "bold"),
                     fg=WHITE, bg=NAVY, width=width, anchor="w",
                     padx=8).pack(side="left")

        # Scrollable rows frame
        canvas = tk.Canvas(content, bg=LIGHT_BG, highlightthickness=0)
        sb = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        self.rows_frame = tk.Frame(canvas, bg=LIGHT_BG)
        self.rows_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

    # -------------------------------------------------------
    def on_show(self):
        """Reload saved trips from database whenever this frame is shown."""
        for w in self.rows_frame.winfo_children():
            w.destroy()

        if not self.app.current_user:
            return

        conn = sqlite3.connect("wanderlust.db")
        cur  = conn.cursor()
        cur.execute(
            "SELECT itinerary_id, itinerary_name, destination, "
            "saved_at, total_cost, items_json "
            "FROM itineraries WHERE user_id=? ORDER BY saved_at DESC",
            (self.app.current_user["user_id"],)
        )
        self._rows = cur.fetchall()
        conn.close()

        if not self._rows:
            self.lbl_none.config(text="No saved trips found. Build an itinerary and save it!")
            return

        self.lbl_none.config(text="")
        even = True
        for row in self._rows:
            bg = "#EEF2FF" if even else WHITE
            even = not even
            self._make_row(row, bg)

    def _make_row(self, row, bg: str):
        """Build a single table row for a saved itinerary."""
        itin_id, name, dest, saved, total, items_json = row
        row_frame = tk.Frame(self.rows_frame, bg=bg)
        row_frame.pack(fill="x")

        for text, width in [(name, 24), (dest, 20), (saved, 18),
                            (f"${total:,.2f}", 14)]:
            tk.Label(row_frame, text=text, font=FONT_BODY,
                     bg=bg, fg=DARK_TXT, width=width, anchor="w",
                     padx=8, pady=6).pack(side="left")

        styled_button(row_frame, "Load Trip",
                      lambda j=items_json, d=dest: self._load_trip(j, d),
                      bg=ACCENT, pady=4, padx=10).pack(side="left", padx=4)

    def _load_trip(self, items_json: str, dest_name: str):
        """Restore a saved itinerary into the active session (FR06)."""
        items = json.loads(items_json)
        self.app.itinerary_items = items

        # Try to match saved destination to mock data
        matched = next((d for d in MOCK_DESTINATIONS
                        if d["name"] == dest_name), None)
        self.app.selected_dest = matched

        messagebox.showinfo("Trip Loaded",
                            f"'{dest_name}' itinerary loaded into the builder.")
        self.app.show_frame(ItineraryFrame)


# ============================================================
# FRAME 7 — COMPANION DISCOVERY  (FR10)
# ============================================================

class CompanionFrame(tk.Frame):
    """
    Travel Companion Discovery feed (FR10).
    Displays mock and user-posted trip cards.
    Logged-in users can post their own companion trip.
    """

    def __init__(self, parent, app: WanderlustApp):
        super().__init__(parent, bg=LIGHT_BG)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        make_header(self, self.app, "Travel Companion Discovery")

        content = tk.Frame(self, bg=LIGHT_BG)
        content.pack(fill="both", expand=True, padx=24, pady=12)

        # ---- Left: post a trip ----
        left = tk.Frame(content, bg=WHITE, padx=20, pady=20,
                        relief="solid", bd=1, width=300)
        left.pack(side="left", fill="y", padx=(0, 20))
        left.pack_propagate(False)

        tk.Label(left, text="Post Your Trip", font=FONT_H3,
                 fg=NAVY, bg=WHITE).pack(anchor="w", pady=(0, 10))

        self.lbl_post_err = tk.Label(left, text="", font=FONT_SM,
                                     fg=ERROR_RED, bg=WHITE, wraplength=240)
        self.lbl_post_err.pack()

        def lbl_ent(label, show=""):
            tk.Label(left, text=label, font=FONT_LABEL,
                     fg=DARK_TXT, bg=WHITE, anchor="w").pack(fill="x")
            ent = tk.Entry(left, font=FONT_BODY, relief="solid", bd=1,
                           bg="#F9FAFB", show=show)
            ent.pack(fill="x", pady=(0, 8))
            return ent

        self.ent_p_dest   = lbl_ent("Destination")
        self.ent_p_depart = lbl_ent("Depart (DD/MM/YYYY)")
        self.ent_p_return = lbl_ent("Return (DD/MM/YYYY)")
        self.ent_p_budget = lbl_ent("Max Budget (AUD)")

        tk.Label(left, text="Travel Style", font=FONT_LABEL,
                 fg=DARK_TXT, bg=WHITE, anchor="w").pack(fill="x")
        self.ddl_p_style = ttk.Combobox(
            left, values=["Adventure", "Relaxation", "Cultural", "Business"],
            state="readonly", font=FONT_BODY)
        self.ddl_p_style.set("Adventure")
        self.ddl_p_style.pack(fill="x", pady=(0, 8))

        tk.Label(left, text="Short Bio", font=FONT_LABEL,
                 fg=DARK_TXT, bg=WHITE, anchor="w").pack(fill="x")
        self.txt_bio = tk.Text(left, font=FONT_BODY, height=4,
                               relief="solid", bd=1, bg="#F9FAFB")
        self.txt_bio.pack(fill="x", pady=(0, 12))

        styled_button(left, "Post to Feed", self._post_trip, pady=6).pack(fill="x")

        # ---- Right: companion feed ----
        right = tk.Frame(content, bg=LIGHT_BG)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="Companion Feed", font=FONT_H3,
                 fg=NAVY, bg=LIGHT_BG).pack(anchor="w", pady=(0, 8))

        canvas = tk.Canvas(right, bg=LIGHT_BG, highlightthickness=0)
        sb = ttk.Scrollbar(right, orient="vertical", command=canvas.yview)
        self.feed_frame = tk.Frame(canvas, bg=LIGHT_BG)
        self.feed_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.feed_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

    # -------------------------------------------------------
    def on_show(self):
        """Refresh feed when frame is shown."""
        self._refresh_feed()

    def _refresh_feed(self):
        """Load mock posts + database posts into the feed."""
        for w in self.feed_frame.winfo_children():
            w.destroy()

        # Mock posts (always shown)
        for post in MOCK_COMPANION_POSTS:
            self._make_feed_card(post["poster"], post["destination"],
                                 post["dates"], post["budget"],
                                 post["style"], post["bio"])

        # Database posts (user-submitted) (FR10)
        conn = sqlite3.connect("wanderlust.db")
        cur  = conn.cursor()
        cur.execute(
            "SELECT poster_name, destination, departure_date, return_date, "
            "budget_max, travel_style, bio "
            "FROM companion_posts ORDER BY post_id DESC"
        )
        db_posts = cur.fetchall()
        conn.close()

        for row in db_posts:
            name, dest, dep, ret, budget, style, bio = row
            dates = f"{dep} – {ret}" if dep and ret else "Dates TBD"
            budget_str = f"${budget:,.0f} AUD" if budget else "Flexible"
            self._make_feed_card(name, dest, dates, budget_str, style, bio)

    def _make_feed_card(self, poster, dest, dates, budget, style, bio):
        """Build a companion post card widget."""
        card = tk.Frame(self.feed_frame, bg=WHITE, padx=14, pady=10,
                        relief="solid", bd=1)
        card.pack(fill="x", pady=5, padx=4)

        top_row = tk.Frame(card, bg=WHITE)
        top_row.pack(fill="x")

        tk.Label(top_row, text=f"👤  {poster}", font=("Arial", 12, "bold"),
                 fg=NAVY, bg=WHITE).pack(side="left")
        tk.Label(top_row, text=f"  {style}  ", font=FONT_SM,
                 bg=TEAL, fg=WHITE).pack(side="right")

        tk.Label(card, text=f"📍  {dest}   |   📅  {dates}   |   💰  {budget}",
                 font=FONT_BODY, fg=ACCENT, bg=WHITE).pack(anchor="w", pady=4)
        tk.Label(card, text=bio, font=FONT_SM, fg=MID_GREY, bg=WHITE,
                 wraplength=500, justify="left").pack(anchor="w")

        styled_button(card, "Request to Join",
                      lambda p=poster: messagebox.showinfo(
                          "Request Sent",
                          f"Your request to join {p}'s trip has been sent!\n"
                          f"{p} will be notified and must approve before "
                          f"contact details are shared."),
                      bg=ACCENT, pady=4).pack(anchor="e", pady=(8, 0))

    # -------------------------------------------------------
    def _post_trip(self):
        """
        Validate and save a companion trip post to the database (FR10).
        User must be logged in.
        """
        if not self.app.current_user:
            messagebox.showwarning("Login Required",
                                   "Please log in to post a trip.")
            self.app.show_frame(LoginRegisterFrame)
            return

        dest   = self.ent_p_dest.get().strip()
        depart = self.ent_p_depart.get().strip()
        ret    = self.ent_p_return.get().strip()
        budget = self.ent_p_budget.get().strip()
        style  = self.ddl_p_style.get()
        bio    = self.txt_bio.get("1.0", "end").strip()

        # Existence check (FR10)
        if not dest:
            self.lbl_post_err.config(text="Destination is required.")
            return

        # Date validation
        if depart and not validate_date_not_past(depart):
            self.lbl_post_err.config(
                text="Departure date must be in the future.")
            return
        if depart and ret and not validate_date_after(ret, depart):
            self.lbl_post_err.config(
                text="Return must be after departure.")
            return

        # Budget validation
        budget_val = None
        if budget:
            try:
                budget_val = float(budget)
                if budget_val <= 0:
                    raise ValueError
            except ValueError:
                self.lbl_post_err.config(
                    text="Budget must be a positive number.")
                return

        # Bio length limit: 500 chars (FR10)
        if len(bio) > 500:
            self.lbl_post_err.config(
                text="Bio must be 500 characters or fewer.")
            return

        user = self.app.current_user
        poster_name = f"{user['first_name']} {user['last_name'][0]}."

        conn = sqlite3.connect("wanderlust.db")
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO companion_posts "
            "(user_id,poster_name,destination,departure_date,return_date,"
            "budget_min,budget_max,travel_style,bio,posted_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                user["user_id"], poster_name, dest, depart, ret,
                0, budget_val, style, bio,
                datetime.now().strftime("%d/%m/%Y %H:%M"),
            )
        )
        conn.commit()
        conn.close()

        # Clear form
        self.ent_p_dest.delete(0, "end")
        self.ent_p_depart.delete(0, "end")
        self.ent_p_return.delete(0, "end")
        self.ent_p_budget.delete(0, "end")
        self.txt_bio.delete("1.0", "end")
        self.lbl_post_err.config(text="")

        self._refresh_feed()
        messagebox.showinfo("Posted!", "Your trip has been posted to the companion feed.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    init_database()
    app = WanderlustApp()
    app.mainloop()
