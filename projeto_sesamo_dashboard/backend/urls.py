from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from .views import UserViewSet, AppUsers

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('app-users', AppUsers,  basename='AppUsers')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url('', include(router.urls)),
    # url('app-users', UserViewSet.as_view({'get': 'list'})),
    url('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]