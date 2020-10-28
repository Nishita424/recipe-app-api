from django.urls import path, include
from rest_framework.routers import DefaultRouter # helps to automatically
# register appropriate urls for all actions in our viewset
# eg. /api/recipe/tags, /api/recipe/tags/1/, ..

from .views import TagViewSet

router = DefaultRouter()
router.register('tags', TagViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
