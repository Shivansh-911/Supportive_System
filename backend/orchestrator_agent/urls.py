from rest_framework.routers import DefaultRouter

from orchestrator_agent.views.chat_history_view import ChatHistoryViewSet
from orchestrator_agent.views.thumbs_up_view import ThumbsUpViewSet
from orchestrator_agent.views.thumbs_down_view import ThumbsDownViewSet
from orchestrator_agent.views.message_view import MessageViewSet
from orchestrator_agent.views.all_sessions_view import SessionViewSet

router = DefaultRouter()
router.register(r"message", MessageViewSet, basename="message")
router.register(r"all_sessions", SessionViewSet, basename="all_sessions")
router.register(r"chat_history", ChatHistoryViewSet, basename="chat_history")
router.register(r"thumbs_up", ThumbsUpViewSet, basename="thumbs_up")
router.register(r"thumbs_down", ThumbsDownViewSet, basename="thumbs_down")

urlpatterns = router.urls
