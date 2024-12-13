import sys
import json
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QHBoxLayout, QLabel, QFrame, QMessageBox, QToolButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QTextCharFormat, QCursor, QIcon

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

        # Create a custom title bar layout (pin button will be here)
        self.title_bar_layout = QHBoxLayout()

        # Create input frame
        self.input_text_box = QTextEdit(self)
        self.input_text_box.setPlaceholderText("Input JSON/Array")
        self.input_layout.addWidget(QLabel("Input JSON/Array"))
        self.input_layout.addWidget(self.input_text_box)
        self.main_layout.addLayout(self.input_layout)

        # Pin Button in title bar (now part of title bar)
        self.pin_button = QToolButton(self)
        self.pin_button.setIcon(QIcon("icons/close.png"))  # Replace with your pin icon image path
        self.pin_button.setIconSize(QSize(20, 20))  # Set the icon size
        self.pin_button.setToolTip("Pin Window")
        self.pin_button.clicked.connect(self.toggle_pin)
        self.title_bar_layout.addWidget(self.pin_button, alignment=Qt.AlignRight)

        # Create output frame
        self.output_text_box = QTextEdit(self)
        self.output_text_box.setPlaceholderText("Formatted JSON Output")
        self.output_text_box.setReadOnly(True)
        self.output_layout.addWidget(QLabel("Formatted JSON Output"))
        self.output_layout.addWidget(self.output_text_box)
        self.main_layout.addLayout(self.output_layout)

        self.setLayout(self.main_layout)

        # Override the title bar and set custom title bar
        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove the default title bar
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.is_pinned)
        self.setWindowTitle("JSON Viewer PRO")

        self.setWindowTitleBarWidget()

    def setWindowTitleBarWidget(self):
        """Set custom title bar with pin button."""
        # Create a frame for the custom title bar
        title_bar = QFrame(self)
        title_bar.setLayout(self.title_bar_layout)
        title_bar.setStyleSheet("background-color: lightgray; border: none; height: 30px;")

        # Add the custom title bar to the window
        self.main_layout.insertWidget(0, title_bar)

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
        self.apply_tag(cursor, key_pattern, "key", 'blue')
        self.apply_tag(cursor, string_pattern, "string", 'green')
        self.apply_tag(cursor, number_pattern, "number", 'red')
        self.apply_tag(cursor, boolean_pattern, "boolean", 'orange')
        self.apply_tag(cursor, array_bracket_pattern, "array", 'purple')
        self.apply_tag(cursor, object_bracket_pattern, "object", 'brown')

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

        # Map color names to QColor
        color_map = {
            'blue': QColor(0, 0, 255),        # Blue
            'green': QColor(0, 255, 0),       # Green
            'red': QColor(255, 0, 0),         # Red
            'orange': QColor(255, 165, 0),    # Orange
            'purple': QColor(128, 0, 128),    # Purple
            'brown': QColor(139, 69, 19)      # Brown
        }

        # Use QColor for valid colors
        if color in color_map:
            fmt.setForeground(color_map[color])

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
        self.pin_button.setIcon(QIcon("pin_icon.png" if not self.is_pinned else "unpinned_icon.png"))  # Update the icon
        self.show()

    def show_error(self, title, message):
        """Shows an error message dialog."""
        QMessageBox.critical(self, title, message)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        viewer = JsonViewer()
        viewer.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)
