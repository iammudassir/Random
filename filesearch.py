import os
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar
from tkinter import ttk
import concurrent.futures

def find_file(root_dir, search_term):
    """
    Optimized file search using scandir and multithreading. It will search
    both in the root directory and all subdirectories for any file containing the search term.
    
    Args:
    root_dir (str): The root directory to start searching from.
    search_term (str): The search term to find in filenames.
    
    Returns:
    list: A list of full file paths that contain the search term in their names.
    """
    matches = []
    
    # Use a thread pool for parallel searching in directories
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        
        # Recursively scan directories using os.walk (includes subdirectories)
        for root, dirs, files in os.walk(root_dir):
            futures.append(executor.submit(find_in_dir, root, files, search_term))
        
        # Collect the results from all threads
        for future in concurrent.futures.as_completed(futures):
            matches.extend(future.result())
    
    return matches

def find_in_dir(directory, files, search_term):
    """Helper function to find matching files in a single directory based on substring matching."""
    matches = []
    for filename in files:
        if search_term.lower() in filename.lower():  # Case-insensitive substring search
            matches.append(os.path.join(directory, filename))
    return matches

def browse_directory():
    """Open a directory selection dialog and set the directory in the entry box."""
    directory = filedialog.askdirectory()
    if directory:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, directory)

def search_files():
    """Search for files and display results in the listbox."""
    search_dir = dir_entry.get()
    search_term = pattern_entry.get()

    if not search_dir or not search_term:
        messagebox.showwarning("Input Error", "Please enter both directory and search term.")
        return

    # Clear the listbox before displaying new results
    listbox.delete(0, tk.END)
    
    # Perform the file search, including subfolders
    found_files = find_file(search_dir, search_term)
    
    if found_files:
        for file in found_files:
            listbox.insert(tk.END, file)
    else:
        messagebox.showinfo("No Files Found", f"No files found containing '{search_term}'.")

def on_click(event):
    """Handle clicking on a file path in the listbox."""
    selected_item = listbox.get(listbox.curselection())
    if selected_item:
        # Open the file path using the default system application (file explorer)
        os.startfile(selected_item)  # For Windows

def toggle_dark_mode():
    """Toggle between dark (night) and light (day) modes."""
    global is_dark_mode
    if is_dark_mode:
        # Switch to day mode (light theme)
        root.config(bg="white")
        frame.config(bg="white")
        dir_label.config(bg="white", fg="black")
        pattern_label.config(bg="white", fg="black")
        dir_entry.config(bg="white", fg="black")
        pattern_entry.config(bg="white", fg="black")
        listbox.config(bg="white", fg="black")
        dark_mode_button.config(text="🌞 Day Mode", bg="lightgray", fg="black")
        is_dark_mode = False
    else:
        # Switch to night mode (dark theme)
        root.config(bg="black")
        frame.config(bg="black")
        dir_label.config(bg="black", fg="white")
        pattern_label.config(bg="black", fg="white")
        dir_entry.config(bg="black", fg="white")
        pattern_entry.config(bg="black", fg="white")
        listbox.config(bg="black", fg="white")
        dark_mode_button.config(text="🌜 Night Mode", bg="darkgray", fg="white")
        is_dark_mode = True

# Create the main window
root = tk.Tk()
root.title("MSearch")

# Make the window resizable
root.resizable(True, True)

# Set the window size (but allow resizing)
root.geometry("750x500")

# Track the current mode (light or dark)
is_dark_mode = False

# Directory label and entry
dir_label = tk.Label(root, text="Directory:", bg="white", fg="black")
dir_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
dir_entry = tk.Entry(root, width=60, bg="white", fg="black")
dir_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')

# Browse button
browse_button = ttk.Button(root, text="Browse", command=browse_directory)
browse_button.grid(row=0, column=2, padx=10, pady=10, sticky='w')

# File pattern label and entry
pattern_label = tk.Label(root, text="Search Term:", bg="white", fg="black")
pattern_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')
pattern_entry = tk.Entry(root, width=60, bg="white", fg="black")
pattern_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

# Search button
search_button = ttk.Button(root, text="Search", command=search_files)
search_button.grid(row=1, column=2, padx=10, pady=10, sticky='w')

# Dark mode toggle button (use tk.Button to allow color changes)
dark_mode_button = tk.Button(root, text="🌞 Day Mode", command=toggle_dark_mode, bg="lightgray", fg="black")
dark_mode_button.grid(row=3, column=0, padx=10, pady=10, sticky='w')

# Listbox to display search results with a scrollbar
frame = tk.Frame(root, bg="white")
frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

scrollbar = Scrollbar(frame, orient="vertical")
listbox = Listbox(frame, width=100, height=20, yscrollcommand=scrollbar.set, bg="white", fg="black", font=("Helvetica", 10))
scrollbar.config(command=listbox.yview)
scrollbar.pack(side="right", fill="y")
listbox.pack(side="left", fill="both", expand=True)

# Bind a click event to the listbox items to open the file
listbox.bind('<Double-1>', on_click)

# Start the GUI event loop
root.mainloop()
