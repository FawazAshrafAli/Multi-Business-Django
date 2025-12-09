from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import Q, Count, F, Sum, DecimalField
from django.db.models.functions import Cast
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework.decorators import action

User = get_user_model()

from company_api.serializers import CompanySerializer
from .serializers import (
    ProductCategorySerializer, DetailSerializer, ProductSerializer, 
    EnquirySerializer, ProductSubCategorySerializer, ReviewSerializer,
    MultiPageSerializer, MiniProductDetailSerializer, DetailListSerializer,
    MiniProductCategorySerializer, HomeProductCategorySerializer,
    CartSerializer, AddressSerializer, OrderSerializer
    )
from product.models import (
    ProductDetailPage, Category, Product, Enquiry, SubCategory, 
    Review, MultiPage, Cart, DeliveryAddress, Order, OrderPlacedCart, 
    OrderPlacedAddress
    )
from company.models import Company
from .paginations import ProductDetailPagination

import logging

logger = logging.getLogger(__name__)

class ProductCompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.filter(type__name = "Product").order_by("name")
    lookup_field = "slug"


class ProductViewset(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")        

        if company_slug:
            return Product.objects.filter(company__slug = company_slug)
        
        return Product.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProductDetailViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = DetailSerializer
    pagination_class = ProductDetailPagination
    lookup_field = "slug"

    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        q = self.request.query_params.get("q")
        catalog = self.request.query_params.get("catalog")
        category = self.request.query_params.get("category")
        sub_category = self.request.query_params.get("sub_category")

        if company_slug:
            if company_slug == "all":
                return ProductDetailPage.objects.all()

            filters = {"company__slug": company_slug}
            
            if category:
                filters["product__category__slug"] = category

            if sub_category:
                filters["product__sub_category__slug"] = sub_category

            if catalog:
                filters["product__sub_category__slug"] = catalog

            details = ProductDetailPage.objects.filter(**filters)

            if q:
                details = details.filter(
                    Q(product__name__icontains = q) |
                    Q(product__category__name__icontains = q) |
                    Q(product__sub_category__name__icontains = q) |
                    Q(product__brand__name__icontains = q)
                )

            return details.select_related(
                "product", "company"
            ).prefetch_related(
                "meta_tags", "features", "bullet_points", "timelines",
            )
        
        return ProductDetailPage.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class DetailListViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = DetailListSerializer
    pagination_class = ProductDetailPagination
    lookup_field = "slug"

    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        q = self.request.query_params.get("q")
        catalog = self.request.query_params.get("catalog")
        category = self.request.query_params.get("category")
        sub_category = self.request.query_params.get("sub_category")

        filters = {}
        queryset = ProductDetailPage.objects.none()        

        if category:
            filters["product__category__slug"] = category

        if sub_category or catalog:
            filters["product__sub_category__slug"] = sub_category or catalog        

        if company_slug:
            queryset = ProductDetailPage.objects.all()

            if company_slug != "all":
                filters["company__slug"] = company_slug

            queryset = queryset.filter(**filters)   

        if q:
            queryset = queryset.filter(
                Q(product__name__icontains = q) |
                Q(product__category__name__icontains = q) |
                Q(product__sub_category__name__icontains = q) |
                Q(product__brand__name__icontains = q)
            )         

        return queryset.select_related(
                "company", "product"
            )
    

class ProductSliderDetailViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = MiniProductDetailSerializer
    pagination_class = ProductDetailPagination
    lookup_field = "slug"

    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")        

        if company_slug:
            if company_slug == "all":
                return (
                    ProductDetailPage.objects.select_related("product")
                    .only(
                        "id", "slug", "meta_description",
                        "meta_title", "product"
                        )
                    .order_by("?")[:12]
                )

            filters = {"company__slug": company_slug}                        

            details = (
                ProductDetailPage.objects.filter(**filters)
                .select_related("product")
                .only(
                    "id", "slug", "meta_description",
                    "meta_title", "product"
                    )
                .order_by("?")[:12]
                )

            return details
        
        return ProductDetailPage.objects.none()
    

class MinProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MiniProductCategorySerializer
    lookup_field = "slug"
    
    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        if company_slug:
            return Category.objects.filter(
                company__slug = company_slug
                ).select_related(
                    "company"
                )
        
        return Category.objects.none()


class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductCategorySerializer
    lookup_field = "slug"
    
    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        if company_slug:
            return Category.objects.filter(
                company__slug = company_slug
            ).select_related(
                "company"
            )
        
        return Category.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class HomeProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HomeProductCategorySerializer
    lookup_field = "slug"
    
    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        if company_slug:
            return Category.objects.filter(
                company__slug = company_slug
            ).select_related(
                "company"
            )
        
        return Category.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class ProductMultipageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MultiPageSerializer
    lookup_field = "slug"
    
    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        if company_slug:
            return MultiPage.objects.filter(
                company__slug = company_slug
            ).select_related(
                "product", "company"
            ).prefetch_related(
                "meta_tags", "features", "bullet_points", "timelines", "faqs",
                "text_editors"
            )
            
        return MultiPage.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class ProductSubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSubCategorySerializer
    pagination_class = ProductDetailPagination
    lookup_field = "slug"
    
    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")
        category_slug = self.request.query_params.get("category")
        location_slug = self.request.query_params.get("location_slug")
        listing_type = self.request.query_params.get("listing_type")

        if company_slug:
            filters = {}

            if company_slug != "all":
                filters = {"company__slug": company_slug}

            if category_slug:
                filters["category__slug"] = category_slug

            if listing_type == "location":
                filters["hide_from_main_listing"] = False

            slug_filters = Q()

            if location_slug:
                slug_filters = Q(location_slug=location_slug) | Q(slug=location_slug)

            return SubCategory.objects.annotate(count = Count("products")).filter(
                **filters
                ).filter(
                    slug_filters
                ).filter(
                    count__gt = 0
                ).select_related(
                    "company", "category"
                ).order_by("-updated")
        
        return SubCategory.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class EnquiryViewSet(viewsets.ModelViewSet):
    serializer_class = EnquirySerializer
    http_method_names = ["post", "get"]
    permission_classes = [AllowAny]    

    def get_queryset(self):
        return Enquiry.objects.filter(company__slug=self.kwargs.get("company_slug")) if self.kwargs.get("company_slug") else Enquiry.objects.none()

    def create(self, request, *args, **kwargs):
        response_data = {
            "success": False,
            "message": "Validation Failed",
            "errors": None
        }

        try:
            company_slug = self.kwargs.get("company_slug")
            if not company_slug:
                response_data["message"] = "Company identifier missing"
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            company = get_object_or_404(Company, slug = company_slug)
            
            enquiry_data = request.data.copy()

            enquiry_data["company"] = company
            serializer = self.get_serializer(data=enquiry_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(company = company)

            response_data.update({
                "success": True,
                "message": "Enquiry submitted successfully",
                "data": serializer.data
            })
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Http404:
            response_data.update({
                "message": "Invalid company specified",
                "error": "Company not found"
            })
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except serializers.ValidationError as e:
            response_data.update({
                "message": "Validation error",
                "errors": e.detail
            })
            print(e)

            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception(
                f"Enquiry submission error - Company: {company_slug}, "
            )
            response_data.update({
                "message": "Server error processing your enquiry",
                "error": "Internal server error"
            })
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    http_method_names = ["post", "get"]
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Review.objects.filter(company__slug=self.kwargs.get("company_slug")) if self.kwargs.get("company_slug") else Review.objects.none()

    def create(self, request, *args, **kwargs):
        response_data = {
            "success": False,
            "message": "Validation Failed",
            "errors": None
        }

        try:
            company_slug = self.kwargs.get("company_slug")
            if not company_slug:
                response_data["message"] = "Company identifier missing"
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            company = get_object_or_404(Company, slug = company_slug)
            
            review_data = request.data.copy()
            review_data["company"] = company
            serializer = self.get_serializer(data=review_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(company = company)

            response_data.update({
                "success": True,
                "message": "Review submitted successfully",
                "data": serializer.data
            })
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Http404:
            response_data.update({
                "message": "Invalid company specified",
                "error": "Company not found"
            })
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except serializers.ValidationError as e:
            response_data.update({
                "message": "Validation error",
                "errors": e.detail
            })
            print(e)

            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception(
                f"Review submission error - Company: {company_slug}, "
            )
            response_data.update({
                "message": "Server error processing your review",
                "error": "Internal server error"
            })
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    lookup_field = "slug"    
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data = request.data)
            serializer.is_valid(raise_exception=True)

            product = serializer.validated_data.get("product")
            quantity = serializer.validated_data.get("quantity")
            color = serializer.validated_data.get("color")

            user = request.user            
            
            cart, _ = Cart.objects.update_or_create(user = user, product = product, color = color, defaults={"quantity": quantity})

            return Response({"success": True, "message": "Product added to cart"}, status=status.HTTP_200_OK)        
        except Exception as e:
            print(e)

    @action(detail=False, methods=['get'])
    def summary(self, request, *args, **kwargs):
        user = request.query_params.get("user")

        try:
            user = User.objects.get(username = user)

            total = user.cart.aggregate(
                total=Sum(
                    F("quantity") * Cast(F("product__price"), output_field=DecimalField(max_digits=10, decimal_places=2)),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )["total"]

            cart_item_count = user.cart.count()
        
            return Response({
                "total": total,
                "item_count": cart_item_count
                }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Invalid Username"}, status=status.HTTP_400_BAD_REQUEST)    


    def update(self, request, *args, **kwargs):
        cart_slug = kwargs.get("slug")  
        data = request.data

        quantity = data.get("quantity")

        if not quantity:
            return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_objs = Cart.objects.filter(slug = cart_slug)

        if not cart_objs.exists():
            return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_objs.update(quantity = quantity)

        return Response({"new_quantity": quantity, "message": "Product added to cart"}, status=status.HTTP_200_OK)        

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")

        if not user_id:
            return self.Cart.objects.none()
        
        return Cart.objects.filter(user__id = user_id).select_related("product", "color").order_by("-created")

    def destroy(self, request, *args, **kwargs):
        cart_slug = kwargs.get("slug")

        if not cart_slug:
            return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        cart_objs = Cart.objects.filter(slug = cart_slug, user = user)

        if not cart_objs.exists():
            return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_objs.delete()

        return Response(
            {
                "success": True,
                "message": "Removed item from cart"
            }, status=status.HTTP_204_NO_CONTENT)        
        

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    queryset = DeliveryAddress.objects.none()

    permission_classes = [IsAuthenticated]
    lookup_field="slug"

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")

        if not user_id:
            return self.queryset
        
        return DeliveryAddress.objects.filter(user__id = user_id).order_by("-created")

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data = request.data)
            serializer.is_valid(raise_exception=True)

            serializer.save(user=request.user)

            return Response({
                "success": True, 
                "message": "Added Address",
                "new_address": serializer.data
                }, status=status.HTTP_200_OK
                )
        except serializers.ValidationError as e:
            logger.exception(e)

            return Response({                
                "message": "Validation error",
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception(
                f"Error in create function AddressViewSet: {e}, "
            )
            return Response({
                "message": "Server error processing your address",
                "error": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        address_slug = kwargs.get("slug")

        if not address_slug:
            return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user

        with transaction.atomic():            
            address_objs = DeliveryAddress.objects.filter(slug = address_slug, user = user)

            if not address_objs.exists():
                return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
            
            address_objs.delete()
            new_checked_address_slug = None

            if not user.addresses.filter(is_default = True).exists():
                user_addresses = user.addresses.order_by("-created")

                if user_addresses.exists():
                    latest_address = user_addresses.first()
                    latest_address.is_default = True
                    latest_address.save()

                    new_checked_address_slug = latest_address.slug

            return Response(
                {
                    "success": True,
                    "message": "Removed Address",
                    "new_checked_address_slug": new_checked_address_slug
                }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        address_slug = kwargs.get("slug")  
        
        try:
            with transaction.atomic():
                address_obj = DeliveryAddress.objects.get(slug = address_slug)
                address_obj.is_default = True
                address_obj.save()

                DeliveryAddress.objects.exclude(pk = address_obj.pk).update(is_default = False)
                return Response(status=status.HTTP_200_OK)            

        except DeliveryAddress.DoesNotExist:
            return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    lookup_field = "slug"

    def create(self, request, *args, **kwargs):
        serializer = OrderSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        cart_items = user.cart.all()
        address = user.addresses.filter(is_default = True).first()

        if not address:
            return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():

            order_placed_address, created = OrderPlacedAddress.objects.get_or_create(
                username = user.username,
                full_name = address.full_name,
                phone = address.phone,
                building = address.building,
                street = address.street,
                landmark = address.landmark,
                city = address.city,
                state = address.state,
                pincode = address.pincode,
                address_type = address.address_type
            )

            order = serializer.save(user=request.user, delivery_address = order_placed_address)

            created_carts = []
            for item in cart_items:
                cart = OrderPlacedCart.objects.create(
                    product=item.product,
                    product_price=item.product.price,
                    username=user.username,
                    quantity=item.quantity,
                    color=item.color
                )
                created_carts.append(cart)

            order.carts.set(created_carts)

            user.cart.all().delete()

            return Response({
                "success": True, 
                "message": "Order Placed. Awaiting Payment",
                "order_slug": order.slug
                },
                status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def recent(self, request, *args, **kwargs):
        try:
            user = request.user
            recent_order = user.orders.all().order_by("-created").first()

            if not recent_order:
                return Response({"error": "No recent order"}, status=status.HTTP_400_BAD_REQUEST)    
            
            serializer = self.get_serializer(recent_order)
        
            return Response(
                serializer.data
                , status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Invalid User"}, status=status.HTTP_400_BAD_REQUEST)    