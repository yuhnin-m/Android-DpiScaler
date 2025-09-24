from PySide6.QtWidgets import QLineEdit


class ValidatedLineEdit(QLineEdit):
    def focusOutEvent(self, event):  # noqa: N802
        super().focusOutEvent(event)
        text = self.text().strip()
        try:
            value = float(text)
            if 0.1 <= value <= 10.0:
                self.setStyleSheet("")
                self.setToolTip("")
            else:
                self._mark_invalid()
        except ValueError:
            self._mark_invalid()

    def _mark_invalid(self):
        self.setStyleSheet("border: 2px solid red; border-radius: 4px;")
        self.setToolTip("Enter a number from 0.1 to 10.0 (scale relative to xxxhdpi)")
