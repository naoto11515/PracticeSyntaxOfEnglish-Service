# PracticeSyntaxOfEnglish-Service

practice Syntax of English Service to improve your English skill.
you can use the service once setting following.
1. register an English syntax you want to memolize to table [M_Syntax].
2. access this URL and let's try to use!

## Requirements

* Python 3.13 or later
* Git

## Clone

```bash
git clone <repository-url>
cd PracticeSyntaxOfEnglish-Service
```

## Create Virtual Environment

```bash
python -m venv .venv
```

## Activate Virtual Environment

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
.venv\Scripts\activate.bat
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Application

```bash
python -m uvicorn main:app --reload
```

## Access Application

Open the following URL in your browser:

```
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically generates API documentation.

Swagger UI:

```
http://127.0.0.1:8000/docs
```

ReDoc:

```
http://127.0.0.1:8000/redoc
```

## Project Structure

```text
PracticeSyntaxOfEnglish-Service/
├─ main.py
├─ requirements.txt
├─ README.md
├─ .gitignore
├─ templates/
├─ static/
└─ data/
```
