from rest_framework import serializers
from .models import Campaign, Lead, LeadDraft, CampaignWorkflowStep

class CampaignWorkflowStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignWorkflowStep
        fields = '__all__'

class CampaignSerializer(serializers.ModelSerializer):
    workflow_steps = CampaignWorkflowStepSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = '__all__'

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'

class LeadDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadDraft
        fields = '__all__'
