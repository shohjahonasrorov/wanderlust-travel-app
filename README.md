# ✈ Wanderlust Travel App

A Python/Tkinter desktop application for **Wanderlust Travel Agency** - search destinations, build itineraries, book trips, and find travel companions, all in one app.

Built for Assessment Task 3A (2026).

---

## Features

- 🔐 **Login & Registration** - secure accounts with hashed passwords
- 🔍 **Destination Search** - filter by type, style, dates, and budget
- 📋 **Itinerary Builder** - add flights and hotels, live running cost total
- 💳 **Payment Screen** - validated card details, booking reference generated
- 💾 **Saved Trips** - save and reload itineraries from your account
- 📄 **Trip Export** - download a `.txt` summary of your booking
- 👥 **Companion Discovery** - post trips and browse travel companions

---

## Requirements

- **Python 3.10 or later** - [download here](https://www.python.org/downloads/)
- No additional libraries needed - uses Python's standard library only

---

## How to Run

### Option 1 - Clone and run (recommended)

```bash
git clone https://github.com/YOUR_USERNAME/wanderlust-travel-app.git
cd wanderlust-travel-app
python wanderlust_app.py
```

### Option 2 - Windows double-click launcher

After cloning, just double-click **`run.bat`** - it checks for Python and launches the app automatically.

### Option 3 - Mac / Linux

```bash
bash run.sh
```

---

## First Run

On first launch, the app automatically creates a local `wanderlust.db` SQLite database in the project folder. This stores your user account, saved itineraries, and companion posts. The database is excluded from the repository (see `.gitignore`).

---

## Project Structure

```
wanderlust-travel-app/
├── wanderlust_app.py     # Main application - all screens and logic
├── requirements.txt      # Python dependencies (none required currently)
├── run.bat               # Windows launcher
├── run.sh                # Mac/Linux launcher
├── .gitignore            # Excludes database and cache files
└── README.md             # This file
```

---

## Screens

| Screen | Description |
|---|---|
| Login / Register | Create account or log in with email + password |
| Home Dashboard | Welcome screen with quick-access tiles |
| Destination Search | Search and filter 6 mock destinations |
| Itinerary Builder | Add flights/hotels, view live cost total |
| Payment | Validate and confirm booking, generate reference |
| Saved Trips | View and reload all previously saved itineraries |
| Companion Discovery | Browse and post companion travel trips |

---

## Developer Notes

- Passwords stored as **SHA-256 hashes** - never plain text
- Payment card details are **validated but never stored**
- All validation functions are independently testable (see Testing Report)
- Code follows **PEP 8** style guidelines throughout
- Every function and class has a **docstring** for maintainability

---

## Future Updates (planned)

- [ ] CustomTkinter upgrade for modern UI
- [ ] Live API integration (Amadeus / Skyscanner)
- [ ] PDF export via ReportLab
- [ ] Profile photos via Pillow
- [ ] In-app messaging between matched companions

---

*Wanderlust Travel App - RMIT University 2026*
