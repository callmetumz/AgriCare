# AgriCare

**Livestock health and biosecurity for small-scale farms and animal sanctuaries.**

AgriCare keeps every animal's health record in one place: profiles, illness reports, vaccinations and quarantine. It flags possible disease outbreaks early and keeps an audit trail of every change. This repository holds the **Step 5 program-code prototype** for the CSC312 Software Engineering project at the University of the Western Cape. It is an evolutionary prototype: the code is the base for the completed application, not a throw-away mock-up.

![AgriCare dashboard](docs/screenshots/dashboard.png)

## Implemented features

| Feature | What it does | Traces to |
|---|---|---|
| Animal files | Create, list and open animal profiles identified by RFID/ear-tag ID; duplicate tags are rejected | UC01, FR-02–04 |
| Illness triage | Records symptoms and classifies severity as Low, Moderate or Urgent; Moderate/Urgent reports flag a healthy animal as Suspect | UC03, FR-07 |
| Quarantine | Veterinarian-only state changes along Healthy → Suspect → Isolated → Monitored → Cleared; invalid jumps are rejected | UC04, FR-08 |
| Vaccinations | Veterinarian-only recording with the booster due date calculated automatically | UC02, FR-05–06 |
| Outbreak flag | Three or more animals in one enclosure with the same body-system symptoms within 72 hours raise an alert | UC06, FR-10 |
| Dashboard | Totals for animals, quarantine, urgent cases, overdue vaccinations and outbreak flags | UC08, FR-12 |
| Audit trail | Every create, report, vaccination and quarantine action is logged; only Manager, Administrator and Auditor can read it | UC10, FR-14 |

All rules and role checks run on the server, so they apply whatever client calls the API.

## Screenshots

| Animal files | Clinical actions |
|---|---|
| ![Animal files](docs/screenshots/animal-files.png) | ![Clinical actions](docs/screenshots/clinical-actions.png) |
| **Audit trail** | **Phone width** |
| ![Audit trail](docs/screenshots/audit-trail.png) | <img src="docs/screenshots/mobile-dashboard.png" width="220" alt="Mobile dashboard"> |

## Technology

- **Backend:** Python, FastAPI, Pydantic, Uvicorn
- **Data:** SQLAlchemy ORM, with SQLite for the prototype and MySQL as the target database
- **Frontend:** HTML, CSS and JavaScript, kept separate from the API so it can be replaced by React later
- **Testing:** pytest

## Project structure

```
AgriCare/
├── backend/
│   ├── main.py          # REST endpoints, role checks, outbreak check, audit logging
│   ├── rules.py         # Business rules: severity, quarantine transitions, booster dates
│   ├── models.py        # SQLAlchemy models (database tables)
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── database.py      # Engine and session setup (DATABASE_URL)
│   └── seed.py          # Demonstration data
├── frontend/            # index.html, app.js, styles.css
├── tests/test_rules.py  # Automated rule tests
├── docs/                # Step 5 report, traceability, architecture, screenshots
├── requirements.txt
├── run_demo.bat         # Windows: seed data and start the server
└── run_demo.sh          # macOS/Linux: seed data and start the server
```

## Run it locally

You need Python 3.10 or newer.

**Windows (PowerShell)**

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m backend.seed
uvicorn backend.main:app --reload
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m backend.seed
uvicorn backend.main:app --reload
```

Open **http://127.0.0.1:8000** and choose a demo role at the top right. After installing the requirements, `run_demo.bat` or `run_demo.sh` runs the seed and start steps in one go.

Run the tests with:

```bash
python -m pytest
```

### Demo roles

| Role | Can do in the prototype |
|---|---|
| Care Staff | Create animal profiles, report illness |
| Farmer / Owner | Create animal profiles, report illness |
| Veterinarian | Record vaccinations, report illness, change quarantine state |
| Facility Manager | Create profiles, read the audit trail |
| Auditor | Read the audit trail |
| Administrator | Read the audit trail |

The role selector stands in for proper login during the prototype stage. Production code will replace it with registered users, hashed passwords and server-side identity.

### Use MySQL instead of SQLite

Install a MySQL driver such as `pymysql`, create a database, then set the connection string before seeding and starting:

```powershell
$env:DATABASE_URL="mysql+pymysql://username:password@localhost/agricare"
```

## Known limitations

These are recorded in the report and planned for the next sprint:

- Symptoms are typed as free text and matched exactly, so "Breathing difficulties" is classed Low instead of Urgent. The fix is a coded symptom checklist.
- The quarantine form lists all five states; only the permitted next states should be offered (the server already rejects invalid ones).
- The dashboard shows the same counts to every role; role-specific views are planned.
- The role selector is not real authentication.
- Treatments, weather alerts, notifications and security incidents are not built yet.

## Documentation

- [Step 5 report: requirements, design model and prototype (PDF)](docs/AgriCare_Step5_Design_and_Prototype_Report.pdf)
- [Requirements traceability](docs/requirements_traceability.md)

## Team: The Equal SQLs

- Tumelo Aphane (group leader)
- Yanga Madosi
- Caleb Meyer
- Nhlamulo Maluleka
- Tanya Hadebe

CSC312 Software Engineering, University of the Western Cape, 2026.
