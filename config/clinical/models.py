from django.db import models
import secrets

class ClinicalAPIKey(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_key():
        return secrets.token_hex(32)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = ClinicalAPIKey.generate_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ClinicalAuditLog(models.Model):
    request_id = models.CharField(max_length=100, unique=True)
    timestamp = models.DateTimeField()
    risk_level = models.CharField(max_length=20)
    approval_required = models.BooleanField()

    agents_executed = models.JSONField()
    status = models.CharField(max_length=50)

    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.request_id} - {self.risk_level}"
