import json
from pathlib import Path
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.templatetags.static import static
from django.conf import settings

APP_DIR = Path(__file__).resolve().parent
PRODUCTS_FILE = APP_DIR / "products.txt"
_PRODUCT_CACHE = None


def _load_products():
    """products.txt dosyasını (BARCODE=NAME) formatında yükler."""
    global _PRODUCT_CACHE
    if _PRODUCT_CACHE is not None:
        return _PRODUCT_CACHE

    mapping = {}
    if PRODUCTS_FILE.exists():
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or "=" not in line:
                    continue
                parts = line.split("=")
                barcode = parts[0].strip()
                name = parts[1].strip() if len(parts) > 1 else ""
                if barcode:
                    mapping[barcode] = {"name": name}
    _PRODUCT_CACHE = mapping
    return mapping


def home(request: HttpRequest) -> HttpResponse:
    cart = request.session.get("cart", {})
    context = {"cart": cart}
    return render(request, "home.html", context)


@csrf_exempt
def check_barcode(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}

    barcode = str(payload.get("barcode", "")).strip()
    products = _load_products()
    info = products.get(barcode)

    if not info:
        return JsonResponse({
            "product_name": "Ürün bulunamadı",
            "product_image": static("images/placeholder.png"),
            "barcode": barcode
        })

    # görseli doğrudan barkod.jpg olarak veriyoruz
    img_url = static(f"images/{barcode}.jpg")

    return JsonResponse({
        "product_name": info["name"],
        "product_image": img_url,
        "barcode": barcode
    })


@csrf_exempt
def update_product_quantity(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}

    barcode = str(payload.get("barcode", "")).strip()
    action = payload.get("action", "increase")
    cart = request.session.get("cart", {})

    if action == "increase":
        cart[barcode] = int(cart.get(barcode, 0)) + 1
    elif action == "decrease":
        qty = int(cart.get(barcode, 0)) - 1
        if qty > 0:
            cart[barcode] = qty
        else:
            cart.pop(barcode, None)

    request.session["cart"] = cart
    return JsonResponse({"quantity": cart.get(barcode, 0)})