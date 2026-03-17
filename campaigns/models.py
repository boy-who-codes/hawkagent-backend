from django.db import models
from django.conf import settings

class Campaign(models.Model):
    SENDER_MODE_CHOICES = (
        ('brand', 'Brand (Official)'),
        ('anonymous', 'Anonymous (Stealth)'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sender_mode = models.CharField(max_length=20, choices=SENDER_MODE_CHOICES, default='brand')
    auto_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CampaignWorkflowStep(models.Model):
    STEP_TYPE_CHOICES = (
        ('ice_breaker', 'Ice Breaker'),
        ('audit', 'Audit'),
        ('follow_up', 'Follow Up'),
        ('custom', 'Custom'),
    )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='workflow_steps')
    step_order = models.IntegerField(default=1)
    step_type = models.CharField(max_length=50, choices=STEP_TYPE_CHOICES)
    instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['step_order']
        unique_together = ('campaign', 'step_order')

    def __str__(self):
        return f"{self.campaign.name} - Step {self.step_order}: {self.get_step_type_display()}"

class Lead(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('enriched', 'Enriched'),
        ('audited', 'Audited'),
        ('drafted', 'Draft Ready'),
        ('emailed', 'Emailed'),
        ('replied', 'Replied'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    )
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='leads')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    company = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    tech_stack = models.JSONField(default=dict, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    score = models.CharField(max_length=2, default='C') 
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company})"

class LeadDraft(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='drafts')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    hook = models.TextField(blank=True, null=True)
    mode = models.CharField(max_length=20, choices=(('brand', 'Brand'), ('anonymous', 'Anonymous')))
    is_approved = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Draft for {self.lead.name} ({self.mode})"
