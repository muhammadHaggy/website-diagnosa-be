from . import views
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('',views.getData),
    path('pred/',views.getPred),
    path('add/', views.addData)
]
 