from . import views
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path('login/', views.user_login),
    path('register/', views.register_basic_user),
    path('',views.getData),
    path('pred/',views.getPred),
    path('add/', views.addData)
]
 