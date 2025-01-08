import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk


# Utility Function: Parse .txt file and interpret nesting
def read_structure_with_nesting(file_path):
    """
    Parses a .txt file and interprets nesting levels for directories and files.

    :param file_path: Path to the .txt file.
    :return: List of tuples with (indent_level, name).
    """
    structure = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            stripped = line.rstrip()
            if stripped:
                indent_level = len(line) - len(line.lstrip())
                structure.append((indent_level, stripped))
    return structure


# Utility Function: Sanitize directory and file names
def sanitize_name(name):
    """
    Sanitizes directory and file names to avoid issues with special characters.

    :param name: Original name from the structure.
    :return: Sanitized name.
    """
    if name.strip() == "__init__.py":
        return name.strip()

    name = name.lstrip("_")
    name = name.strip()
    name = name.replace(" ", "_")
    sanitized_name = ''.join(c for c in name if c.isalnum() or c in ('_', '-', '.'))
    return sanitized_name


# Utility Function: Create nested directories and files
def create_nested_structure(base_path, structure):
    """
    Creates directories and files based on the parsed nested structure.

    :param base_path: Root directory where the structure will be created.
    :param structure: List of tuples with (indent_level, name).
    """
    path_stack = [base_path]
    for indent_level, name in structure:
        while len(path_stack) > indent_level + 1:
            path_stack.pop()
        sanitized_name = sanitize_name(name)
        current_path = os.path.join(path_stack[-1], sanitized_name)
        if name.endswith('/'):
            os.makedirs(current_path, exist_ok=True)
            path_stack.append(current_path)
        else:
            with open(current_path, 'w', encoding='utf-8') as f:
                f.write(f"# Placeholder for {sanitized_name}")


# Utility Function: Generate a .txt representation of a directory
def create_txt_from_directory(directory, output_path):
    """
    Converts a directory structure into a .txt representation.

    :param directory: Directory to convert.
    :param output_path: Path to save the generated .txt file.
    """
    with open(output_path, 'w', encoding='utf-8') as txt_file:
        for root, dirs, files in os.walk(directory):
            level = root.replace(directory, "").count(os.sep)
            indent = "    " * level
            if level == 0:
                txt_file.write(f"{os.path.basename(root)}/\n")
            else:
                txt_file.write(f"{indent}{os.path.basename(root)}/\n")
            sub_indent = "    " * (level + 1)
            for file in files:
                txt_file.write(f"{sub_indent}{file}\n")


# Utility Function: Scrape Python files and compile them into a .txt
def scrape_python_files(directory, output_file):
    """
    Scrapes all Python (.py) files in a directory and compiles their content into a single .txt file.

    :param directory: Directory to scrape.
    :param output_file: Path to save the compiled .txt file.
    """
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as py_file:
                        out_file.write(f"# File: {file}\n")
                        out_file.write(py_file.read() + "\n\n")


