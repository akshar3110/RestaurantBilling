from django.urls import path
from . import views
urlpatterns = [
    
    path('dashboard/',views.loginView, name='loginPage'),
    path('logout/',views.logoutView, name='logout'),
    path('dashboard/shop-owner/<str:username>/', views.dashboard_shop_owner, name='dashboard_shop_owner'),
    # path('dashboard_shop_owner',views.dashboard_shop_owner, name='dashboard_shop_owner'),
    path('dashboard/shop-owner/<str:username>/add-category/', views.add_category, name='add_category'),
    path('dashboard/shop-owner/<str:username>/add-product/', views.add_product, name='add_product'),




    path('dashboard/shop-manager/<str:username>/', views.dashboard_shop_manager, name='dashboard_shop_manager'),
    # path('dashboard_shop_manager',views.dashboard_shop_manager, name='dashboard_shop_manager'),
    path('dashboard/chef/<str:username>/', views.dashboard_chef, name='dashboard_chef'),


    # path('dashboard_chef',views.dashboard_chef, name='dashboard_chef'),
    path('dashboard/shop-owner/<str:username>/change-password/',views.changePasswordView, name ='changePassword'),
    path('forgot-password/', views.forgotPasswordView, name='forgotPassword'),

    #view categories page
    path('dashboard/shop-owner/<str:username>/view-categories/',views.viewCategories, name ='viewCategories'),
    path('dashboard/shop-owner/<str:username>/edit-category/<int:category_id>/', views.editCategory, name='editCategory'),

    path('dashboard/shop-owner/<str:username>/delete-category/<int:category_id>/', views.deleteCategory, name='deleteCategory'),

    path('dashboard/shop-owner/<str:username>/view-products/', views.view_products, name='viewProducts'),
    
    # path('dashboard/shop-owner/<str:username>/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('dashboard/shop-owner/<str:username>/delete-product/<int:product_id>/', views.deleteProduct, name='delete_product'),



]

