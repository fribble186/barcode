from django.urls import path
from BarcodeGround import views

urlpatterns = [
    path('wx_login/', views.AuthView.as_view()),
    path('get_barcode_info/', views.BarcodeInfo.as_view()),
    path('post_comment/', views.Comment.as_view())
]