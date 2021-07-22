from rest_framework.routers import DefaultRouter

from category_tree_app.views import CategoryViewSet


router = DefaultRouter()
router.register('', CategoryViewSet, basename='category')
urlpatterns = router.urls
