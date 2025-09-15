# Software Summit – Django Project

This is a Django-based web application that powers the **Software Summit** platform.  
It includes features like PDF generation using **WeasyPrint**, which requires some additional system setup.

---

## Prerequisites

Linux servers (Ubuntu/Debian-based) will need these installed before Python dependencies:

```bash
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-venv python3-dev \
    build-essential \
    libffi-dev \
    libcairo2 libcairo2-dev \
    libpango1.0-0 libpango1.0-dev \
    libjpeg-dev libpng-dev libopenjp2-7-dev \
    shared-mime-info \
    fonts-dejavu-core fonts-liberation


1. Clone the repository
git clone https://github.com/edanodongo/software-summit.git
cd software-summit

2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

3. Install dependencies
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt


requirements.txt includes Django, WeasyPrint, and all required project packages.

4. Configure environment variables

Create a .env file (or export variables) with values:

# SECURITY
DEBUG=True

# DATABASE CONFIGURATION
DB_DEFAULT_NAME=summit
DB_DEFAULT_USER=summitadmin
DB_DEFAULT_PASSWORD=database-password
DB_DEFAULT_HOST=localhost
DB_DEFAULT_PORT=5432
DATABASE_URL=postgres://user:password@localhost:5432/dbname

# ALLOWED HOSTS
ALLOWED_HOSTS = ['localhost', '127.0.0.1','domain.com']



5. Database setup
python manage.py migrate

6. Collect static files
python manage.py collectstatic

7. Test locally
python manage.py runserver 0.0.0.0:8000

Production Deployment

Gunicorn + Nginx setup.

Run with Gunicorn
gunicorn software_summit.wsgi:application --bind 0.0.0.0:8000


For long-running processes, use systemd or supervisor to keep Gunicorn alive.

Configure Nginx (reverse proxy)

Example /etc/nginx/sites-available/software-summit:

server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/software-summit/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}


Enable it:

sudo ln -s /etc/nginx/sites-available/software-summit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

WeasyPrint Notes

Verify installation with:

weasyprint --info


If fonts don’t render correctly in PDFs, install additional fonts:

sudo apt install fonts-noto fonts-freefont-ttf

Troubleshooting

WeasyPrint ImportError → Missing system libs (check libpango, libcairo, libjpeg).

500 errors in Gunicorn → Check logs: journalctl -u gunicorn.

Static files not loading → Ensure collectstatic was run and Nginx alias points to the correct path.

License



---



