from chatbot.schemas.twilio_message import TwilioMessage
from services.redis_service import RedisService
from fastapi.background import BackgroundTasks


class BaseDialogue:

    def __init__(self, context: TwilioMessage):
        self._redis_client = RedisService()
        self._context = context

    async def get_current_dialogue(self) -> "BaseDialogue":
        """
        Find the current dialogue the user has now entered by sending a message and save/create the user session
        """
        from chatbot.dialogues.main_menu import MainMenu
        from chatbot.dialogues.pulsebot import PulseBot

        dialogue = MainMenu(self._context)
        if self._context.user_session is None:
            await self._redis_client.init_user_session(self._context.account_sid)
            return dialogue

        answers = [*self._context.user_session.dialogue_answers, self._context.body]
        for answer in answers:
            if isinstance(dialogue, PulseBot):
                return dialogue

            dialogue = dialogue.get_next(answer)

        session = await self._redis_client.update_chatbot_dialogue(self._context.user_session, self._context.body)
        self._context.user_session = session

        return dialogue

    def get_next(self, answer: str) -> "BaseDialogue":
        raise NotImplementedError

    async def get_response(self) -> str:
        raise NotImplementedError
