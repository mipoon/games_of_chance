'''
Games of Chance with Prizes:
1. Password
2. Tokens
3. Rarities
4. Prizes
5. Re-rolls
6. 1 hour timer
'''

from random import choice
from sqlite3 import IntegrityError
from time import sleep

from games import GameFactory
from database.database import SessionLocal, init_db
from database.models import User


def clear_output():
    '''
    Hacky way to simulate clearing the output screen

    Args: None
    Returns: None
    '''
    print("\n" * 100)

# Password


def password():
    '''
    Protected with the password 'Room2617'.
    > 3 opportunities to correctly enter the password.
    > Message displayed to program user for successful/unsuccessful attempt.
    > Exit message displayed in the event of 3 incorrect password attempts.

    Args: None
    Returns: counter (int - number of failed attempts)
    '''
    secret_password = 'Room2617'
    counter = 0

    while counter < 3:    # 3 Tries
        user_ipt = input("Password: ")
        if user_ipt != secret_password:
            print("Not correct\n")
            counter += 1
            if counter == 3:    # Failed 3 times
                print("You failed all 3 tries, please wait 1 hour\n")
        else:
            print("Correct\n")
            break

    return counter

# Instructions


def instructions():
    '''
    Display game instructions.

    Args: None
    Returns: None
    '''
    print("\nWelcome to Games of Chance with Prizes!")
    print("In this game, you'll play a series of mini-games to earn tokens, which you can then use to win prizes.")
    print("\nHere's how it works:")
    print("1. There will be three mini-games to earn tokens.")
    print("2. The mini-games include guessing a number, flipping a coin, and rolling dice, which will be randomly selected.")
    print("3. After earning tokens, you can spend them to try and win prizes of various rarities.")
    print("4. You'll also be given a choice to spend tokens to increase your chances of getting a rarer prize.")
    print("5. Prizes are categorized into common, odd, rare, epic, and legendary.")
    print("6. If you roll a prize that you already own, you might get some tokens back as a refund.")
    print("\nGood luck and have fun!")


# 1. Randomly select game
def select_game():
    '''
    Randomly select minigame to play from a list.

    Args: None
    Returns: (int) Minigame number to play
    '''
    return choice([1, 2, 3])

# Spend for rarity


def spend_for_rarity(user_rarity, tokens):
    '''
    Spend tokens for a chance to increase rarity.

    Args:
        user_rarity: (str) Desired rarity
        tokens: (int) Amount of tokens to spend
    Returns:
        tuple (str, int): Selected rarity and extra tokens back to the user
    '''
    add_percent = tokens // 3
    extra = tokens % 3

    # Base percentages: Refactored by ChatGPT
    common, odd, rare, epic, legendary = 35, 60, 80, 95, 100
    roll_rarity = list(range(1, 101 + add_percent))

    # Alter percentages
    if user_rarity == 'common':
        common += add_percent
        odd += add_percent
        rare += add_percent
        epic += add_percent
        legendary += add_percent
    elif user_rarity == 'odd':
        odd += add_percent
        rare += add_percent
        epic += add_percent
        legendary += add_percent
    elif user_rarity == 'rare':
        rare += add_percent
        epic += add_percent
        legendary += add_percent
    elif user_rarity == 'epic':
        epic += add_percent
        legendary += add_percent
    elif user_rarity == 'legendary':
        legendary += add_percent

    roll = choice(roll_rarity)

    if roll <= common:
        rarity = 'common'
    elif roll <= odd:
        rarity = 'odd'
    elif roll <= rare:
        rarity = 'rare'
    elif roll <= epic:
        rarity = 'epic'
    else:
        rarity = 'legendary'

    print(roll)
    print(rarity)
    print(roll_rarity)
    return rarity, extra

# Select prize


def select_prize(rarity):
    '''
    Args: rarity from spend_for_rarity

    Randomly select prize from rarity prize list selected

    Returns: selected prize
    '''
    # Prize Lists:
    common = ["Cat", "Dog", "Gerbil", "Guinea Pig",
              "Hamster", "Mouse", "Pig", "Starfish"]

    odd = ["Bird", "Chicken", "Fish", "Lizard", "Snake", "Spider", "Turkey"]

    rare = ["Ferret", "Hedgehog", "Owl", "Shrimp", "Turtle"]

    epic = ["Butterfly", "Crab", "Duck", "Frog"]

    legendary = ["Crocodile", "Elephant", "Toad"]

    # Roll random prize
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

# Add prizes to user's prize list


