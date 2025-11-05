
# Hostel Management System (Streamlit + CSV)

A lightweight, file-based Hostel Management System built with **Python** and **Streamlit**.
Data is stored in simple **CSV** files under the `data/` directory.

## Features
- Dashboard with quick metrics
- Students management (add/list)
- Rooms management (add/list)
- Bookings and Fees stubs (ready to extend)
- File-based services with CSV CRUD helpers

## Run Locally
```bash
# 1) create and activate a virtual env (recommended)
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# 2) install dependencies
pip install -r requirements.txt

# 3) run app
streamlit run app.py
```

## Project Layout
```
.
├─ app.py
├─ requirements.txt
├─ src/
│  ├─ models/
│  ├─ services/
│  ├─ utils/
│  └─ views/
├─ data/           # CSV data saved here
└─ tests/
```

## Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Hostel Management System scaffold"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```
