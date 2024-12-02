
from scrapy.selector import Selector

from rest_framework import viewsets
from .models import Category, Product, Cart, CartItem, Order, OrderItem,OrderHistory
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
OrderHistorySerializer,
)
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated


from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView




class OrderHistoryViewSet(viewsets.ModelViewSet):
    queryset = OrderHistory.objects.all()
    serializer_class = OrderHistorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# ViewSet for Product
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# ViewSet for Cart
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

# ViewSet for CartItem
class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

# ViewSet for Order
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

# ViewSet for OrderItem
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class RegisterAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response({"detail": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"detail": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "detail": "User created successfully.",
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)


class CustomLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Generate tokens for the authenticated user
            refresh = RefreshToken.for_user(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
        })

class AllProductsView(APIView):
        def get(self, request):
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)








class ScrapeProductsView(APIView):
    def post(self, request):
        # Get target URL and category ID from request
        target_url = request.data.get("url")
        category_id = request.data.get("category")

        if not target_url or not category_id:
            return Response({"error": "URL and category are required"}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1'
        }

        try:
            # Fetch the content of the URL
            response = requests.get(target_url, headers=headers)
            if response.status_code != 200:
                return Response(
                    {"error": "Failed to fetch the URL", "status_code": response.status_code},
                    status=response.status_code
                )

            # Parse the response content
            sel = Selector(text=response.text)
            products = []

            # Select product elements
            heads = sel.xpath("//*[@class='sg-col-inner']")
            print(f"Number of products found: {len(heads)}")

            # Ensure the category exists
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

            for head in heads:
                try:
                    title = head.xpath(".//*[@class='a-size-base-plus a-color-base a-text-normal']/text()").extract_first()
                    price = head.xpath(".//*[@class='a-offscreen']//text()").extract_first()
                    image_url = head.xpath(".//*[@class='a-section aok-relative s-image-square-aspect']/img/@src").extract_first()
                    link = head.xpath(".//*[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']/@href").extract_first()

                    # Validate the link to ensure it doesn't start with `/sspa/clic`
                    if link and not link.startswith('/sspa/clic'):
                        full_link = link
                    else:
                        full_link = None

                    print(f"Scraped product - Title: {title}, Price: {price}, Image URL: {image_url}, Link: {full_link}")

                    if title and price and image_url and full_link:
                        # Convert price to decimal format
                        try:
                            numeric_price = float(price.replace('ILS', '').replace('$', '').replace(',', '').strip())
                        except ValueError:
                            numeric_price = 0.0  # Default price if parsing fails

                        # Save the product to the database
                        product = Product.objects.create(
                            name=title,
                            description=full_link,  # Save the full link as the description for now
                            price=numeric_price,
                            image_url=image_url,
                            stock=10,  # Default stock value
                            category=category,
                        )

                        # Append the saved product to the response list
                        products.append({
                            "id": product.id,
                            "name": product.name,
                            "price": product.price,
                            "image_url": product.image_url,
                            "link": full_link,
                        })
                except Exception as product_error:
                    print(f"Error processing product: {product_error}")

            return Response({"message": "Products scraped and saved successfully", "products": products}, status=status.HTTP_201_CREATED)

        except requests.RequestException as req_error:
            print(f"Request error: {req_error}")
            return Response({"error": "Failed to fetch the target URL. Check the URL and try again."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Server Error: {e}")
            return Response({"error": "An internal server error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Get or create the CartItem
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if cart_item.quantity == 1:
             cart_item.quantity=cart_item.quantity-1
             cart_item.quantity += quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()

        return Response({"message": "Product added to cart successfully"}, status=status.HTTP_200_OK)
class FetchCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=200)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart is empty."}, status=404)


class CartItemDeleteView(APIView):
    def delete(self, request, pk):
        try:
            # Get the cart item by its primary key (pk)
            cart_item = CartItem.objects.get(pk=pk)

            # Ensure the cart item belongs to the logged-in user
            if cart_item.cart.user != request.user:
                return Response({"error": "You are not authorized to delete this item."}, status=status.HTTP_403_FORBIDDEN)

            # Delete the cart item
            cart_item.delete()
            return Response({"message": "Cart item deleted successfully."}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from parsel import Selector


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from parsel import Selector
from django.shortcuts import get_object_or_404


class FetchAmazonItemView(APIView):
    def get(self, request):
        try:
            # Get and validate query parameters
            amazon_item_id = request.query_params.get("id")

            amazon_item_product = request.query_params.get("product")

            if not amazon_item_id:
                return Response(
                    {"error": "Amazon Item ID is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not amazon_item_product:
                return Response(
                    {"error": "Product ID is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the product safely
            try:
                product = Product.objects.get(id=amazon_item_product)
                product_serializer = ProductSerializer(product, context={'request': request})
            except (ValueError, Product.DoesNotExist):
                return Response(
                    {"error": "Invalid product ID or product not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Clean and construct Amazon URL
            amazon_url = f"{amazon_item_id.strip()}"

            cleaned_text = amazon_url.strip("{")
            cleaned_text = cleaned_text.strip("}")

            amazon_url = "https://www.amazon.com" + cleaned_text
            print(amazon_url)



            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'DNT': '1'
            }

            # Fetch Amazon page with timeout and error handling
            try:
                response = requests.get(amazon_url, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.Timeout:
                return Response(
                    {"error": "Request timed out"},
                    status=status.HTTP_504_GATEWAY_TIMEOUT
                )
            except requests.ConnectionError:
                return Response(
                    {"error": "Failed to connect to Amazon"},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            except requests.RequestException as e:
                return Response(
                    {"error": f"Request failed: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Parse content
            sel = Selector(text=response.text)
            product_description = sel.xpath("//*[@id='productDescription']/p/span/text()").extract_first()

            if not product_description:
                # Try alternative xpath if first one fails
                product_description = sel.xpath("//div[@id='productDescription']//text()").extract_first()
                if not product_description:
                    return Response(
                        {"error": "Product description not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )

            return Response({
                "description": product_description.strip(),
                "product": product_serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Log unexpected errors
            import traceback
            print(f"Unexpected error: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
import paypalrestsdk


PAYPAL_CLIENT_ID = 'AW4X8xS_gvNoFFOwHmnjqsptF7F9oGKRl1nF_zcokJMguTzhztUAwx5LbF2cmmEU3e-jpHsfFMXOVKBN'
PAYPAL_SECRET = 'EKoKF5ShPE1mABpdeTjaxIY93Q4CLVH-CK1EH3cc00LMGtAXKapvQPILZkYrl0PQ1tPyMgzOVKyvr7O7'

# PayPal SDK configuration
paypalrestsdk.configure({
    "mode": "sandbox",  # or "live" for production
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_SECRET,
})
# class CheckoutView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         user = request.user
#         cart = Cart.objects.filter(user=user).first()
#
#         if not cart or not cart.items.exists():
#             return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Calculate total amount
#         total_amount = 0
#         items = []
#         for item in cart.items.all():
#             total_amount += item.product.price * item.quantity
#             items.append({
#                 "name": item.product.name,
#                 "sku": str(item.product.id),
#                 "price": f"{item.product.price:.2f}",
#                 "currency": "USD",
#                 "quantity": item.quantity,
#             })
#
#         # Create PayPal payment
#         payment = paypalrestsdk.Payment({
#             "intent": "sale",
#             "payer": {
#                 "payment_method": "paypal",
#             },
#             "redirect_urls": {
#                 "return_url": "http://127.0.0.1:8000/api/payment-success/",
#                 "cancel_url": "http://127.0.0.1:8000/api/payment-cancel/",
#             },
#             "transactions": [{
#                 "item_list": {"items": items},
#                 "amount": {
#                     "total": f"{total_amount:.2f}",
#                     "currency": "USD",
#                 },
#                 "description": f"Order by {user.username}",
#             }]
#         })
#
#         if payment.create():
#             approval_url = payment["links"][1]["href"]  # Get PayPal approval URL
#             return Response({"approval_url": approval_url}, status=status.HTTP_200_OK)
#         else:
#             return Response({"error": payment.error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
# class PaymentCancelView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         return Response({"message": "Payment cancelled."}, status=status.HTTP_200_OK)
# class PaymentSuccessView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         payment_id = request.query_params.get("paymentId")
#         payer_id = request.query_params.get("PayerID")
#
#         if not payment_id or not payer_id:
#             return Response({"error": "Missing payment details"}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             payment = paypalrestsdk.Payment.find(payment_id)
#
#             if payment.execute({"payer_id": payer_id}):
#                 # Mark the order as paid, clear the cart
#                 user = request.user
#                 Cart.objects.filter(user=user).delete()
#                 return Response({"message": "Payment successful!"}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"error": payment.error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class ValidatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the order details from the request
            order_data = request.data

            # Log the received data for debugging
            print("Received payment data:", order_data)

            # Here you would typically:
            # 1. Validate the payment
            # 2. Create an order in your database
            # 3. Clear the user's cart
            # 4. Send confirmation email, etc.

            return Response({
                "status": "success",
                "message": "Payment validated successfully"
            })

        except Exception as e:
            print(f"Error processing payment: {str(e)}")
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class OrderHistoryView(APIView):
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Add debug prints
        print(f"Current user: {request.user}")
        print(f"Is user authenticated: {request.user.is_authenticated}")

        orders = OrderHistory.objects.filter(user=request.user)

        # Debug the queryset
        print(f"Total orders found: {orders.count()}")

        serializer = OrderHistorySerializer(orders, many=True,context={'request': request})
        return Response(serializer.data)
class SaveOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Create order history
            order = OrderHistory.objects.create(
                user=request.user,
                transaction_id=request.data['transaction_id'],
                total_amount=request.data['total_amount'],
                payer_email=request.data['payer_email'],
                payer_name=request.data['payer_name'],
                status='completed'
            )

            return Response({
                'status': 'success',
                'message': 'Order saved successfully',
                'order_id': order.id
            })

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ProductView(APIView):
    def get(self, request, amazonid=None):
        if amazonid:
            try:

                products = Product.objects.filter(category=amazonid)
                if not products.exists():
                    return Response({'error': 'No products found in this category'}, status=status.HTTP_404_NOT_FOUND)

                serializer = ProductSerializer(products, many=True)  # `many=True` because filter() returns a queryset
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
