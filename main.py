import tkinter as tk
from tkinter import ttk, messagebox
import json
import re


def format_json():
    """Formats and displays the JSON or JavaScript array with coloring."""
    input_text = input_text_box.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showerror("Error", "Input box is empty!")
        return

    try:
        # Parse and format JSON
        parsed = json.loads(input_text)
        formatted_json = json.dumps(parsed, indent=4)

        # Clear and display formatted JSON
        output_text_box.delete("1.0", tk.END)
        apply_syntax_coloring(formatted_json)

    except json.JSONDecodeError as e:
        messagebox.showerror("Invalid JSON", f"Error in JSON: {str(e)}")


def clear_text():
    """Clears both input and output text boxes."""
    input_text_box.delete("1.0", tk.END)
    output_text_box.delete("1.0", tk.END)


def apply_syntax_coloring(json_text):
    """Applies advanced syntax coloring to the formatted JSON."""
    output_text_box.config(state=tk.NORMAL)
    output_text_box.delete("1.0", tk.END)

    # Regex patterns for coloring
    key_pattern = r'\"(.*?)\":'  # Matches keys
    string_pattern = r'\"(.*?)\"(?=,|\n|\})'  # Matches strings
    number_pattern = r'\b\d+\b'  # Matches numbers
    boolean_pattern = r'\b(true|false|null)\b'  # Matches booleans/null
    array_bracket_pattern = r'(\[|\])'  # Matches array brackets
    object_bracket_pattern = r'(\{|\})'  # Matches object brackets

    # Insert text into the text box
    output_text_box.insert("1.0", json_text)

    # Apply tags for different parts
    for match in re.finditer(key_pattern, json_text):
        start = f"1.{match.start()}"
        end = f"1.{match.end() - 1}"
        output_text_box.tag_add("key", start, end)

    for match in re.finditer(string_pattern, json_text):
        start = f"1.{match.start()}"
        end = f"1.{match.end()}"
        output_text_box.tag_add("string", start, end)

    for match in re.finditer(number_pattern, json_text):
        start = f"1.{match.start()}"
        end = f"1.{match.end()}"
        output_text_box.tag_add("number", start, end)

    for match in re.finditer(boolean_pattern, json_text):
        start = f"1.{match.start()}"
        end = f"1.{match.end()}"
        output_text_box.tag_add("boolean", start, end)

    for match in re.finditer(array_bracket_pattern, json_text):
        start = f"1.{match.start()}"
        end = f"1.{match.end()}"
        output_text_box.tag_add("array", start, end)

    for match in re.finditer(object_bracket_pattern, json_text):
        start = f"1.{match.start()}"
        end = f"1.{match.end()}"
        output_text_box.tag_add("object", start, end)

    # Configure tag colors
    output_text_box.tag_config("key", foreground="blue")         # Key: Blue
    output_text_box.tag_config("string", foreground="green")     # String: Green
    output_text_box.tag_config("number", foreground="darkred")   # Number: Dark Red
    output_text_box.tag_config("boolean", foreground="orange")   # Boolean/Null: Orange
    output_text_box.tag_config("array", foreground="purple")     # Array brackets: Purple
    output_text_box.tag_config("object", foreground="brown")     # Object brackets: Brown

    output_text_box.config(state=tk.DISABLED)


def search_in_json():
    """Searches for a term in the JSON output."""
    search_term = search_entry.get().strip()
    if not search_term:
        messagebox.showerror("Error", "Search term is empty!")
        return

    output_text_box.tag_remove("highlight", "1.0", tk.END)
    output_text_box.config(state=tk.NORMAL)

    start_idx = "1.0"
    while True:
        start_idx = output_text_box.search(search_term, start_idx, tk.END, nocase=True)
        if not start_idx:
            break
        end_idx = f"{start_idx}+{len(search_term)}c"
        output_text_box.tag_add("highlight", start_idx, end_idx)
        start_idx = end_idx

    output_text_box.tag_config("highlight", background="yellow")
    output_text_box.config(state=tk.DISABLED)


def toggle_pin():
    """Toggles the 'always on top' status of the application."""
    global is_pinned
    is_pinned = not is_pinned
    app.wm_attributes("-topmost", is_pinned)
    pin_button.config(text="Unpin" if is_pinned else "Pin")


# Initialize pin state
is_pinned = False

# Create the main application window
app = tk.Tk()
app.title("JSON Formatter with Advanced Coloring & Search")
app.geometry("800x700")

# Create input frame
input_frame = ttk.LabelFrame(app, text="Input JSON/Array", padding=(10, 10))
input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Input text box
input_text_box = tk.Text(input_frame, wrap=tk.WORD, height=10)
input_text_box.pack(fill=tk.BOTH, expand=True)

# Button frame
button_frame = ttk.Frame(app, padding=(10, 10))
button_frame.pack(fill=tk.X, pady=5)

# Format Button
format_button = ttk.Button(button_frame, text="Format JSON", command=format_json)
format_button.pack(side=tk.LEFT, padx=5)

# Clear Button
clear_button = ttk.Button(button_frame, text="Clear", command=clear_text)
clear_button.pack(side=tk.LEFT, padx=5)

# Search Entry
search_entry = ttk.Entry(button_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)

# Search Button
search_button = ttk.Button(button_frame, text="Search", command=search_in_json)
search_button.pack(side=tk.LEFT, padx=5)

# Pin Button
pin_button = ttk.Button(button_frame, text="Pin", command=toggle_pin)
pin_button.pack(side=tk.LEFT, padx=5)

# Create output frame
output_frame = ttk.LabelFrame(app, text="Formatted JSON Output", padding=(10, 10))
output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Output text box
output_text_box = tk.Text(output_frame, wrap=tk.WORD, height=15, state=tk.DISABLED)
output_text_box.pack(fill=tk.BOTH, expand=True)

# Run the application
app.mainloop()
