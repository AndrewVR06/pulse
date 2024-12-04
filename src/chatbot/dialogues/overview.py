from textwrap import dedent

from chatbot.dialogues.base_dialogue import BaseDialogue


class Overview(BaseDialogue):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    async def get_response(self) -> str:
        content = f"""
        Welcome to the overview!
        """

        return dedent(content)
