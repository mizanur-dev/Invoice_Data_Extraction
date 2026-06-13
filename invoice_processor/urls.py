from django.urls import path
from .views import InvoiceCreateAPIView

urlpatterns = [
    path('extract-invoice/', InvoiceCreateAPIView.as_view(), name='extract_invoice'),
]