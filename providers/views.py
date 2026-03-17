from rest_framework import viewsets, permissions
from .models import LLMProvider
from .serializers import LLMProviderSerializer

class LLMProviderViewSet(viewsets.ModelViewSet):
    serializer_class = LLMProviderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LLMProvider.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
