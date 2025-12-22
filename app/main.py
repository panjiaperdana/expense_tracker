# app/main.py
from datetime import date

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivymd.uix.pickers import MDDatePicker
from loguru import logger

from app.services.expenses import (
    add_transaction,
    query_transactions,
    list_categories,
    delete_transaction,
    list_accounts,
)
from app.utils.validation import (
    validate_date,
    validate_amount,
    validate_category,
    validate_category_type,
    validate_note,
    validate_account,
)


class MainScreen(BoxLayout):
    categories = ListProperty([])
    accounts = ListProperty([])
    types = ListProperty([])  # UI-only: unique ["Debit","Credit"]
    category_map: dict[str, int] = {}
    account_map: dict[str, int] = {}
    type_map: dict[str, str] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Defer data loading until on_start to avoid KV id access before build
        Clock.schedule_once(self._safe_init, 0)

    def _safe_init(self, *_):
        try:
            self._load_data()
            self._populate_spinners()
            self.refresh_table()
        except Exception as e:
            logger.exception(f"UI initialization failed: {e}")
            if hasattr(self.ids, "error_label"):
                self.ids.error_label.text = f"Init failed: {e}"

    def _load_data(self):
        # Categories
        raw_categories = list_categories()
        self.categories = [c["name"] for c in raw_categories]
        self.category_map = {c["name"]: c["id"] for c in raw_categories}
        self.type_map = {c["name"]: c["type"] for c in raw_categories}
        self.types = sorted(set(self.type_map.values()))  # ["Debit","Credit"]

        # Accounts
        raw_accounts = list_accounts()
        self.accounts = [a["name"] for a in raw_accounts]
        self.account_map = {a["name"]: a["id"] for a in raw_accounts}

    def _populate_spinners(self):
        # Guard IDs to avoid None access if KV failed or changed
        if "category_spinner" in self.ids:
            self.ids.category_spinner.values = self.categories
            self.ids.category_spinner.text = ""  # force selection
        if "filter_category" in self.ids:
            self.ids.filter_category.values = ["All"] + self.categories
            self.ids.filter_category.text = "All"
        if "account_spinner" in self.ids:
            self.ids.account_spinner.values = self.accounts
            self.ids.account_spinner.text = ""  # force selection
        if "type_spinner" in self.ids:
            self.ids.type_spinner.text = "Type"  # disabled in KV; auto-filled

    def _get_filter_values(self):
        sd = self.ids.start_date.text.strip() or None if "start_date" in self.ids else None
        ed = self.ids.end_date.text.strip() or None if "end_date" in self.ids else None
        cat = self.ids.filter_category.text if "filter_category" in self.ids else None
        cat = None if cat == "All" else cat
        return sd, ed, cat

    def refresh_table(self):
        try:
            sd, ed, cat = self._get_filter_values()
            rows = query_transactions(sd, ed, cat)

            rv_data = [{
                "exp_id": str(r["id"]),
                "date": r["date"],
                "category": r.get("category", "Unknown"),
                "amount": f"{r['amount']:.2f}",
                "note": r.get("note", "")
            } for r in rows]

            if "rv" in self.ids:
                self.ids.rv.data = rv_data
        except Exception as e:
            logger.exception(f"Refresh table failed: {e}")
            if hasattr(self.ids, "error_label"):
                self.ids.error_label.text = f"Load failed: {e}"

    def open_date_picker(self):
        picker = MDDatePicker(
            year=date.today().year,
            month=date.today().month,
            day=date.today().day
        )
        picker.bind(on_save=self._on_date_selected)
        picker.open()

    def _on_date_selected(self, instance, value, date_range):
        self.ids.date_input.text = value.isoformat()

    def update_type_spinner(self, category_name: str):
        # called from KV when category changes
        if "type_spinner" in self.ids:
            self.ids.type_spinner.text = self.type_map.get(category_name, "Type")

    def on_add_transaction(self):
        d = self.ids.date_input.text.strip()
        if not d:
            d = date.today().isoformat()
        d = validate_date(d)
        amt_text = self.ids.amount_input.text.strip() if "amount_input" in self.ids else ""
        cat = self.ids.category_spinner.text if "category_spinner" in self.ids else ""
        note = self.ids.note_input.text.strip() if "note_input" in self.ids else ""
        account = self.ids.account_spinner.text if "account_spinner" in self.ids else ""
        txn_type = self.ids.type_spinner.text if "type_spinner" in self.ids else ""

        try:
            d = validate_date(d)
            amt = validate_amount(amt_text)
            cat_id = validate_category(cat, self.category_map)
            note = validate_note(note)
            account_id = validate_account(account, self.account_map)
            txn_type = validate_category_type(txn_type, ["Debit", "Credit"])

            txn = {
                "account_id": account_id,
                "category_id": cat_id,
                "transaction_date": d,
                "amount": amt,
                "remark": note,
                "category_type": txn_type,  # server-side consistency check
            }

            logger.info(f"Adding transaction: {txn}")
            ok = add_transaction(txn)
            if not ok:
                raise ValueError("Insert failed. See logs.")

            # Refresh datasets and table
            self.refresh_categories()
            self.refresh_accounts()
            self.refresh_table()

            # Reset inputs and errors
            if "amount_input" in self.ids:
                self.ids.amount_input.text = ""
            if "note_input" in self.ids:
                self.ids.note_input.text = ""
            if "error_label" in self.ids:
                self.ids.error_label.text = ""

        except ValueError as ve:
            if "error_label" in self.ids:
                self.ids.error_label.text = str(ve)
            logger.error(f"Validation error: {ve}")
        except Exception as e:
            if "error_label" in self.ids:
                self.ids.error_label.text = "Unexpected error. See logs."
            logger.exception(f"Add failed: {e}")

    def on_delete(self, rid: int):
        try:
            if delete_transaction(int(rid)):
                logger.info(f"Deleted transaction {rid}")
                self.refresh_table()
        except Exception as e:
            logger.exception(f"Delete failed: {e}")
            if "error_label" in self.ids:
                self.ids.error_label.text = f"Delete failed: {e}"

    def refresh_categories(self):
        try:
            raw_categories = list_categories()
            self.categories = [c["name"] for c in raw_categories]
            self.category_map = {c["name"]: c["id"] for c in raw_categories}
            self.type_map = {c["name"]: c["type"] for c in raw_categories}
            if "category_spinner" in self.ids:
                self.ids.category_spinner.values = self.categories
            if "filter_category" in self.ids:
                self.ids.filter_category.values = ["All"] + self.categories
            if "type_spinner" in self.ids:
                self.ids.type_spinner.text = "Type"
        except Exception as e:
            logger.exception(f"Refresh categories failed: {e}")

    def refresh_accounts(self):
        try:
            raw_accounts = list_accounts()
            self.accounts = [a["name"] for a in raw_accounts]
            self.account_map = {a["name"]: a["id"] for a in raw_accounts}
            if "account_spinner" in self.ids:
                self.ids.account_spinner.values = self.accounts
        except Exception as e:
            logger.exception(f"Refresh accounts failed: {e}")


class ExpenseTrackerApp(MDApp):
    def build(self):
        try:
            Builder.load_file("app/ui.kv")
        except Exception as e:
            # Fail fast and visible if KV cannot load
            logger.exception(f"KV load failed: {e}")
            # Minimal fallback UI to show the error
            from kivy.uix.label import Label
            return Label(text=f"KV load failed: {e}")
        return MainScreen()

    def on_start(self):
        logger.info("ExpenseTrackerApp started")


if __name__ == "__main__":
    ExpenseTrackerApp().run()