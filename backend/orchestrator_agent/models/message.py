import uuid

from django.db import models
from orchestrator_agent.managers.message_manager import MessageManager
from orchestrator_agent.models.session import Session


class Message(models.Model):

    objects = MessageManager()

    request_id = models.UUIDField(primary_key=True)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    raw_query = models.TextField()
    rewritten_query = models.TextField()
    intent = models.CharField(max_length=50)
    is_follow_up = models.BooleanField(default=False)
    last_qa_id = models.UUIDField(null=True, blank=True)

    vector_chunks = models.JSONField(default=list)
    bm_25_chunks = models.JSONField(default=list)
    fused_chunks = models.JSONField(default=list)
    cited_chunks = models.JSONField(default=list)
    raw_answer = models.TextField()
    parsed_answer = models.JSONField()

    feedback = models.SmallIntegerField(null=True, blank=True, default=None)
    feedback_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["session", "created_at"]),
        ]
