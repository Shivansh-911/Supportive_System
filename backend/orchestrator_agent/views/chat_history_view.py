from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.services.utils.logger import get_logger
from orchestrator_agent.models.message import Message
from orchestrator_agent.serializers import SessionIdSerializer

logger = get_logger(__name__)


class ChatHistoryViewSet(ViewSet):
    http_method_names = ['get']

    def list(self, request):
        input_serializer = SessionIdSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)

        session_id = input_serializer.validated_data.get("session_id")

        logger.info("CHAT HISTORY => fetching messages [session_id = %s]", session_id)

        messages = Message.objects.get_all_messages_for_session(session_id=session_id)
        return Response(
            list(messages.values("request_id", "raw_query", "parsed_answer", "created_at")),
            status=status.HTTP_200_OK,
        )
