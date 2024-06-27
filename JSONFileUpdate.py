import io
import json
import base64
import os
import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
from PIL import Image, ImageTk
import threading

class App(tk.Tk):
    """
    The main application window for displaying and updating records in a JSON file.
    """
    def __init__(self):
        super().__init__()

        # Set window title, size, and initial data
        self.title("Database Update")
        self.geometry("1080x780")
        self.data = []
        self.current_record_index = None
        self.file_path = None

        # Create frames for record display, search, and navigation
        self.record_frame = tk.Frame(self)
        self.record_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.search_frame = tk.Frame(self)
        self.search_frame.pack(pady=10, fill=tk.X)
        self.search_label = tk.Label(self.search_frame, text="Identifier to find:")
        self.search_label.pack(side=tk.LEFT)
        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search_record)
        self.search_button.pack(side=tk.LEFT)

        self.navigation_frame = tk.Frame(self)
        self.navigation_frame.pack(pady=10, fill=tk.X)
        self.prev_button = tk.Button(self.navigation_frame, text="Show previous", command=self.show_previous_record)
        self.prev_button.pack(side=tk.LEFT)
        self.modify_button = tk.Button(self.navigation_frame, text="Modify", command=self.update_record)
        self.modify_button.pack(side=tk.LEFT)
        self.next_button = tk.Button(self.navigation_frame, text="Show next", command=self.show_next_record)
        self.next_button.pack(side=tk.LEFT)

        # Create a file menu with an "Open File" option
        self.file_menu = tk.Menu(self)
        self.config(menu=self.file_menu)
        self.file_menu.add_command(label="Open File", command=self.open_file)

        # Mappings of widgets in the record frame
        self.record_widgets = {}

        self.load_sample_file()

    def load_sample_file(self):
        # load the sample.json file
        # Use the path to the script and append the filename to get the path to the sample.json file
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample.json")
        if os.path.exists(file_path):
            try:
                # Load the data from the sample.json file
                with open(file_path, "r") as file:
                    self.data = json.load(file)
                self.file_path = file_path
                self.display_record(0)
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Invalid JSON file: {e}")

    def open_file(self):
        # If there is data in the app, save the current file
        if self.data:
            self.save_file_async()

        # Open a new file using filedialog
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            self.data = []  # Clear the current data
            self.current_record_index = None
            self.file_path = None

            try:
                # Load the data from the new file
                with open(file_path, "r") as file:
                    self.data = json.load(file)
                self.file_path = file_path
                self.display_record(0)
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Invalid JSON file: {e}")

    def search_record(self):
        # Search for a record based on the provided search term
        search_term = self.search_entry.get()
        for i, record in enumerate(self.data):
            if record.get("confirmed_identifier") == search_term:
                self.display_record(i)
                break
        else:
            for i, record in enumerate(self.data):
                if record.get("identifier") == search_term:
                    self.display_record(i)
                    break
            else:
                messagebox.showinfo("Not Found", "Record not found.")

    def display_record(self, index):
        # Undisplay the current record
        self.undisplay_record()

        # Display the selected record
        self.current_record_index = index
        record = self.data[index]

        # Create labels and entries for the record's identifier, confirmed identifier, results, and confirmed results
        # 'identifier_label' and 'identifier_value' display the identifier
        identifier_label = tk.Label(self.record_frame, text="Identifier:")
        identifier_label.grid(row=0, column=0, sticky=tk.W)
        identifier_value = tk.Label(self.record_frame, text=record["identifier"])
        identifier_value.grid(row=0, column=1, sticky=tk.W)

        # 'confirmed_identifier_label' and 'confirmed_identifier_entry' display or allow modification of the confirmed identifier
        confirmed_identifier_label = tk.Label(
            self.record_frame, text="Confirmed identifier:"
        )
        confirmed_identifier_label.grid(row=1, column=0, sticky=tk.W)
        self.confirmed_identifier_entry = tk.Entry(self.record_frame)
        self.confirmed_identifier_entry.grid(row=1, column=1, sticky=tk.EW)
        self.confirmed_identifier_entry.insert(
            0, record.get("confirmed_identifier", record["identifier"])
        )

        # Display the identifier image if it exists
        identifier_image_label = tk.Label(self.record_frame, text="Identifier image")
        identifier_image_label.grid(row=2, column=0, columnspan=2)

        identifier_image = record.get("identifier_image")
        if identifier_image:
            image = self.load_image_data(identifier_image)
            image_label = tk.Label(self.record_frame, image=image)
            image_label.image = image
            image_label.grid(row=3, column=0, columnspan=2, sticky=tk.W + tk.E)

        # Display the results and confirmed results
        results_label = tk.Label(self.record_frame, text="Results:")
        results_label.grid(row=4, column=0, sticky=tk.W)
        results_value = tk.Label(self.record_frame, text=str(record["results"]))
        results_value.grid(row=4, column=1, sticky=tk.W)

        confirmed_results_label = tk.Label(self.record_frame, text="Confirmed results:")
        confirmed_results_label.grid(row=5, column=0, sticky=tk.W)
        self.confirmed_results_entry = tk.Entry(self.record_frame)
        self.confirmed_results_entry.grid(row=5, column=1, sticky=tk.EW)
        self.confirmed_results_entry.insert(
            0,
            ", ".join(map(str, record.get("confirmed_results", record["results"]))),
        )

        # Display the result image if it exists
        result_image_label = tk.Label(self.record_frame, text="Results images")
        result_image_label.grid(row=6, column=0, columnspan=2)

        result_image = record.get("result_image")
        if result_image:
            image = self.load_image_data(result_image)
            image_label = tk.Label(self.record_frame, image=image)
            image_label.image = image
            image_label.grid(row=7, column=0, columnspan=2, sticky=tk.W + tk.E)

        # Configure column 1 to expand and fill the available space
        self.record_frame.grid_columnconfigure(1, weight=1)

        # Store the widgets in the record frame
        self.record_widgets = {
            "identifier_label": identifier_label,
            "identifier_value": identifier_value,
            "confirmed_identifier_label": confirmed_identifier_label,
            "confirmed_identifier_entry": self.confirmed_identifier_entry,
            "identifier_image_label": identifier_image_label,
            "identifier_image": image_label,
            "results_label": results_label,
            "results_value": results_value,
            "confirmed_results_label": confirmed_results_label,
            "confirmed_results_entry": self.confirmed_results_entry,
            "result_image_label": result_image_label,
            "result_image": image_label,
        }

    def undisplay_record(self):
        # Undisplay the current record
        for widget in self.record_frame.winfo_children():
            widget.destroy()

    def update_record(self):
        # Update the current record with the new confirmed identifier and confirmed results
        if self.current_record_index is not None:
            record = self.data[self.current_record_index]
            confirmed_identifier = self.confirmed_identifier_entry.get()
            try:
                confirmed_results = [int(x) for x in self.confirmed_results_entry.get().split(",")]
            except ValueError:
                messagebox.showerror("Error", "Invalid input for confirmed results.")
                return

            record["confirmed_identifier"] = confirmed_identifier
            record["confirmed_results"] = confirmed_results
            self.save_file_async()
            self.display_record(self.current_record_index)

    def show_previous_record(self):
        # Show the previous record in the data
        if self.current_record_index is not None and self.current_record_index > 0:
            self.display_record(self.current_record_index - 1)

    def show_next_record(self):
        # Show the next record in the data
        if self.current_record_index is not None and self.current_record_index < len(self.data) - 1:
            self.display_record(self.current_record_index + 1)

    def save_file_async(self):
        # Save the current data to the file asynchronously
        if self.file_path:
            def save_file_thread():
                with open(self.file_path, "w") as file:
                    json.dump(self.data, file, indent=4)

            threading.Thread(target=save_file_thread).start()

    def load_image_data(self, image_data):
        # Load the image data from a dictionary
        if isinstance(image_data, str):
            img = Image.open(image_data)
            photo = ImageTk.PhotoImage(img)
            self.record_frame.image = photo  # keep a reference to the image data
            return photo
        elif isinstance(image_data, dict):
            image_bytes = base64.b64decode(image_data['data'])
            img = Image.open(io.BytesIO(image_bytes))
            photo = ImageTk.PhotoImage(img)
            self.record_frame.image = photo  
            return photo
        else:
            print("Invalid image data")
            return None

if __name__ == "__main__":
    app = App()
    app.mainloop()