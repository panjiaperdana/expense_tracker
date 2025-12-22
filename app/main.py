from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from loguru import logger
from datetime import date
from kivymd.uix.pickers import MDDatePicker  # ✅ for date picker

from app.services.expenses import (
    add_transaction, query_transactions, list_categories,
    summary_by_month, summary_by_category, delete_transaction, update_transaction
)
from app.widgets.dialogs import EditExpensePopup

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.categories = list_categories()
        self.refresh_table()

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
        """Open a calendar and set the chosen date into date_input."""
        picker = MDDatePicker(year=date.today().year,
                              month=date.today().month,
                              day=date.today().day)
        picker.bind(on_save=self._on_date_selected)
        picker.open()

    def _on_date_selected(self, instance, value, date_range):
        """Callback when date is chosen."""
        self.ids.date_input.text = value.isoformat()

    def on_add(self):
        d = self.ids.date_input.text.strip() or date.today().isoformat()
        amt_text = self.ids.amount_input.text.strip()
        cat = self.ids.category_spinner.text
        note = self.ids.note_input.text.strip()
        try:
            if cat == "Category":
                raise ValueError("Please choose a category.")
            amt = float(amt_text)

            # ✅ Adjusted call: you need account_id and type_id
            # For demo, assume account_id=1, type_id=2 (expense)
            add_transaction(account_id=1,
                            category_id=self.categories.index(cat) + 1,
                            type_id=2,
                            transaction_date=d,
                            amount=amt,
                            remark=note)

            logger.info(f"Added transaction: {d}, {amt}, {cat}, {note}")
            self.ids.amount_input.text = ""
            self.ids.note_input.text = ""
            self.refresh_table()
        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
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
    def build(self):
        Builder.load_file("app/ui.kv")
        return MainScreen()

if __name__ == "__main__":
    ExpenseTrackerApp().run()