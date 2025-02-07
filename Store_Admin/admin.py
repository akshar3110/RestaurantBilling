from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Cafe, Role, Category, Product
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'phone_number', 'cafe', 'role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'role__role_name')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'cafe', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'cafe', 'role')}),
    )

@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ('cafe_name', 'address', 'phone_number', 'email')
    search_fields = ('cafe_name',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name',)
    search_fields = ('role_name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category__name')