import tkinter as tk
from tkinter import scrolledtext

class TextGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-Based Game")

        # Text area for game output
        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, width=60, state='disabled')
        self.output_area.pack(padx=10, pady=10)

        # Input field
        self.input_field = tk.Entry(root, width=60)
        self.input_field.pack(padx=10, pady=(0, 10))
        self.input_field.bind("<Return>", self.process_input)

        # Game state
        self.running = True
        self.show_text("Welcome to the game! Type 'quit' to exit.")

    def show_text(self, text):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state='disabled')

    def process_input(self, event=None):
        user_input = self.input_field.get().strip()
        self.input_field.delete(0, tk.END)
        if not user_input:
            return
        self.show_text(f"> {user_input}")

        # Game logic
        if user_input.lower() == 'quit':
            self.show_text("Thanks for playing!")
            self.root.after(1000, self.root.quit)
        else:
            self.show_text(f"You typed: {user_input}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextGameGUI(root)
    root.mainloop()
