from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/invoice_processor/', include('invoice_processor.urls')),
]
