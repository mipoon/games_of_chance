"""
GUI Module

Provides a graphical user interface for the Games of Chance application
using tkinter. Supports threaded game execution with real-time updates.
"""

import queue
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from time import sleep

from .games.game_loader import GameLoader
from .play_session import PlaySession


class GameGUI:
    def __init__(self, root, auto_start=True):
        self.root = root
        self.root.title("Games of Chance with Prizes")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Game state
        self.play_session = None
        self.game_thread = None
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.waiting_for_input = False
        self.game_running = False

        self.setup_ui(auto_start)

    def setup_ui(self, auto_start=True):
        # Top section - Player info
        self.info_frame = ttk.Frame(self.root)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.name_label = ttk.Label(self.info_frame, text="Player: Not logged in", font=("Arial", 12, "bold"))
        self.name_label.pack(side=tk.LEFT)

        self.tokens_label = ttk.Label(self.info_frame, text="Tokens: 0", font=("Arial", 12))
        self.tokens_label.pack(side=tk.LEFT, padx=(20, 0))

        self.prizes_label = ttk.Label(self.info_frame, text="Prizes: 0", font=("Arial", 12))
        self.prizes_label.pack(side=tk.LEFT, padx=(20, 0))

        # Main conversation area
        self.conversation_frame = ttk.Frame(self.root)
        self.conversation_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.conversation_text = scrolledtext.ScrolledText(
            self.conversation_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 10)
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)

        # Bottom section - Input and controls
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.input_entry = ttk.Entry(self.input_frame, font=("Arial", 10))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", self.send_input)

        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_input)
        self.send_button.pack(side=tk.RIGHT, padx=(0, 5))

        self.end_game_button = ttk.Button(self.input_frame, text="End Game", command=self.end_game)
        self.end_game_button.pack(side=tk.RIGHT)

        # Start the game only if auto_start is True
        if auto_start:
            self.start_game()

    def start_game(self):
        """Start the game in a separate thread"""
        if not self.game_running:
            self.game_running = True
            self.game_thread = threading.Thread(target=self.run_game_session, daemon=True)
            self.game_thread.start()
            self.check_output_queue()

    def run_game_session(self):
        """Run the game session with custom I/O handling"""
        try:
            self.play_session = GUIPlaySession(self.input_queue, self.output_queue)
            self.play_session.run_session()
        except Exception as e:
            self.output_queue.put(f"Error: {str(e)}\n")
        finally:
            self.output_queue.put("GAME_ENDED")

    def check_output_queue(self):
        """Check for output from the game thread"""
        try:
            while True:
                message = self.output_queue.get_nowait()
                if message == "GAME_ENDED":
                    self.game_running = False
                    self.add_to_conversation("Game ended. You can close the window.\n")
                    return
                elif message == "WAITING_FOR_INPUT":
                    self.waiting_for_input = True
                    self.input_entry.config(state=tk.NORMAL)
                    self.send_button.config(state=tk.NORMAL)
                    self.input_entry.focus()
                elif message == "INPUT_RECEIVED":
                    self.waiting_for_input = False
                    self.input_entry.config(state=tk.DISABLED)
                    self.send_button.config(state=tk.DISABLED)
                elif message.startswith("UPDATE_PLAYER_INFO:"):
                    self.update_player_info(message[19:])
                else:
                    self.add_to_conversation(message)
        except queue.Empty:
            pass

        if self.game_running:
            self.root.after(100, self.check_output_queue)

    def add_to_conversation(self, text):
        """Add text to the conversation area"""
        self.conversation_text.config(state=tk.NORMAL)
        self.conversation_text.insert(tk.END, text)
        self.conversation_text.see(tk.END)
        self.conversation_text.config(state=tk.DISABLED)

    def update_player_info(self, info):
        """Update player information display"""
        parts = info.split("|")
        if len(parts) >= 3:
            name, tokens, total_prizes = parts[0], parts[1], parts[2]
            self.name_label.config(text=f"Player: {name}")
            self.tokens_label.config(text=f"Tokens: {tokens}")
            self.prizes_label.config(text=f"Prizes: {total_prizes}")

    def send_input(self, event=None):
        """Send user input to the game"""
        if self.waiting_for_input:
            user_input = self.input_entry.get()
            self.input_entry.delete(0, tk.END)
            self.input_queue.put(user_input)
            self.add_to_conversation(f"> {user_input}\n")

    def end_game(self):
        """End the game and close the window"""
        if self.game_running:
            # Send a signal to end the game gracefully
            self.input_queue.put("exit")
            self.game_running = False
        self.on_closing()

    def on_closing(self):
        """Handle window closing"""
        if self.game_running:
            self.game_running = False
        self.root.quit()
        self.root.destroy()


