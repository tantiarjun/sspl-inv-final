from django.shortcuts import render
from operation.models import PurchaseDetails,SaleDetails
from master.models import Item
from django.db.models import Sum
from django.db.models import Q
from django.utils.dateparse import parse_date
from datetime import datetime,timedelta
from django.http import JsonResponse
from django.db import connection # Use this to execute raw SQL


def stock_list(request):

    # SQL query to get total purchased, sold, and available stock for each item
    stock_query = """
    SELECT 
        master_item.item_name, 
        COALESCE(SUM(purchase.quantity), 0) AS total_purchased, 
        COALESCE(SUM(sale.quantity), 0) AS total_sold, 
        COALESCE(SUM(purchase.quantity), 0) - COALESCE(SUM(sale.quantity), 0) AS available_stock
    FROM 
        master_item
    LEFT JOIN operation_purchasedetails AS purchase 
        ON master_item.id = purchase.item_id_id
    LEFT JOIN operation_saledetails AS sale 
        ON master_item.id = sale.item_id_id
    WHERE master_item.status=true 
    GROUP BY 
        master_item.item_name;
    """

    # Execute the SQL query and fetch the results
    with connection.cursor() as cursor:
        cursor.execute(stock_query)
        stock_data = cursor.fetchall()  
    
    context = {
        'stock_data': stock_data,
    }
    return render(request, 'stock-report/stock_list.html', context)


def detailed_report(request):
    items = Item.objects.filter(status=1)

    # Get query params
    item_name = request.GET.get('item', '')
    from_date = request.GET.get('fromdate', '1900-01-01')  # Default to earliest date
    to_date = request.GET.get('todate', str(datetime.now().date()))  # Default to current date
    report_type = request.GET.get('type', 'purchase')  # Default to purchase type

    # Convert string to date
    from_date = parse_date(from_date) or datetime.strptime('1900-01-01', '%Y-%m-%d').date()
    to_date = (parse_date(to_date) or datetime.now().date()) + timedelta(days=1)  # Add one day to include current day fully

    stock_data = []

    # Base SQL query, which we will modify based on report type (purchase/sale)
    base_query = """
    SELECT 
        item_name, 
        unit_price, 
        quantity, 
        amount, 
        opsd.datetime,
        supplier_name 
    FROM 
        {operation_purchase_ya_sale_details} opsd
    LEFT JOIN 
        master_item on master_item.id = opsd.item_id_id 
    LEFT JOIN 
        {operation_purchase_ya_sale_master} opsm ON opsm.id = opsd.{purchase_ya_sale_master_id_id} 
    LEFT JOIN 
       master_supplier on master_supplier.id = opsm.{supplier_ya_customer_id_id}
    WHERE 
        opsd.datetime BETWEEN '{from_date}' AND '{to_date}'
    
    """

    # Modify query based on report_type
    if report_type == 'purchase':
        query = base_query.format(
            operation_purchase_ya_sale_details="operation_purchasedetails",
            operation_purchase_ya_sale_master="operation_purchasemaster",
            purchase_ya_sale_master_id_id="purchase_master_id_id",
            supplier_ya_customer_id_id="supplier_id_id",
            from_date=from_date,
            to_date=to_date
        )
    else:  # report_type == 'sales'
        query = base_query.format(
            operation_purchase_ya_sale_details="operation_saledetails",
            operation_purchase_ya_sale_master="operation_salemaster",
            purchase_ya_sale_master_id_id="sale_master_id_id ",
            supplier_ya_customer_id_id="customer_id_id",
            from_date=from_date,
            to_date=to_date
        )

    # Add item filter if item_name is provided
    if item_name:
        query += f" AND item_name LIKE '%{item_name}%'"

    # Execute the SQL query and fetch the data
    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    # Process fetched data
    for result in results:
        stock_data.append({
            'item_name': result[0],  # item_name
            'item_price': result[1],  # item_price
            'quantity': result[2],  # quantity
            'total_price': result[3],  # total_price
            'datetime': result[4].strftime("%d-%m-%Y"),  # datetime
            'supplier_or_customer': result[5]  # supplier_or_customer_id (use the name if needed)
        })

    # Handle AJAX request for JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'stock_data': stock_data})

    # Pass the stock data and items to the template
    context = {
        'stock_data': stock_data,
        'items': items,
    }

    return render(request, 'detailed-report/detailed_report.html', context)




