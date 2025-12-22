from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.label import Label

class EditExpensePopup(Popup):
    def __init__(self, record: dict, categories: list[str], on_save, **kwargs):
        super().__init__(**kwargs)
        self.title = f"Edit Expense #{record['id']}"
        self.size_hint = (0.6, 0.6)
        self.auto_dismiss = True
        self.on_save = on_save
        self.record = record

        layout = BoxLayout(orientation='vertical', spacing=8, padding=8)
        self.date_input = TextInput(text=record["date"])
        self.amount_input = TextInput(text=f"{record['amount']:.2f}", input_filter='float')
        self.category_spinner = Spinner(text=record["category"], values=categories)
        self.note_input = TextInput(text=record.get("note", ""))

        btns = BoxLayout(size_hint_y=None, height=40, spacing=8)
        btns.add_widget(Button(text="Cancel", on_release=lambda *_: self.dismiss()))
        btns.add_widget(Button(text="Save", on_release=self._save))

        for w in [Label(text="Date"), self.date_input, Label(text="Amount"), self.amount_input,
                  Label(text="Category"), self.category_spinner, Label(text="Note"), self.note_input, btns]:
            layout.add_widget(w)

        self.content = layout

    def _save(self, *_):
        try:
            updated = {
                "id": self.record["id"],
                "date": self.date_input.text.strip(),
                "amount": float(self.amount_input.text.strip()),
                "category": self.category_spinner.text,
                "note": self.note_input.text.strip(),
            }
            self.on_save(updated)
            self.dismiss()
        except Exception:
            # keep it simple; you can add error labels
            self.dismiss()