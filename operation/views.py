from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
from .models import PurchaseMaster, PurchaseDetails, Supplier, Item ,SaleMaster,SaleDetails
from django.db.models import Sum  # Import Sum for aggregation



# purchase views section start

def purchase_list(request):
    purchases = PurchaseMaster.objects.filter(status=1).order_by('-datetime')
    return render(request, 'purchase_list.html' , {'purchases' : purchases })

def purchase_master(request):
    if request.method == "POST":
        # Extract form data
        invoice_no = request.POST.get('invoice_no')
        invoice_date = request.POST.get('invoice_date')
        supplier_id = request.POST.get('supplier_id')
        total_amount = 0  # Initialize total amount

        # Create the PurchaseMaster object
        supplier = Supplier.objects.get(id=supplier_id)
        purchase_master = PurchaseMaster.objects.create(
            invoice_no=invoice_no,
            invoice_date=invoice_date,
            supplier_id=supplier,
            total_amount=0  # This will be updated after PurchaseDetails are added
        )

        # Process the items[] data sent as hidden inputs
        items = request.POST.getlist('items[]')  # Fetch all items[] sent via POST

        # Loop through the items and create PurchaseDetails
        for item in items:
            item_data = item.split(',')  # Format: "item_id,quantity,total"
            item_id = item_data[0]
            quantity = int(item_data[1])
            total = float(item_data[2])

            # Fetch item and price
            item_obj = Item.objects.get(id=item_id)
            price = item_obj.unit_price  # Assuming 'unit_price' is a field in your 'Item' model

            # Create PurchaseDetails record
            PurchaseDetails.objects.create(
                item_id=item_obj,
                quantity=quantity,
                price=price,
                amount=total,
                purchase_master_id=purchase_master  # Using purchase_master_id
            )

            # Update total_amount for PurchaseMaster
            total_amount += total

        # After all PurchaseDetails are added, update the total amount in PurchaseMaster
        purchase_master.total_amount = total_amount
        purchase_master.save()

        # Redirect or render success page
        return redirect('purchase_list')  

    # Render the form (GET request)
    suppliers = Supplier.objects.filter(status=1)
    items = Item.objects.filter(status=1)
    return render(request, 'purchase_master.html', {'suppliers': suppliers, 'items': items})

def purchase_details_view(request, purchase_id):
    # Get the purchase by ID
    purchase_master = get_object_or_404(PurchaseMaster, id=purchase_id)

    # Fetch all related purchase details
    purchase_details = PurchaseDetails.objects.filter(purchase_master_id=purchase_master)

    return render(request, 'purchase_details_view.html', {
        'purchase_master': purchase_master,
        'purchase_details': purchase_details,
    })
    

# Function to fetch item rate via AJAX
def get_item_rate(request):
    item_id = request.GET.get('item_name_id')
    try:
        item = Item.objects.get(id=item_id)
        return JsonResponse({'rate': item.unit_price})
    except Item.DoesNotExist:
        return JsonResponse({'rate': 0})
 
# Function to fetch supplier details  via AJAX   
def get_supplier_details(request):
    supplier_id = request.GET.get('supplier_id')
    try:
        supplier = Supplier.objects.get(id=supplier_id)
        supplier_details = {
           
            'phone': supplier.phone_no,
             'address': supplier.address,

        }
        return JsonResponse({'success': True, 'supplier_details': supplier_details})
    except Supplier.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Supplier not found'})
  
  
# purchase views section end



# sales views section start

def sales_list(request):
    sales = SaleMaster.objects.filter(status=1).order_by("-datetime")
    return render(request,'sales/sales_list.html' ,{'sales':sales} )

def sales_details_view(request,sale_id):
    # Get the sale by ID
    sale_master = get_object_or_404(SaleMaster, id=sale_id)

    # Fetch all related sale details
    sale_details = SaleDetails.objects.filter(sale_master_id=sale_master)

    return render(request, 'sales/sales_details_view.html', {
        'sale_master': sale_master,
        'sale_details': sale_details,
    })

def sales_master(request):
    if request.method == "POST":
        # Extract form data
        invoice_no = request.POST.get('invoice_no')
        invoice_date = request.POST.get('invoice_date')
        supplier_id = request.POST.get('supplier_id')
        total_amount = 0  # Initialize total amount

        # Create the SaleMaster object
        supplier = Supplier.objects.get(id=supplier_id)
        sale_master = SaleMaster.objects.create(
            invoice_no=invoice_no,
            invoice_date=invoice_date,
            customer_id=supplier,
            total_amount=0  # This will be updated after PurchaseDetails are added
        )

        # Process the items[] data sent as hidden inputs
        items = request.POST.getlist('items[]')  # Fetch all items[] sent via POST

        # Loop through the items and create PurchaseDetails
        for item in items:
            item_data = item.split(',')  # Format: "item_id,quantity,total"
            item_id = item_data[0]
            quantity = int(item_data[1])
            total = float(item_data[2])

            # Fetch item and price
            item_obj = Item.objects.get(id=item_id)
            price = item_obj.unit_price  # Assuming 'unit_price' is a field in your 'Item' model

            # Create SaleDetails record
            SaleDetails.objects.create(
                item_id=item_obj,
                quantity=quantity,
                price=price,
                amount=total,
                sale_master_id=sale_master 
            )

            # Update total_amount for SaleMaster
            total_amount += total

        # After all SaleDetails are added, update the total amount in SaleMaster
        sale_master.total_amount = total_amount
        sale_master.save()

        # Redirect or render success page
        return redirect('sales_list')  
    suppliers = Supplier.objects.filter(status=1)
    items = Item.objects.filter(status=1)
    return render(request,'sales/sales_master.html',{"suppliers":suppliers,"items":items} )


def get_available_stock(request):
    item_id = request.GET.get('item_id')
    
    if item_id:
        # Total quantity purchased
        total_purchased = PurchaseDetails.objects.filter(item_id=item_id).aggregate(
            total=Sum('quantity')  # Use Sum to aggregate the quantity field
        )['total'] or 0
        
        # Total quantity sold
        total_sold = SaleDetails.objects.filter(item_id=item_id).aggregate(
            total=Sum('quantity')  # Use Sum to aggregate the quantity field
        )['total'] or 0
        
        # Available stock is purchased - sold
        available_stock = total_purchased - total_sold

        return JsonResponse({'available_stock': available_stock})
    
    return JsonResponse({'error': 'Item not found'}, status=400)