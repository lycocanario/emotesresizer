import os
import sys
import subprocess
import webbrowser

import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk


# --------------------------------------------------
# App Configuration
# --------------------------------------------------

APP_NAME = "Tomato Resizer"
VERSION = "1.1.0"
OUTPUT_FOLDER = "Resized"
GITHUB_URL = "https://github.com/lycocanario/tomatoresizer"
DEFAULT_SIZES = "28, 56, 112"

custom_output_folder = None

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# --------------------------------------------------
# Window Helpers
# --------------------------------------------------

def get_resource_path(relative_path):
    """Get resource path for normal and PyInstaller builds."""
    base_path = getattr(
        sys,
        "_MEIPASS",
        os.path.dirname(os.path.abspath(__file__))
    )

    return os.path.join(base_path, relative_path)


def center_window(window, width=None, height=None):
    """Center a window and use its natural size when dimensions are omitted."""
    window.update_idletasks()

    window_width = width or window.winfo_reqwidth()
    window_height = height or window.winfo_reqheight()

    x = (window.winfo_screenwidth() - window_width) // 2
    y = (window.winfo_screenheight() - window_height) // 2

    window.geometry(
        f"{window_width}x{window_height}+{x}+{y}"
    )


def apply_window_icon(window):
    """Apply the Tomato Resizer icon to additional windows."""
    if app_icon:
        try:
            window.iconphoto(False, app_icon)
        except Exception:
            pass

    if os.path.exists(icon_path):

        def set_icon():
            try:
                window.iconbitmap(icon_path)
            except Exception:
                pass

        window.after(250, set_icon)


def open_folder(path):
    """Open a folder in the system file manager."""
    if sys.platform == "win32":
        os.startfile(path)

    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])

    else:
        subprocess.Popen(["xdg-open", path])


# --------------------------------------------------
# Dialogs
# --------------------------------------------------

def show_popup(title, message, is_success=False, target_path=""):
    """Show a custom message window."""
    pop = ctk.CTkToplevel(root)
    pop.title(title)

    apply_window_icon(pop)
    center_window(pop, 380, 160)

    pop.resizable(False, False)
    pop.transient(root)
    pop.grab_set()

    ctk.CTkLabel(
        pop,
        text=message,
        font=("Arial", 12, "bold" if is_success else "normal"),
        wraplength=340
    ).pack(pady=(25, 20))

    button_frame = ctk.CTkFrame(
        pop,
        fg_color="transparent"
    )
    button_frame.pack(pady=10)

    if is_success:

        def open_output_folder():
            if target_path and os.path.exists(target_path):
                open_folder(target_path)

            pop.destroy()

        ctk.CTkButton(
            button_frame,
            text="Open Folder",
            width=130,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=open_output_folder,
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=10)

    ctk.CTkButton(
        button_frame,
        text="Ok!" if is_success else "OK",
        width=100,
        command=pop.destroy,
        font=("Arial", 11, "bold")
    ).pack(side="left", padx=10)


def show_about_window():
    """Show application information."""
    about_win = ctk.CTkToplevel(root)
    about_win.title(f"About")

    apply_window_icon(about_win)
    center_window(about_win, 380, 320)

    about_win.resizable(False, False)
    about_win.transient(root)
    about_win.grab_set()

    ctk.CTkLabel(
        about_win,
        text=APP_NAME,
        font=("Arial", 14, "bold")
    ).pack(pady=(20, 2))

    ctk.CTkLabel(
        about_win,
        text=f"Version {VERSION}",
        font=("Arial", 10, "italic"),
        text_color="gray"
    ).pack(pady=(0, 10))

    info_text = (
        "It's a simple and lightweight tool designed to make resizing Emotes File process faster and easier.\n\n"
        f"Feature v{VERSION}:\n"
        "  • Mutliple Size Resizing.\n"
        "  • Automatic File Naming.\n"
        "  • Flexible Output Folder.\n"
        "  • Two Ways to Select.\n"
        "  • Quick Access to Result.\n\n"
        "Less resizing, more creating!"
    )

    ctk.CTkLabel(
        about_win,
        text=info_text,
        font=("Arial", 11),
        wraplength=340,
        justify="left"
    ).pack(pady=5, padx=20)

    ctk.CTkButton(
        about_win,
        text="Close",
        width=100,
        command=about_win.destroy,
        font=("Arial", 11, "bold")
    ).pack(pady=18)


