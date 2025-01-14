from chatbot.dialogues.base_dialogue import BaseDialogue
from chatbot.dialogues.overview import Overview

from textwrap import dedent

from chatbot.dialogues.pulsebot import PulseBot
from chatbot.dialogues.wrong_option import WrongOption


class MainMenu(BaseDialogue):

    async def get_response(self) -> str:
        content = f"""
        Hi {self._context.profile_name} and welcome to MetisAI!

        Here you can chat with our chatbot PulseBot as well as get a high level overview of what's currently happening
        in the crypto market.

        What would you like to do?
        1. Chat with PulseBot.
        2. Get a general overview.
        """

        return dedent(content)

    def get_next(self, answer: str) -> BaseDialogue:
        if answer == "1":
            return PulseBot(self._context)
        elif answer == "2":
            return Overview(self._context)
        else:
            return WrongOption(self._context)
