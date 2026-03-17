from rest_framework import serializers
from .models import LLMProvider

class LLMProviderSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True)

    class Meta:
        model = LLMProvider
        fields = ['id', 'provider', 'default_model', 'base_url', 'api_key', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        api_key = validated_data.pop('api_key')
        provider = LLMProvider(**validated_data)
        provider.set_api_key(api_key)
        provider.save()
        return provider
