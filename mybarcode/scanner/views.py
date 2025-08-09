import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return render(request, 'scanner/home.html')

def get_products_dict():
    products_file = os.path.join(os.path.dirname(__file__), 'products.txt')
    products = {}
    try:
        with open(products_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    parts = line.split('=')
                    if len(parts) == 3:
                        bcode, name, image_folder = parts
                    elif len(parts) == 2:
                        bcode, name = parts
                        image_folder = 'images'  # default folder
                    else:
                        continue
                    products[bcode] = {
                        'name': name,
                        'image_folder': image_folder,
                    }
    except FileNotFoundError:
        print("products.txt bulunamadı!")
    return products

@csrf_exempt
def check_barcode(request):
    if request.method == "POST":
        data = json.loads(request.body)
        barcode = data.get('barcode')

        products = get_products_dict()
        product = products.get(barcode)

        if product:
            image_url = f"/static/{product['image_folder']}/{barcode}.jpg"
            scanned_products = request.session.get('scanned_products', [])
            if barcode not in scanned_products:
                scanned_products.append(barcode)
                request.session['scanned_products'] = scanned_products
                request.session.modified = True

            return JsonResponse({
                "product_name": product['name'],
                "product_image": image_url,
                "scanned_products": scanned_products,
            })
        else:
            return JsonResponse({
                "product_name": "Ürün bulunamadı",
            })
    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def update_product_quantity(request):
    if request.method == "POST":
        data = json.loads(request.body)
        barcode = data.get('barcode')
        action = data.get('action')  # 'increase' veya 'decrease'

        cart = request.session.get('cart', {})

        if barcode not in cart:
            if action == 'increase':
                cart[barcode] = 1
        else:
            if action == 'increase':
                cart[barcode] += 1
            elif action == 'decrease':
                cart[barcode] = max(1, cart[barcode] - 1)

        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({
            "barcode": barcode,
            "quantity": cart.get(barcode, 0)
        })
    return JsonResponse({"error": "Invalid method"}, status=405)