def append_prizes(user_list, prize, rarity):
    """
    Add prize to user's list.

    Args:
        user_list: (list) User's list of prizes
        prize: (str) Prize to add
        rarity: (str) Rarity of the prize
    Returns: None
    """
    # Refactored by ChatGPT
    rarity_index = ['common', 'odd', 'rare', 'epic', 'legendary'].index(rarity)
    user_list[rarity_index].append(prize)
    user_list[rarity_index].sort()

# Find rerolls


def refund_rerolls(user_list, prize, rarity):
    '''
    Refund tokens if prize is already owned.

    Args:
        user_list: (list) User's list of prizes
        prize: (str) Prize just earned
        rarity: (str) Rarity of prize
    Returns: (int) Refunded tokens
    '''
    # 'Inspired' by ChatGPT's work on append_prizes()
    refund_amounts = [['common', 3], ['odd', 5], [
        'rare', 7], ['epic', 10], ['legendary', 20]]
    rarity_index = ['common', 'odd', 'rare', 'epic', 'legendary'].index(rarity)
    if prize in user_list[rarity_index]:
        print(f"You already own this prize, refunding {
              refund_amounts[rarity_index][1]} tokens")
        return refund_amounts[rarity_index][1]
    return 0

# Main program (run the program)


def start():
    '''
    Main function to run the game

    Args: none
    Returns: none
    '''
    user_list = [[], [], [], [], []]
    user_tokens = 0
    # Money Games
    for _ in range(3):
        game = GameFactory.pick_random_game()
        earned_tokens = game.play()
        user_tokens += earned_tokens

    sleep(3)
    clear_output()
    print("You have", user_tokens, "tokens\n")

    while user_tokens >= 20:
        # Spend for rarity
        while True:
            try:
                # Enter tokens
                spend_tokens = int(input(
                    "\nEnter an amount of tokens\nEvery 3 tokens grants +1% chance of rolling your desired rarity: "))
                if spend_tokens < 0:
                    print("You cannot spend a negative amount of tokens.")
                    continue
                # Enter desired rarity
                user_rarity = input(
                    "'Common'\n'Odd'\n'Rare'\n'Epic'\n'Legendary'\n\nEnter your desired rarity, or 'None': ").lower()
                if user_rarity not in ['common', 'odd', 'rare', 'epic', 'legendary', 'none']:
                    print("\nYou must enter a valid rarity\n")
                # If the user enters too many tokens
                else:
                    rarity, extras = spend_for_rarity(
                        user_rarity, spend_tokens)
                    if (user_tokens - spend_tokens + extras) < 20:
                        print("You do not have enough tokens to continue playing")
                    else:
                        user_tokens -= spend_tokens
                        user_tokens += extras
                        break
            except ValueError:
                print("\nERROR: Enter a valid numerical value:\n")

        # Spending for prizes
        print("Rolling for prize...")
        sleep(2)
        prize = select_prize(rarity)
        user_tokens -= 20
        print("You won a", rarity, prize)

        refunded_tokens = refund_rerolls(user_list, prize, rarity)
        user_tokens += refunded_tokens
        if refunded_tokens == 0:
            append_prizes(user_list, prize, rarity)

        print("\nYou have", user_tokens, "tokens left.\n")

        # Want to keep playing?
        while True:
            user_play = input(
                "Enter 'continue' to keep going, or 'exit' to finish playing: ").lower()
            if user_play not in ('continue', 'exit'):
                print("Invalid response\n")
            else:
                break
        if user_play == 'exit':
            clear_output()
            break

    final_results(user_list)

# Print 'final results':


def final_results(user_list):
    '''
    Display final results.

    Args:
        user_list: (list) User's list of prizes
    Returns: None
    '''
    print(50 * "-")
    print("\nPrizes earned:\n")

    # ChatGPT helped fix the function, using an index counter in a loop
    index = 0
    categories = ['Common', 'Odd', 'Rare', 'Epic', 'Legendary']
    for row in user_list:
        print(f"{categories[index]} -", end="  ")
        for col in row:
            print(f"{col}", end=", ")

        print("\n")
        index += 1
    print(50 * "-")


def main():
    ''' Playing the game'''
    # if password() < 3:
    try:
        init_db()
        session = SessionLocal()
        user = User(username='Player1', tokens=30)
        session.add(user)
        print("Added new entry for Player1")
        session.commit()
        print("User saved!")
    except IntegrityError as e:
        # Rollback the session in case of an error
        session.rollback()
        print(f"Session rolled back. Error: {e}")
    finally:
        # Close the session
        session.close()

    instructions()
    start()
    print("\nThanks for playing!\n")

    sleep(10)


if __name__ == "__main__":
    main()
