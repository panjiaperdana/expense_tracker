# Expense Tracker Desktop App

A Windows desktop expense tracker built with Python, Kivy, SQLAlchemy, and PostgreSQL.

## Features
- Add, edit, delete expenses
- Category management and filtering
- Monthly and category summaries
- Export to CSV and Excel
- Basic chart generation

## Setup
1. Ensure PostgreSQL database `expense_tracker` exists with tables `categories` and `expenses`.
2. Update `DATABASE_URL` in `app/config.py`.
3. Install dependencies: