import logging
from PySide6.QtCore import QObject, Signal

class QtSignalHandler(logging.Handler, QObject):
    # 定义信号：传递格式化后的日志字符串
    log_signal = Signal(int, str)

    def __init__(self) -> None:
        # 必须先调用 QObject.__init__ 才能使用信号
        QObject.__init__(self)
        logging.Handler.__init__(self)

    def emit(self, record) -> None:
        # 格式化日志记录
        msg = self.format(record)
        # 发射信号（线程安全）
        self.log_signal.emit(record.levelno, msg)