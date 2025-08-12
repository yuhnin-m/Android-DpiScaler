from PySide6.QtCore import QObject, Signal

from domain.export_models import ExportRequest
from services.export_service import execute_export


class ExportWorker(QObject):
    progress = Signal(int)
    finished = Signal()
    error = Signal(str)

    def __init__(self, request: ExportRequest):
        super().__init__()
        self.request = request

    def run(self):
        try:
            execute_export(self.request, progress_callback=self.progress.emit)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
