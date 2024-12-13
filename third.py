import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QHBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from CustomTextEdit import CustomTextEdit
class JsonViewer(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize window
        self.setWindowTitle("JSON Viewer PRO")
        self.setGeometry(100, 100, 800, 700)

        # Layouts
        self.main_layout = QVBoxLayout(self)
        self.input_layout = QVBoxLayout()
        self.output_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        # Create input frame with the custom QTextEdit
        self.input_text_box = CustomTextEdit(self)
        self.input_text_box.setPlaceholderText("Input JSON/Array")
        self.input_layout.addWidget(QLabel("Input JSON/Array"))
        self.input_layout.addWidget(self.input_text_box)
        self.main_layout.addLayout(self.input_layout)

        # Create buttons
        self.format_button = QPushButton("Format JSON", self)
        self.format_button.clicked.connect(self.format_json)
        self.clear_button = QPushButton("Clear", self)
        self.clear_button.clicked.connect(self.clear_text)
        self.search_entry = QLineEdit(self)
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.search_in_json)
        self.pin_button = QPushButton("Pin", self)
        self.pin_button.clicked.connect(self.toggle_pin)
        self.button_layout.addWidget(self.format_button)
        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.search_entry)
        self.button_layout.addWidget(self.search_button)
        self.button_layout.addWidget(self.pin_button)
        self.main_layout.addLayout(self.button_layout)

        # Create output frame
        self.output_text_box = QTextEdit(self)
        self.output_text_box.setPlaceholderText("Formatted JSON Output")
        self.output_text_box.setReadOnly(True)
        self.output_layout.addWidget(QLabel("Formatted JSON Output"))
        self.output_layout.addWidget(self.output_text_box)
        self.main_layout.addLayout(self.output_layout)

        self.setLayout(self.main_layout)

    def format_json(self):
        """Formats and displays the JSON or JavaScript array with coloring."""
        input_text = self.input_text_box.toPlainText().strip()
        if not input_text:
            self.output_text_box.clear()
            return  # Don't continue formatting if empty
        try:
            parsed = json.loads(input_text)
            formatted_json = json.dumps(parsed, indent=4)
            self.apply_syntax_coloring(formatted_json)
        except json.JSONDecodeError as e:
            self.show_error("Invalid JSON", f"Error in JSON: {str(e)}")
        except Exception as e:
            self.show_error("Error", f"An unexpected error occurred: {str(e)}")

    def apply_syntax_coloring(self, json_text):
        """Applies advanced syntax coloring to the formatted JSON."""
        self.output_text_box.clear()
        # Regex patterns for coloring
        patterns = {
            r'\"(.*?)\":': QColor(31, 123, 255),  # key
            r'\"(.*?)\"(?=,|\n|\})': QColor(46, 139, 87),  # string
            r'\b\d+\b': QColor(211, 47, 47),  # number
            r'\b(true|false|null)\b': QColor(245, 124, 0),  # boolean
            r'(\[|\])': QColor(117, 117, 117),  # array brackets
            r'(\{|\})': QColor(156, 39, 176)  # object brackets
        }
        cursor = self.output_text_box.textCursor()
        self.output_text_box.setPlainText(json_text)
        for pattern, color in patterns.items():
            self.apply_tag(cursor, pattern, color)

    def apply_tag(self, cursor, pattern, color):
        """Helper function to apply tags to matched text."""
        cursor.setPosition(0)
        format = QTextCharFormat()
        format.setForeground(color)
        regex = re.compile(pattern)
        while True:
            match = regex.search(self.output_text_box.toPlainText(), cursor.position())
            if not match:
                break
            cursor.setPosition(match.start(), QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(match.group(0)))
            cursor.mergeCharFormat(format)

    def clear_text(self):
        """Clears both input and output text boxes."""
        self.input_text_box.clear()
        self.output_text_box.clear()

    def search_in_json(self):
        """Searches for a term in the JSON output."""
        search_term = self.search_entry.text().strip()
        if not search_term:
            self.show_error("Error", "Search term is empty!")
            return
        self.search_results = []
        cursor = self.output_text_box.textCursor()
        self.output_text_box.moveCursor(QTextCursor.Start)
        while True:
            cursor = self.output_text_box.find(search_term, cursor, QTextCursor.FindCaseSensitively)
            if cursor.isNull():
                break
            cursor.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
            cursor.mergeCharFormat(self.create_text_format(QColor(255, 255, 0)))  # Highlight color
            self.search_results.append(cursor)

    def highlight_current_search_result(self):
        """Highlights the current search result."""
        if self.search_results:
            cursor = self.search_results[self.search_index]
            self.output_text_box.setTextCursor(cursor)

    def toggle_pin(self):
        """Toggles the 'always on top' status of the application."""
        self.is_pinned = not self.is_pinned
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.is_pinned)
        self.pin_button.setText("Unpin" if self.is_pinned else "Pin")

    def show_error(self, title, message):
        """Shows an error message dialog."""
        QMessageBox.critical(self, title, message)

    def keyPressEvent(self, event):
        """Handle key events."""
        if event.key() == Qt.Key_Return:
            self.search_in_json()
        super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = JsonViewer()
    viewer.show()
    sys.exit(app.exec_())
