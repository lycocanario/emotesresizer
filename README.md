# Emotes Resizer

An automatic PNG image resizer built with Python and Tkinter. This tool automatically resizes a single high-resolution PNG image into three standard dimensions required for platform emotes (28px, 56px, and 112px) and organizes them into a dedicated folder.

## Features
* **One-Click Automation:** Instantly generates 3 mandatory resolutions.
* **Auto-Naming:** Files are renamed automatically (e.g., `28p_yourfile.png`).
* **High-Quality Resizing:** Uses `LANCZOS` resampling to keep pixel art and text clean and sharp.
* **Smart Organization:** Saves all output files into a separate `Twitch Emotes` folder.
* **Portable:** Runs anywhere as a standalone application.

## How to Run from Source Code
If you want to run this project using Python, follow these steps:
1. Install Python from [python.org](https://python.org).
2. Open your terminal or Command Prompt and install the required image library:
   ```bash
   pip install Pillow
   ```
3. Run the script:
   ```bash
   python resizer.py
   ```

---
