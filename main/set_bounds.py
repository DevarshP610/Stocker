import tkinter as tk
import json

class RegionSelector:
    def __init__(self):
        self.root = tk.Tk()
        # Make the window semi-transparent and fullscreen
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-fullscreen', True)
        self.root.config(cursor="cross")

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black")
        self.canvas.pack(fill="both", expand=True)

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # FIXED: Initialized to 0 to satisfy Pylance type-checking
        self.rect = None
        self.start_x = 0
        self.start_y = 0

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=3)

    def on_drag(self, event):
        # FIXED: Safety check so Pylance knows rect is valid
        if self.rect is not None:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        end_x, end_y = event.x, event.y
        
        # Calculate standard region format: (X, Y, Width, Height)
        x = min(self.start_x, end_x)
        y = min(self.start_y, end_y)
        width = abs(self.start_x - end_x)
        height = abs(self.start_y - end_y)

        # Save to a config file
        bounds = {"region": [x, y, width, height]}
        with open("config.json", "w") as f:
            json.dump(bounds, f)

        print(f"\n[SUCCESS] Chart region saved to config.json: {bounds['region']}")
        self.root.destroy()

if __name__ == "__main__":
    print("Screen dimmed. Click and drag a box tightly around your trading chart...")
    app = RegionSelector()
    app.root.mainloop()