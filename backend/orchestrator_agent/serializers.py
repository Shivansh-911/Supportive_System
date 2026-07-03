from rest_framework import serializers

from orchestrator_agent.models.message import Message


class OrchestratorInputSerializer(serializers.Serializer):
    session_id = serializers.IntegerField(required=False, allow_null=True)
    user_id = serializers.CharField(required=True)
    question = serializers.CharField()


class RequestIdSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()

class SessionIdSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()

class UserIdSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()

class MessageCreateSerializer(serializers.ModelSerializer):
    response = serializers.CharField()
    metadata = serializers.DictField(default=dict)

    class Meta:
        model = Message
        fields = [
            "request_id",
            "session",
            "raw_query",
            "rewritten_query",
            "intent",
            "is_follow_up",
            "last_qa_id",
            "response",
            "metadata",
        ]

    def create(self, validated_data):
        metadata = validated_data.pop("metadata", {})
        response = validated_data.pop("response")
        return Message.objects.create(
            **validated_data,
            raw_answer=response,
            vector_chunks=metadata.get("vector_chunks", []),
            bm_25_chunks=metadata.get("bm25_chunks", []),
            fused_chunks=metadata.get("fused_chunks", []),
            cited_chunks=metadata.get("cited_chunks", []),
            parsed_answer=metadata.get("parsed_answer", {}),
        )
