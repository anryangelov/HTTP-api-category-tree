from django.http import Http404
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.status import HTTP_400_BAD_REQUEST

from category_tree_app.serializers import (
    CategorySerializer,
    CategoryImageSerializer,
    QueryParamsSerializer,
    CategoryWithDepthSerializer,
)
from category_tree_app.models import Category
from category_tree_app.utils import make_tree_for_category_list


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(
        detail=True,
        methods=['PUT'],
        serializer_class=CategoryImageSerializer,
        parser_classes=[MultiPartParser],
    )
    def image(self, request, pk):
        obj = self.get_object()
        serializer = self.serializer_class(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_categories(self, request, pk, raw_queryset_obj):
        query_params_ser = QueryParamsSerializer(data=request.query_params)
        query_params_ser.is_valid(raise_exception=True)
        depth = query_params_ser.data.get('depth')
        tree = query_params_ser.data.get('tree')

        categories = raw_queryset_obj(pk, depth)
        data = CategoryWithDepthSerializer(categories, many=True).data
        if tree:
            data = make_tree_for_category_list(data, field_name='children')
        return Response(data)

    @action(detail=True, methods=['GET'])
    def parents(self, request, pk):
        return self.get_categories(request, pk, Category.objects.parent_list)

    @action(detail=True, methods=['GET'])
    def children(self, request, pk):
        return self.get_categories(request, pk, Category.objects.child_list)

    @action(detail=True, methods=['GET'])
    def parent(self, request, pk):
        category = Category.objects.get(category_id=pk)
        if not category.parent_category:
            raise Http404
        data = self.serializer_class(category.parent_category).data
        return Response(data)
