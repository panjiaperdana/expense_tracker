import os
import sys
from pathlib import Path

# --- Ensure imports like `from app.services...` work even if launched directly ---
ROOT = Path(__file__).resolve().parents[1]  # D:\Project\expense_tracker
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from loguru import logger
from datetime import date
from kivymd.uix.pickers import MDDatePicker
from kivy.clock import Clock

from app.services.expenses import (
    add_transaction, query_transactions, list_categories,
    summary_by_month, summary_by_category, delete_transaction, update_transaction
)
from app.widgets.dialogs import EditExpensePopup


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        raw_categories = list_categories()
        self.categories = [c["name"] for c in raw_categories]   # spinner values
        self.category_map = {c["name"]: c["id"] for c in raw_categories}  # name → real DB id

        Clock.schedule_once(self._populate_spinners, 0)
        self.refresh_table()
        logger.info(f"Category map: {self.category_map}")


    def _populate_spinners(self, *args):
        self.ids.category_spinner.values = self.categories
        self.ids.filter_category.values = ["All"] + self.categories
        if self.categories:
            self.ids.category_spinner.text = self.categories[0]  # default selection
        # Debug
        logger.info(f"Categories loaded: {self.categories}")

    @property
    def categories(self):
        return getattr(self, "_categories", [])

    @categories.setter
    def categories(self, value):
        self._categories = value

    def _get_filter_values(self):
        sd = self.ids.start_date.text.strip() or None
        ed = self.ids.end_date.text.strip() or None
        cat = self.ids.filter_category.text
        cat = None if cat == "All" else cat
        return sd, ed, cat

    def refresh_table(self):
        sd, ed, cat = self._get_filter_values()
        rows = query_transactions(sd, ed, cat)

        rv_data = []
        for r in rows:
            rv_data.append({
                "exp_id": str(r["id"]),
                "date": r["date"],
                "category": r.get("category") or r.get("category_name", "Unknown"),
                "amount": f"{r['amount']:.2f}",
                "note": r.get("note", "")
            })
        self.ids.rv.data = rv_data

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

    def on_add_transaction(self):
        d = self.ids.date_input.text.strip() or date.today().isoformat()
        amt_text = self.ids.amount_input.text.strip()
        cat = self.ids.category_spinner.text
        note = self.ids.note_input.text.strip()

        try:
            if cat not in self.category_map:
                raise ValueError(f"Invalid category: {cat}")
            amt = float(amt_text)
            cat_id = self.category_map[cat]
            type_id = 2  # expense

            txn = {
                "account_id": 1,
                "category_id": cat_id,
                "type_id": type_id,
                "transaction_date": d,
                "amount": amt,
                "remark": note,
            }

            logger.info(f"Adding transaction: {txn}")
            add_transaction(txn)

            self.ids.amount_input.text = ""
            self.ids.note_input.text = ""
            self.refresh_table()
        except Exception as e:
            logger.error(f"Add failed: {e}")

    def on_delete(self, rid: int):
        try:
            if delete_transaction(int(rid)):
                logger.info(f"Deleted transaction {rid}")
                self.refresh_table()
        except Exception as e:
            logger.error(f"Delete failed: {e}")

    def open_edit_dialog(self, rid: int):
        rows = query_transactions()
        record = next((r for r in rows if str(r["id"]) == str(rid)), None)
        if not record:
            return

        def on_save(updated):
            update_transaction(
                updated["id"], updated["date"], updated["amount"],
                updated["category"], updated["note"]
            )
            logger.info(f"Updated transaction {updated['id']}")
            self.refresh_table()

        popup = EditExpensePopup(record, self.categories, on_save)
        popup.open()

    def show_monthly_summary(self):
        data = summary_by_month()
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        summary_text = "\n".join([f"{d['month']}: {d['total']:.2f}" for d in data])
        Popup(title="Monthly Summary", content=Label(text=summary_text),
              size_hint=(0.6, 0.6)).open()

    def show_category_summary(self):
        sd, ed, _ = self._get_filter_values()
        data = summary_by_category(sd, ed)
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        summary_text = "\n".join([f"{d.get('category') or d.get('category_name')}: {d['total']:.2f}" for d in data])
        Popup(title="Category Summary", content=Label(text=summary_text),
              size_hint=(0.6, 0.6)).open()


class ExpenseTrackerApp(MDApp):
    def restart(self, *args):
        """Restart the app using module form to preserve package imports."""
        os.execl(sys.executable, sys.executable, "-m", "app.main")

    def build(self):
        Builder.load_file("app/ui.kv")
        return MainScreen()


if __name__ == "__main__":
    ExpenseTrackerApp().run()