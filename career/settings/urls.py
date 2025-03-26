from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework_swagger.views import get_swagger_view
from django.conf.urls import url

from api.views_v2 import test1
from career import views

from career.views import get_image

schema_view = get_swagger_view(title='Pastebin API')

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
    # url(r'^$', schema_view),
    # path('', include(router.urls)),
    # path('api/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('login', views.LoginView.as_view()),
    # path('api/user/', views.UserView.as_view()),
    # path('login', include('rest_framework.urls')),
    path('logout', views.Logout.as_view()),
    path("img/<slug:id>/", get_image),
    # url(r'^api/v1/', include('api.urls')),
    # url(r'^api/v2/', include('api.urls_v2')),

    # path('', include(router.urls)),
    path('api/v1/', include('api.urls')),
    path('api/v2/', include('api.urls_v2')),
    path('v1/', include('api.urls')),
    path('v2/', include('api.urls_v2')),
    # path('test1', test1)
]

