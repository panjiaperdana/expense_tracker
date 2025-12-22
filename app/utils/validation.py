from datetime import datetime, date

def validate_date(d: str) -> str:
    if not d:
        return date.today().isoformat()
    try:
        parsed = datetime.strptime(d, "%Y-%m-%d").date()
        if parsed > date.today():
            raise ValueError("Transaction date cannot be in the future.")
        return parsed.isoformat()
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

def validate_amount(amt_text: str) -> float:
    # Guard empty input explicitly for clearer error message
    if amt_text is None or amt_text.strip() == "":
        raise ValueError("Amount cannot be empty.")
    try:
        amt = float(amt_text)
        if amt < 0:
            raise ValueError("Transaction amount must be greater than 0.")
        return amt
    except ValueError:
        raise ValueError("Amount must be a number.")

def validate_category(cat: str, category_map: dict) -> int:
    # Guard placeholder/default text
    if not cat or cat == "Category":
        raise ValueError("Please select a valid category.")
    if cat not in category_map:
        raise ValueError(f"Invalid category {cat}.")
    return category_map[cat]

def validate_category_type(cat_type: str, valid_types: list[str]) -> str:
    # UI passes "Debit"/"Credit" reflected from selected category
    if not cat_type:
        raise ValueError("Category type is missing.")
    if cat_type not in valid_types:
        raise ValueError(f"Invalid category type {cat_type}. Must be one of {valid_types}.")
    return cat_type

def validate_note(note: str) -> str:
    if note is None:
        return ""
    if len(note) > 200:
        raise ValueError("Transaction note must be less than 200 characters.")
    return note

def validate_account(account: str, account_map: dict) -> int:
    # Guard placeholder/default text
    if not account or account == "Account":
        raise ValueError("Please select a valid account.")
    if account not in account_map:
        raise ValueError(f"Invalid account {account}")
    return account_map[account]