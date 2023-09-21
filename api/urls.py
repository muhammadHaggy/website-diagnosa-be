from . import views
from django.urls import path

urlpatterns = [
    path('',views.getData),
    path('pred/',views.getPred),
    path('add/', views.addData)
]
 