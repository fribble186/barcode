from django.urls import path
from daily import views

urlpatterns = [
    path('my_dream/', views.Dream.as_view()),
    path('user/login', views.AuthView.as_view()),
    path('user/get_sms', views.GetSms.as_view()),
    path('user/change_account', views.Account.as_view()),
    path('friend/', views.Friend.as_view()),
    path('sparklers/', views.Sparklers.as_view()),
    path('stranger/', views.Stranger.as_view()),
]