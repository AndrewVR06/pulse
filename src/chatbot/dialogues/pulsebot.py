from textwrap import dedent
import datetime
from chatbot.dialogues.base_dialogue import BaseDialogue
from chatbot.schemas.twilio_message import TwilioMessage
from chatbot.schemas.user_session import PulsebotAnswer
from services.anthropic_service import AnthropicService
from services.vector_service import VectorService


class PulseBot(BaseDialogue):

    base_content = f"""
    PulseBot here and ready to answer your questions!

    I know alot about what's been happening in the CryptoCurrency markets recently. 
    Ask anything you'd like to know and I'll do my best to give you answers.
    """

    def __init__(self, context: TwilioMessage):
        super().__init__(context)

        self._anthropic_service = AnthropicService()
        self._vector_service = VectorService()

    async def get_response(self) -> str:

        if not self._context.user_session.initiated_pulsebot:
            await self._redis_client.init_pulsebot_session(self._context.user_session)
            return dedent(self.base_content)

        question = self._context.body
        time_cutoff = datetime.datetime.now() - datetime.timedelta(days=3)
        top_results = await self._vector_service.retrieve_top_k_results(question, time_cutoff, k=128)
        reranked_results = await self._vector_service.rerank_results(question, top_results)

        # First question directed at PulseBot
        if not self._context.user_session.pulsebot_answers:
            question = self._anthropic_service.create_initial_prompt(question, reranked_results)
        else:
            question = self._anthropic_service.prepare_question(question, reranked_results)

        new_user_answer = PulsebotAnswer(role="user", content=question)
        self._context.user_session = await self._redis_client.update_pulsebot_conversation_history(self._context.user_session, new_user_answer)

        answer = await self._anthropic_service.answer_question(question, reranked_results, self._context.user_session.pulsebot_answers)
        new_pulsebot_answer = PulsebotAnswer(role="assistant", content=answer)
        await self._redis_client.update_pulsebot_conversation_history(self._context.user_session, new_pulsebot_answer)

        return dedent(answer)

    def next_dialogue(self, answer: str) -> str:
        pass
