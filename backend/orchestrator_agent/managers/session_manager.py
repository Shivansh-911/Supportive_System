from django.db import models
from django.db.models.functions import Now

from core.services.utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager(models.Manager):

    def create_session(self, user_id: str):
        return self.create(user_id=user_id)

    def get_session(self, session_id: int):
        return self.get(id=session_id)

    def all_sessions(self, user_id: str):
        return self.filter(user_id=user_id).order_by("-updated_at")

    def touch_session(self, session_id: int):
        self.filter(id=session_id).update(updated_at=Now())

    def set_session_title(self, session_id: int, title: str):
        self.filter(id=session_id).update(title=title)

    def session_has_title(self, session_id: int):
        session = self.filter(id=session_id).first()
        return session is not None and session.title is not None
