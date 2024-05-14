# from django.urls import path
# from swagger.views import SchemaView
#
# # urlpatterns = [
# #     re_path(r'^$', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
# #     re_path(r'^redoc/$', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
# #     re_path(r'^swagger(?P<format>\.json|\.yaml)$', SchemaView.without_ui(cache_timeout=0), name='schema-json'),
# # ]
# urlpatterns = [
#     path('swagger/', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#     path('redoc/', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
# ]