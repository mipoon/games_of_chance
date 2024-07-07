from abc import ABC, abstractmethod

class AbstractGame(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._tokens = 0

    def add_tokens(self, numberOfTokens):
        self._tokens += numberOfTokens

    @abstractmethod
    def _play_game(self):
       '''
       Implement this abstract method in a concrete class
       '''

    def play(self):
        earned_tokens = self._play_game()
        print("Tokens earned:", earned_tokens, "\n")
        self.add_tokens(earned_tokens)
        return self._tokens