class GUIPlaySession(PlaySession):
    """Modified PlaySession that works with GUI I/O"""

    def __init__(self, input_queue, output_queue):
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue

    def gui_print(self, text):
        """Send text to GUI"""
        self.output_queue.put(str(text) + "\n")

    def gui_input(self, prompt):
        """Get input from GUI"""
        self.gui_print(prompt)
        self.output_queue.put("WAITING_FOR_INPUT")

        # Wait for input
        while True:
            try:
                user_input = self.input_queue.get(timeout=0.1)
                self.output_queue.put("INPUT_RECEIVED")
                return user_input
            except queue.Empty:
                continue

    def update_player_display(self):
        """Update the player info display"""
        total_prizes = sum(len(prize_list) for prize_list in self.player.prizes)
        info = f"{self.player.name}|{self.player.tokens}|{total_prizes}"
        self.output_queue.put(f"UPDATE_PLAYER_INFO:{info}")

    def display_instructions(self):
        """Display game instructions using GUI output"""
        self.gui_print("\nWelcome to Games of Chance with Prizes!")
        self.gui_print("In this game, you'll play a series of mini-games to earn tokens, which you can then use to win prizes.")
        self.gui_print("\nHere's how it works:")
        self.gui_print("1. There will be three mini-games to earn tokens.")
        self.gui_print("2. The mini-games include guessing a number, flipping a coin, and rolling dice, which will be randomly selected.")
        self.gui_print("3. After earning tokens, you can spend them to try and win prizes of various rarities.")
        self.gui_print("4. You'll also be given a choice to spend tokens to increase your chances of getting a rarer prize.")
        self.gui_print("5. Prizes are categorized into common, odd, rare, epic, and legendary.")
        self.gui_print("6. If you roll a prize that you already own, you might get some tokens back as a refund.")
        self.gui_print("\nGood luck and have fun!\n")

    def setup_player(self):
        """Setup player using GUI input"""
        input_name = self.gui_input("Please enter your name: ")
        player_exists = self.db.does_user_exist(input_name)
        if player_exists:
            player_data = self.db.get_user_data(input_name)
            self.player.name = input_name
            self.player.tokens = player_data.get("tokens")
            self.player.prizes = player_data.get("prizes")
            self.gui_print(f"Welcome back, {self.player.name}! Let's play some more games!")
        else:
            self.db.add_user_data(input_name)
            self.player.name = input_name
            self.player.tokens = 30
            self.player.prizes = [[], [], [], [], []]
            self.gui_print(f"Welcome, {self.player.name}! Let's play some games!")

        self.gui_print(f"Set up complete. You, {self.player.name}, currently have {self.player.tokens} tokens, and your prize list is: {self.player.prizes}.")
        self.update_player_display()

    def play_games(self):
        """Play games using GUI I/O"""
        for _ in range(3):
            game = GUIGameWrapper(GameLoader.pick_random_game(), self.gui_input, self.gui_print)
            earned_tokens = game.play()
            self.player.tokens += earned_tokens
            self.update_player_display()

        sleep(1)  # Reduced sleep time for GUI
        self.gui_print(f"You have {self.player.tokens} tokens\n")

    def prize_booth_interaction(self):
        """Handle prize booth with GUI"""
        gui_prize_booth = GUIPrizeBooth(self.player, self.gui_input, self.gui_print, self.update_player_display)
        gui_prize_booth.spend_tokens()

    def run_session(self):
        """Override run_session to use GUI prize booth"""
        self.setup_player()
        self.display_instructions()
        self.play_games()
        self.prize_booth_interaction()
        self.final_results()
        self.conclude()

    def final_results(self):
        """Display final results using GUI output"""
        self.gui_print("-" * 50)
        self.gui_print("\nPrizes earned:\n")

        categories = ["Common", "Odd", "Rare", "Epic", "Legendary"]
        for index, row in enumerate(self.player.prizes):
            self.gui_print(f"{categories[index]} - {', '.join(row) if row else 'None'}")

        self.gui_print("-" * 50)

    def conclude(self):
        """Conclude the play session"""
        self.db.update_user_data(self.player)
        self.gui_print("\nThanks for playing!\n")


class GUIGameWrapper:
    """Wrapper for games to use GUI I/O"""

    def __init__(self, game, input_func, output_func):
        self.game = game
        self.gui_input = input_func
        self.gui_print = output_func

    def gui_print_wrapper(self, *args, **kwargs):
        """Wrapper for print that handles multiple arguments"""
        # Convert all arguments to strings and join them
        text_parts = []
        for arg in args:
            text_parts.append(str(arg))

        # Handle separator and end parameters
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')

        # Join the parts with separator and add end
        text = sep.join(text_parts) + end
        self.gui_print(text)

    def play(self):
        """Play the game with GUI I/O"""
        # Monkey patch the game's input/output
        import builtins
        original_input = builtins.input
        original_print = builtins.print

        builtins.input = self.gui_input
        builtins.print = self.gui_print_wrapper

        try:
            result = self.game.play()
            return result
        finally:
            # Restore original functions
            builtins.input = original_input
            builtins.print = original_print