# def detailed_report(request):
#     items = Item.objects.filter(status=1)
    
#     # Get query params
#     item_name = request.GET.get('item', '')
#     from_date = request.GET.get('fromdate', '1900-01-01')  # Default to earliest date
#     to_date = request.GET.get('todate', str(datetime.now().date()))  # Default to current date
#     report_type = request.GET.get('type', 'purchase')  # Default to purchase type

#     # Convert string to date
#     from_date = parse_date(from_date) or datetime.strptime('1900-01-01', '%Y-%m-%d').date()
#     to_date = parse_date(to_date) or datetime.now().date()

#     stock_data = []

#     if report_type == 'purchase':
#         # Fetch purchase data
#         purchases = PurchaseDetails.objects.filter(datetime__date__range=[from_date, to_date] , item_id__status=1).order_by('-datetime')

#         if item_name:
#             purchases = purchases.filter(item_id__item_name__icontains=item_name)
#             purchases = purchases.filter(item_id__status=1)
           

#         for purchase in purchases:
#             stock_data.append({
#                 'item_name': purchase.item_id.item_name,  
#                 'quantity': purchase.quantity,
#                 'total': purchase.amount,
#                 'created_at': purchase.datetime,
#                 'supplier_or_customer': purchase.purchase_master_id.supplier_id.supplier_name
#             })

#     elif report_type == 'sales':
#         # Fetch sales data
#         sales = SaleDetails.objects.filter(datetime__date__range=[from_date, to_date], item_id__status=1).order_by('-datetime')
        
#         if item_name:
#             sales = sales.filter(item_id__item_name__icontains=item_name)
#             sales = sales.filter(item_id__status=1)
            
#         for sale in sales:
#             stock_data.append({
#                 'item_name': sale.item_id.item_name,
#                 'quantity': sale.quantity,
#                 'total': sale.amount,
#                 'created_at': sale.datetime,
#                 'supplier_or_customer': sale.sale_master_id.customer_id.supplier_name
#             })

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         return JsonResponse({'stock_data': stock_data})

    
#     context = {
#         'stock_data': stock_data,
#         'items': items
#     }


#     return render(request, 'detailed-report/detailed_report.html', context)





















# def stock_list(request):
#     # SQL query to fetch total purchased quantity per item
#     purchase_query = """
#     SELECT item_name, SUM(quantity) AS Total_purchased_quantity
#     FROM operation_purchasedetails
#     INNER JOIN master_item ON master_item.id = operation_purchasedetails.item_id_id
#     WHERE master_item.status=true
#     GROUP BY item_name;
#     """

#     # SQL query to fetch total sold quantity per item
#     sale_query = """
#     SELECT item_name, SUM(quantity) AS Total_sold_quantity
#     FROM operation_saledetails
#     INNER JOIN master_item ON master_item.id = operation_saledetails.item_id_id
#     WHERE master_item.status=true
#     GROUP BY item_name;
#     """

#     # Execute the purchase and sale query and fetch results
#     with connection.cursor() as cursor:
#         cursor.execute(purchase_query)
#         purchased_data = cursor.fetchall()  # Returns a list of tuples (item_name, total_purchased_quantity)
#         cursor.execute(sale_query)
#         sold_data = cursor.fetchall()  # Returns a list of tuples (item_name, total_sold_quantity)
        

#     # Combine the purchase and sale data into a final stock_data list
#     stock_data = []

