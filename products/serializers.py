from rest_framework import serializers
from .models import Review, Product, FavoriteProduct, Cart

# class ProductSerializer(serializers.Serializer):
#     name = serializers.CharField()
#     description = serializers.CharField()
#     price = serializers.FloatField()
#     currency = serializers.ChoiceField(choices=['GEL', 'USD', 'EUR'])


# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         # fields = "__all__"
#         exclude = ['uuid', 'created_at', 'updated_at']
#         model = Product



class ReviewSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    content = serializers.CharField()
    rating = serializers.IntegerField()

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product_id. Product does not exist.")
        return value

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        product = Product.objects.get(id=validated_data['product_id'])
        user = self.context['request'].user

        review = Review.objects.create(
            product=product,
            user=user,
            content=validated_data['content'],
            rating=validated_data['rating'],
        )
        return review
    



class FavoriteProductSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FavoriteProduct
        fields = ['id', 'user', 'product_id', 'product']
        read_only_fields = ['id', 'product']

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid product_id. Product does not exist.")
        return value

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        user = validated_data.pop('user')

        product = Product.objects.get(id=product_id)
        favorite, created = FavoriteProduct.objects.get_or_create(
            user=user,
            product=product
        )

        if not created:
            raise serializers.ValidationError("This product is already in favorites.")

        return favorite






from .models import ProductTag

class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    tags = ProductTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        source="tags",
        queryset=ProductTag.objects.all(),
        many=True,
        write_only=True
    )
    
    class Meta:
        model = Product
        exclude = ['created_at', 'updated_at']

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        product = Product.objects.create(**validated_data)
        product.tags.set(tags)
        return product

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)
        return super().update(instance, validated_data)


class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        source='products',
        queryset=Product.objects.all(),
        many=True,
        # write_only=True
    )

    class Meta:
        model = Cart
        fields = ["user", 'product_ids', 'products']

    def create(self, validated_data):
        user = validated_data.pop('user')
        products = validated_data.get('products')

        cart, _ = Cart.objects.get_or_create(user=user)
        cart.products.add(*products)

        return 
    


from .models import ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'product']