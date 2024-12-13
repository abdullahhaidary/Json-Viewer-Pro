from PyQt5.QtWidgets import QTextEdit

class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(CustomTextEdit, self).__init__(parent)

    def insertFromMimeData(self, source):
        super().insertFromMimeData(source)  # Perform the normal paste functionality
        self.parent().format_json()  # Call the format_json method of the parent widget
