class User():
    def __init__(self) -> None:
        self.username = "Test User"
        self.tokens = 0
        self.prizes = [[], [], [], [], []]

    def add_tokens(self, tokens):
        self.tokens += tokens

    def subtract_tokens(self, tokens):
        if tokens <= self.tokens:
            self.tokens -= tokens
            return True
        return False

    # Add prizes to user's prize list
    def add_prize(self, prize, rarity):
        """
        Add prize to user's list.

        Args:
            prize: (str) Prize to add
            rarity: (str) Rarity of the prize
        Returns: None
        """
        # Refactored by ChatGPT
        rarity_index = ['common', 'odd', 'rare',
                        'epic', 'legendary'].index(rarity)
        self.prizes[rarity_index].append(prize)
        self.prizes[rarity_index].sort()
