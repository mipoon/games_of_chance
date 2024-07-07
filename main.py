'''
Games of Chance with Prizes:
1. Password
2. Tokens
3. Rarities
4. Prizes
5. Re-rolls
6. 1 hour timer
'''
from play_session import PlaySession


# Password
# def password():
#     '''
#     Protected with the password 'Room2617'.
#     > 3 opportunities to correctly enter the password.
#     > Message displayed to program user for successful/unsuccessful attempt.
#     > Exit message displayed in the event of 3 incorrect password attempts.

#     Args: None
#     Returns: counter (int - number of failed attempts)
#     '''
#     secret_password = 'Room2617'
#     counter = 0

#     while counter < 3:    # 3 Tries
#         user_ipt = input("Password: ")
#         if user_ipt != secret_password:
#             print("Not correct\n")
#             counter += 1
#             if counter == 3:    # Failed 3 times
#                 print("You failed all 3 tries, please wait 1 hour\n")
#         else:
#             print("Correct\n")
#             break

#     return counter


if __name__ == "__main__":
    # Playing the game
    # if password() < 3:
    PlaySession().run_session()
