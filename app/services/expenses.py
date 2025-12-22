from datetime import date
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from loguru import logger
from app.db import get_session, SessionLocal
from app.models import Account, Category, InitialBalance, ActualBalance, TransactionRecord

# ────────────────────────────────
# Category CRUD
# ────────────────────────────────
def list_categories() -> list[dict]:
    with SessionLocal() as session:
        categories = session.query(Category).order_by(Category.category_name).all()
        return [{"id": c.category_id, "name": c.category_name, "type": c.category_type} for c in categories]

def add_category(name: str, category_type: str) -> None:
    with SessionLocal() as session:
        if not session.query(Category).filter_by(category_name=name).first():
            session.add(Category(category_name=name, category_type=category_type))
            session.commit()

def update_category(category_id: int, new_name: str | None = None, new_type: str | None = None) -> bool:
    with SessionLocal() as session:
        cat = session.get(Category, category_id)
        if not cat:
            return False
        if new_name:
            cat.category_name = new_name
        if new_type:
            cat.category_type = new_type
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
def list_accounts():
    with get_session() as session:
        accounts = session.query(Account).order_by(Account.account_name).all()
        return [{"id": a.account_id, "name": a.account_name} for a in accounts]

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
# Initial Balance
# ────────────────────────────────
def ensure_initial_balance(account_id: int, balance: float) -> None:
    with SessionLocal() as session:
        ib = session.query(InitialBalance).filter_by(account_id=account_id).first()
        if not ib:
            session.add(InitialBalance(account_id=account_id, balance=balance))
        else:
            ib.balance = balance
        session.commit()

def get_initial_balance(account_id: int) -> float | None:
    with SessionLocal() as session:
        ib = session.query(InitialBalance).filter_by(account_id=account_id).first()
        if not ib:
            ib = InitialBalance(account_id=account_id, balance=0.00)
            session.add(ib)
            session.commit()
        return float(ib.balance)

def update_initial_balance(account_id: int, new_balance: float) -> bool:
    with SessionLocal() as session:
        ib = session.query(InitialBalance).filter_by(account_id=account_id).first()
        if not ib:
            return False
        ib.balance = new_balance
        session.commit()
        return True

# ────────────────────────────────
# Actual Balance
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

def update_actual_balance(balance_id: int, new_date: str | None = None, new_amount: float | None = None) -> bool:
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
# Transaction Record
# ────────────────────────────────
def add_transaction(txn: dict) -> bool:
    session = get_session()
    try:
        # Optional safety: ensure selected category exists and matches type (if provided)
        cat = session.get(Category, txn["category_id"])
        if not cat:
            raise ValueError("Selected category does not exist.")
        # If UI passed category_type for validation, ensure consistency
        if "category_type" in txn and txn["category_type"] and txn["category_type"] != cat.category_type:
            raise ValueError("Selected category type does not match the category.")

        new_txn = TransactionRecord(
            account_id=txn["account_id"],
            category_id=txn["category_id"],
            transaction_date=txn["transaction_date"],
            amount=txn["amount"],
            remark=txn.get("remark"),
        )
        session.add(new_txn)
        session.commit()
        logger.info(f"Transaction added: {txn}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"DB insert failed: {e}")
        return False
    finally:
        session.close()

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

def query_transactions(start_date=None, end_date=None, category=None):
    with SessionLocal() as session:
        q = session.query(TransactionRecord).options(joinedload(TransactionRecord.category_rel))

        if start_date:
            q = q.filter(TransactionRecord.transaction_date >= start_date)
        if end_date:
            q = q.filter(TransactionRecord.transaction_date <= end_date)
        if category and category != "All":
            q = q.join(Category).filter(Category.category_name == category)

        rows = q.order_by(TransactionRecord.transaction_date.desc(),
                          TransactionRecord.id.desc()).all()

        return [
            {
                "id": r.id,
                "date": r.transaction_date.isoformat(),
                "amount": float(r.amount),
                "category": r.category_rel.category_name if r.category_rel else "Unknown",
                "type": r.category_rel.category_type if r.category_rel else "Unknown",
                "note": r.remark or ""
            }
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
        q = session.query(
                Category.category_name,
                Category.category_type,
                func.sum(TransactionRecord.amount).label("total")
            ).join(TransactionRecord, TransactionRecord.category_id == Category.category_id)
        if start_date:
            q = q.filter(TransactionRecord.transaction_date >= date.fromisoformat(start_date))
        if end_date:
            q = q.filter(TransactionRecord.transaction_date <= date.fromisoformat(end_date))
        rows = q.group_by(Category.category_name, Category.category_type) \
                .order_by(func.sum(TransactionRecord.amount).desc()).all()
        return [{"category": r[0], "type": r[1], "total": float(r[2])} for r in rows]