from django.urls import path
from . import views
urlpatterns = [
    
    path('',views.loginView, name='loginPage'),
    path('logout/',views.logoutView, name='logout'),
    path('dashboard/shop-owner/<str:username>/', views.dashboard_shop_owner, name='dashboard_shop_owner'),
    # path('dashboard_shop_owner',views.dashboard_shop_owner, name='dashboard_shop_owner'),
    path('dashboard/shop-owner/<str:username>/add-category/', views.add_category, name='add_category'),
    path('dashboard/shop-owner/<str:username>/add-product/', views.add_product, name='add_product'),




    path('dashboard/shop-manager/<str:username>/', views.dashboard_shop_manager, name='dashboard_shop_manager'),
    # path('dashboard_shop_manager',views.dashboard_shop_manager, name='dashboard_shop_manager'),
    path('dashboard/chef/<str:username>/', views.dashboard_chef, name='dashboard_chef'),


    # path('dashboard_chef',views.dashboard_chef, name='dashboard_chef'),
    path('change-password/',views.changePasswordView, name ='changePassword'),
    path('forgot-password/', views.forgotPasswordView, name='forgotPassword'),

]
