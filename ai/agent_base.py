class BaseAgent:
    def decide(self, game_state: dict) -> str:
        """
        Must return an action: 'jump' or 'wait'
        """
        raise NotImplementedError("Agent must implement decide()")