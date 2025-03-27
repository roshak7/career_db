from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework_swagger.views import get_swagger_view
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
import os

from api.views_v2 import test1
from career import views

from career.views import get_image

schema_view = get_swagger_view(title='Career API')

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # Добавляем корневой URL для показа главной страницы
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    # Swagger документация теперь доступна по отдельному URL
    path('api-docs/', schema_view, name='api-docs'),
    
    path('admin/', admin.site.urls),
    path('login', views.LoginView.as_view()),
    path('logout', views.Logout.as_view()),
    path("img/<slug:id>/", get_image),
    
    path('api/v1/', include('api.urls')),
    path('api/v2/', include('api.urls_v2')),
    path('v1/', include('api.urls')),
    path('v2/', include('api.urls_v2')),
    
    # Фронтенд-страница, если используется отдельный фронтенд
    path('app/', TemplateView.as_view(template_name='index.html'), name='frontend'),
]

# Добавляем обслуживание статических файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Добавляем обслуживание assets из директории front
    urlpatterns += static('/assets/', document_root=os.path.join(settings.BASE_DIR, '../front/assets'))

