from rest_framework import serializers
from .models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'image_url', 'extracted_data', 'created_at']
        read_only_fields = ['extracted_data', 'created_at']