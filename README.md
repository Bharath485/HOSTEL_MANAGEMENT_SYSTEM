
# 🏨 Hostel Management System (Streamlit + Python)

A full-featured **Hostel Management System** built using **Python**, **Streamlit**, and **CSV-based persistent storage**.  
This system is designed for hostel owners to manage **rooms, students, bookings, payments, and occupancy** with ease.  
Each user who signs up gets a **separate, private hostel account** — meaning **no data is shared between users**.

---

## 🚀 Live Demo
| App | Status |
|-----|--------|
| **Live Streamlit App** | https://hostel-management-system.streamlit.app/ |

Click to open → Sign up → Generate rooms → Start managing ✅

---

## ✨ Key Features
### 🧑‍🎓 Student Management
- Add students with contact details
- View and manage student records (per user only)

### 🏠 Room Management
- Auto-generate **100 rooms**:
  - Rooms `01–50` → **3-Sharing** (₹40,000 / 6 months)
  - Rooms `51–100` → **2-Sharing** (₹50,000 / 6 months)
- Automatic **capacity & occupancy tracking**
- Visual room map (color-coded availability)

### 🛏️ Booking System
- Book a room for any student
- Prevents **overbooking** (real-time availability check)
- Updates occupancy automatically

### 💰 Fees & Payment Tracking
- Pay-and-Book workflow integrated
- Stores payment date, amount, and status

### 🔐 Secure Multi-User Data Isolation
- Every signup becomes **Admin** of their hostel
- Users **do not see or share each other's data**

---

## 🖼️ Dashboard Overview
The dashboard displays:

| Metric | Description |
|--------|-------------|
| Total Students | Count in your hostel |
| Total Rooms | Assigned to your account |
| Active Bookings | Students currently staying |
| Vacant Beds | Available capacity |

Plus segment-wise vacancy (2-share vs 3-share).


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
