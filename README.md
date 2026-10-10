# AgriCare - Step 5 Program-Code Prototype

This prototype implements a runnable subset of the Step 4 requirements so it can evolve into the completed AgriCare application.

## Implemented key functionality
- Animal profile creation and viewing (UC01; FR-02 to FR-04)
- Illness and symptom reporting with rule-based severity classification (UC03; FR-07)
- Automatic Suspect flag for Moderate/Urgent illness reports
- Veterinarian-only quarantine state changes with transition validation (UC04; FR-08)
- Veterinarian-only vaccination recording with calculated booster due date (UC02; FR-05/FR-06)
- Dashboard summary of animals, quarantine, urgent reports, overdue vaccination records and outbreak flags (part of UC08)
- Simple 72-hour/enclosure outbreak flag rule from the Step 4 behavioural analysis (part of UC06/FR-10)
- Audit logging and role-limited audit viewing (UC10/FR-14)
- Role-aware prototype restrictions using the `X-Role` header

## Technology
- Backend/API: Python + FastAPI
- ORM: SQLAlchemy
- Prototype database: SQLite by default for easy demonstration
- Target database: MySQL is supported by setting `DATABASE_URL`
- Frontend: coded HTML/CSS/JavaScript prototype served by FastAPI

The Step 4 proposal selected React for the production front end. The Step 5 prototype deliberately keeps the browser layer dependency-free so the group can run it immediately on a lab/Windows machine. The UI and API are separated, so the same FastAPI endpoints can be consumed by React in the next iteration.

## Run on Windows
From the project folder:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m backend.seed
uvicorn backend.main:app --reload
```

Open: `http://127.0.0.1:8000`

## Run on macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m backend.seed
uvicorn backend.main:app --reload
```

## Demo roles
Select a role in the top-right of the interface.
- Care Staff: create animal profiles and report illness
- Farmer/Owner: create animal profiles and report illness
- Veterinarian: record vaccinations, report illness, change quarantine state
- Manager: view audit trail and create profiles
- Auditor: read audit trail
- Administrator: read audit trail in this prototype

The role selector is a prototype substitute for full authentication. Production code should replace it with secure login, hashed credentials, session/JWT handling and server-side user/role lookup.

## Use MySQL instead of SQLite
Install a MySQL driver such as `pymysql`, create a database, then set:

```powershell
$env:DATABASE_URL="mysql+pymysql://username:password@localhost/agricare"
```

Then rerun `python -m backend.seed` and start Uvicorn.
