# E-Center Research Collector (Django)

An authenticated Django website for collecting anonymized EBQS-linked transaction events and producing delayed/on-time labels for later machine-learning research.

## Setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and sign in. Before field use, replace the sample categories in `collector/forms.py`, validate category thresholds with E-Center staff, change `SECRET_KEY`, disable `DEBUG`, and configure production hosts.

Never store names, SSS numbers, contact details, or other direct identifiers in this research collector.
