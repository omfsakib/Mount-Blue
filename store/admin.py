from django.contrib import admin
from .models import *

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "phone","date_created")
    search_fields = ("phone", )
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name","price","quantity","get_category")
    list_filter = ("category",)
    search_fields = ("name", )

    def get_category(self, obj):
        return "\n".join([p.name for p in obj.category.all()])
    

admin.site.register(Order)
admin.site.register(Delivery_charge)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(ProductImages)
admin.site.register(Color)
admin.site.register(Size)

admin.site.site_header = "Mount Blue Admin Panel"
admin.site.site_title = "Mount Blue Admin Portal"
admin.site.index_title = "Welcome to Mount Blue Portal"
