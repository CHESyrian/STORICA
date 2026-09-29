from PyQt6.QtWidgets import (
    QTableView, QTableWidget, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt


class StandardTable(QTableWidget):
    def __init__(self, headers, stretch=True):
        super().__init__()
        
        self.headers = headers

        # Items Table
        self.setColumnCount(len(self.headers))
        self.setHorizontalHeaderLabels(headers)

        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.horizontalHeader().setStretchLastSection(
            stretch
        )
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.setDragDropOverwriteMode(False)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(50)
    
    def resize_to_content(self):
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.horizontalHeader().setStretchLastSection(
            True
        )
        self.resizeColumnsToContents
