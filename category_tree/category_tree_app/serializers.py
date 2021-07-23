from rest_framework import serializers

from category_tree_app.models import Category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "category_id",
            "parent_category",
            "image",
            "name",
            "description",
            "similarities",
        ]

    def validate_similarities(self, value):
        if self.instance in value:
            raise serializers.ValidationError(
                "Same category is not allowed for similarity"
            )
        return value


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