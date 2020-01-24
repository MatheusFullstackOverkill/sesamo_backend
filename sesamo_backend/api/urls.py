from django.urls import path
from django.conf.urls import url, include
# from rest_framework import routers
from rest_framework_nested import routers
from .views import UserViewSet, FAQViewSet, LocationsViewSet, QuestionsViewSet, reset_password

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register('users', UserViewSet)
router.register('faq', FAQViewSet)
faq_router = routers.NestedSimpleRouter(router, 'faq', lookup='category')
faq_router.register('questions', QuestionsViewSet, basename='category-question')
router.register('questions', QuestionsViewSet)
router.register('locations', LocationsViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('', include(faq_router.urls)),
    path('reset_password', reset_password, name='reset_password'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]