# Main GUI Class
class CodeStreamGUI:
    """
    The main GUI class for CodeStream.
    Provides tabs for multiple functionalities: Convert for AI, .txt to Directory, Directory to .txt, and File Converters.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("CodeStream")
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f8ff")  # Light blue theme

        # Tab control
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, pady=10, padx=10)

        # Tabs
        self.tab_convert_ai = ttk.Frame(self.notebook)
        self.tab_txt_to_dir = ttk.Frame(self.notebook)
        self.tab_dir_to_txt = ttk.Frame(self.notebook)
        self.tab_file_converters = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_convert_ai, text="Convert for AI")
        self.notebook.add(self.tab_txt_to_dir, text=".txt to Directory")
        self.notebook.add(self.tab_dir_to_txt, text="Directory to .txt")
        self.notebook.add(self.tab_file_converters, text="File Converters")

        # Setup each tab
        self._setup_convert_ai_tab()
        self._setup_txt_to_dir_tab()
        self._setup_dir_to_txt_tab()
        self._setup_file_converters_tab()

    def _setup_convert_ai_tab(self):
        """Sets up the Convert for AI tab."""
        tk.Label(
            self.tab_convert_ai, text="Convert for AI", font=("Segoe UI", 18, "bold"),
            bg="#f0f8ff", fg="#333333"
        ).pack(pady=10)

        self.btn_select_ai_dir = ttk.Button(
            self.tab_convert_ai, text="Select Directory to Scrape", command=self.select_ai_directory
        )
        self.btn_select_ai_dir.pack(pady=10)

        self.btn_save_ai_txt = ttk.Button(
            self.tab_convert_ai, text="Save Compiled .txt File", command=self.save_ai_txt_file
        )
        self.btn_save_ai_txt.pack(pady=10)

        self.ai_directory = None
        self.ai_output_file = None

    def _setup_txt_to_dir_tab(self):
        """Sets up the .txt to Directory tab."""
        tk.Label(
            self.tab_txt_to_dir, text=".txt to Directory", font=("Segoe UI", 18, "bold"),
            bg="#f0f8ff", fg="#333333"
        ).pack(pady=10)

        self.btn_select_txt = ttk.Button(
            self.tab_txt_to_dir, text="Select .txt File", command=self.select_txt_file
        )
        self.btn_select_txt.pack(pady=10)

        self.btn_select_txt_dir = ttk.Button(
            self.tab_txt_to_dir, text="Select Base Directory", command=self.select_txt_base_directory, state="disabled"
        )
        self.btn_select_txt_dir.pack(pady=10)

        self.btn_create_txt_dir = ttk.Button(
            self.tab_txt_to_dir, text="Create Directory Structure", command=self.create_txt_structure, state="disabled"
        )
        self.btn_create_txt_dir.pack(pady=10)

        self.txt_file_path = None
        self.txt_base_directory = None

    def _setup_dir_to_txt_tab(self):
        """Sets up the Directory to .txt tab."""
        tk.Label(
            self.tab_dir_to_txt, text="Directory to .txt", font=("Segoe UI", 18, "bold"),
            bg="#f0f8ff", fg="#333333"
        ).pack(pady=10)

        self.btn_select_dir_to_txt = ttk.Button(
            self.tab_dir_to_txt, text="Select Directory to Convert", command=self.select_dir_to_txt
        )
        self.btn_select_dir_to_txt.pack(pady=10)

        self.btn_save_dir_to_txt = ttk.Button(
            self.tab_dir_to_txt, text="Save as .txt File", command=self.save_dir_to_txt_file
        )
        self.btn_save_dir_to_txt.pack(pady=10)

        self.dir_to_txt_directory = None
        self.dir_to_txt_output_file = None

    def _setup_file_converters_tab(self):
        """Sets up the File Converters tab."""
        tk.Label(
            self.tab_file_converters, text="File Converters", font=("Segoe UI", 18, "bold"),
            bg="#f0f8ff", fg="#333333"
        ).pack(pady=10)

        tk.Label(
            self.tab_file_converters, text="(Future converters can be added here)", font=("Segoe UI", 14),
            bg="#f0f8ff", fg="#555555"
        ).pack(pady=10)

    # Tab 1: Convert for AI
    def select_ai_directory(self):
        """Handles selecting a directory for AI input conversion."""
        self.ai_directory = filedialog.askdirectory(title="Select Directory to Scrape")
        if self.ai_directory:
            messagebox.showinfo("Directory Selected", f"Selected: {self.ai_directory}")
        else:
            messagebox.showerror("Error", "No directory selected!")

    def save_ai_txt_file(self):
        """Saves the scraped Python files as a compiled .txt."""
        if not self.ai_directory:
            messagebox.showerror("Error", "No directory selected!")
            return
        self.ai_output_file = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Save as .txt File"
        )
        if self.ai_output_file:
            scrape_python_files(self.ai_directory, self.ai_output_file)
            messagebox.showinfo("Success", f"Compiled .txt file saved at: {self.ai_output_file}")

    # Tab 2: .txt to Directory
    def select_txt_file(self):
        """Handles selecting a .txt file."""
        self.txt_file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")], title="Select a .txt File")
        if self.txt_file_path:
            messagebox.showinfo("File Selected", f"Selected File: {self.txt_file_path}")
            self.btn_select_txt_dir.config(state="normal")

    def select_txt_base_directory(self):
        """Handles selecting a base directory for .txt to directory conversion."""
        self.txt_base_directory = filedialog.askdirectory(title="Select Base Directory")
        if self.txt_base_directory:
            messagebox.showinfo("Directory Selected", f"Selected: {self.txt_base_directory}")
            self.btn_create_txt_dir.config(state="normal")

    def create_txt_structure(self):
        """Creates a directory structure from a .txt file."""
        if not self.txt_file_path or not self.txt_base_directory:
            messagebox.showerror("Error", "Both a .txt file and base directory must be selected!")
            return
        try:
            structure = read_structure_with_nesting(self.txt_file_path)
            create_nested_structure(self.txt_base_directory, structure)
            messagebox.showinfo("Success", f"Directories created in: {self.txt_base_directory}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Tab 3: Directory to .txt
    def select_dir_to_txt(self):
        """Handles selecting a directory for conversion to .txt."""
        self.dir_to_txt_directory = filedialog.askdirectory(title="Select Directory to Convert")
        if self.dir_to_txt_directory:
            messagebox.showinfo("Directory Selected", f"Selected: {self.dir_to_txt_directory}")

    def save_dir_to_txt_file(self):
        """Saves a directory structure as a .txt file."""
        if not self.dir_to_txt_directory:
            messagebox.showerror("Error", "No directory selected!")
            return
        self.dir_to_txt_output_file = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Save as .txt File"
        )
        if self.dir_to_txt_output_file:
            create_txt_from_directory(self.dir_to_txt_directory, self.dir_to_txt_output_file)
            messagebox.showinfo("Success", f".txt file saved at: {self.dir_to_txt_output_file}")


# Main Application
if __name__ == "__main__":
    root = tk.Tk()
    app = CodeStreamGUI(root)
    root.mainloop()
