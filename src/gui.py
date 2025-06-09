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
from random import choice

from .games.game_loader import GameLoader
from .player import Player
from .db import Database


class PlayerInfoDisplay:
    """Manages the player information display at the top of the GUI."""
    
    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame)
        self.frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.name_label = ttk.Label(self.frame, text="Player: Not logged in", font=("Arial", 12, "bold"))
        self.name_label.pack(side=tk.LEFT)
        
        self.tokens_label = ttk.Label(self.frame, text="Tokens: 0", font=("Arial", 12))
        self.tokens_label.pack(side=tk.LEFT, padx=(20, 0))
        
        self.prizes_label = ttk.Label(self.frame, text="Prizes: 0", font=("Arial", 12))
        self.prizes_label.pack(side=tk.LEFT, padx=(20, 0))
    
    def update(self, name, tokens, total_prizes):
        """Update the player information display."""
        self.name_label.config(text=f"Player: {name}")
        self.tokens_label.config(text=f"Tokens: {tokens}")
        self.prizes_label.config(text=f"Prizes: {total_prizes}")


class ConversationArea:
    """Manages the main conversation/output area of the GUI."""
    
    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.text_widget = scrolledtext.ScrolledText(
            self.frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 10)
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
    
    def add_text(self, text):
        """Add text to the conversation area."""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)


class InputControls:
    """Manages the input controls at the bottom of the GUI."""
    
    def __init__(self, parent_frame, send_callback, end_game_callback):
        self.frame = ttk.Frame(parent_frame)
        self.frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.entry = ttk.Entry(self.frame, font=("Arial", 10))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry.bind("<Return>", send_callback)
        
        self.send_button = ttk.Button(self.frame, text="Send", command=send_callback)
        self.send_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        self.end_game_button = ttk.Button(self.frame, text="End Game", command=end_game_callback)
        self.end_game_button.pack(side=tk.RIGHT)
        
        self.set_enabled(False)
    
    def set_enabled(self, enabled):
        """Enable or disable input controls."""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.entry.config(state=state)
        self.send_button.config(state=state)
        if enabled:
            self.entry.focus()
    
    def get_input(self):
        """Get and clear the input text."""
        text = self.entry.get()
        self.entry.delete(0, tk.END)
        return text


class GameIOHandler:
    """Handles input/output communication between GUI and game logic."""
    
    def __init__(self, input_queue, output_queue):
        self.input_queue = input_queue
        self.output_queue = output_queue
    
    def send_output(self, text):
        """Send text to GUI output."""
        self.output_queue.put(str(text) + "\n")
    
    def request_input(self, prompt):
        """Request input from GUI."""
        self.send_output(prompt)
        self.output_queue.put("WAITING_FOR_INPUT")
        
        # Wait for input
        while True:
            try:
                user_input = self.input_queue.get(timeout=0.1)
                self.output_queue.put("INPUT_RECEIVED")
                return user_input
            except queue.Empty:
                continue
    
    def update_player_info(self, player):
        """Send player info update to GUI."""
        total_prizes = sum(len(prize_list) for prize_list in player.prizes)
        info = f"{player.name}|{player.tokens}|{total_prizes}"
        self.output_queue.put(f"UPDATE_PLAYER_INFO:{info}")


