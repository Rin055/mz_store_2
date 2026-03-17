from django.contrib import admin
from .models import Product, ProductImage, ProductTag, FavoriteProduct, Cart, Review


admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductTag)
admin.site.register(FavoriteProduct)
admin.site.register(Cart)
admin.site.register(Review)
