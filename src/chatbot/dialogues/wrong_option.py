from textwrap import dedent

from chatbot.dialogues.base_dialogue import BaseDialogue


class WrongOption(BaseDialogue):

    async def get_response(self) -> str:
        content = f"""
        You have selected an incorrect option!
        Please start again.
        """

        await self._redis_client.delete_value(self._context.account_sid)
        return dedent(content)
