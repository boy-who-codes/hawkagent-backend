from rest_framework import viewsets, status, response
from rest_framework.decorators import action
from .models import Campaign, Lead, LeadDraft, CampaignWorkflowStep
from .serializers import CampaignSerializer, LeadSerializer, LeadDraftSerializer, CampaignWorkflowStepSerializer
from .auditor import WebsiteAuditor
from chat.hawk_agent import HawkAgent
from providers.models import LLMProvider, SMTPServer
import asyncio

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

    def get_queryset(self):
        return self.queryset.filter(campaign__user=self.request.user)

    @action(detail=True, methods=['post'])
    def audit(self, request, pk=None):
        lead = self.get_object()
        role_config = request.data.get('role_config', {'ux': True, 'conversion': True})
        
        auditor = WebsiteAuditor(lead.website, role_config)
        results = asyncio.run(auditor.run_audit())
        
        lead.tech_stack = results.get('findings', {})
        lead.status = 'audited'
        lead.save()
        
        return response.Response(results)

    @action(detail=True, methods=['post'])
    def generate_draft(self, request, pk=None):
        lead = self.get_object()
        mode = request.data.get('mode', lead.campaign.sender_mode)
        
        # Get user's provider
        provider = LLMProvider.objects.filter(user=request.user).first()
        if not provider:
            return response.Response({"error": "No LLM Provider found. Add one in settings."}, status=status.HTTP_400_BAD_REQUEST)
            
        agent = HawkAgent({
            "type": provider.provider,
            "api_key": provider.get_api_key(),
            "model": provider.default_model
        })
        
        agency_info = {
            "name": request.user.username, # Should be from AgencySettings
            "services": ["Web Dev", "Marketing"]
        }
        
        draft_data = agent.generate_outreach(
            lead_data={
                "name": lead.name,
                "company": lead.company,
                "website": lead.website,
                "audit": lead.tech_stack
            },
            agency_info=agency_info,
            mode=mode
        )
        
        draft = LeadDraft.objects.create(
            lead=lead,
            subject=draft_data.get('subject'),
            body=draft_data.get('body'),
            hook=draft_data.get('hook'),
            mode=mode
        )
        
        lead.status = 'drafted'
        lead.save()
        
        return response.Response(LeadDraftSerializer(draft).data)

class LeadDraftViewSet(viewsets.ModelViewSet):
    queryset = LeadDraft.objects.all()
    serializer_class = LeadDraftSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        draft = self.get_object()
        draft.is_approved = True
        draft.save()
        return response.Response({"status": "approved"})

class CampaignWorkflowStepViewSet(viewsets.ModelViewSet):
    queryset = CampaignWorkflowStep.objects.all()
    serializer_class = CampaignWorkflowStepSerializer

    def get_queryset(self):
        return self.queryset.filter(campaign__user=self.request.user)
