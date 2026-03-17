from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatSession, Message
from .serializers import ChatSessionSerializer, MessageSerializer
from .hawk_agent import HawkAgent
from providers.models import LLMProvider

class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        session = self.get_object()
        msgs = session.messages.all().order_by('created_at')
        serializer = MessageSerializer(msgs, many=True)
        return Response({'results': serializer.data})

    @messages.mapping.post
    def send_message(self, request, pk=None):
        session = self.get_object()
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Save user message
        user_msg = Message.objects.create(session=session, role='user', content=content)

        # 2. Find active provider
        provider = LLMProvider.objects.filter(user=request.user).first()
        if not provider:
            return Response({'error': 'No LLM provider configured. Please add one in Settings.'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Setup Agent
        agent = HawkAgent({
            'type': provider.provider,
            'api_key': provider.get_api_key(),
            'model': provider.default_model or 'llama3-8b-8192',
            'base_url': provider.base_url
        })

        # 4. Execute with Tools
        try:
            from .tools import get_tools_for_user
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
            
            tools = get_tools_for_user(request.user)
            executor = agent.get_agent_executor(
                tools, 
                system_prompt="You are HAWK AI, an expert assistant for an outreach agency. You can manage campaigns, leads, and drafts."
            )
            
            # Reconstruct history
            history = []
            for m in session.messages.all().exclude(id=user_msg.id).order_by('created_at'):
                if m.role == 'user':
                    history.append(HumanMessage(content=m.content))
                elif m.role == 'assistant':
                    history.append(AIMessage(content=m.content))
            
            response = executor.invoke({
                "input": content,
                "chat_history": history
            })
            bot_content = response.get("output", "Sorry, I could not process your request.")

            # 5. Save assistant message
            bot_msg = Message.objects.create(session=session, role='assistant', content=bot_content)

            return Response({
                'response': bot_content,
                'message': MessageSerializer(bot_msg).data
            })
            
        except Exception as e:
            # We want to remove the user message if it completely failed so they can retry without broken history
            user_msg.delete() 
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
