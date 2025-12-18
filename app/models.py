from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, Date, Numeric, ForeignKey
from decimal import Decimal
import datetime

Base = declarative_base()

# ────────────────────────────────
# Account Table
# ────────────────────────────────
class Account(Base):
    __tablename__ = "account"

    account_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    initial_balances = relationship("InitialBalance", back_populates="account_rel")
    actual_balances = relationship("ActualBalance", back_populates="account_rel")
    transactions = relationship("TransactionRecord", back_populates="account_rel")


# ────────────────────────────────
# Category Table
# ────────────────────────────────
class Category(Base):
    __tablename__ = "category"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    transactions = relationship("TransactionRecord", back_populates="category_rel")


# ────────────────────────────────
# Transaction Type Table
# ────────────────────────────────
class TransactionType(Base):
    __tablename__ = "transaction_type"

    type_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    transactions = relationship("TransactionRecord", back_populates="type_rel")


# ────────────────────────────────
# Initial Balance Table
# ────────────────────────────────
class InitialBalance(Base):
    __tablename__ = "initial_balance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    account_rel = relationship("Account", back_populates="initial_balances")


# ────────────────────────────────
# Actual Balance Table
# ────────────────────────────────
class ActualBalance(Base):
    __tablename__ = "actual_balance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"), nullable=False)
    transaction_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    account_rel = relationship("Account", back_populates="actual_balances")


# ────────────────────────────────
# Transaction Record Table
# ────────────────────────────────
class TransactionRecord(Base):
    __tablename__ = "transaction_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.category_id"), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("transaction_type.type_id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    remark: Mapped[str | None] = mapped_column(String, nullable=True)

    account_rel = relationship("Account", back_populates="transactions")
    category_rel = relationship("Category", back_populates="transactions")
    type_rel = relationship("TransactionType", back_populates="transactions")