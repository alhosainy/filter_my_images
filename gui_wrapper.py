import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import threading
import subprocess
from datetime import datetime
from PIL import Image, ImageTk
import sys
from tkinter import PhotoImage

class ModernFaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Studio")
        self.root.geometry("800x700")
        self.root.minsize(600, 600)
        
        # Set window icon
        self.root.iconphoto(False, PhotoImage(file='assets/icon.png'))
        self.root.iconbitmap('assets/icon.ico')
        
        # Theme setup
        self.style = ttk.Style("darkly")  # Modern dark theme
        
        # Variables
        self.known_image_dir = ""
        self.input_images_path = ""
        self.output_image_path = "recognized"
        self.tolerance_level = 0.6
        self.delete_after_copy = tk.BooleanVar(value=False)
        self.config_file = "config.json"
        self.process = None
        
        # Create UI
        self.create_main_layout()
        self.load_config()
        
    def create_main_layout(self):
        # Main Frame
        self.main_container = ttk.Frame(self.root, padding=20)
        self.main_container.pack(fill=BOTH, expand=True)
        
        # Header
        ttk.Label(self.main_container, text="Face Recognition Studio", font=("Segoe UI", 24, "bold"), bootstyle=PRIMARY).pack(pady=10)
        
        # Control Frame
        control_frame = ttk.Frame(self.main_container)
        control_frame.pack(fill=X, pady=10)
        
        # Directory Selection
        self.create_directory_selection(control_frame)
        
        # Settings Frame
        self.create_settings_section(control_frame)
        
        # Run Button
        self.run_button = ttk.Button(self.main_container, text="Start Recognition", bootstyle=SUCCESS, command=self.toggle_recognition, padding=10)
        self.run_button.pack(fill=X, pady=15)
        
        # Output Text Box
        self.create_output_display()
        
    def create_directory_selection(self, parent):
        frame = ttk.Labelframe(parent, text="Directories", padding=10)
        frame.pack(fill=X, expand=True, padx=5, pady=5)
        
        ttk.Button(frame, text="Select Known Images", command=self.select_known_images_dir, bootstyle=INFO).pack(fill=X, pady=5)
        self.known_images_label = ttk.Label(frame, text="No directory selected", bootstyle=SECONDARY)
        self.known_images_label.pack(fill=X)
        
        ttk.Button(frame, text="Select Input Images", command=self.select_input_images_dir, bootstyle=INFO).pack(fill=X, pady=5)
        self.input_images_label = ttk.Label(frame, text="No directory selected", bootstyle=SECONDARY)
        self.input_images_label.pack(fill=X)
        
        ttk.Button(frame, text="Select Output Directory", command=self.select_output_images_dir, bootstyle=INFO).pack(fill=X, pady=5)
        self.output_images_label = ttk.Label(frame, text="No directory selected", bootstyle=SECONDARY)
        self.output_images_label.pack(fill=X)
        
    def create_settings_section(self, parent):
        frame = ttk.Labelframe(parent, text="Recognition Settings", padding=10)
        frame.pack(fill=X, expand=True, padx=5, pady=5)
        
        ttk.Label(frame, text="Recognition Tolerance", bootstyle=INFO).pack(anchor=W)
        self.tolerance_slider = ttk.Scale(frame, from_=0.1, to=1.0, orient=HORIZONTAL, command=self.update_tolerance_label)
        self.tolerance_slider.set(self.tolerance_level)
        self.tolerance_slider.pack(fill=X)
        
        ttk.Checkbutton(frame, text="Delete after copy", variable=self.delete_after_copy).pack(anchor=W)
        
        ttk.Button(frame, text="Save Config", command=self.save_config, bootstyle=PRIMARY).pack(fill=X, pady=5)
        
    def create_output_display(self):
        frame = ttk.Labelframe(self.main_container, text="Processing Output", padding=10)
        frame.pack(fill=BOTH, expand=True)
        
        self.output_text = tk.Text(frame, wrap=WORD, height=10, bg="black", fg="white", font=("Consolas", 10))
        self.output_text.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
    def select_known_images_dir(self):
        self.known_image_dir = filedialog.askdirectory(title="Select Known Images Directory")
        if self.known_image_dir:
            self.known_images_label.config(text=os.path.basename(self.known_image_dir))
    
    def select_input_images_dir(self):
        self.input_images_path = filedialog.askdirectory(title="Select Input Images Directory")
        if self.input_images_path:
            self.input_images_label.config(text=os.path.basename(self.input_images_path))
    
    def select_output_images_dir(self):
        self.output_image_path = filedialog.askdirectory(title="Select Output Directory")
        if self.output_image_path:
            self.output_images_label.config(text=os.path.basename(self.output_image_path))
    
    def save_config(self):
        config = {
            'known_image_dir': self.known_image_dir,
            'input_images_path': self.input_images_path,
            'output_image_path': self.output_image_path,
            'tolerance_level': self.tolerance_slider.get(),
            'delete_after_copy': self.delete_after_copy.get()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        messagebox.showinfo("Configuration Saved", "Configuration has been saved successfully.")
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.known_image_dir = config.get('known_image_dir', '')
                self.input_images_path = config.get('input_images_path', '')
                self.output_image_path = config.get('output_image_path', 'recognized')
                self.tolerance_level = config.get('tolerance_level', 0.6)
                self.delete_after_copy.set(config.get('delete_after_copy', False))
                self.tolerance_slider.set(self.tolerance_level)
                self.update_directory_labels()

    def update_directory_labels(self):
        self.known_images_label.config(text=os.path.basename(self.known_image_dir) if self.known_image_dir else "No directory selected")
        self.input_images_label.config(text=os.path.basename(self.input_images_path) if self.input_images_path else "No directory selected")
        self.output_images_label.config(text=os.path.basename(self.output_image_path) if self.output_image_path else "No directory selected")

    def update_tolerance_label(self, value):
        pass
    
    def toggle_recognition(self):
        if self.process:
            self.confirm_stop()
        else:
            self.run_face_recognition()

    def confirm_stop(self):
        if messagebox.askyesno("Confirm Stop", "Are you sure you want to stop the recognition process?"):
            self.stop_face_recognition()

    def run_face_recognition(self):
        if not self.known_image_dir or not self.input_images_path:
            messagebox.showerror("Error", "Please select input and known images directories.")
            return
        
        self.output_text.delete("1.0", tk.END)  # Clear previous output
        self.run_button.config(text="Stop Recognition", bootstyle=DANGER)
        
        command = [
            sys.executable, "-u", "face_recognition_cli.py",
            "--known", self.known_image_dir,
            "--input", self.input_images_path,
            "--output", self.output_image_path,
            "--tolerance", str(self.tolerance_slider.get())
        ]
        
        if self.delete_after_copy.get():
            command.append("--delete-after-copy")

        # Run in a separate thread to prevent UI freeze
        thread = threading.Thread(target=self.process_recognition, args=(command,))
        thread.daemon = True
        thread.start()

    def stop_face_recognition(self):
        if self.process:
            self.process.terminate()
            self.update_output("⚠️ Stop signal sent to the recognition process.")
            self.run_button.config(text="Start Recognition", bootstyle=SUCCESS)

    def process_recognition(self, command):
        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffering
                universal_newlines=True
            )

            # Read line-by-line to update GUI in real-time
            for line in iter(self.process.stdout.readline, ""):
                self.update_output(line.strip())

            self.process.stdout.close()
            self.process.wait()

            if self.process.returncode == 0:
                self.update_output("\n✅ Recognition completed successfully!")
            else:
                self.update_output("\n❌ Recognition failed!")

        except Exception as e:
            self.update_output(f"\n⚠️ Error: {str(e)}")
        finally:
            self.root.after(0, lambda: self.run_button.config(text="Start Recognition", bootstyle=SUCCESS))
            self.process = None

    def update_output(self, text):
        self.root.after(0, lambda: self.output_text.insert(tk.END, text + "\n"))
        self.root.after(0, lambda: self.output_text.see(tk.END))

        
if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = ModernFaceRecognitionApp(root)
    root.mainloop()
