from django.urls import path
from . import views

urlpatterns = [
    path('stock-report/', views.stock_list , name='stock_list'),
    path('detailed-report/', views.detailed_report , name='detailed_report'),
]



    
   
