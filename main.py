import sys
import json
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QHBoxLayout, QLabel, QFrame, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from CustomTextEdit import CustomTextEdit
class JsonViewer(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize window
        self.setWindowTitle("JSON Viewer PRO")
        self.setGeometry(100, 100, 800, 700)

        # Variables
        self.search_results = []
        self.search_index = 0
        self.is_pinned = False

        # Layouts
        self.main_layout = QVBoxLayout(self)
        self.input_layout = QVBoxLayout()
        self.output_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        # Create input frame
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

    def clear_text(self):
        """Clears both input and output text boxes."""
        self.input_text_box.clear()
        self.output_text_box.clear()

    def apply_syntax_coloring(self, json_text):
        """Applies advanced syntax coloring to the formatted JSON."""
        self.output_text_box.clear()

        # Regex patterns for coloring
        key_pattern = r'\"(.*?)\":'
        string_pattern = r'\"(.*?)\"(?=,|\n|\})'
        number_pattern = r'\b\d+\b'
        boolean_pattern = r'\b(true|false|null)\b'
        array_bracket_pattern = r'(\[|\])'
        object_bracket_pattern = r'(\{|\})'

        # Insert text into the text box
        self.output_text_box.setPlainText(json_text)

        # Apply tags for different parts
        cursor = self.output_text_box.textCursor()
        cursor.setPosition(0)

        # Apply coloring using regex
        self.apply_tag(cursor, key_pattern, "key", QColor(31, 123, 255))
        self.apply_tag(cursor, string_pattern, "string", QColor(46, 139, 87))
        self.apply_tag(cursor, number_pattern, "number", QColor(211, 47, 47))
        self.apply_tag(cursor, boolean_pattern, "boolean", QColor(245, 124, 0))
        self.apply_tag(cursor, array_bracket_pattern, "array", QColor(117, 117, 117))
        self.apply_tag(cursor, object_bracket_pattern, "object", QColor(156, 39, 176))

    def apply_tag(self, cursor, pattern, tag, color):
        """Helper function to apply tags to matched text."""
        regex = re.compile(pattern)
        for match in regex.finditer(self.output_text_box.toPlainText()):
            start = match.start()
            end = match.end()
            cursor.setPosition(start)
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, end - start)
            cursor.setCharFormat(self.create_text_format(color))

    def create_text_format(self, color):
        """Create text format for coloring"""
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        return fmt

    def search_in_json(self):
        """Searches for a term in the JSON output."""
        search_term = self.search_entry.text().strip()
        if not search_term:
            self.show_error("Error", "Search term is empty!")
            return

        self.search_results.clear()
        text = self.output_text_box.toPlainText()

        # Perform search and highlight the results
        cursor = self.output_text_box.textCursor()
        cursor.setPosition(0)
        while cursor.hasSelection():
            cursor.movePosition(cursor.NextCharacter, cursor.KeepAnchor)

        self.highlight_current_search_result()

    def highlight_current_search_result(self):
        """Highlights the current search result."""
        if self.search_results:
            start, end = self.search_results[self.search_index]
            cursor = self.output_text_box.textCursor()
            cursor.setPosition(start)
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, end - start)
            self.output_text_box.setTextCursor(cursor)

    def toggle_pin(self):
        """Toggles the 'always on top' status of the application."""
        self.is_pinned = not self.is_pinned
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.is_pinned)
        self.pin_button.setText("Unpin" if self.is_pinned else "Pin")
        self.show()

    def show_error(self, title, message):
        """Shows an error message dialog."""
        QMessageBox.critical(self, title, message)

    def keyPressEvent(self, event):
        """Handle key events."""
        if event.key() == Qt.Key_Return:
            # Enter key will trigger the search functionality
            self.search_in_json()
        super().keyPressEvent(event)

    def pasteEvent(self, event):
        """Override the paste event."""
        super().pasteEvent(event)  # Call the base class pasteEvent to handle pasting
        self.format_json()  # Automatically format JSON when pasted
        print('Paste event detected!')  # Optional: debug print to verify


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        viewer = JsonViewer()
        viewer.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)
