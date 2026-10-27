# AI Face Recognition Attendance System

An automated facial recognition attendance logging system powered by Django, OpenCV, and `face_recognition` (dlib). The application provides real-time face detection, liveness verification, automated daily attendance recording, and an administrative dashboard for managing employees and attendance records.

---

## 🌟 Key Features

- **Automated Facial Attendance**: Real-time detection and recognition of registered employees via webcam/IP camera stream.
- **Liveness Detection**: Integrated anti-spoofing verification to prevent fraud via static photos or screen replays.
- **Duplicate Prevention**: Enforces a strict one-attendance-per-day constraint per employee.
- **Admin Management Portal**:
  - Employee enrollment with photo uploads.
  - Live employee records management (Add, View, Edit, Delete).
  - Attendance analytics, filterable daily logs, and Excel/CSV report exports.
- **Threaded Face Encoding Cache**: Preloads and caches face encodings in memory for low-latency real-time inference.
- **Standalone CLI Logging Utility**: Includes a `main.py` script for running local camera recognition and CSV logging independently of the web UI.

---

## 📁 Repository Structure

```
├── Mainapp/                  # Core Django application
│   ├── liveness.py           # Liveness & anti-spoofing detection logic
│   ├── models.py             # Employee & Attendance models
│   ├── services.py           # Face encoding caching & matching engine
│   ├── views.py              # Camera stream & dashboard views
│   ├── forms.py              # Employee management forms
│   └── migrations/           # Database schema migrations
├── faceapp/                  # Django project configuration & routing
│   ├── settings.py           # Application settings
│   ├── urls.py               # Root URL declarations
│   └── wsgi.py               # WSGI configuration
├── templates/                # Frontend HTML templates (Admin & Attendance UI)
├── static/                   # Static assets (CSS, JS, images)
├── media/                    # Uploaded employee photos (ignored by git)
│   └── documents/
├── main.py                   # Standalone OpenCV face attendance logger script
├── manage.py                 # Django management script
├── requirements.txt          # Python package dependencies
├── .env.example              # Environment variables template
└── .gitignore                # Git ignore rules for virtual environments & media
```

---

## ⚙️ Prerequisites

1. **Python 3.10+**
2. **C++ Compiler & CMake** (Required for building `dlib`):
   - **macOS**: `brew install cmake`
   - **Ubuntu/Debian**: `sudo apt-get install build-essential cmake libopenblas-dev liblapack-dev`
   - **Windows**: Install Visual Studio with C++ CMake tools.
3. **MySQL Server**: Ensure MySQL server is running and a database named `faceapp` is created.

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Face app"
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Configure Database & Environment
1. Create a MySQL database for the project:
   ```sql
   CREATE DATABASE faceapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. Check `faceapp/settings.py` and configure your database credentials:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'faceapp',
           'USER': 'root',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

### 5. Apply Migrations & Create Superuser
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the Application
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🖥️ Running Standalone CLI Attendance Logger

To run the camera face recognition script outside the web interface:
```bash
python main.py
```
Press `q` to terminate the video stream. Attendance records will be logged to MySQL and exported to `detection_log_YYYY-MM-DD.csv`.

---

## 🔒 Security & Privacy Notes

- Employee photos uploaded into `media/documents/` contain personal biometric information and are excluded from git version tracking via `.gitignore`.
- Ensure production deployments generate a unique `SECRET_KEY` and set `DEBUG = False`.

---

## 📄 License
This project is licensed under the MIT License.
