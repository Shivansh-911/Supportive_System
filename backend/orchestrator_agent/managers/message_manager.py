from django.db import models
from django.db.models.functions import Now

from core.services.utils.logger import get_logger

logger = get_logger(__name__)


class MessageManager(models.Manager):

    def get_last_message(self, session_id: int):
        return (
            self.filter(session=session_id)
            .order_by("-created_at")
            .first()
        )

    def get_all_messages_for_session(self, session_id: int):
        return (
            self.filter(session_id=session_id)
            .order_by("created_at")
        )

    def update_feedback(self, request_id: str, feedback: int):
        self.filter(request_id=request_id).update(feedback=feedback, feedback_at=Now())
