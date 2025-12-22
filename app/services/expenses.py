from datetime import date
from sqlalchemy import func, select
from app.db import SessionLocal
from app.models import (
    Account, Category, TransactionType, InitialBalance, ActualBalance, TransactionRecord
)

# ────────────────────────────────
# Category CRUD
# ────────────────────────────────
def list_categories() -> list[str]:
    with SessionLocal() as session:
        return [c.category_name for c in session.query(Category).order_by(Category.category_name).all()]

def add_category(name: str) -> None:
    with SessionLocal() as session:
        if not session.query(Category).filter_by(category_name=name).first():
            session.add(Category(category_name=name))
            session.commit()

def update_category(category_id: int, new_name: str) -> bool:
    with SessionLocal() as session:
        cat = session.get(Category, category_id)
        if not cat:
            return False
        cat.category_name = new_name
        session.commit()
        return True

def delete_category(category_id: int) -> bool:
    with SessionLocal() as session:
        cat = session.get(Category, category_id)
        if not cat:
            return False
        session.delete(cat)
        session.commit()
        return True

# ────────────────────────────────
# Account CRUD
# ────────────────────────────────
def list_accounts() -> list[str]:
    with SessionLocal() as session:
        return [a.account_name for a in session.query(Account).order_by(Account.account_name).all()]

def add_account(name: str) -> None:
    with SessionLocal() as session:
        if not session.query(Account).filter_by(account_name=name).first():
            session.add(Account(account_name=name))
            session.commit()

def update_account(account_id: int, new_name: str) -> bool:
    with SessionLocal() as session:
        acc = session.get(Account, account_id)
        if not acc:
            return False
        acc.account_name = new_name
        session.commit()
        return True

def delete_account(account_id: int) -> bool:
    with SessionLocal() as session:
        acc = session.get(Account, account_id)
        if not acc:
            return False
        session.delete(acc)
        session.commit()
        return True

# ────────────────────────────────
# Transaction Type R, default value provided
# ────────────────────────────────
def list_transaction_types() -> list[str]:
    with SessionLocal() as session:
        return [t.type_name for t in session.query(TransactionType).order_by(TransactionType.type_name).all()]

# ────────────────────────────────
# Initial Balance CRU
# ────────────────────────────────
def ensure_initial_balance(account_id: int, balance: float) -> None:
    with SessionLocal() as session:
        any_row = session.query(InitialBalance).first()
        if not any_row:
            session.add(InitialBalance(account_id=account_id, balance=balance))
        else:
            ib = session.query(InitialBalance).filter_by(account_id=account_id).first()
            if ib:
                ib.balance = balance
        session.commit()

def get_initial_balance(account_id: int) -> float | None:
    with SessionLocal() as session:
        if not session.query(InitialBalance).first():
            ib = InitialBalance(account_id=account_id, balance=0.00)
            session.add(ib)
            session.commit()
            return float(ib.balance)
        ib = session.query(InitialBalance).filter_by(account_id=account_id).first()
        return float(ib.balance) if ib else None

def update_initial_balance(account_id: int, new_balance: float) -> bool:
    with SessionLocal() as session:
        ib = session.query(InitialBalance).filter_by(account_id=account_id).first()
        if not ib:
            return False
        ib.balance = new_balance
        session.commit()
        return True

# ────────────────────────────────
# Actual Balance CRUD
# ────────────────────────────────
def add_actual_balance(account_id: int, transaction_date: str, amount: float) -> None:
    with SessionLocal() as session:
        ab = ActualBalance(
            account_id=account_id,
            transaction_date=date.fromisoformat(transaction_date),
            amount=amount
        )
        session.add(ab)
        session.commit()

def get_actual_balance(account_id: int) -> list[dict]:
    with SessionLocal() as session:
        rows = session.query(ActualBalance).filter_by(account_id=account_id).all()
        return [{"date": r.transaction_date.isoformat(), "amount": float(r.amount)} for r in rows]

def update_actual_balance(balance_id: int, new_date: str | None = None, new_amount:float | None = None) -> bool:
    with SessionLocal() as session:
        ab = session.get(ActualBalance, balance_id)
        if not ab:
            return False
        if new_date:
            ab.transaction_date = date.fromisoformat(new_date)
        if new_amount is not None:
            ab.amount = new_amount
        session.commit()
        return True

def delete_actual_balance(balance_id: int) -> bool:
    with SessionLocal() as session:
        ab = session.get(ActualBalance, balance_id)
        if not ab:
            return False
        session.delete(ab)
        session.commit()
        return True

# ────────────────────────────────
# Transaction Record CRUD
# ────────────────────────────────
def add_transaction(account_id: int, category_id: int, type_id: int,
                    transaction_date: str, amount: float, remark: str = "") -> int:
    with SessionLocal() as session:
        tr = TransactionRecord(
            account_id=account_id,
            category_id=category_id,
            type_id=type_id,
            transaction_date=date.fromisoformat(transaction_date),
            amount=amount,
            remark=remark
        )
        session.add(tr)
        session.commit()
        return tr.id

def update_transaction(transaction_id: int, **kwargs) -> bool:
    with SessionLocal() as session:
        tr = session.get(TransactionRecord, transaction_id)
        if not tr:
            return False
        for key, value in kwargs.items():
            setattr(tr, key, value)
        session.commit()
        return True

def delete_transaction(transaction_id: int) -> bool:
    with SessionLocal() as session:
        tr = session.get(TransactionRecord, transaction_id)
        if not tr:
            return False
        session.delete(tr)
        session.commit()
        return True

def query_transactions(start_date: str | None = None,
                       end_date: str | None = None,
                       category_id: int | None = None) -> list[dict]:
    with SessionLocal() as session:
        q = session.query(TransactionRecord)
        if start_date:
            q = q.filter(TransactionRecord.transaction_date >= date.fromisoformat(start_date))
        if end_date:
            q = q.filter(TransactionRecord.transaction_date <= date.fromisoformat(end_date))
        if category_id:
            q = q.filter(TransactionRecord.category_id == category_id)
        rows = q.order_by(TransactionRecord.transaction_date.desc(), TransactionRecord.id.desc()).all()
        return [
            {"id": r.id, "date": r.transaction_date.isoformat(),
             "amount": float(r.amount), "remark": r.remark or ""}
            for r in rows
        ]

# ────────────────────────────────
# UTILITY Functions
# ────────────────────────────────
def summary_by_month() -> list[dict]:
    with SessionLocal() as session:
        stmt = select(
            func.to_char(TransactionRecord.transaction_date, 'YYYY-MM').label("month"),
            func.sum(TransactionRecord.amount).label("total")
        ).group_by("month").order_by("month DESC")
        rows = session.execute(stmt).all()
        return [{"month": r[0], "total": float(r[1])} for r in rows]

def summary_by_category(start_date: str | None = None, end_date: str | None = None) -> list[dict]:
    with SessionLocal() as session:
        q = session.query(Category.category_name, func.sum(TransactionRecord.amount).label("total")) \
                   .join(TransactionRecord, TransactionRecord.category_id == Category.category_id)
        if start_date:
            q = q.filter(TransactionRecord.transaction_date >= date.fromisoformat(start_date))
        if end_date:
            q = q.filter(TransactionRecord.transaction_date <= date.fromisoformat(end_date))
        rows = q.group_by(Category.category_name).order_by(func.sum(TransactionRecord.amount).desc()).all()
        return [{"category": r[0], "total": float(r[1])} for r in rows]