#     # Convert the raw SQL data into a usable dictionary format
#     for purchase in purchased_data:
#         item_name = purchase[0]
#         total_purchased = purchase[1]
#         # Find the corresponding sale data
#         total_sold = next((sale[1] for sale in sold_data if sale[0] == item_name), 0)
#         available_stock = total_purchased - total_sold

#         stock_data.append({
#             'item_name': item_name,
#             'total_purchased': total_purchased,
#             'total_sold': total_sold,
#             'available_stock': available_stock
#         })

#     # Pass the stock data to the template
#     context = {
#         'stock_data': stock_data,
#     }
#     return render(request, 'stock-report/stock_list.html', context)

# def stock_list(request):
#     # Initialize an empty stock data list
#     stock_data = []

#     # SQL query to get total purchased quantity for each item
#     purchased_query = """
#         SELECT master_item.item_name, SUM(operation_purchasedetails.quantity) AS total_purchased_quantity
#         FROM operation_purchasedetails
#         INNER JOIN master_item ON master_item.id = operation_purchasedetails.item_id_id
#         GROUP BY master_item.item_name
#     """

#     # SQL query to get total sold quantity for each item
#     sold_query = """
#         SELECT master_item.item_name, SUM(operation_saledetails.quantity) AS total_sold_quantity
#         FROM operation_saledetails
#         INNER JOIN master_item ON master_item.id = operation_saledetails.item_id_id
#         GROUP BY master_item.item_name
#     """

#     # Fetch total purchased quantity
#     with connection.cursor() as cursor:
#         cursor.execute(purchased_query)
#         purchased_results = cursor.fetchall()  # List of tuples (item_name, total_purchased_quantity)

#     # Fetch total sold quantity
#     with connection.cursor() as cursor:
#         cursor.execute(sold_query)
#         sold_results = cursor.fetchall()  # List of tuples (item_name, total_sold_quantity)

#     # Convert the purchased and sold results to dictionaries for easier lookup
#     purchased_dict = {row[0]: row[1] for row in purchased_results}
#     sold_dict = {row[0]: row[1] for row in sold_results}

#     # Combine the results and calculate available stock
#     for item_name, total_purchased in purchased_dict.items():
#         total_sold = sold_dict.get(item_name, 0)  # Get the sold quantity or 0 if not found
#         available_stock = total_purchased - total_sold

#         # Append data to stock_data list
#         stock_data.append({
#             'item_name': item_name,
#             'total_purchased': total_purchased,
#             'total_sold': total_sold,
#             'available_stock': available_stock
#         })

#     # Pass the stock data to the template
#     context = {
#         'stock_data': stock_data,
#     }
#     return render(request, 'stock-report/stock_list.html', context)

# def stock_list(request):
#     # Fetch all items
#     items = Item.objects.filter(status=1)

#     # Prepare data for each item with total purchased, sold, and available stock
#     stock_data = []
#     for item in items:
#         # Total quantity purchased for the item
#         total_purchased = PurchaseDetails.objects.filter(item_id=item.id).aggregate(
#             total_purchased=Sum('quantity')
#         )['total_purchased'] or 0
        
        
#         # Total quantity sold for the item
#         total_sold = SaleDetails.objects.filter(item_id=item.id).aggregate(
#             total_sold=Sum('quantity')
#         )['total_sold'] or 0
        
#         # Available stock is purchased quantity - sold quantity
#         available_stock = total_purchased - total_sold

#         # Add data to stock_data list
#         stock_data.append({
#             'item_name': item.item_name,
#             'total_purchased': total_purchased,
#             'total_sold': total_sold,
#             'available_stock': available_stock
#         })

#     # Pass the stock data to the template
#     context = {
#         'stock_data': stock_data,
#     }
#     return render(request,'stock-report/stock_list.html',context)





# def detailed_report(request):
#     items = Item.objects.filter(status=1)
#     Purchase_details = PurchaseDetails.objects.filter(status=1)
    
#     context = {
#         'items': items,
#         'Purchase_details': Purchase_details,
#     }
    
#     return render(request,'detailed-report/detailed_report.html',context)
    




































