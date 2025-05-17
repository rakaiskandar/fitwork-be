from .models import ChatSession, ChatMessage
from .ai.chat_engine import chat_chain, format_chat_history
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class CareerConsultationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data.get("question")
        if not question:
            return Response({"error": "Question is required."}, status=400)

        # Use or create session
        session, _ = ChatSession.objects.get_or_create(user=request.user)

        # Store user message
        ChatMessage.objects.create(session=session, role="user", content=question)

        # Prepare chat history for Gemini
        history = format_chat_history(session.messages)

        try:
            response = chat_chain.invoke({
                "chat_history": history,
                "user_input": question
            })

            ChatMessage.objects.create(session=session, role="assistant", content=response.content)

            return Response({
                "response": response.content
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = ChatSession.objects.filter(user=request.user).first()
        if not session:
            return Response([])

        messages = session.messages.order_by("created_at")
        return Response([
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ])
