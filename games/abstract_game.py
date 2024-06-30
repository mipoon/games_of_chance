from abc import ABC, abstractmethod

class AbstractGame(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._tokens = 0
    
    def add_tokens(self, numberOfTokens):
        self._tokens += numberOfTokens

    @abstractmethod
    def _play_game(self):
        pass

    def play(self):
        self._play_game()
        return self._tokens

