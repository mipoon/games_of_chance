from sqlite3 import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from database.database import SessionLocal, init_db
from database.models import User
from player import Player

class Database():
    def __init__(self) -> None:
        init_db()


    def does_user_exist(self, username):
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.username == username).one()
            print(f"User {user.username} exists.")
            return True
        except NoResultFound:
            print(f"User {username} does not exist.")
            return False

    
    def get_user_data(self, username):
        session = SessionLocal()
        user_data = {}
        try:
            user = session.query(User).filter(User.username == username).one()
            user_data["tokens"] = user.tokens
            user_data["prizes"] = user.prizes
            return user_data
        except NoResultFound:
            print(f"No user found: {username}")


    def add_user_data(self, username):
        session = SessionLocal()
        user = User(username=username, tokens=30, prizes=[[], [], [], [], []])
        session.add(user)
        print(f"Adding new entry for user {username}")
        try:
            session.commit()
            print(f"User {username} saved!")
            return user
        except IntegrityError as e:
            # Rollback the session in case of an error
            session.rollback()
            print(f"Session rolled back. Error: {e}")
        session.close()


    def update_user_data(self, player:Player):
        session = SessionLocal()
        user = session.query(User).filter(User.username == player.name).one()
        user.tokens = player.tokens
        user.prizes = player.prizes
        session.commit()
        print("User data updated successfully.")
        session.close()



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
