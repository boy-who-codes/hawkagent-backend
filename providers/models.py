from django.db import models
from django.conf import settings
from core.utils.crypto import encrypt, decrypt

class LLMProvider(models.Model):
    PROVIDER_CHOICES = (
        ('groq', 'Groq'),
        ('anthropic', 'Anthropic (Claude)'),
        ('openai', 'OpenAI'),
        ('gemini', 'Google Gemini'),
        ('deepseek', 'DeepSeek'),
        ('grok', 'Grok (xAI)'),
        ('sarvam', 'Sarvam AI'),
        ('openrouter', 'OpenRouter'),
        ('custom', 'Custom (BYOK URL)'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='providers')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    api_key_encrypted = models.TextField()
    base_url = models.URLField(blank=True, null=True)
    default_model = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'provider')

    def set_api_key(self, raw_api_key):
        self.api_key_encrypted = encrypt(raw_api_key)

    def get_api_key(self):
        return decrypt(self.api_key_encrypted)

    def __str__(self):
        return f"{self.user.username} - {self.get_provider_display()}"

class SMTPServer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='smtp_servers')
    name = models.CharField(max_length=100, help_text="Nickname for this SMTP config")
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=587)
    username = models.CharField(max_length=255)
    password_encrypted = models.TextField()  # Encrypted
    use_tls = models.BooleanField(default=True)
    from_name = models.CharField(max_length=255)
    from_email = models.EmailField()
    is_active = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.password_encrypted = encrypt(raw_password)

    def get_password(self):
        return decrypt(self.password_encrypted)

    def __str__(self):
        return f"{self.name} ({self.from_email})"
