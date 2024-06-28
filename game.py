'''
Games of Chance with Prizes:
1. Password
2. Tokens
3. Rarities
4. Prizes
5. Re-rolls
6. 1 hour timer
'''
# Put cursor at the bottom of the page before running the code

from IPython.display import clear_output
from random import choice, randint
from time import sleep

# Password
def password():
    '''
    Protected with the password ‘Room2617’.
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

# Money Games
# 1. Guess the number
def guess_the_number(guess):
    '''
    Guess the number game.

    Args: (int) User's guessed number between 1 and 10
    Returns: (int) Tokens earned
    '''
    base_tokens = 15
    num = randint(1, 10)
    multiplier = abs(num - guess)
    earned_tokens = base_tokens * multiplier

    if multiplier == 0:
        print("Tokens earned:", base_tokens, "\n")
        return base_tokens
    else:
        print("Tokens earned:", earned_tokens, "\n")
        return earned_tokens

# 2. Flip a coin
def flip_a_coin(guess):
    '''
    Flip a coin game.

    Args: (str) User's guess "heads" or "tails"
    Returns: (int) Tokens earned
    '''
    base_tokens = 10
    coin = ["heads", "tails"]
    flip = choice(coin)

    if guess == flip:
        earned_tokens = base_tokens * 10
    else:
        earned_tokens = base_tokens * 2

    print("Tokens earned from this game:", earned_tokens, "\n")
    return earned_tokens

# 3. Roll the dice
def roll_the_dice():
    '''
    Roll the dice game.

    Args: None
    Returns: (int) Tokens earned
    '''
    base_tokens = 15
    roll1 = randint(1, 6)
    roll2 = randint(1, 6)

    print("Rolling...\n")
    sleep(3)

    multip = roll1 + roll2
    earned_tokens = base_tokens * multip
    print("You rolled a", multip)
    print("Tokens earned from this game:", earned_tokens, "\n")
    return earned_tokens

# 1. Randomly select game
def select_game():
    '''
    Randomly select game to play from a list.

    Args: None
    Returns: (int) Game number to play
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

    if (roll <= common):
        rarity = 'common'
    elif (roll <= odd):
        rarity = 'odd'
    elif (roll <= rare):
        rarity = 'rare'
    elif (roll <= epic):
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
    common = ["Cat", "Dog", "Gerbil", "Guinea Pig", "Hamster", "Mouse", "Pig", "Starfish"]

    odd = ["Bird", "Chicken", "Fish", "Lizard", "Snake", "Spider", "Turkey"]

    rare = ["Ferret", "Hedgehog", "Owl", "Shrimp", "Turtle"]

    epic = ["Butterfly", "Crab", "Duck", "Frog"]

    legendary = ["Crocodile", "Elephant", "Toad"]

    # Roll random prize
    if rarity == "common":
        prize = choice(common)
    if rarity == "odd":
        prize = choice(odd)
    if rarity == "rare":
        prize = choice(rare)
    if rarity == "epic":
        prize = choice(epic)
    if rarity == "legendary":
        prize = choice(legendary)

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
    refund_amounts = [['common', 3], ['odd', 5], ['rare', 7], ['epic', 10], ['legendary', 20]]
    rarity_index = ['common', 'odd', 'rare', 'epic', 'legendary'].index(rarity)
    if prize in user_list[rarity_index]:
        print("You already own this prize, refunding %s tokens" % refund_amounts[rarity_index][1])
        return refund_amounts[rarity_index][1]
    return 0

# Main program (run the program)
def game():
    '''
    Main function to run the game

    Args: none
    Returns: none
    '''
    global user_list
    global user_tokens
    # Money Games
    for num in range(3):
        game = select_game()
        # Guess the Number
        if game == 1:
            while True:
                try:
                    user_guess = int(input("Guess the number 1 - 10\nThe FARTHER you are, the more tokens you'll earn!: "))
                    if user_guess >= 1 and user_guess <= 10:
                        break
                    else:
                        print("Plase enter a number 1 - 10")
                except ValueError:
                    print("Please enter a numerical value\n")
            user_tokens += guess_the_number(user_guess)
        # Flip a Coin
        elif game == 2:
            while True:
                user_guess = input(("Guess 'heads' or 'tails'\nIf you're correct, you'll gain a lot of tokens!: ")).lower()
                if user_guess in ['heads', 'tails']:
                    break
                else:
                    print("Please enter 'heads' or 'tails'\n")
            user_tokens += flip_a_coin(user_guess)
        # Roll the dice
        else:
            print("You don't have to do anything here, just hope you have good luck!")
            user_tokens += roll_the_dice()

    sleep(3)
    clear_output()
    print("You have", user_tokens, "tokens\n")

    while user_tokens >= 20:
        # Spend for rarity
        while True:
            try:
                # Enter tokens
                spend_tokens = int(input("\nEnter an amount of tokens\nEvery 3 tokens grants +1% chance of rolling your desired rarity: "))
                if spend_tokens < 0:
                    print("You cannot spend a negative amount of tokens.")
                    continue
                # Enter desired rarity
                user_rarity = input("'Common'\n'Odd'\n'Rare'\n'Epic'\n'Legendary'\n\nEnter your desired rarity, or 'None': ").lower()
                if user_rarity not in ['common', 'odd', 'rare', 'epic', 'legendary', 'none']:
                    print("\nYou must enter a valid rarity\n")
                # If the user enters too many tokens
                else:
                    rarity, extras = spend_for_rarity(user_rarity, spend_tokens)
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
            user_play = input("Enter 'continue' to keep going, or 'exit' to finish playing: ").lower()
            if user_play != 'continue' and user_play != 'exit':
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
        print("%s -" % categories[index], end = "  ")
        for col in row:
            print("%s" % col, end = ", ")

        print("\n")
        index += 1
    print(50 * "-")

# Playing the game
if password() < 3:
    user_list = [[], [], [], [], []]
    user_tokens = 0
    instructions()
    game()
    print("\nThanks for playing!\n")

sleep(10)