# --------------------------------------------------
# Output Directory
# --------------------------------------------------

def choose_output_folder():
    """Choose a custom output directory."""
    global custom_output_folder

    selected_folder = filedialog.askdirectory(
        title="Select Output Folder"
    )

    if selected_folder:
        custom_output_folder = selected_folder
        update_output_display()


def reset_output_folder():
    """Reset output directory to the default source location."""
    global custom_output_folder

    custom_output_folder = None
    update_output_display()


def update_output_display():
    """Update the output directory display."""
    if custom_output_folder:
        folder_name = os.path.basename(
            os.path.normpath(custom_output_folder)
        )

        output_label.configure(
            text=f"Output Folder: ...\\{folder_name}"
        )

        reset_output_button.configure(
            state="normal"
        )

    else:
        output_label.configure(
            text="Output Folder: Same as source"
        )

        reset_output_button.configure(
            state="disabled"
        )


# --------------------------------------------------
# Image Processing
# --------------------------------------------------

def get_sizes():
    """Read and validate target image sizes."""
    size_input = entry_sizes.get().strip()

    if not size_input:
        raise ValueError

    sizes = [
        int(size.strip())
        for size in size_input.split(",")
    ]

    if any(size <= 0 for size in sizes):
        raise ValueError

    # Remove duplicates while keeping their original order.
    return list(dict.fromkeys(sizes))


def process_images(file_paths):
    """Resize selected PNG files."""
    try:
        sizes = get_sizes()

    except ValueError:
        show_popup(
            "Error",
            "Invalid format! Use positive numbers separated by commas "
            "(e.g., 28, 56, 112)."
        )
        return

    if not file_paths:
        return

    # Custom output selected by the user.
    if custom_output_folder:
        target_folder = custom_output_folder

    # Default behavior: create "Resized"
    # beside the source images.
    else:
        target_folder = os.path.join(
            os.path.dirname(file_paths[0]),
            OUTPUT_FOLDER
        )

    try:
        os.makedirs(
            target_folder,
            exist_ok=True
        )

        for file_path in file_paths:

            with Image.open(file_path) as image:

                for size in sizes:

                    output_path = os.path.join(
                        target_folder,
                        f"{size}p_{os.path.basename(file_path)}"
                    )

                    resized_image = image.resize(
                        (size, size),
                        Image.Resampling.LANCZOS
                    )

                    resized_image.save(
                        output_path,
                        "PNG"
                    )

        show_popup(
            "Success!",
            f"Successfully processed {len(file_paths)} images\n"
            f"into {len(sizes)} resolutions!",
            is_success=True,
            target_path=target_folder
        )

    except Exception as error:
        show_popup(
            "Error",
            f"An error occurred while processing.\n"
            f"Details: {error}"
        )


# --------------------------------------------------
# File Selection
# --------------------------------------------------

def select_images():
    """Select PNG files using the file dialog."""
    file_paths = filedialog.askopenfilenames(
        title="Select PNG Files",
        filetypes=[("PNG Files", "*.png")]
    )

    if file_paths:
        process_images(file_paths)


# --------------------------------------------------
# Drag & Drop
# --------------------------------------------------

def handle_drop(event):
    """Process PNG files dropped onto the drop area."""
    file_paths = root.tk.splitlist(event.data)

    png_files = [
        path
        for path in file_paths
        if os.path.isfile(path)
        and path.lower().endswith(".png")
    ]

    if not png_files:
        show_popup(
            "Invalid File",
            "Please drop PNG images only."
        )
        return

    process_images(png_files)


# --------------------------------------------------
# Links
# --------------------------------------------------

def open_github(event=None):
    """Open the Tomato Resizer GitHub repository."""
    webbrowser.open(GITHUB_URL)


