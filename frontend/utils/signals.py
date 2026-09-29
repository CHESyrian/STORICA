from PyQt6.QtCore import QObject, pyqtSignal, QDate


class SignalBus(QObject):

    statusbar_msg      = pyqtSignal(str, int, bool)
    brand_clicked      = pyqtSignal()



signals = SignalBus()
