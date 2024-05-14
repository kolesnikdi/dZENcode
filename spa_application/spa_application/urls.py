from django.contrib import admin
from django.urls import path, include

from spa_application import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('comments.urls')),
]

if settings.DEBUG:
    urlpatterns.append(
        path('', include('swagger.urls')),
    )
