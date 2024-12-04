import logging
from typing import Optional, List

import redis.asyncio as redis

from app_config import get_settings
from chatbot.schemas.user_session import PulsebotAnswer, UserSession


class RedisService:
    _instance = None
    _logger = None
    _client: redis.Redis

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._logger = logging.getLogger(cls.__name__)
        return cls._instance

    async def init_redis(self):
        self._client = redis.Redis.from_url(get_settings().redis_url, decode_responses=True)
        await self._client.ping()
        self._logger.info("Started redis")

    async def close_redis(self):
        await self._client.aclose(close_connection_pool=True)
        self._logger.info("Successfully closed redis")

    async def set_value(self, key: str, value: str):
        """Set a redis value with a timeout of 1 hour (3600)"""
        await self._client.set(key, value, ex=3600)

    async def get_value(self, key: str) -> Optional[str]:
        """Get a value from redis for key"""
        return await self._client.get(key)

    async def get_chatbot_session(self, account_sid: str) -> Optional[UserSession]:
        """Get the session associated with the account sid"""
        if session := await self.get_value(account_sid):
            return UserSession.model_validate_json(session)
        return None

    async def init_user_session(self, account_sid: str) -> None:
        """Initialize the User session associated with the account sid"""
        session = UserSession.empty(account_sid)
        await self.set_value(account_sid, session.model_dump_json())

    async def update_chatbot_dialogue(self, old_session: UserSession, message_body: str) -> UserSession:
        """Set a new session for the account sid"""
        dialogue_answers = [*old_session.dialogue_answers, message_body]

        new_session = UserSession(account_sid=old_session.account_sid, dialogue_answers=dialogue_answers)
        await self.set_value(new_session.account_sid, new_session.model_dump_json())

        return new_session

    async def update_pulsebot_conversation_history(self, old_session: UserSession, answer: PulsebotAnswer) -> UserSession:
        """Set a new session for the account sid"""
        pulsebot_answers = [*old_session.pulsebot_answers, answer]
        new_session = UserSession(pulsebot_answers=pulsebot_answers, **old_session.model_dump(exclude=["pulsebot_answers"]))
        await self.set_value(new_session.account_sid, new_session.model_dump_json())

        return new_session

    async def init_pulsebot_session(self, old_session: UserSession) -> None:
        """Set a new session for the account sid"""
        new_session = UserSession(initiated_pulsebot=True, **old_session.model_dump(exclude=["initiated_pulsebot"]))
        await self.set_value(new_session.account_sid, new_session.model_dump_json())

    async def delete_value(self, key: str):
        """Delete a redis value for key"""
        await self._client.delete(key)
