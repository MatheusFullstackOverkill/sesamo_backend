from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from .views import UserViewSet, FAQViewSet, LocationsViewSet
from rest_framework.authtoken import views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register('', UserViewSet, basename='users')
router.register('', FAQViewSet, basename='faq')
router.register('', LocationsViewSet, basename='locations')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]