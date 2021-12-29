from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_page, name='register'),

    path('mobile-features/', views.template_page, name='mobile-features'),
    path('web-features/', views.template_page, name='web-features'),

    path('', views.home, name='home'),

]
