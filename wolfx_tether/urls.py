from django.urls import path, include
from django.contrib import admin


urlpatterns = [
    path('', include('web.urls')),  # Use custom admin
    path('admin/', admin.site.urls),  # Use custom admin
]