class GUIPrizeBooth:
    """GUI version of PrizeBooth"""

    def __init__(self, player, input_func, output_func, update_display_func):
        self.user = player
        self.gui_input = input_func
        self.gui_print = output_func
        self.update_display = update_display_func

    def spend_tokens(self):
        """Spend tokens on prizes using GUI"""
        while self.user.tokens >= 20:
            # Spend for rarity
            while True:
                try:
                    spend_tokens = int(self.gui_input(
                        "\nEnter an amount of tokens\nEvery 3 tokens grants +1% chance of rolling your desired rarity: "
                    ))
                    if spend_tokens < 0:
                        self.gui_print("You cannot spend a negative amount of tokens.")
                        continue

                    user_rarity = self.gui_input(
                        "'Common'\n'Odd'\n'Rare'\n'Epic'\n'Legendary'\n\nEnter your desired rarity, or 'None': "
                    ).lower()

                    if user_rarity not in ["common", "odd", "rare", "epic", "legendary", "none"]:
                        self.gui_print("\nYou must enter a valid rarity\n")
                    else:
                        rarity, extras = self.spend_for_rarity(user_rarity, spend_tokens)
                        if (self.user.tokens - spend_tokens + extras) < 20:
                            self.gui_print("You do not have enough tokens to continue playing")
                        else:
                            self.user.tokens -= spend_tokens
                            self.user.tokens += extras
                            break
                except ValueError:
                    self.gui_print("\nERROR: Enter a valid numerical value:\n")

            # Spending for prizes
            self.gui_print("Rolling for prize...")
            sleep(1)  # Reduced sleep for GUI
            prize = self.select_prize(rarity)
            self.user.tokens -= 20
            self.gui_print(f"You won a {rarity} {prize}")

            refunded_tokens = self.refund_rerolls(prize, rarity)
            self.user.tokens += refunded_tokens
            if refunded_tokens == 0:
                self.user.add_prize(prize, rarity)

            self.gui_print(f"\nYou have {self.user.tokens} tokens left.\n")
            self.update_display()

            # Want to keep playing?
            while True:
                user_play = self.gui_input(
                    "Enter 'continue' to keep going, or 'exit' to finish playing: "
                ).lower()
                if user_play not in ("continue", "exit"):
                    self.gui_print("Invalid response\n")
                else:
                    break
            if user_play == "exit":
                break

    def spend_for_rarity(self, user_rarity, tokens):
        """Same logic as original PrizeBooth"""
        from random import choice

        add_percent = tokens // 3
        extra = tokens % 3

        common, odd, rare, epic, legendary = 35, 60, 80, 95, 100
        roll_rarity = list(range(1, 101 + add_percent))

        if user_rarity == "common":
            common += add_percent
            odd += add_percent
            rare += add_percent
            epic += add_percent
            legendary += add_percent
        elif user_rarity == "odd":
            odd += add_percent
            rare += add_percent
            epic += add_percent
            legendary += add_percent
        elif user_rarity == "rare":
            rare += add_percent
            epic += add_percent
            legendary += add_percent
        elif user_rarity == "epic":
            epic += add_percent
            legendary += add_percent
        elif user_rarity == "legendary":
            legendary += add_percent

        roll = choice(roll_rarity)

        if roll <= common:
            rarity = "common"
        elif roll <= odd:
            rarity = "odd"
        elif roll <= rare:
            rarity = "rare"
        elif roll <= epic:
            rarity = "epic"
        else:
            rarity = "legendary"

        self.gui_print(f"Roll: {roll}")
        self.gui_print(f"Rarity: {rarity}")
        return rarity, extra

    def select_prize(self, rarity):
        """Same logic as original PrizeBooth"""
        from random import choice

        common = ["Cat", "Dog", "Gerbil", "Guinea Pig", "Hamster", "Mouse", "Pig", "Starfish"]
        odd = ["Bird", "Chicken", "Fish", "Lizard", "Snake", "Spider", "Turkey"]
        rare = ["Ferret", "Hedgehog", "Owl", "Shrimp", "Turtle"]
        epic = ["Butterfly", "Crab", "Duck", "Frog"]
        legendary = ["Crocodile", "Elephant", "Toad"]

        if rarity == "common":
            prize = choice(common)
        elif rarity == "odd":
            prize = choice(odd)
        elif rarity == "rare":
            prize = choice(rare)
        elif rarity == "epic":
            prize = choice(epic)
        elif rarity == "legendary":
            prize = choice(legendary)
        else:
            raise ValueError("Invalid prize rarity")

        return prize

    def refund_rerolls(self, prize, rarity):
        """Same logic as original PrizeBooth"""
        refund_amounts = [
            ["common", 3],
            ["odd", 5],
            ["rare", 7],
            ["epic", 10],
            ["legendary", 20],
        ]
        rarity_index = ["common", "odd", "rare", "epic", "legendary"].index(rarity)
        if prize in self.user.prizes[rarity_index]:
            self.gui_print(f"You already own this prize, refunding {refund_amounts[rarity_index][1]} tokens")
            return refund_amounts[rarity_index][1]
        return 0


def run_gui():
    """Run the GUI version of the game"""
    root = tk.Tk()
    GameGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
