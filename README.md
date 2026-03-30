# TaskFlow 🚀

**TaskFlow** is a modern, full-stack productivity application built with Flask and Tailwind CSS. It features a clean, minimalist design with a focus on ease of use, security, and personal customization.

---

## ✨ Features

- **✅ Task Management**: Effortlessly add, view, and delete tasks. Stay organized with a simple completion toggle.
- **👤 Profile Customization**: 
  - Upload a custom **Profile Picture**.
  - Automatically generated **Smart Avatars** based on your username.
  - Edit your username and securely update your password.
- **🔐 Security**: 
  - **Password Hashing** using `werkzeug.security` (PBKDF2 with SHA256).
  - **Session-based Authentication** for secure access to personal data.
  - **Secure File Uploads** for profile images.
- **🎨 Modern UI/UX**:
  - **Tailwind CSS**: Professional, responsive, and aesthetically pleasing interface.
  - **Glassmorphism**: High-end navbar with backdrop-blur.
  - **Animations**: Smooth fade-in transitions and interactive hover effects.
  - **Dynamic Flash Messages**: Real-time feedback for all user actions.
- **📁 Local Persistence**: Fast and lightweight **SQLite** database integration.

---

## 🛠 Tech Stack

- **Backend**: Python (Flask)
- **Database**: SQLite
- **Frontend**: Tailwind CSS, Jinja2, FontAwesome
- **Configuration**: `python-dotenv` for environment secrets

---

## 🚀 Setup & Run

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your machine.

### 2. Clone and Install
```bash
# Clone the repository
git clone <your-repo-link>
cd taskflow-flask-app

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and set a strong `SECRET_KEY`.

### 4. Launch
```bash
python app.py
```
- **Access the app**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- *Note: The database (`database.db`) is automatically initialized on the first launch.*

---

## 📸 Screenshots

*(Add screenshots here after running the app)*

---

## 📄 License
MIT License. Feel free to use and modify for your own projects!
