from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Slot
from PySide6.QtCore import QDateTime
import logging

class LogEntry:
    def __init__(self, level: int, message: str):
        self.level = level
        self.message = message
        self.timestamp = QDateTime.currentDateTime()

class LogModel(QAbstractListModel):
    LevelRole = Qt.UserRole + 1
    MAX_LOGS = 1000

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._logs: list[LogEntry] = []
        self._min_visible_level = logging.NOTSET

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._logs)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None

        log_entry = self._logs[index.row()]

        if role == Qt.DisplayRole:
            timestamp_str = log_entry.timestamp.toString("hh:mm:ss")
            return f"[{timestamp_str}] {log_entry.message}"
        elif role == self.LevelRole:
            return log_entry.level

        return None
    
    @Slot(int, str)
    def add_log(self, level: int, message: str):

        if level < self._min_visible_level:
            return

        log_entry = LogEntry(level, message)
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._logs.append(log_entry)
        self.endInsertRows()

        if len(self._logs) > self.MAX_LOGS:
            remove_count = len(self._logs) - self.MAX_LOGS
            self.beginRemoveRows(QModelIndex(), 0, remove_count - 1)
            del self._logs[:remove_count]
            self.endRemoveRows()
            
    @Slot()
    def clear(self):
        self.beginResetModel()
        self._logs.clear()
        self.endResetModel()

    @Slot(int)
    def set_min_visible_level(self, level: int):
        self._min_visible_level = level
        # refilter logs
        self.beginResetModel()
        self._logs = [log for log in self._logs if log.level >= self._min_visible_level]
        self.endResetModel()

    def min_visible_level(self) -> int:
        return self._min_visible_level