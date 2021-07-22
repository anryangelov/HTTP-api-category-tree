from rest_framework import serializers

from category_tree_app.models import Category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class CategoryWithDepthSerializer(CategorySerializer):
    depth = serializers.IntegerField()


class CategoryImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["image"]
        extra_kwargs = {"image": {"required": True}}


class QueryParamsSerializer(serializers.Serializer):
    depth = serializers.IntegerField(required=False)
    tree = serializers.BooleanField(required=False)