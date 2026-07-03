import uuid

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.services.utils.logger import get_logger
from orchestrator_agent.graphs.orchestrator_graph import orchestrator_graph
from orchestrator_agent.models.message import Message
from orchestrator_agent.models.session import Session
from orchestrator_agent.serializers import MessageCreateSerializer, OrchestratorInputSerializer
from orchestrator_agent.services.answer_parser import FinalAnswerService
from orchestrator_agent.states.orchestrator_state import OrchestratorAgentState

logger = get_logger(__name__)

_parser = FinalAnswerService()


class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageCreateSerializer
    http_method_names = ['post']

    def create(self, request):
        input_serializer = OrchestratorInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        session_id = input_serializer.validated_data.get("session_id")
        user_id    = input_serializer.validated_data.get("user_id")
        question   = input_serializer.validated_data.get("question")
        request_id = uuid.uuid4()

        logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => received message request [user_id = %s] [session_id = %s]", request_id, user_id, session_id)

        state = OrchestratorAgentState(
            request_id=request_id,
            session_id=session_id,
            user_id=user_id,
            raw_query=question,
        )
        logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => Graph Invoked",request_id)
        result = orchestrator_graph.invoke(state)
        logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => Graph Execution completed",request_id)

        
        response      = result.get("response") or ""
        metadata      = result.get("metadata") or {}
        cited_chunks  = metadata.get("cited_chunks", [])


        logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => parsing answer with %d cited chunks]",request_id, len(cited_chunks))

        parsed_answer = _parser.parse(response, cited_chunks)

        logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => answer is parsed with %d blocks]",request_id, len(parsed_answer.get("blocks")))

        
        resolved_session_id = result.get("session_id")
        if not Session.objects.session_has_title(resolved_session_id):
            logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => Saving session title for [session id = %s]", request_id, resolved_session_id)
            Session.objects.set_session_title(resolved_session_id, result.get("session_title"))
        
        
        message_serializer = MessageCreateSerializer(data={
            "request_id":      request_id,
            "session":         result.get("session_id"),
            "raw_query":       question,
            "rewritten_query": result.get("rewritten_query"),
            "intent":          result.get("intent"),
            "is_follow_up":    result.get("is_follow_up"),
            "last_qa_id":      (result.get("last_qa_pair") or {}).get("id"),
            "response":        response,
            "metadata":        {**metadata, "parsed_answer": parsed_answer},
        })
        message_serializer.is_valid(raise_exception=True)
        message_serializer.save()

        return Response(
            {
                "session_id":    result.get("session_id"),
                "session_title": result.get("session_title"),
                "request_id":    request_id,
                "answer":        parsed_answer,
                "intent":        result.get("intent"),
                "is_follow_up":  result.get("is_follow_up"),
            },
            status=status.HTTP_201_CREATED,
        )