class GameSession:
    """Manages the game session logic without GUI dependencies."""
    
    def __init__(self, io_handler):
        self.io = io_handler
        self.db = Database()
        self.player = Player()
    
    def run(self):
        """Run the complete game session."""
        try:
            self.setup_player()
            self.display_instructions()
            self.play_games()
            self.run_prize_booth()
            self.show_final_results()
            self.conclude()
        except Exception as e:
            self.io.send_output(f"Error: {str(e)}\n")
        finally:
            self.io.output_queue.put("GAME_ENDED")
    
    def setup_player(self):
        """Set up player data."""
        input_name = self.io.request_input("Please enter your name: ")
        player_exists = self.db.does_user_exist(input_name)
        
        if player_exists:
            player_data = self.db.get_user_data(input_name)
            self.player.name = input_name
            self.player.tokens = player_data.get("tokens")
            self.player.prizes = player_data.get("prizes")
            self.io.send_output(f"Welcome back, {self.player.name}! Let's play some more games!")
        else:
            self.db.add_user_data(input_name)
            self.player.name = input_name
            self.player.tokens = 30
            self.player.prizes = [[], [], [], [], []]
            self.io.send_output(f"Welcome, {self.player.name}! Let's play some games!")
        
        self.io.send_output(f"Set up complete. You, {self.player.name}, currently have {self.player.tokens} tokens, and your prize list is: {self.player.prizes}.")
        self.io.update_player_info(self.player)
    
    def display_instructions(self):
        """Display game instructions."""
        self.io.send_output("\nWelcome to Games of Chance with Prizes!")
        self.io.send_output("In this game, you'll play a series of mini-games to earn tokens, which you can then use to win prizes.")
        self.io.send_output("\nHere's how it works:")
        self.io.send_output("1. There will be three mini-games to earn tokens.")
        self.io.send_output("2. The mini-games include guessing a number, flipping a coin, and rolling dice, which will be randomly selected.")
        self.io.send_output("3. After earning tokens, you can spend them to try and win prizes of various rarities.")
        self.io.send_output("4. You'll also be given a choice to spend tokens to increase your chances of getting a rarer prize.")
        self.io.send_output("5. Prizes are categorized into common, odd, rare, epic, and legendary.")
        self.io.send_output("6. If you roll a prize that you already own, you might get some tokens back as a refund.")
        self.io.send_output("\nGood luck and have fun!\n")
    
    def play_games(self):
        """Play the mini-games."""
        for _ in range(3):
            game = GameWrapper(GameLoader.pick_random_game(), self.io)
            earned_tokens = game.play()
            self.player.tokens += earned_tokens
            self.io.update_player_info(self.player)
        
        sleep(1)
        self.io.send_output(f"You have {self.player.tokens} tokens\n")
    
    def run_prize_booth(self):
        """Run the prize booth interaction."""
        prize_booth = PrizeBooth(self.player, self.io)
        prize_booth.spend_tokens()
    
    def show_final_results(self):
        """Display final results."""
        self.io.send_output("-" * 50)
        self.io.send_output("\nPrizes earned:\n")
        
        categories = ["Common", "Odd", "Rare", "Epic", "Legendary"]
        for index, row in enumerate(self.player.prizes):
            self.io.send_output(f"{categories[index]} - {', '.join(row) if row else 'None'}")
        
        self.io.send_output("-" * 50)
    
    def conclude(self):
        """Conclude the session."""
        self.db.update_user_data(self.player)
        self.io.send_output("\nThanks for playing!\n")


class GameWrapper:
    """Wrapper for games to use GUI I/O."""
    
    def __init__(self, game, io_handler):
        self.game = game
        self.io = io_handler
    
    def _print_wrapper(self, *args, **kwargs):
        """Wrapper for print that handles multiple arguments."""
        text_parts = [str(arg) for arg in args]
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        text = sep.join(text_parts) + end
        self.io.send_output(text)
    
    def play(self):
        """Play the game with GUI I/O."""
        import builtins
        original_input = builtins.input
        original_print = builtins.print
        
        builtins.input = self.io.request_input
        builtins.print = self._print_wrapper
        
        try:
            return self.game.play()
        finally:
            builtins.input = original_input
            builtins.print = original_print


