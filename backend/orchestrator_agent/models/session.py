from django.db import models
from orchestrator_agent.managers.session_manager import SessionManager


class Session(models.Model):

    objects     = SessionManager()
    title       = models.CharField(max_length=255, null=True, blank=True)
    user_id     = models.CharField(max_length=255, db_index=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
