from django.urls import path
from . import views

urlpatterns = [
    
    # path for puchase 
    path('purchase/', views.purchase_list, name='purchase_list'),
    path('purchase-master/', views.purchase_master, name='purchase_master'),
    path('get-item-rate/', views.get_item_rate, name='get_item_rate'),
    path('purchase/<int:purchase_id>/', views.purchase_details_view, name='purchase_details_view'),
    path('get-supplier-details/', views.get_supplier_details, name='get_supplier_details'),
    
    
    # path for sales
    path('sale/' , views.sales_list , name='sales_list'),
    path('sale-master/' , views.sales_master , name='sales_master'),
    path('sale-details/<int:sale_id>' , views.sales_details_view , name='sales_details_view'),
    path('get-available-stock/' , views.get_available_stock,name='get_available_stock'),
    
]


