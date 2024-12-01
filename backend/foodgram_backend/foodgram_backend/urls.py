
from django.contrib import admin
from django.urls import path, include

from api.views import short_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<int:pk>/', short_url)
]
