import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import font
import os
from pathlib import Path
import csv
from pygame import mixer

class AudioLabelingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Audio Labeling Tool")
        self.master.columnconfigure(0, weight=1)
        # Fontオブジェクトを作成
        self.custom_font = font.Font(family='Helvetica', size=12, weight='bold')
        
        # Initialize pygame mixer
        mixer.init()

        # Variables
        self.audio_folder_path = tk.StringVar()
        self.current_audio_index = 0
        self.main8_attributes = ["joy","anticipation","trust","surprise","sadness","anger","fear", "disgust"]
        self.positive_attributes = ["fun","understand","certainly","shall_we","encouraging","confidently","happiness"]
        self.negative_attributes = ["pain","flustered"]
        self.other_attributes = ["underestimate","question"]
        self.attributes = self.positive_attributes+self.negative_attributes+self.other_attributes  # Example attributes
        self.primary_label = []
        self.secondary_labels = []
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
        
        #index jump button
        self.index_frame = tk.Frame(master)
        self.index_frame.grid(row=2,column=0,columnspan=3)
        self.index_label = tk.Label(self.index_frame, text=f"current index:")
        self.index_label.grid(row=0,column=0,padx=10)
        self.index_strvar = tk.StringVar()
        self.index_strvar.set("0")
        self.index_entry = tk.Entry(self.index_frame, textvariable=self.index_strvar, width=4)
        self.index_entry.grid(row=0,column=1,padx=10)
        self.index_jump_button = tk.Button(self.index_frame,text="jump",command=self.index_seek)
        self.index_jump_button.grid(row=0,column=2,padx=10)
        
        # Control Buttons
        self.control_button_frame = tk.Frame(master)
        self.control_button_frame.grid(row=3,column=0,columnspan=3)
        self.button_prev = tk.Button(self.control_button_frame, text="previous", command=self.play_previous)
        self.button_prev.grid(row=2, column=0, padx=10, pady=10)
        self.button_play = tk.Button(self.control_button_frame, text="play", command=self.play_current)
        self.button_play.grid(row=2, column=1, padx=10, pady=10)
        self.button_next = tk.Button(self.control_button_frame, text="next", command=self.play_next)
        self.button_next.grid(row=2, column=2, padx=10, pady=10)
        

        # Label for Added Attributes Section
        self.label_added_attributes = tk.Label(master, text="Primary Attribute")
        self.label_added_attributes.grid(row=4, column=0, columnspan=3)

        # Frame for Added Attributes
        self.added_primary_attributes_frame = tk.Frame(master)
        self.added_primary_attributes_frame.grid(row=5, column=0, columnspan=3)
        
        # Label for Added Attributes Section
        self.label_added_attributes = tk.Label(master, text="Secondary Attributes")
        self.label_added_attributes.grid(row=6, column=0, columnspan=3)
        
        # Frame for Added Attributes
        self.added_secondary_attributes_frame = tk.Frame(master)
        self.added_secondary_attributes_frame.grid(row=7, column=0, columnspan=3)

        # Attributes Section
        self.attributes_frame = tk.LabelFrame(master, text="Attributes choices", padx=10, pady=10)
        self.attributes_frame.grid(row=8, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        self.attributes_frame.columnconfigure(0, weight=1)
        self.main8_frame = tk.LabelFrame(self.attributes_frame,text="main8",padx=10,pady=10)
        self.main8_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        for i, attribute in enumerate(self.main8_attributes):
            btn = tk.Button(self.main8_frame, text=attribute, command=lambda attr=attribute: self.add_attribute(attr))
            btn.grid(row=0, column=i, padx=10, pady=10)
        self.positive_frame = tk.LabelFrame(self.attributes_frame,text="positive",padx=10,pady=10)
        self.positive_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        for i, attribute in enumerate(self.positive_attributes):
            btn = tk.Button(self.positive_frame, text=attribute, command=lambda attr=attribute: self.add_attribute(attr))
            btn.grid(row=0, column=i, padx=10, pady=10)
        self.negative_frame = tk.LabelFrame(self.attributes_frame,text="negative",padx=10,pady=10)
        self.negative_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        for i, attribute in enumerate(self.negative_attributes):
            btn = tk.Button(self.negative_frame, text=attribute, command=lambda attr=attribute: self.add_attribute(attr))
            btn.grid(row=0, column=i, padx=10, pady=10)
        self.other_frame = tk.LabelFrame(self.attributes_frame,text="other",padx=10,pady=10)
        self.other_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        for i, attribute in enumerate(self.other_attributes):
            btn = tk.Button(self.other_frame, text=attribute, command=lambda attr=attribute: self.add_attribute(attr))
            btn.grid(row=0, column=i, padx=10, pady=10)

        # Save Button
        self.button_save = tk.Button(master, text="Save to CSV", command=self.save_labels)
        self.button_save.grid(row=9, column=2, padx=10, pady=10)
        
        
        self.apply_font_to_all_widgets(self.master,self.custom_font)

    def apply_font_to_all_widgets(self,parent, font):
        for widget in parent.winfo_children():
            if hasattr(widget, 'children'):
                self.apply_font_to_all_widgets(widget, font)
            try:
                widget.configure(font=font)
            except tk.TclError:
                pass  # ウィジェットがフォントプロパティをサポートしていない場合は無視
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        self.audio_folder_path.set(folder_selected)
        self.load_audio_files()

    def load_audio_files(self):
        self.audio_files = [f for f in os.listdir(self.audio_folder_path.get()) if f.endswith('.wav')]
        audio_folder_parent_path = Path(self.audio_folder_path.get()).parent
        self.current_audio_index = 0
        self.primary_label = [{"primary_att":None} for _ in self.audio_files]
        self.secondary_labels = [{} for _ in self.audio_files]
        
        self.update_ui_elements()
        self._load_csv((audio_folder_parent_path/"emotion_labels_utf8.csv"),error_msg=True)

    def update_ui_elements(self):
        if self.audio_files:
            self.current_audio_file_name.set(self.audio_files[self.current_audio_index])
            self.index_strvar.set(self.current_audio_index)
            self.update_added_attributes_frame()
        else:
            self.current_audio_file_name.set("No audio files found in the folder")

    # def update_added_attributes_frame(self):
    #     # Clear existing attribute buttons
    #     for widget in self.added_attributes_frame.winfo_children():
    #         widget.destroy()

    #     # Create a button for each added attribute
    #     for attr in self.labels[self.current_audio_index].keys():
    #         btn = tk.Button(self.added_attributes_frame, text=attr, command=lambda attr=attr: self.remove_attribute(attr))
    #         btn.pack(side="left", padx=5)

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

    def index_seek(self):
        index = int(self.index_entry.get())
        if index < len(self.audio_files) - 1:
            self.play_audio(index)
            
    def add_attribute(self, attribute):
        if self.primary_label[self.current_audio_index]["primary_att"] is None:
            # This is the first label clicked, make it the primary label
            if attribute not in self.secondary_labels[self.current_audio_index]:
                self.primary_label[self.current_audio_index]["primary_att"] = attribute
        else:
            # All other labels are considered secondary
            if attribute not in self.secondary_labels[self.current_audio_index]:
                if attribute != self.primary_label[self.current_audio_index]["primary_att"]:
                    self.secondary_labels[self.current_audio_index][attribute] = True
        self.update_added_attributes_frame()

    def remove_attribute(self, attribute):
        if attribute == self.primary_label[self.current_audio_index]["primary_att"]:
            # Removing the primary label
            self.primary_label[self.current_audio_index]["primary_att"] = None
        elif attribute in self.secondary_labels[self.current_audio_index]:
            # Remove from secondary labels
            del self.secondary_labels[self.current_audio_index][attribute]
        self.update_added_attributes_frame()

    def update_added_attributes_frame(self):
        # Clear existing attribute buttons
        for widget in self.added_primary_attributes_frame.winfo_children():
            widget.destroy()
        for widget in self.added_secondary_attributes_frame.winfo_children():
            widget.destroy()

        # Create a button for primary attribute if it exists
        if self.primary_label[self.current_audio_index]["primary_att"]:
            btn = tk.Button(self.added_primary_attributes_frame, text=self.primary_label[self.current_audio_index]["primary_att"],font=self.custom_font, command=lambda: self.remove_attribute(self.primary_label[self.current_audio_index]["primary_att"]))
            btn.pack(side="left", padx=5)

        # Create a button for each secondary attribute
        for attr in self.secondary_labels[self.current_audio_index]:
            btn = tk.Button(self.added_secondary_attributes_frame, text=attr,font=self.custom_font, command=lambda attr=attr: self.remove_attribute(attr))
            btn.pack(side="left", padx=5)


    def save_labels(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".csv",initialfile="emotion_labels_utf8.csv",initialdir=Path(self.audio_folder_path.get()).parent)
        with open(save_path, mode="w", newline='') as file:
            writer = csv.writer(file)
            for file_name, primary,secondary in zip(self.audio_files, self.primary_label,self.secondary_labels):
                writer.writerow([file_name,primary["primary_att"], '|'.join(secondary.keys())])
        messagebox.showinfo("Save Successful", "Labels have been saved successfully.")
        
    def load_csv(self):
        csv_file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not csv_file_path:
            return  # User cancelled the dialog
        self._load_csv(csv_file_path)
        
    def _load_csv(self,filepath,error_msg=True):
        print(filepath)
        try:
            with open(filepath, mode="r", newline='') as file:
                reader = csv.reader(file)
                # Reset labels
                self.labels = [{} for _ in self.audio_files]
                for row in reader:
                    file_name, primary, secondary_str = row
                    secondaries = secondary_str.split('|')
                    # Find the index of the file_name in audio_files
                    if file_name in self.audio_files:
                        index = self.audio_files.index(file_name)
                        if primary:
                            self.primary_label[index]["primary_att"] = primary
                            self.current_audio_index = index
                        for attr in secondaries:
                            if attr == "":
                                break
                            self.secondary_labels[index][attr] = True
                self.current_audio_index += 1
                messagebox.showinfo("Load Successful", "CSV file has been loaded successfully.")
                self.update_ui_elements()
        except Exception as e:
            if error_msg:
                messagebox.showerror("Load Error", f"Failed to load CSV file: {e}")
        

def main():
    root = tk.Tk()
    app = AudioLabelingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()