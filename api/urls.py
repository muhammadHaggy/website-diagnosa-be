from . import views
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path('login/', views.user_login),
    path('register/', views.register_basic_user),
    path('',views.getData),
    path('pred/',views.getPred),
    path('add/', views.addData),
    path('chart-data/', views.chart_data),
    path('score-distribution/', views.score_distribution),
    path('probability-distribution/', views.probability_distribution),
    path('send_email/<int:prediction_id>/', views.send_email_to_submitter, name='send_ipa_prediction_email'),
]
 