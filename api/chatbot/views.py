from .models import ChatSession, ChatMessage
from .ai.chat_engine import chat_chain, format_chat_history
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .ai.title_generator import chat_title

class CareerConsultationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data.get("question")
        history_id = request.data.get("history_id")

        if not question:
            return Response({"error": "Question is required."}, status=400)

        if history_id:
            # Ambil session berdasarkan ID
            try:
                session = ChatSession.objects.get(id=history_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({"error": "Invalid history ID"}, status=400)
        else:
            # Buat session baru
            session = ChatSession.objects.create(user=request.user)

        # Simpan pesan user
        ChatMessage.objects.create(session=session, role="user", content=question)

        # Format riwayat chat
        history = format_chat_history(session.messages)

        try:
            response = chat_chain.invoke({
                "chat_history": history,
                "user_input": question
            })

        # Simpan respon AI
            ChatMessage.objects.create(session=session, role="assistant", content=response.content)

            return Response({
                "response": response.content,
                "history_id": str(session.id)  # kirim agar frontend bisa pakai kembali
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class ChatSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        # Pastikan session milik user yang login
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        messages = session.messages.order_by("created_at")
        return Response([
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ])

class ChatSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = request.user.chat_sessions.order_by("-created_at")
        session_summaries = []

        for session in sessions:
            if session.title:
                title = session.title
            else:
                # Gabungkan isi semua pesan dalam sesi
                messages = session.messages.order_by("created_at")
                chat_transcript = "\n".join([f"{m.role.capitalize()}: {m.content}" for m in messages])

                try:
                    result = chat_title.invoke({"conversation": chat_transcript})
                    title = result.content.strip()

                    session.title = title
                    session.save(update_fields=["title"])
                except Exception as e:
                    print(f"Failed to generate title for session {session.id}: {e}")
                    title = "Untitled Session"

            session_summaries.append({
                "id": str(session.id),
                "title": title,
                "created_at": session.created_at.isoformat(),
            })

        return Response(session_summaries)