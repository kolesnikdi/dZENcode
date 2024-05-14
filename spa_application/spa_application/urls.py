from django.contrib import admin
from django.urls import path, include

# from spa_application import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

DESCRIPTION = """
Project `_spa_application`.
"""

SchemaView = get_schema_view(
    openapi.Info(
        title='spa_application',
        default_version='v1',
        description=DESCRIPTION,
        contact=openapi.Contact(email='kolesnik.d.i@gmail.com'),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('comments.urls')),
    path('swagger/', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# if settings.DEBUG:
#     urlpatterns.append(
#         path('', include('swagger.urls')),
#     )