class PrizeBooth:
    """Prize booth for GUI version."""
    
    def __init__(self, player, io_handler):
        self.player = player
        self.io = io_handler
    
    def spend_tokens(self):
        """Main prize booth interaction."""
        while self.player.tokens >= 20:
            # Get rarity enhancement
            while True:
                try:
                    spend_tokens = int(self.io.request_input(
                        "\nEnter an amount of tokens\nEvery 3 tokens grants +1% chance of rolling your desired rarity: "
                    ))
                    if spend_tokens < 0:
                        self.io.send_output("You cannot spend a negative amount of tokens.")
                        continue
                    
                    user_rarity = self.io.request_input(
                        "'Common'\n'Odd'\n'Rare'\n'Epic'\n'Legendary'\n\nEnter your desired rarity, or 'None': "
                    ).lower()
                    
                    if user_rarity not in ["common", "odd", "rare", "epic", "legendary", "none"]:
                        self.io.send_output("\nYou must enter a valid rarity\n")
                    else:
                        rarity, extras = self._calculate_rarity(user_rarity, spend_tokens)
                        if (self.player.tokens - spend_tokens + extras) < 20:
                            self.io.send_output("You do not have enough tokens to continue playing")
                        else:
                            self.player.tokens -= spend_tokens
                            self.player.tokens += extras
                            break
                except ValueError:
                    self.io.send_output("\nERROR: Enter a valid numerical value:\n")
            
            # Roll for prize
            self.io.send_output("Rolling for prize...")
            sleep(1)
            prize = self._select_prize(rarity)
            self.player.tokens -= 20
            self.io.send_output(f"You won a {rarity} {prize}")
            
            # Handle duplicates
            refunded_tokens = self._handle_duplicate(prize, rarity)
            self.player.tokens += refunded_tokens
            if refunded_tokens == 0:
                self.player.add_prize(prize, rarity)
            
            self.io.send_output(f"\nYou have {self.player.tokens} tokens left.\n")
            self.io.update_player_info(self.player)
            
            # Continue playing?
            while True:
                user_play = self.io.request_input(
                    "Enter 'continue' to keep going, or 'exit' to finish playing: "
                ).lower()
                if user_play not in ("continue", "exit"):
                    self.io.send_output("Invalid response\n")
                else:
                    break
            if user_play == "exit":
                break
    
    def _calculate_rarity(self, user_rarity, tokens):
        """Calculate rarity based on tokens spent."""
        add_percent = tokens // 3
        extra = tokens % 3
        
        common, odd, rare, epic, legendary = 35, 60, 80, 95, 100
        roll_rarity = list(range(1, 101 + add_percent))
        
        # Adjust thresholds based on desired rarity
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
        
        self.io.send_output(f"Roll: {roll}")
        self.io.send_output(f"Rarity: {rarity}")
        return rarity, extra
    
    def _select_prize(self, rarity):
        """Select a prize from the specified rarity."""
        prize_pools = {
            "common": ["Cat", "Dog", "Gerbil", "Guinea Pig", "Hamster", "Mouse", "Pig", "Starfish"],
            "odd": ["Bird", "Chicken", "Fish", "Lizard", "Snake", "Spider", "Turkey"],
            "rare": ["Ferret", "Hedgehog", "Owl", "Shrimp", "Turtle"],
            "epic": ["Butterfly", "Crab", "Duck", "Frog"],
            "legendary": ["Crocodile", "Elephant", "Toad"]
        }
        
        if rarity not in prize_pools:
            raise ValueError(f"Invalid prize rarity: {rarity}")
        
        return choice(prize_pools[rarity])
    
    def _handle_duplicate(self, prize, rarity):
        """Handle duplicate prize refunds."""
        refund_rates = {
            "common": 3,
            "odd": 5,
            "rare": 7,
            "epic": 10,
            "legendary": 20
        }
        
        rarity_categories = ["common", "odd", "rare", "epic", "legendary"]
        rarity_index = rarity_categories.index(rarity)
        
        if prize in self.player.prizes[rarity_index]:
            refund_amount = refund_rates[rarity]
            self.io.send_output(f"You already own this prize, refunding {refund_amount} tokens")
            return refund_amount
        
        return 0


class GameGUI:
    """Main GUI application class."""
    
    def __init__(self, root, auto_start=True):
        self.root = root
        self.root.title("Games of Chance with Prizes")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Communication queues
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        
        # Game state
        self.game_thread = None
        self.game_running = False
        self.waiting_for_input = False
        
        # Set up UI components
        self.player_info = PlayerInfoDisplay(self.root)
        self.conversation = ConversationArea(self.root)
        self.input_controls = InputControls(self.root, self.send_input, self.end_game)
        
        if auto_start:
            self.start_game()
    
    def start_game(self):
        """Start the game in a separate thread."""
        if not self.game_running:
            self.game_running = True
            io_handler = GameIOHandler(self.input_queue, self.output_queue)
            game_session = GameSession(io_handler)
            self.game_thread = threading.Thread(target=game_session.run, daemon=True)
            self.game_thread.start()
            self.check_output_queue()
    
    def check_output_queue(self):
        """Check for output from the game thread."""
        try:
            while True:
                message = self.output_queue.get_nowait()
                if message == "GAME_ENDED":
                    self.game_running = False
                    self.conversation.add_text("Game ended. You can close the window.\n")
                    return
                elif message == "WAITING_FOR_INPUT":
                    self.waiting_for_input = True
                    self.input_controls.set_enabled(True)
                elif message == "INPUT_RECEIVED":
                    self.waiting_for_input = False
                    self.input_controls.set_enabled(False)
                elif message.startswith("UPDATE_PLAYER_INFO:"):
                    self._update_player_info(message[19:])
                else:
                    self.conversation.add_text(message)
        except queue.Empty:
            pass
        
        if self.game_running:
            self.root.after(100, self.check_output_queue)
    
    def _update_player_info(self, info):
        """Update player information display."""
        parts = info.split("|")
        if len(parts) >= 3:
            name, tokens, total_prizes = parts[0], parts[1], parts[2]
            self.player_info.update(name, tokens, total_prizes)
    
    def send_input(self, _event=None):
        """Send user input to the game."""
        if self.waiting_for_input:
            user_input = self.input_controls.get_input()
            self.input_queue.put(user_input)
            self.conversation.add_text(f"> {user_input}\n")
    
    def end_game(self):
        """End the game and close the window."""
        if self.game_running:
            self.input_queue.put("exit")
            self.game_running = False
        self.on_closing()
    
    def on_closing(self):
        """Handle window closing."""
        if self.game_running:
            self.game_running = False
        self.root.quit()
        self.root.destroy()


def run_gui():
    """Run the GUI version of the game."""
    root = tk.Tk()
    GameGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
