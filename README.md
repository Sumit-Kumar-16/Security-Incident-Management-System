# Security Incident & Log Management System

A web-based **Security Incident & Log Management System** built with **Python Flask, MySQL, HTML, CSS, and Jinja2**.

The application helps security teams record, monitor, investigate, and manage security incidents with role-based access control.

## 🚀 Features

* 🔐 User authentication and secure password hashing
* 🛡️ Role-Based Access Control (Admin, Analyst, Viewer)
* 🚨 Create and manage security incidents
* 🔎 Search and filter incidents
* 👨‍💻 Assign incidents to security analysts
* 📝 Add investigation notes
* 📊 Security dashboard
* 👥 User and role management
* 📋 Activity/audit logging
* 🔒 Server-side authorization and input validation

## 🛠️ Technologies

* Python
* Flask
* MySQL
* HTML5
* CSS3
* Jinja2
* Werkzeug

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sumit-Kumar-16/Security-Incident-Management-System.git
cd Security-Incident-Management-System
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

Create a MySQL database and configure the database connection in `database.py`.

Update the following values according to your local MySQL setup:

```python
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_MYSQL_PASSWORD",
    database="security_incident_db"
)
```

Create the required database tables before running the application.

### 5. Run the application

```bash
python app.py
```

The application will start locally. Open the URL shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

## 👤 Roles

| Role        | Access                                |
| ----------- | ------------------------------------- |
| **Admin**   | Full system access                    |
| **Analyst** | Incident investigation and management |
| **Viewer**  | Read-only incident access             |

## 📂 Project Structure

```text
security_incident_system/
│
├── app.py
├── auth.py
├── database.py
├── requirements.txt
│
├── static/
│   └── style.css
│
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── incidents.html
    ├── create_incident.html
    ├── incident_details.html
    ├── edit_incident.html
    ├── admin.html
    ├── manage_users.html
    └── activity_logs.html
```

## 🎯 Security Concepts

This project demonstrates:

* Authentication & Authorization
* Role-Based Access Control (RBAC)
* Password Hashing
* SQL Injection Prevention
* Input Validation
* Session Management
* Audit Logging
* Least-Privilege Access



## 👨‍💻 Author

**Sumit Kumar**

Cybersecurity Engineer


