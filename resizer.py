import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def resize_image():
    # 1. Select the image file
    file_path = filedialog.askopenfilename(
        title="Select PNG File",
        filetypes=[("PNG Files", "*.png")]
    )
    
    if not file_path:
        return # If the user cancels the dialog
        
    try:
        # 2. Open the original image
        img = Image.open(file_path)
        
        # Get the original directory folder and file name
        folder = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        
        # 3. Define the new 'Twitch Emotes' subfolder path
        target_folder = os.path.join(folder, "Twitch Emotes")
        
        # Automatically create the 'Twitch Emotes' folder if it doesn't exist yet
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        
        # 4. Define target resolution sizes
        sizes = [28, 56, 112]
        
        # 5. Automatically process the resizing
        for size in sizes:
            # Use Resampling.LANCZOS to keep the image sharp and high quality
            resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Format the new file name (e.g., 28p_EMOTES.png)
            new_file_name = f"{size}p_{base_name}"
            
            # Save inside the 'Twitch Emotes' subfolder
            save_path = os.path.join(target_folder, new_file_name)
            
            # Save the file
            resized_img.save(save_path, "PNG")
            
        messagebox.showinfo("Success!", "Successfully created 3 image resolutions in the 'Twitch Emotes' folder!")
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing the image.\nDetails: {str(e)}")

# --- Create Application User Interface (GUI) ---
root = tk.Tk()
root.title("Emotes Resizer")
root.geometry("350x150")
root.resizable(False, False)

# Main descriptive label
label = tk.Label(root, text="Automatically generate PNG emotes in\n28px, 56px, and 112px", font=("Arial", 11), pady=15)
label.pack()

# Green action button
btn_pilih = tk.Button(root, text="Choose PNG Image", command=resize_image, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", padx=10, pady=5)
btn_pilih.pack()

root.mainloop()
