from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.services.utils.logger import get_logger
from orchestrator_agent.models.message import Message
from orchestrator_agent.serializers import RequestIdSerializer

logger = get_logger(__name__)


class ThumbsUpViewSet(ViewSet):
    http_method_names = ['post']

    def create(self, request):
        input_serializer = RequestIdSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        request_id = input_serializer.validated_data.get("request_id")
        logger.info("FEEDBACK => thumbs up [request_id = %s]", request_id)
        Message.objects.update_feedback(request_id=request_id, feedback=1)
        return Response(status=status.HTTP_204_NO_CONTENT)