# --------------------------------------------------
# Main Window
# --------------------------------------------------

root = ctk.CTk()
root.title(APP_NAME)

# Enable native Drag & Drop support.
TkinterDnD.require(root)


# --------------------------------------------------
# App Icon
# --------------------------------------------------

app_icon = None
icon_path = get_resource_path("logo.ico")

if os.path.exists(icon_path):
    try:
        with Image.open(icon_path) as icon_image:
            app_icon = ImageTk.PhotoImage(icon_image)

        root.iconphoto(
            False,
            app_icon
        )

        if sys.platform == "win32":
            root.iconbitmap(icon_path)

    except Exception:
        pass


# --------------------------------------------------
# About Button
# --------------------------------------------------

btn_about = ctk.CTkButton(
    root,
    text="❓",
    width=30,
    height=22,
    font=("Arial", 10, "bold"),
    fg_color="transparent",
    text_color=("#555555", "#CCCCCC"),
    hover_color=("#E5E5E5", "#333333"),
    command=show_about_window
)

btn_about.place(
    x=360,
    y=10
)


# --------------------------------------------------
# Main Interface
# --------------------------------------------------

ctk.CTkLabel(
    root,
    text="PNG Emotes Resizer",
    font=("Arial", 16, "bold")
).pack(
    pady=(20, 5)
)


ctk.CTkLabel(
    root,
    text="Enter target sizes (separate with commas):",
    font=("Arial", 11)
).pack(
    pady=5
)


entry_sizes = ctk.CTkEntry(
    root,
    width=250,
    placeholder_text=f"e.g. {DEFAULT_SIZES}"
)

entry_sizes.insert(
    0,
    DEFAULT_SIZES
)

entry_sizes.pack(
    pady=(5, 10)
)


# --------------------------------------------------
# Output Directory
# --------------------------------------------------

output_frame = ctk.CTkFrame(
    root,
    fg_color="transparent"
)

output_frame.pack(
    pady=(0, 5)
)


output_label = ctk.CTkLabel(
    output_frame,
    text="Output Folder: Same as source",
    width=180,
    anchor="w",
    font=("Arial", 11)
)

output_label.pack(
    side="left",
    padx=(0, 5)
)


reset_output_button = ctk.CTkButton(
    output_frame,
    text="×",
    width=25,
    height=24,
    command=reset_output_folder,
    state="disabled",
    fg_color="transparent",
    hover_color=("#E5E5E5", "#333333"),
    text_color=("#555555", "#CCCCCC")
)

reset_output_button.pack(
    side="left",
    padx=2
)


output_button = ctk.CTkButton(
    output_frame,
    text="...",
    width=35,
    height=24,
    command=choose_output_folder
)

output_button.pack(
    side="left",
    padx=2
)


# --------------------------------------------------
# Drag & Drop Area
# --------------------------------------------------

drop_area = ctk.CTkLabel(
    root,
    width=250,
    height=85,
    text="Drop PNG Images Here\nor click to browse",
    font=("Arial", 12, "bold"),
    corner_radius=10,
    fg_color=("#F3E8FF", "#332A3A"),
    text_color=("#6F4A85", "#E4C7F7"),
    cursor="hand2"
)

drop_area.pack(
    pady=5,
    padx=40
)


drop_area.drop_target_register(
    DND_FILES
)

drop_area.dnd_bind(
    "<<Drop>>",
    handle_drop
)


drop_area.bind(
    "<Button-1>",
    lambda event: select_images()
)


# --------------------------------------------------
# GitHub Footer
# --------------------------------------------------

footer = ctk.CTkLabel(
    root,
    text="View Source Code & Documentation on GitHub",
    font=("Arial", 10, "underline"),
    text_color="#3498db",
    cursor="hand2"
)

footer.bind(
    "<Button-1>",
    open_github
)

footer.pack(
    pady=(12, 0)
)


# --------------------------------------------------
# Final Window Setup
# --------------------------------------------------

# Fixed width, automatic height.
center_window(
    root,
    width=400
)

root.resizable(
    False,
    False
)

root.mainloop()
