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
