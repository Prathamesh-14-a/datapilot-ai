# Contributing to DataPilot AI

Thank you for your interest in contributing to DataPilot AI.

At the moment, this project is maintained by the repository owner.

## Reporting Issues

If you find a bug or have a feature request, please open a GitHub Issue with:

- A clear title
- Description
- Steps to reproduce
- Expected behavior
- Screenshots (if applicable)

---

## Development Setup

Clone the repository

```bash
git clone https://github.com/Prathamesh-14-a/datapilot-ai.git
```

Go into the project

```bash
cd datapilot-ai
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create your environment variables

```bash
cp .env.example .env
```

Configure your:

- PostgreSQL Database
- Gemini API Key
- SMTP Credentials

Run the application

```bash
streamlit run app.py
```

---

## Branch Naming

Use descriptive branch names.

Examples

```
feature/ats-improvements
feature/portfolio-analyzer
bugfix/login-error
docs/readme-update
```

---

## Commit Messages

Examples

```
feat: add AI interview module

fix: resolve sidebar mobile issue

docs: update README

refactor: optimize resume parser
```

---

## Pull Requests

Before submitting a PR:

- Ensure the project builds successfully.
- Keep commits clean and meaningful.
- Update documentation when necessary.
- Test your changes.

---

## Code Style

- Follow PEP 8
- Use meaningful variable names
- Keep functions modular
- Write reusable code

---

Thank you for helping improve DataPilot AI.