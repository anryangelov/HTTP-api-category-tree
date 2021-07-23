from rest_framework import serializers

from category_tree_app.models import Category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "category_id",
            "parent_category_id",
            "image",
            "name",
            "description",
            "similarities",
        ]


class CategoryWithDepthSerializer(CategorySerializer):
    depth = serializers.IntegerField()

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ["depth"]


class CategoryImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["image"]
        extra_kwargs = {"image": {"required": True}}


class QueryParamsSerializer(serializers.Serializer):
    depth = serializers.IntegerField(required=False)
    tree = serializers.BooleanField(required=False)