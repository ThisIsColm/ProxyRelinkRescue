import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import threading
from tkinter import ttk
from tkinter import messagebox


root = tk.Tk()
root.title("PROXY RELINK RESCUE v0.1")
root.geometry("570x480")  # Set the initial window size

output_dir = ""  # Define output_dir as a global variable

def select_input_directory():
    input_dir = filedialog.askdirectory()
    input_dir_entry.delete(0, tk.END)
    input_dir_entry.insert(0, input_dir)

def select_output_directory():
    global output_dir  # Use the global variable
    output_dir = filedialog.askdirectory()
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, output_dir)

def add_blank_audio_channels():
    input_dir = input_dir_entry.get()
    output_dir = output_dir_entry.get()
    num_channels = num_channels_var.get()

    if not input_dir or not output_dir or not num_channels:
        messagebox.showwarning("Input Error", "Please provide values for all required fields.")
        return

    def process_files():
        global output_dir  # Use the global variable

        try:
            os.makedirs(output_dir, exist_ok=True)

            eligible_files = [file for file in os.listdir(input_dir) if file.lower().endswith((".mov", ".mp4"))]
            total_files = len(eligible_files)
            processed_files = 0

            if len(os.listdir(output_dir)) > 0:
                confirm = messagebox.askokcancel("Files Exist",
                                                 "Output directory is not empty. It's recommended to use an empty folder.")
                if not confirm:
                    add_button.config(state=tk.NORMAL)
                    cancel_button.config(state=tk.DISABLED)
                    return  # Return here to stop processing
                else:
                    output_dir = filedialog.askdirectory()
                    output_dir_entry.delete(0, tk.END)
                    output_dir_entry.insert(0, output_dir)

            for file in eligible_files:
                if cancel_processing:
                    progress_bar["value"] = 0
                    break

                input_file = os.path.join(input_dir, file)
                output_file = os.path.join(output_dir, file)

                ffmpeg_command = [
                    "ffmpeg",
                    "-i", input_file,
                    "-c:v", "copy",
                    "-filter_complex", f"[0:a]pan={num_channels}c|"
                                       + "|".join([f"c{i}=c{i}" for i in range(num_channels)])
                                       + "[aout]",
                    "-map", "0:v",
                    "-map", "[aout]",
                    "-c:a", "aac",
                    "-strict", "experimental",
                    output_file
                ]

                process = subprocess.Popen(ffmpeg_command, stderr=subprocess.PIPE, text=True)

                while True:
                    line = process.stderr.readline()
                    if not line:
                        break
                    text_widget.insert(tk.END, line)  # Display FFmpeg output in the text window
                    text_widget.see("end")  # Scroll to the end

                process.communicate()
                processed_files += 1

                # Update the label with the current progress
                result_label.config(text=f"Processed {processed_files}/{total_files} files")
                progress_bar["value"] = (processed_files / total_files) * 100
                root.update_idletasks()

            if not cancel_processing:
                result_label.config(
                    text=f"Added {num_channels} blank audio channels to {processed_files} files in {input_dir}.")
            else:
                result_label.config(text="Processing cancelled.")
        except Exception as e:
            result_label.config(text=f"Error: {str(e)}")

    global cancel_processing
    cancel_processing = False

    # Create a new thread for processing
    processing_thread = threading.Thread(target=process_files)
    processing_thread.start()
    add_button.config(state=tk.DISABLED)
    cancel_button.config(state=tk.NORMAL)

def cancel_process():
    global cancel_processing
    cancel_processing = True
    add_button.config(state=tk.NORMAL)
    cancel_button.config(state=tk.DISABLED)




# Make the window non-resizable
root.resizable(False, False)

style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", foreground="black")  # Dark text color
style.configure("TEntry", padding=6, relief="flat")
style.configure("TLabel", padding=6, background="#E0E0E0")
style.configure("TProgressbar", thickness=10)

frame = ttk.Frame(root)
frame.pack(padx=20, pady=20)

result_label = ttk.Label(frame, text="Ready to fix proxies")
result_label.grid(row=8, column=0, pady=10, padx=10, sticky="w")

input_dir_label = ttk.Label(frame, text="Input Directory:")
input_dir_label.grid(row=0, column=0, sticky="w")
input_dir_entry = ttk.Entry(frame)
input_dir_entry.grid(row=0, column=1, padx=10, sticky="ew")
input_dir_button = ttk.Button(frame, text="Select Input Directory", command=select_input_directory)
input_dir_button.grid(row=0, column=2)

output_dir_label = ttk.Label(frame, text="Output Directory:")
output_dir_label.grid(row=1, column=0, sticky="w")
output_dir_entry = ttk.Entry(frame)
output_dir_entry.grid(row=1, column=1, padx=10, sticky="ew")
output_dir_button = ttk.Button(frame, text="Select Output Directory", command=select_output_directory)
output_dir_button.grid(row=1, column=2)

num_channels_label = ttk.Label(frame, text="Number of Audio Channels:")
num_channels_label.grid(row=2, column=0, sticky="w")

# Dropdown for the number of audio channels
num_channels_var = tk.IntVar()
num_channels_var.set(8)  # Default selection
num_channels_dropdown = ttk.Combobox(frame, textvariable=num_channels_var, values=list(range(1, 9)))
num_channels_dropdown.grid(row=2, column=1, padx=10, sticky="ew")

add_button = ttk.Button(frame, text="Fix My Proxies", command=add_blank_audio_channels)
add_button.grid(row=3, column=1, pady=10)

cancel_button = ttk.Button(frame, text="Cancel", command=cancel_process, state=tk.DISABLED)
cancel_button.grid(row=8, column=1, pady=10)

progress_bar = ttk.Progressbar(frame, mode='determinate')
progress_bar.grid(row=7, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

# Create a Text widget for displaying terminal-like messages
text_widget = tk.Text(frame, wrap=tk.WORD, height=10, width=60)
text_widget.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

# Insert your initial text here
text_widget.insert(tk.END, "Use this program to solve the issue of linking proxy files in Adobe Premiere Pro when your proxy files and full resolution media have mismatching audio channels. \n\n")
text_widget.insert(tk.END, "It does this by adding blank audio channels so Premiere Pro will recognize the files while relinking. \n\n")
text_widget.insert(tk.END, "Select the total number of audio channels you need (should match full-res media). \n")



# Add the "Created by Colm Moore, 2023" text to the bottom right-hand corner
created_by_label = ttk.Label(frame, text="Created by Colm Moore, 2023", font=("Helvetica", 8))
created_by_label.grid(row=8, column=2, pady=10, padx=10, sticky="se")

root.mainloop()

