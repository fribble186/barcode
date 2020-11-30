from django.urls import path, include

urlpatterns = [
    path('barcode/', include('BarcodeGround.urls')),
    path('daily/', include('daily.urls')),
]
