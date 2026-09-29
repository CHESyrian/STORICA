#!/usr/bin/env python3
#/STORICA/frontend/api/worker.py

from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
import traceback


class WorkerSignals(QObject):
    result = pyqtSignal(object)
    error = pyqtSignal(object)
    finished = pyqtSignal()


class ApiWorker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super().__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs

        self.signals = WorkerSignals()

        # Prevent automatic deletion if needed
        self.setAutoDelete(True)

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)

        except Exception as e:
            self.signals.error.emit({
                "type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc(),
            })

        finally:
            self.signals.finished.emit()


class AsyncExecutor:

    def __init__(self):
        self.pool = QThreadPool.globalInstance()

    def run(
        self,
        fn,
        *args,
        on_result=None,
        on_error=None,
        on_finished=None,
        **kwargs,
    ):
        worker = ApiWorker(fn, *args, **kwargs)

        if on_result:
            worker.signals.result.connect(on_result)

        if on_error:
            worker.signals.error.connect(on_error)

        if on_finished:
            worker.signals.finished.connect(on_finished)

        self.pool.start(worker)