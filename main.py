import tkinter as tk
from tkinter import filedialog, messagebox
import os
import csv
from pygame import mixer

class AudioLabelingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Audio Labeling Tool")
        
        # Initialize pygame mixer
        mixer.init()

        # Variables
        self.audio_folder_path = tk.StringVar()
        self.current_audio_index = 0
        self.attributes = ["happy", "angry", "sad","relax"]  # Example attributes
        self.labels = []
        self.current_audio_file_name = tk.StringVar(value="No audio selected")

        # Audio Folder Input
        self.entry_audio_folder = tk.Entry(master, textvariable=self.audio_folder_path, width=50)
        self.entry_audio_folder.grid(row=0, column=0, padx=10, pady=10)
        self.button_browse = tk.Button(master, text="Browse", command=self.browse_folder)
        self.button_browse.grid(row=0, column=1, padx=10, pady=10)
        
        # Load CSV Button
        self.button_load_csv = tk.Button(master, text="Load CSV", command=self.load_csv)
        self.button_load_csv.grid(row=0, column=2, padx=10, pady=10)

        # Current Audio File Name Display
        self.label_current_audio = tk.Label(master, textvariable=self.current_audio_file_name)
        self.label_current_audio.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Control Buttons
        self.control_button_frame = tk.Frame(master)
        self.control_button_frame.grid(row=2,column=0,columnspan=3)
        self.button_prev = tk.Button(self.control_button_frame, text="previous", command=self.play_previous)
        self.button_prev.grid(row=2, column=0, padx=10, pady=10)
        self.button_play = tk.Button(self.control_button_frame, text="play", command=self.play_current)
        self.button_play.grid(row=2, column=1, padx=10, pady=10)
        self.button_next = tk.Button(self.control_button_frame, text="next", command=self.play_next)
        self.button_next.grid(row=2, column=2, padx=10, pady=10)

        # Label for Added Attributes Section
        self.label_added_attributes = tk.Label(master, text="selected:")
        self.label_added_attributes.grid(row=3, column=0, columnspan=3)

        # Frame for Added Attributes
        self.added_attributes_frame = tk.Frame(master)
        self.added_attributes_frame.grid(row=4, column=0, columnspan=3)

        # Attributes Section
        self.attributes_frame = tk.LabelFrame(master, text="Attributes", padx=10, pady=10)
        self.attributes_frame.grid(row=5, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        for i, attribute in enumerate(self.attributes):
            btn = tk.Button(self.attributes_frame, text=attribute, command=lambda attr=attribute: self.add_attribute(attr))
            btn.grid(row=0, column=i, padx=10, pady=10)

        # Save Button
        self.button_save = tk.Button(master, text="Save to CSV", command=self.save_labels)
        self.button_save.grid(row=6, column=2, padx=10, pady=10)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        self.audio_folder_path.set(folder_selected)
        self.load_audio_files()

    def load_audio_files(self):
        self.audio_files = [f for f in os.listdir(self.audio_folder_path.get()) if f.endswith('.wav')]
        self.current_audio_index = 0
        self.labels = [{} for _ in self.audio_files]
        self.update_ui_elements()

    def update_ui_elements(self):
        if self.audio_files:
            self.current_audio_file_name.set(self.audio_files[self.current_audio_index])
            self.update_added_attributes_frame()
        else:
            self.current_audio_file_name.set("No audio files found in the folder")

    def update_added_attributes_frame(self):
        # Clear existing attribute buttons
        for widget in self.added_attributes_frame.winfo_children():
            widget.destroy()

        # Create a button for each added attribute
        for attr in self.labels[self.current_audio_index].keys():
            btn = tk.Button(self.added_attributes_frame, text=attr, command=lambda attr=attr: self.remove_attribute(attr))
            btn.pack(side="left", padx=5)

    def play_audio(self, index):
        if 0 <= index < len(self.audio_files):
            mixer.music.load(os.path.join(self.audio_folder_path.get(), self.audio_files[index]))
            mixer.music.play()
            self.current_audio_index = index
            self.update_ui_elements()

    def play_previous(self):
        if self.current_audio_index > 0:
            self.play_audio(self.current_audio_index - 1)

    def play_current(self):
        self.play_audio(self.current_audio_index)

    def play_next(self):
        if self.current_audio_index < len(self.audio_files) - 1:
            self.play_audio(self.current_audio_index + 1)

    def add_attribute(self, attribute):
        current_file = self.audio_files[self.current_audio_index]
        if attribute not in self.labels[self.current_audio_index]:
            self.labels[self.current_audio_index][attribute] = True
            self.update_added_attributes_frame()

    def remove_attribute(self, attribute):
        if attribute in self.labels[self.current_audio_index]:
            del self.labels[self.current_audio_index][attribute]
            self.update_added_attributes_frame()

    def save_labels(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".csv")
        with open(save_path, mode="w", newline='') as file:
            writer = csv.writer(file)
            for file_name, attributes in zip(self.audio_files, self.labels):
                writer.writerow([file_name, '|'.join(attributes.keys())])
        messagebox.showinfo("Save Successful", "Labels have been saved successfully.")
        
    def load_csv(self):
        csv_file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not csv_file_path:
            return  # User cancelled the dialog
        
        try:
            with open(csv_file_path, mode="r", newline='') as file:
                reader = csv.reader(file)
                # Reset labels
                self.labels = [{} for _ in self.audio_files]
                for row in reader:
                    file_name, attributes_str = row
                    attributes = attributes_str.split('|')
                    # Find the index of the file_name in audio_files
                    if file_name in self.audio_files:
                        index = self.audio_files.index(file_name)
                        for attr in attributes:
                            if attr == "":
                                break
                            self.labels[index][attr] = True
                messagebox.showinfo("Load Successful", "CSV file has been loaded successfully.")
                self.update_ui_elements()
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load CSV file: {e}")

def main():
    root = tk.Tk()
    app = AudioLabelingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()