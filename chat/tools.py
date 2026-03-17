from langchain_core.tools import tool
from campaigns.models import Campaign, Lead, LeadDraft
from campaigns.auditor import WebsiteAuditor
from chat.hawk_agent import HawkAgent
from providers.models import LLMProvider
import asyncio
from asgiref.sync import sync_to_async

def get_tools_for_user(user):

    @tool
    def get_campaigns() -> str:
        """Retrieves a list of all campaigns owned by the user. Returns their IDs, names, and sender modes."""
        campaigns = Campaign.objects.filter(user=user)
        if not campaigns.exists():
            return "You have no campaigns."
        
        result = "Your campaigns:\n"
        for c in campaigns:
            result += f"- ID: {c.id}, Name: {c.name}, Mode: {c.sender_mode}\n"
        return result

    @tool
    def create_campaign(name: str, description: str = "", sender_mode: str = "brand") -> str:
        """Creates a new campaign for the user. Requires a name and optionally a description and sender_mode ('brand' or 'anonymous')."""
        campaign = Campaign.objects.create(
            user=user, 
            name=name, 
            description=description, 
            sender_mode=sender_mode
        )
        return f"Campaign '{campaign.name}' created successfully with ID {campaign.id} in {campaign.sender_mode} mode."

    @tool
    def get_leads(campaign_id: int) -> str:
        """Retrieves a list of leads for a specific campaign ID. Returns lead IDs, names, companies, and their status."""
        try:
            campaign = Campaign.objects.get(id=campaign_id, user=user)
        except Campaign.DoesNotExist:
            return f"Campaign with ID {campaign_id} not found."
            
        leads = campaign.leads.all()
        if not leads.exists():
            return f"No leads found in campaign '{campaign.name}'."
            
        result = f"Leads in campaign '{campaign.name}':\n"
        for l in leads:
            result += f"- ID: {l.id}, Name: {l.name}, Company: {l.company}, Status: {l.status}\n"
        return result

    @tool
    def add_lead(campaign_id: int, name: str, email: str, company: str, website: str) -> str:
        """Adds a new lead to a specific campaign. Requires campaign_id, name, email, company, and website."""
        try:
            campaign = Campaign.objects.get(id=campaign_id, user=user)
        except Campaign.DoesNotExist:
            return f"Campaign with ID {campaign_id} not found."
            
        lead = Lead.objects.create(
            campaign=campaign,
            name=name,
            email=email,
            company=company,
            website=website
        )
        return f"Lead '{lead.name}' successfully added to campaign '{campaign.name}' with ID {lead.id}."

    @tool
    def audit_lead(lead_id: int) -> str:
        """Runs a website audit for a specific lead ID. Returns the audit findings."""
        try:
            lead = Lead.objects.get(id=lead_id, campaign__user=user)
        except Lead.DoesNotExist:
            return f"Lead with ID {lead_id} not found."
            
        if not lead.website:
            return "Lead has no website to audit."
            
        auditor = WebsiteAuditor(lead.website, {'ux': True, 'conversion': True})
        
        # Run async function in sync context
        try:
            loop = asyncio.get_event_loop()
            results = loop.run_until_complete(auditor.run_audit())
        except RuntimeError:
            results = asyncio.run(auditor.run_audit())
            
        lead.tech_stack = results.get('findings', {})
        lead.status = 'audited'
        lead.save()
        
        return f"Audit completed for {lead.name}. Findings: {results.get('findings', 'No findings')}"

    @tool
    def generate_draft_for_lead(lead_id: int) -> str:
        """Generates an AI outreach draft for a specific lead ID based on their audit results and campaign settings."""
        try:
            lead = Lead.objects.get(id=lead_id, campaign__user=user)
        except Lead.DoesNotExist:
            return f"Lead with ID {lead_id} not found."
            
        provider = LLMProvider.objects.filter(user=user).first()
        if not provider:
            return "No LLM Provider found. Add one in settings to generate drafts."
            
        agent = HawkAgent({
            "type": provider.provider,
            "api_key": provider.get_api_key(),
            "model": provider.default_model
        })
        
        agency_info = {
            "name": user.username,
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
            mode=lead.campaign.sender_mode
        )
        
        draft = LeadDraft.objects.create(
            lead=lead,
            subject=draft_data.get('subject', 'No Subject'),
            body=draft_data.get('body', ''),
            hook=draft_data.get('hook', ''),
            mode=lead.campaign.sender_mode
        )
        
        lead.status = 'drafted'
        lead.save()
        
        return f"Draft generated successfully for {lead.name}.\nSubject: {draft.subject}\nBody:\n{draft.body}"

    return [get_campaigns, create_campaign, get_leads, add_lead, audit_lead, generate_draft_for_lead]
