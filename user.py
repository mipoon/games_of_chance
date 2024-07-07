class User():
    def __init__(self) -> None:
        self.username = "Test User"
        self.tokens = 0
        self.prizes = [[], [], [], [], []]

    def add_tokens(self, tokens):
        self.tokens += tokens

    def subtract_tokens(self, tokens):
        self.tokens -= tokens

    def add_prize(self, prize):
        self.prizes.append(prize)
