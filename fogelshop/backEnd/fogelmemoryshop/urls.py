from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    CartViewSet,
    CartItemViewSet,
    OrderViewSet,
    OrderItemViewSet,
    RegisterAPIView,
SaveOrderView,
CustomLoginView,
UserInfoView,
    AllProductsView,
ScrapeProductsView,
CategoryView,
AddToCartView,
FetchCartView,
CartItemDeleteView,
FetchAmazonItemView,
ValidatePaymentView,
OrderHistoryViewSet,
OrderHistoryView,
ProductView


)
from django.conf import settings
from django.conf.urls.static import static
# יצירת רואטר לנתיבים
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'order-history', OrderHistoryViewSet)  # Add this line



urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterAPIView.as_view(), name='register'),  #
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('user-info/', UserInfoView.as_view(), name='user_info'),
    path('products/', AllProductsView.as_view(), name='all_products'),
    path('single-product/<int:amazonid>/', ProductView.as_view(), name='single_product'),

    path('scrape-products/', ScrapeProductsView.as_view(), name='scrape_products'),
    path('categories/', CategoryView.as_view(), name='categories'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path("cart/", FetchCartView.as_view(), name="fetch_cart"),
    path('cart-item/<int:pk>/', CartItemDeleteView.as_view(), name='cart-item-delete'),
    path('fetch-amazon-item/', FetchAmazonItemView.as_view(), name='fetch_amazon_item'),
    path('api/validate-payment/', ValidatePaymentView.as_view(), name='validate-payment'),
    path('orders-history/', OrderHistoryView.as_view(), name='order'),
    # path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('save-order/', SaveOrderView.as_view(), name='save-order'),

    # User info endpoint

    # נתיב למחלקת ההרשמה

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)