# AI Meeting Decision & Action Extractor — Company Meeting Portal

Production-ready company meeting management portal and Generative AI-based meeting transcript analysis system built using **Django, Python, and Firebase**.

---

## 🏛️ 1. PROJECT ARCHITECTURE & DESIGN

```
Schedule/
│
├── manage.py
│
├── config/                  # Global Settings & URLs
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                # Firebase Auth, User Models & Weekly Availabilities
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   ├── services.py
│   └── authentication.py
│
├── meetings/                # Meeting Creation, Scheduling & Availability Engine
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── services.py
│
├── transcripts/             # File Upload (TXT, PDF, DOCX) & Parser Pipeline
│   ├── models.py
│   ├── views.py
│   ├── parsers.py
│   └── serializers.py
│
├── ai_extractor/            # Generative AI Prompting, Schemas & Multi-LLM Engine
│   ├── prompts.py
│   ├── extractor.py
│   ├── schemas.py
│   └── services.py
│
├── actions/                 # Action Register, My Action Items & Dependencies
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
│
├── notifications/           # In-App & SMTP Email Dispatcher
│   ├── models.py
│   ├── email_service.py
│   ├── services.py
│   └── views.py
│
├── templates/               # Responsive HTML5 Company Portal Interface
├── static/                  # Vanilla CSS Design System & JS Client Modules
├── media/                   # Uploaded Media & Transcripts
├── tests/                   # 20 Automated Integration & Unit Test Cases
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📊 2. DATABASE ER DIAGRAM

```mermaid
erDiagram
    User ||--o{ Availability : "configures weekly"
    User ||--o{ Meeting : "organizes"
    User ||--o{ MeetingParticipant : "participates"
    User ||--o{ ActionItem : "assigned"
    User ||--o{ Notification : "receives"
    
    Meeting ||--o{ MeetingParticipant : "has"
    Meeting ||--o{ MeetingTranscript : "contains"
    Meeting ||--o{ Decision : "yields"
    Meeting ||--o{ ActionItem : "generates"
    Meeting ||--o{ UnresolvedQuestion : "tracks"
    Meeting ||--o{ Dependency : "identifies"

    User {
        int id PK
        string firebase_uid
        string email
        string employee_id
        string department
        string job_role
        string status
        time work_start_time
        time work_end_time
    }

    Meeting {
        int id PK
        string title
        string meeting_type
        date date
        time start_time
        time end_time
        string status
    }

    MeetingParticipant {
        int id PK
        string response_status
        string response_note
    }

    ActionItem {
        int id PK
        string task
        string owner_name
        string deadline
        string priority
        string evidence
        string status
    }

    Decision {
        int id PK
        string decision
        string evidence
        float confidence
    }
```

---

## 🚀 3. LOCAL SETUP & INSTALLATION

### Step 1: Python Installation
Ensure **Python 3.11+** is installed on your system.

```bash
python --version
```

### Step 2: Create & Activate Virtual Environment
```bash
python -m venv venv

# On Windows:
.\venv\Scripts\activate

# On Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Variables Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Fill in your configuration:
```env
SECRET_KEY=django-insecure-prod-key-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*

# Database (Leave blank for SQLite local dev, or provide PostgreSQL URL)
DATABASE_URL=postgres://meeting_user:meeting_pass@localhost:5432/meeting_portal_db

# Firebase Authentication Credentials
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_CLIENT_EMAIL=your-firebase-client-email@appspot.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----"

# Generative AI Config (Gemini API or OpenAI)
LLM_PROVIDER=gemini
LLM_API_KEY=your-gemini-or-openai-api-key
GEMINI_MODEL=gemini-2.5-flash

# Email Settings (SMTP)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=notifications@company.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 5: Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Run Local Server
```bash
python manage.py runserver
```

Open your browser at: `http://127.0.0.1:8000/`

---

## 🔐 4. FIREBASE & AUTHENTICATION CONFIGURATION

### Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com/).
2. Create a project `meeting-portal`.
3. Under **Build -> Authentication**, enable **Google** and **Apple** sign-in providers.
4. Navigate to **Project Settings -> Service accounts**.
5. Click **Generate new private key** and download the JSON file.
6. Copy `project_id`, `client_email`, and `private_key` into your `.env` file.

### Demo Persona Switcher (Local Testing)
For instant evaluation without Firebase keys, use the bottom buttons on the `/login/` screen:
- 👨‍💼 **Rahul** (Manager)
- 👩‍💻 **Priya** (QA Lead)
- 👨‍💼 **Anil** (Client Lead)
- 👩‍🔬 **Sneha** (Dev)

---

## 🤖 5. GENERATIVE AI TRANSCRIPT EXTRACTOR CONFIGURATION

The AI engine extracts structured decisions, actions, deadlines, owners, unresolved questions, dependencies, and grounded transcript evidence using fixed JSON schemas.

### Setting Up Gemini API Key
1. Obtain an API Key from [Google AI Studio](https://aistudio.google.com/).
2. Set `LLM_PROVIDER=gemini` and `LLM_API_KEY=your_key` in `.env`.

*Note: If no API key is set or during offline testing, the system automatically uses an intelligent heuristic rule-based fallback extractor so the application remains fully functional.*

---

## 🧪 6. RUNNING AUTOMATED TESTS

The application includes 20 comprehensive automated unit and integration test cases covering login, unauthorized protection, meeting creation, availability checking, alternative slot suggestions, email dispatching, transcript parsing, AI extraction, evidence grounding, and action status updates.

Run tests using:
```bash
python manage.py test tests
```

---

## ☁️ 7. AWS EC2 PRODUCTION DEPLOYMENT GUIDE

### Prerequisites
- AWS EC2 instance (Ubuntu 22.04 LTS, t3.small or higher)
- Domain name pointing to EC2 Elastic IP
- Security Group rules allowing ports `22` (SSH), `80` (HTTP), `443` (HTTPS)

### Step 1: EC2 Server Initialization
SSH into your instance:
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

Update packages and install dependencies:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx -y
```

### Step 2: Configure PostgreSQL Database
```bash
sudo -u postgres psql
```
Inside SQL shell:
```sql
CREATE DATABASE meeting_portal_db;
CREATE USER meeting_user WITH PASSWORD 'secure_production_password';
ALTER ROLE meeting_user SET client_encoding TO 'utf8';
ALTER ROLE meeting_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE meeting_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE meeting_portal_db TO meeting_user;
\q
```

### Step 3: Clone Code & Configure Python Environment
```bash
cd /var/www
sudo git clone <your-repository-url> schedule
sudo chown -R ubuntu:ubuntu /var/www/schedule
cd /var/www/schedule

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

Create production `.env`:
```bash
nano .env
```
Fill production secrets:
```env
SECRET_KEY=super-secret-random-production-key-998877
DEBUG=False
ALLOWED_HOSTS=YOUR_DOMAIN.com,YOUR_EC2_PUBLIC_IP
DATABASE_URL=postgres://meeting_user:secure_production_password@localhost:5432/meeting_portal_db
LLM_PROVIDER=gemini
LLM_API_KEY=your_production_gemini_key
```

Run migrations & collect static files:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 4: Configure Gunicorn Systemd Service
Create `/etc/systemd/system/gunicorn.service`:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Paste:
```ini
[Unit]
Description=gunicorn daemon for AI Meeting Portal
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/schedule
ExecStart=/var/www/schedule/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/schedule/gunicorn.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start Gunicorn:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### Step 5: Configure Nginx Reverse Proxy
Create `/etc/nginx/sites-available/meeting_portal`:
```bash
sudo nano /etc/nginx/sites-available/meeting_portal
```

Paste:
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN.com YOUR_EC2_PUBLIC_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/schedule;
    }

    location /media/ {
        root /var/www/schedule;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/schedule/gunicorn.sock;
    }
}
```

Enable site & restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/meeting_portal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: HTTPS SSL Setup with Certbot
```bash
sudo certbot --nginx -d YOUR_DOMAIN.com
```

Your production AI Meeting Decision & Action Extractor portal is now live with **HTTPS SSL**!
