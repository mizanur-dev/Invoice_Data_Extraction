from django.db import models

class Invoice(models.Model):
    image_url = models.URLField(max_length=2048)
    extracted_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.id} - {self.created_at}"