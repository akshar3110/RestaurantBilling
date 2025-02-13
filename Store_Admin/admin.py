from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Cafe, Role, Category, Product
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'phone_number', 'cafe', 'role', 'is_staff', 'is_superuser')
    # search_fields = ('username', 'email', 'role__role_name')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'cafe', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email','phone_number', 'cafe', 'role')}),
    )
    list_filter = ('cafe',)

@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ('is_active','cafe_name', 'email')
    list_filter = ('is_active',)
    # search_fields = ('cafe_name',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name',)
    # search_fields = ('role_name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at','cafe')
    list_filter = ('cafe',)
    # search_fields = ('name','cafe')



class ProductAdmin(admin.ModelAdmin):
    list_display = ('is_active', 'get_cafe_name', 'name', 'category', 'price',)
    list_filter = ('category__cafe__cafe_name', 'is_active')

    def get_cafe_name(self, obj):
        return obj.category.cafe.cafe_name  # ✅ Show café name instead of ID
    get_cafe_name.admin_order_field = 'category__cafe__cafe_name'
    get_cafe_name.short_description = 'Cafe Name'

admin.site.register(Product, ProductAdmin)