from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.services.utils.logger import get_logger
from orchestrator_agent.models.session import Session
from orchestrator_agent.serializers import UserIdSerializer

logger = get_logger(__name__)


class SessionViewSet(ViewSet):
    http_method_names = ['get']

    def list(self, request):
        input_serializer = UserIdSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
    
        logger.info("SESSIONS => fetching all sessions [user_id = %s]", input_serializer.validated_data.get("user_id"))
        sessions = Session.objects.all_sessions(user_id=input_serializer.validated_data.get("user_id"))
        return Response(list(sessions.values("id","title", "user_id", "created_at", "updated_at")), status=status.HTTP_200_OK)
