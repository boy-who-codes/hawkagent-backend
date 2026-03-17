from django.db import models
from django.conf import settings

class SMTPServer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='smtp_servers')
    name = models.CharField(max_length=100, help_text="Nickname for this SMTP config")
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=587)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Should be encrypted in production
    use_tls = models.BooleanField(default=True)
    from_name = models.CharField(max_length=255)
    from_email = models.EmailField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.from_email})"
