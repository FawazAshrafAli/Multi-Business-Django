from django.db.models.base import Model as Model
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, View
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404, JsonResponse
from datetime import timedelta
import logging

from company.models import Company, Client, Testimonial
from locations.models import UniquePlace, UniqueState, UniqueDistrict

from educational.models import Course, Program, Specialization, Faq as CourseFaq, Enquiry as CourseEnquiry, Testimonial as StudentTestimonial
from product.models import Category as ProductCategory, Brand, Size, Color, Product, SubCategory as ProductSubCategory, Faq as ProductFaq
from service.models import Service, Category as ServiceCategory, SubCategory as ServiceSubCategory, Enquiry as ServiceEnquiry, Faq as ServiceFaq
from registration.models import Registration, RegistrationType, RegistrationSubType, Faq as RegistrationFaq, Enquiry as RegistrationEnquiry

logger = logging.getLogger(__name__)

class CustomerBaseView(LoginRequiredMixin, View):
    login_url = reverse_lazy("authentication:customer_login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["company"] = get_object_or_404(Company, email = self.request.user.email)
            context["categories"] = ProductCategory.objects.all()
            context["brands"] = Brand.objects.all()
            context["standards"] = sorted(["UK", "US", "EU", "JP", "INT", "AUS", "FR"])
        except Exception as e:
            logger.error("Error in fetching context data for Customer Base View: {e}")
        return context
    

class CustomerHomeView(CustomerBaseView, TemplateView):
    template_name = "customer/home.html"


# Product Company
class BaseProductCategoryView(CustomerBaseView, View):
    model = ProductCategory
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_category_page"] = True
        return context
    

class AddProductCategoryView(BaseProductCategoryView, CreateView):
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("customer:product_categories")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                product, created = self.model.objects.get_or_create(name = name)

                if created:
                    messages.success(request, "Success! Product category created.")
                    return redirect(self.success_url)

                else:
                    messages.warning(request, "Category already exists.")
            
            else:
                messages.error(request, "Category name is required.")                        
        
        except Exception as e:
            logger.error(f"Error in creating product category: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.redirect_url)
    

class UpdateProductCategoryView(BaseProductCategoryView, UpdateView):
    fields = ["name", "slug"]
    success_url = redirect_url = reverse_lazy("customer:product_categories")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                if not self.model.objects.filter(name = name).exists():
                    self.object = self.get_object()

                    self.object.name = name
                    self.object.slug = None
                    self.object.save()
                    
                    messages.success(request, "Success! Product category updated.")
                    return redirect(self.success_url)

                else:
                    messages.warning(request, "Category already exists.")
            
            else:
                messages.error(request, "Category name is required.")                        
        
        except Exception as e:
            logger.error(f"Error in updating product category: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.redirect_url)    
    

class ListProductCategoryView(BaseProductCategoryView, ListView):
    queryset = ProductCategory.objects.all().order_by("name")
    template_name = "customer_product/category/list.html"    
    context_object_name = "categories"


class DeleteProductCategoryView(BaseProductCategoryView, View):
    success_url = redirect_url = reverse_lazy("customer:product_categories")

    def get_object(self):
        try:
            return get_object_or_404(ProductCategory, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid category object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed category.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting category object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)
        

class BaseProductSubCategoryView(CustomerBaseView, View):
    model = ProductSubCategory
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_sub_category_page"] = True
        return context
    

class AddProductSubCategoryView(BaseProductSubCategoryView, CreateView):
    fields = ["name", "category"]
    success_url = redirect_url = reverse_lazy("customer:product_sub_categories")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            category_slug = request.POST.get("category")

            if not category_slug or not name:
                error_msg = "Name of sub category is required."
                if not category_slug:
                    error_msg = "Category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.redirect_url)
            
            category = get_object_or_404(ProductCategory, slug = category_slug)
            
            sub_category, created = self.model.objects.get_or_create(name = name, category = category)

            if created:
                messages.success(request, "Success! Product sub category created.")
                return redirect(self.success_url)

            else:
                messages.warning(request, "Sub Category already exists.")

        except Http404:
            messages.error(request, "Invalid category")                                                
        
        except Exception as e:
            logger.error(f"Error in creating product sub category: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.redirect_url)
    

class UpdateProductSubCategoryView(BaseProductSubCategoryView, UpdateView):
    fields = ["name", "category"]
    success_url = redirect_url = reverse_lazy("customer:product_sub_categories")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            category_slug = request.POST.get("category")

            if not category_slug or not name:
                error_msg = "Name of sub category is required."
                if not category_slug:
                    error_msg = "Category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.redirect_url)
            
            category = get_object_or_404(ProductCategory, slug = category_slug)                        

            if not self.model.objects.filter(name = name, category = category).exists():
                self.object = self.get_object()

                self.object.name = name
                self.object.category = category
                self.object.save()

                messages.success(request, "Success! Product sub category updated.")
                return redirect(self.success_url)

            else:
                messages.warning(request, "Sub category already exists.")

        except Http404:
            messages.error(request, "Invalid category")                      
        
        except Exception as e:
            logger.error(f"Error in updating product sub category: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.redirect_url)
    

class ListProductSubCategoryView(BaseProductSubCategoryView, ListView):
    queryset = ProductSubCategory.objects.all().order_by("name")
    template_name = "customer_product/sub_category/list.html"    
    context_object_name = "sub_categories"


def get_sub_categories_and_sizes(request):
        data = {}
        try:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                categorySlug = request.GET.get("category")

                if categorySlug:
                    category = get_object_or_404(ProductCategory, slug = categorySlug)

                    sub_categories = list(ProductSubCategory.objects.filter(category = category).values("name", "slug"))
                    sizes = Size.objects.filter(category = category)

                    list_sizes = []
                    for size in sizes:
                        list_sizes.append({
                            "name": size.name,
                            "standard": size.standard if size.standard else None,
                            "slug": size.slug
                        })

                    data.update({
                        "sub_categories": sub_categories,
                        "sizes": list_sizes
                        })

        except Http404:
            data = {"error": "Invalid category"}

        except Exception as e:
            error_msg = "Error in getting sub categories and sizes."
            logger.exception(f"{error_msg}: {e}")

            data = {"error": error_msg}
        
        return JsonResponse(data)



class DeleteProductSubCategoryView(BaseProductSubCategoryView, View):
    success_url = redirect_url = reverse_lazy("customer:product_sub_categories")

    def get_object(self):
        try:
            return get_object_or_404(ProductSubCategory, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid sub category object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed sub category.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting sub category object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)

        
class BaseBrandView(CustomerBaseView, View):
    model = Brand
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_brand_page"] = True
        return context


class AddBrandView(BaseBrandView, CreateView):
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("customer:brands")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                product, created = self.model.objects.get_or_create(name = name)

                if created:
                    messages.success(request, "Success! Product brand created.")
                    return redirect(self.success_url)

                else:
                    messages.warning(request, "Brand already exists.")

            else:
                messages.error(request, "Brand name is required.")                        
        
        except Exception as e:
            logger.error(f"Error in creating product brand: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.redirect_url)
    

class UpdateBrandView(BaseBrandView, UpdateView):
    fields = ["name", "slug"]
    success_url = redirect_url = reverse_lazy("customer:brands")
    slug_url_kwarg = "slug"

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                if not self.model.objects.filter(name = name).exists():

                    self.object = self.get_object()
                    self.object.name = name
                    self.object.save()

                    messages.success(request, "Success! Product brand updated.")
                    return redirect(self.success_url)

                else:
                    messages.warning(request, "Brand already exists.")

            else:
                messages.error(request, "Brand name is required.")                        
        
        except Exception as e:
            logger.error(f"Error in updating product brand: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.redirect_url)
    

class ListBrandView(BaseBrandView, ListView):
    queryset = Brand.objects.all().order_by("name")
    template_name = "customer_product/brand/list.html"    
    context_object_name = "brands"


class DeleteBrandView(BaseBrandView, View):
    success_url = redirect_url = reverse_lazy("customer:brands")

    def get_object(self):
        try:
            return get_object_or_404(Brand, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid brand object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed brand.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting brand object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)


class BaseSizeView(CustomerBaseView, View):
    model = Size
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_size_page"] = True
        return context
    

class AddSizeView(BaseSizeView, CreateView):
    fields = ["name", "category", "standard"]
    success_url = redirect_url = reverse_lazy("customer:sizes")

    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."

        try:
            created_count = 0
            ignored_count = 0

            name = request.POST.get("name")
            name = name.strip() if name else None
            if name:
                names = name.split(',')
            
            category_slug = request.POST.get("category")
            standard = request.POST.get("standard")

            if not name or not category_slug:
                if not name:
                    error_msg = "Failed! Name is required."

                if not category_slug:
                    error_msg = "Failed! Category is required."

                return redirect(self.redirect_url)            

            category = get_object_or_404(ProductCategory, slug = category_slug)
            
            for name in names:
                name = name.strip()

                if name:
                    size, created = self.model.objects.get_or_create(name = name.upper(), category = category, standard = standard)

                    if created:
                        created_count += 1

                    else:
                        ignored_count += 1


            if created_count > 0:
                success_msg = "Success! Size created."

                if ignored_count > 0:
                    success_msg = f"Success! Created {created_count} sizes. Ignored {ignored_count} sizes as they already exists in the database"
                elif created_count > 1:
                    success_msg = "Success! Created all the sizes."                                

                messages.success(request, success_msg)
                return redirect(self.success_url)
            
            else:
                messages.warning(request, "Given size/sizes already exists in the database.")

        except Http404:
            error_msg = "Failed! Invalid category"
        
        except Exception as e:
            logger.error(f"Error in creating product size: {e}")

        messages.error(request, error_msg)
        return redirect(self.redirect_url)
    

class UpdateSizeView(BaseSizeView, UpdateView):
    fields = ["name", "category", "standard", "slug"]
    success_url = redirect_url = reverse_lazy("customer:sizes")
    slug_url_kwarg = "slug"

    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."

        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            category_slug = request.POST.get("category")
            standard = request.POST.get("standard")

            if not name or not category_slug:
                if not name:
                    error_msg = "Failed! Name is required."

                if not category_slug:
                    error_msg = "Failed! Category is required."

                return redirect(self.redirect_url)            

            category = get_object_or_404(ProductCategory, slug = category_slug)
            
            self.object = self.get_object()

            if not self.model.objects.filter(name = name, category = category, standard = standard).exists():
                self.object.name = name
                self.object.category = category
                self.slug = None
                self.object.standard = standard if standard else None
                self.object.save()

                messages.success(request, "Success! Size Updated.")
                return redirect(self.success_url)

            else:
                messages.warning(request, "Failed! Size already exists.")        

        except Http404:
            error_msg = "Failed! Invalid category"
        
        except Exception as e:
            logger.error(f"Error in updating product size: {e}")

        messages.error(request, error_msg)
        return redirect(self.redirect_url)
    

class ListSizeView(BaseSizeView, ListView):
    queryset = Size.objects.all().order_by("name")
    template_name = "customer_product/size/list.html"    
    context_object_name = "sizes"


class DeleteSizeView(BaseSizeView, View):
    success_url = redirect_url = reverse_lazy("customer:sizes")

    def get_object(self):
        try:
            return get_object_or_404(Size, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid size object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed size.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting size object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)


class BaseColorView(CustomerBaseView, View):
    model = Color
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_color_page"] = True
        return context
    

class AddColorView(BaseColorView, CreateView):
    fields = ["name", "hexa"]
    success_url = redirect_url = reverse_lazy("customer:colors")

    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."

        try:            
            name = request.POST.get("name")
            name = name.strip() if name else None

            hexa = request.POST.get("hexa")
            hexa = hexa.strip() if hexa else None

            if not name or not hexa:
                if not name:
                    error_msg = "Failed! Name is required."

                if not hexa:
                    error_msg = "Failed! Hexa is required."

                return redirect(self.redirect_url)            
            
            color, created = self.model.objects.get_or_create(name = name, hexa = hexa)

            if created:
                messages.success(request, "Success! Color created.")
                return redirect(self.success_url)            
            else:
                messages.warning(request, "Failed! Color already exists.")
                return redirect(self.redirect_url)       
        
        except Exception as e:
            logger.error(f"Error in creating product color: {e}")

        messages.error(request, error_msg)
        return redirect(self.redirect_url)


class UpdateColorView(BaseColorView, UpdateView):
    fields = ["name", "hexa"]
    success_url = redirect_url = reverse_lazy("customer:colors")
    slug_url_kwarg = "slug"


    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."

        try:            
            name = request.POST.get("name")
            name = name.strip() if name else None

            hexa = request.POST.get("hexa")
            hexa = hexa.strip() if hexa else None

            if not name or not hexa:
                if not name:
                    error_msg = "Failed! Name is required."

                if not hexa:
                    error_msg = "Failed! Hexa is required."

            if not self.model.objects.filter(name = name, hexa = hexa).exists():

                self.object = self.get_object()
                
                self.object.name = name
                self.object.hexa = hexa
                self.object.slug = None
                self.object.save()

                messages.success(request, "Success! Color updated.")
                return redirect(self.success_url)
                                    
            else:
                messages.warning(request, "Failed! Color already exists.")

        except Exception as e:
            logger.error(f"Error in updating product color: {e}")

        messages.error(request, error_msg)
        return redirect(self.redirect_url)
    

class ListColorView(BaseColorView, ListView):
    queryset = Color.objects.all().order_by("name")
    template_name = "customer_product/color/list.html"    
    context_object_name = "colors"


class DeleteColorView(BaseColorView, View):
    success_url = redirect_url = reverse_lazy("customer:colors")

    def get_object(self):
        try:
            return get_object_or_404(Color, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid color object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed color.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting color object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)


class BaseProductView(CustomerBaseView, View):
    model = Product
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_page"] = True        
        return context
    

class AddProductView(BaseProductView, CreateView):
    fields = "__all__"
    success_url = redirect_url = reverse_lazy("customer:add_product")
    template_name = "customer_product/product/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["sizes"] = Size.objects.all()
            context["colors"] = Color.objects.all()
            context["units"] = sorted(["mm", "cm", "m"])
        except Exception as e:
            logger.warning(f"Error in loading context data of add product view: {e}")
        return context
    
    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."
        try:
            name = request.POST.get("name").strip() if request.POST.get("name") else None
            category_slug = request.POST.get("category")
            sub_category_slug = request.POST.get("sub_category")
            brandSlug = request.POST.get("brand")
            image = request.FILES.get("image")
            sku = request.POST.get("sku").strip() if request.POST.get("sku") else None
            stock = request.POST.get("stock").strip() if request.POST.get("stock") else None
            price = request.POST.get("price").strip() if request.POST.get("price") else None
            description = request.POST.get("description").strip() if request.POST.get("description") else None
            size = request.POST.getlist("size")
            color = request.POST.getlist("color")
            length = request.POST.get("length")
            width = request.POST.get("width").strip() if request.POST.get("width") else None
            height = request.POST.get("height").strip() if request.POST.get("height") else None
            weight = request.POST.get("weight").strip() if request.POST.get("weight") else None
            unit = request.POST.get("unit").strip() if request.POST.get("unit") else None

            required_fields = {
                "Name": name,
                "Product Category": category_slug,
                "Product Sub Category": sub_category_slug,
                "Brand": brandSlug,
                "Product Image": image,
                "Stock": stock,
                "Price": price                
            }

            if length or width or height:                
                required_fields["unit"] = unit

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed. {field_name.title()} is required.")
                    return redirect(self.redirect_url)
                
            try:
                stock = int(stock)
                if stock <= 0:
                    raise ValueError("Stock must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid stock number.")
                return redirect(self.redirect_url)
                            
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid price.")
                return redirect(self.redirect_url)
            
            if length:
                try:
                    length = float(length)
                    if length <= 0:
                        raise ValueError("Length must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid length.")
                    return redirect(self.redirect_url)
                
            if width:
                try:
                    width = float(width)
                    if width <= 0:
                        raise ValueError("Width must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid width.")
                    return redirect(self.redirect_url)
                
            if height:
                try:
                    height = float(height)
                    if height <= 0:
                        raise ValueError("Height must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid height.")
                    return redirect(self.redirect_url)                            
                
            category = get_object_or_404(ProductCategory, slug = category_slug)
            sub_category = get_object_or_404(ProductSubCategory, slug = sub_category_slug)
            brand = get_object_or_404(Brand, slug = brandSlug)

            product, created = self.model.objects.get_or_create(
                name = name, category = category, sub_category = sub_category, 
                brand = brand, image = image, sku = sku, stock = stock, price = price,
                description = description, length = length if length else 0, width = width if width else 0,
                height = height if height else 0, weight = weight if weight else 0, unit = unit if unit else None
                )
            
            if created:
                if size and len(size) > 0:
                    size_list = []
                    for sizeSlug in size:
                        try:
                            size_obj = get_object_or_404(Size, slug = sizeSlug)
                            size_list.append(size_obj.pk)
                        except Http404:
                            logger.error(f"Size object not found for slug: {sizeSlug}")
                            continue

                    product.sizes.set(size_list)

                if color and len(color) > 0:
                    color_list = []
                    for colorSlug in color:
                        try:
                            color_obj = get_object_or_404(Color, slug = colorSlug)
                            color_list.append(color_obj.pk)
                        except Http404:
                            logger.error(f"Color object not found for slug: {sizeSlug}")
                            continue

                    product.colors.set(color_list)

                product.save()
            else:
                messages.warning(request, "Failed! Product already exists.")
                return redirect(self.redirect_url)

            messages.success(request, "Success! Product created.")
            return redirect(self.success_url)

        except Http404:
            error_msg = "Failed. Invalid Category."
            if category:
                error_msg = "Failed! Invalid sub category"

        except Exception as e:
            logger.exception(f"Error in adding product: {e}")            

        messages.error(request, error_msg)
        return redirect(self.redirect_url)
    

class UpdateProductView(BaseProductView, UpdateView):
    fields = "__all__"
    success_url = redirect_url = reverse_lazy("customer:products")
    template_name = "customer_product/product/update.html"
    slug_url_kwarg = "slug"

    def get_redirect_url(self):
        try:
            return redirect(reverse_lazy("customer:update_product", kwargs = {"slug" : self.kwargs.get("slug")}))
        except Exception as e:
            logger.exception(f"Error in fetching the redirect url of update product view: {e}.")
            messages.error(self.request, "Failed! Server Error.")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            self.object = self.get_object()

            context["sizes"] = Size.objects.filter(category = self.object.category)
            context["colors"] = Color.objects.all()
            context["units"] = sorted(["mm", "cm", "m"])
            context["sub_categories"] = ProductSubCategory.objects.filter(category = self.object.category)
        except Exception as e:
            logger.warning(f"Error in loading context data of update product view: {e}")
        return context
    
    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."
        try:
            name = request.POST.get("name").strip() if request.POST.get("name") else None
            category_slug = request.POST.get("category")
            sub_category_slug = request.POST.get("sub_category")
            brandSlug = request.POST.get("brand")
            image = request.FILES.get("image")
            sku = request.POST.get("sku").strip() if request.POST.get("sku") else None
            stock = request.POST.get("stock").strip() if request.POST.get("stock") else None
            price = request.POST.get("price").strip() if request.POST.get("price") else None
            description = request.POST.get("description").strip() if request.POST.get("description") else None
            size = request.POST.getlist("size")
            color = request.POST.getlist("color")
            length = request.POST.get("length")
            width = request.POST.get("width").strip() if request.POST.get("width") else None
            height = request.POST.get("height").strip() if request.POST.get("height") else None
            weight = request.POST.get("weight").strip() if request.POST.get("weight") else None
            unit = request.POST.get("unit").strip() if request.POST.get("unit") else None

            required_fields = {
                "Name": name,
                "Product Category": category_slug,
                "Product Sub Category": sub_category_slug,
                "Brand": brandSlug,
                "Stock": stock,
                "Price": price                
            }

            if length or width or height:                
                required_fields["unit"] = unit

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed. {field_name.title()} is required.")
                    return redirect(self.redirect_url)
                
            try:
                stock = int(stock)
                if stock <= 0:
                    raise ValueError("Stock must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid stock number.")
                return redirect(self.redirect_url)
                            
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid price.")
                return redirect(self.redirect_url)
            
            if length:
                try:
                    length = float(length)
                    if length <= 0:
                        raise ValueError("Length must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid length.")
                    return redirect(self.redirect_url)
                
            if width:
                try:
                    width = float(width)
                    if width <= 0:
                        raise ValueError("Width must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid width.")
                    return redirect(self.redirect_url)
                
            if height:
                try:
                    height = float(height)
                    if height <= 0:
                        raise ValueError("Height must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid height.")
                    return redirect(self.redirect_url)                            
                
            category = get_object_or_404(ProductCategory, slug = category_slug)
            sub_category = get_object_or_404(ProductSubCategory, slug = sub_category_slug)
            brand = get_object_or_404(Brand, slug = brandSlug)

            self.object = self.get_object()
            if not image:
                image = self.object.image

            length = length if length else 0.00
            width = width if width else 0.00
            height = height if height else 0.00
            weight = weight if weight else None
            self.object.unit = unit if unit else None

            if not self.model.objects.filter(
                name = name, category = category, sub_category = sub_category, brand = brand, image = image,
                sku = sku, stock = stock, price = price,
                description = description, length = length, width = width,
                height = height, weight = weight, unit = unit
                ).exists():                                                                                                                                                                                                                

                self.object.name = name
                self.object.category = category
                self.object.sub_category = sub_category
                self.object.brand = brand
                self.object.image = image
                self.object.sku = sku
                self.object.stock = stock
                self.object.price = price
                self.object.description = description
                self.object.length = length
                self.object.width = width
                self.object.height = height
                self.object.weight = weight
                self.object.unit = unit
                self.object.save()

                if size and len(size) > 0:
                    size_list = []
                    for sizeSlug in size:
                        try:
                            size_obj = get_object_or_404(Size, slug = sizeSlug)
                            size_list.append(size_obj.pk)
                        except Http404:
                            logger.error(f"Size object not found for slug: {sizeSlug}")
                            continue

                    self.object.sizes.set(size_list)

                if color and len(color) > 0:
                    color_list = []
                    for colorSlug in color:
                        try:
                            color_obj = get_object_or_404(Color, slug = colorSlug)
                            color_list.append(color_obj.pk)
                        except Http404:
                            logger.error(f"Color object not found for slug: {sizeSlug}")
                            continue

                    self.object.colors.set(color_list)

                self.object.save()
            else:
                messages.warning(request, "Failed! Product already exists.")
                return redirect(self.redirect_url)

            messages.success(request, "Success! Product updated.")
            return redirect(self.success_url)

        except Http404:
            error_msg = "Failed. Invalid Category."

        except Exception as e:
            logger.exception(f"Error in updating product: {e}")            

        messages.error(request, error_msg)
        return redirect(self.redirect_url)
    

class ListProductView(BaseProductView, ListView):
    queryset = Product.objects.all().order_by("name")
    template_name = "customer_product/product/list.html"    
    context_object_name = "products"


class DeleteProductView(BaseProductView, View):
    success_url = redirect_url = reverse_lazy("customer:products")

    def get_object(self):
        try:
            return get_object_or_404(Product, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid product object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed product.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting product object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)
        

class BaseCustomerView(LoginRequiredMixin):
    login_url = reverse_lazy('authentication:login')
    success_url = redirect_url = reverse_lazy("customer:testimonials")

    def get_company(self):
        try:
            email = self.request.user.email
            self.company = get_object_or_404(Company, email = email)
            return self.company
        except Http404:
            messages.error(self.request, "Invalid Company")
        
        except Exception as e:
            logger.exception(f"Error in get_company function of BaseCustomerView in customer app: {e}")

        return  redirect(reverse_lazy('authentication:logout'))
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = self.get_company()
        return context


# Service Company
class BaseServiceView(BaseCustomerView, View):
    model = Service
    success_url = redirect_url = reverse_lazy("customer:services")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["service_page"] = True

        return context
    
    def get_category(self, category_slug):
        try:
            return get_object_or_404(ServiceCategory, slug = category_slug)
        except Http404:
            return None
        
    def get_sub_category(self, sub_category_slug):
        try:
            return get_object_or_404(ServiceSubCategory, slug = sub_category_slug)
        except Http404:
            return None


class AddServiceView(BaseServiceView, CreateView):
    model = Service
    fields = ["company", "image", "name", "category", "sub_category", "is_active", "price"]
    template_name = "customer_services/service/add.html"
    success_url = redirect_url = reverse_lazy("customer:add_services")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_service_page"] = True
        context["categories"] = ServiceCategory.objects.filter(company = self.get_company()).order_by("name")
        context["sub_categories"] = ServiceSubCategory.objects.filter(company = self.get_company()).order_by("name")        

        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()

            image = request.FILES.get('image')
            name = request.POST.get("name")
            category_slug = request.POST.get("category")
            sub_category_slug = request.POST.get("sub_category")

            price = request.POST.get("price")
            duration = request.POST.get("duration")
            is_active = request.POST.get("is_active")
            
            name = name.strip() if name else None
            category_slug = category_slug.strip() if category_slug else None
            sub_category_slug = sub_category_slug.strip() if sub_category_slug else None
            price = price.strip() if price else None
            duration = duration.strip() if duration else None
            is_active = is_active.strip() if is_active else None

            required_fields = {
                "Service Name": name,
                "Category": category_slug,
                "Sub Category": sub_category_slug,                
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)

            category = self.get_category(category_slug)
            
            sub_category = self.get_sub_category(sub_category_slug)

            if not category or not sub_category:
                invalid_msg = "Invalid "
                
                if not category:
                    invalid_msg += "Category"
                else:
                    invalid_msg += "Sub Category"

                messages.error(request, invalid_msg)
                return redirect(self.redirect_url)
            
            if Service.objects.filter(company=company, name=name, category=category, sub_category=sub_category).exists():
                messages.warning(request, "Similar Service already exists")
                return redirect(self.redirect_url)

            Service.objects.create(
                company = company, image = image, name = name, category = category, sub_category = sub_category, 
                price = price, duration = timedelta(days = int(duration.strip())) if duration else None, 
                is_active = bool(is_active)
                )
            
            messages.success(request, "Success! Service Created.")
            return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in post functio of AddServiceView in customer app: {e}")
            messages.error(request, "Server Error")
            return redirect(self.redirect_url)
        

class UpdateServiceView(BaseServiceView, UpdateView):
    model = Service
    fields = ["name", "image", "category", "sub_category", "price", "duration", "is_active"]
    success_url = redirect_url = reverse_lazy("customer:services")    
    template_name = "customer_services/service/edit.html"
    slug_url_kwarg = 'slug'

    def get_redirect_url(self):
        try:  
            return reverse_lazy("customer:update_service", kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function of UpdateServiceView in customer app: {e}")
            return self.redirect_url    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company = self.get_company()
        context["categories"] = ServiceCategory.objects.filter(company = company).order_by("name")
        context["sub_categories"] = ServiceSubCategory.objects.filter(company = company).order_by("name")        
        
        return context      

    def post(self, request, *args, **kwargs):
        try:
            image = request.FILES.get("image")
            name = request.POST.get("name")
            category_slug = request.POST.get("category")
            sub_category_slug = request.POST.get("sub_category")

            price = request.POST.get("price")
            duration = request.POST.get("duration")
            is_active = request.POST.get("is_active")

            name = name.strip() if name else None
            category_slug = category_slug.strip() if category_slug else None
            sub_category_slug = sub_category_slug.strip() if sub_category_slug else None
            price = price.strip() if price else None
            duration = duration.strip() if duration else None
            is_active = is_active.strip() if is_active else None

            required_fields = {
                "Service Name": name,
                "Category": category_slug,
                "Sub Category": sub_category_slug,                
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            category = self.get_category(category_slug)
            
            sub_category = self.get_sub_category(sub_category_slug)

            if not category or not sub_category:
                invalid_msg = "Invalid "
                
                if not category:
                    invalid_msg += "Category"
                else:
                    invalid_msg += "Sub Category"

                messages.error(request, invalid_msg)
                return redirect(self.get_redirect_url())
            
            service = self.get_object()

            similar_service = self.model.objects.filter(
                company = service.company, name = name, category = category, sub_category = sub_category
                ).first()

            if similar_service and similar_service.slug != service.slug:                
                messages.warning(request, "Similar service already exists")
                return redirect(self.get_redirect_url())

            service.name = name
            service.category = category
            service.sub_category = sub_category
            service.price = price
            service.is_active = bool(is_active)

            if duration:
                service.duration = timedelta(days = int(duration))
            if image:
                service.image = image
            service.save()
            
            messages.success(request, "Success! Service Updated")
            return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in post function of UpdateServiceView in customer app: {e}")
            messages.error(request, "An unexpected error occurred")
            return redirect(self.get_redirect_url())


class ServiceListView(BaseServiceView, ListView):
    queryset = Service.objects.none()
    template_name = "customer_services/service/list.html"
    context_object_name = "services"

    def get_queryset(self):
        try:
            company = self.get_company()
            if company.type.name == "Service":
                return self.model.objects.filter(company = company)                            
        except Exception as e:
            logger.exception(f"Error in get_queryset function of list ServiceListView of customer app: {e}")

        return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["list_service_page"] = True

        return context
    

class DeleteServiceView(BaseServiceView, View): 
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted service")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid service")

        except Exception as e:
            logger.exception(f"Error in get function of DeleteServiceView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class BaseServiceCategoryView(BaseCustomerView, View):
    model = ServiceCategory
    success_url = redirect_url = reverse_lazy("customer:service_categories")
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["service_category_page"] = True

        return context


class AddServiceCategoryView(BaseServiceCategoryView, CreateView):
    fields = ["company", "name"]
    success_url = redirect_url = reverse_lazy("customer:service_categories")    

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()

            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                product, created = self.model.objects.get_or_create(company = company, name = name)

                if created:
                    messages.success(request, "Success! Service category created.")
                    return redirect(self.success_url)

                else:
                    messages.warning(request, "Service category already exists.")
            
            else:
                messages.error(request, "Service category name is required.")            
        
        except Exception as e:
            logger.error(f"Error in post function of AddServiceCategoryView in customer app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.redirect_url)
    

class ListServiceCategoryView(BaseServiceCategoryView, ListView):
    queryset = ServiceCategory.objects.none()
    context_object_name = "categories"
    template_name = "customer_services/category/list.html"

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListServiceCategoryView in customer app: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["list_service_category_page"] = True

        return context
    

class UpdateServiceCategoryView(BaseServiceCategoryView, UpdateView):
    fields = ["name"]

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            if not name:
                messages.error(request, f"Failed! Name of service category is required")
                return redirect(self.redirect_url)
            
            category = self.get_object()
            
            existing_category = self.model.objects.filter(company = category.company, name = name).first()

            if existing_category:
                if existing_category.slug == category.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar category already exists")

                return redirect(self.redirect_url)
            
            category.name = name
            category.save()

            messages.success(request, "Success! Service category updated.")
            return redirect(self.success_url)                                                       
        
        except Exception as e:
            logger.exception(f"Error post function of UpdateServiceCategoryView in customer app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.redirect_url)
    

class DeleteServiceCategoryView(BaseServiceCategoryView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()
            messages.success(request, "Success! Deleted service category")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid service category")

        except Exception as e:
            logger.exception(f"Error in get function of DeleteServiceCategoryView in customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class BaseServiceSubCategoryView(BaseCustomerView, View):
    model = ServiceSubCategory
    success_url = redirect_url = reverse_lazy("customer:service_sub_categories")
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["service_sub_category_page"] = True
        context["categories"] = ServiceCategory.objects.filter(company = self.get_company())

        return context
    
    def get_category(self, category_slug):
        try:
            return get_object_or_404(ServiceCategory, slug = category_slug)
        except Http404:
            return None
    

class AddServiceSubCategoryView(BaseServiceSubCategoryView, CreateView):
    model = ServiceSubCategory
    fields = ["company", "name", "category"]  

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()

            name = request.POST.get("name")
            name = name.strip() if name else None

            category_slug = request.POST.get("category")

            if not category_slug or not name:
                error_msg = "Name of service sub category is required."
                if not category_slug:
                    error_msg = "Service category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.redirect_url)
            
            category = self.get_category(category_slug)

            if not category:
                messages.error(request, "Invalid category")
                return redirect(self.redirect_url)
            
            sub_category, created = self.model.objects.get_or_create(company = company, name = name, category = category)

            if created:
                messages.success(request, "Success! Service sub category created.")
                return redirect(self.success_url)

            else:
                messages.warning(request, "Service sub category already exists.")                                    
        
        except Exception as e:
            logger.error(f"Error in post function of AddServiceSubCategoryView in customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class ListServiceSubCategoryView(BaseServiceSubCategoryView, ListView):
    queryset = ServiceSubCategory.objects.none()
    context_object_name = "sub_categories"
    template_name = "customer_services/sub_category/list.html"

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListServiceSubCategoryView in customer app: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["list_service_sub_category_page"] = True

        return context
    

class UpdateServiceSubCategoryView(BaseServiceSubCategoryView, UpdateView):
    fields = ["name", "category"]        

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            category_slug = request.POST.get("category")

            name = name.strip() if name else None
            category_slug = category_slug.strip() if category_slug else None

            if not category_slug or not name:
                error_msg = "Name of service sub category is required."
                if not category_slug:
                    error_msg = "Service category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.redirect_url)
            
            category = self.get_category(category_slug)

            if not category:
                messages.error(request, "Failed! Invalid Category")
                return redirect(self.redirect_url)
            
            sub_category = self.get_object()
            
            existing_sub_category = self.model.objects.filter(company = sub_category.company, name = name, category = category).first()

            if existing_sub_category:
                if existing_sub_category.slug == sub_category.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar Sub category already exists")
                return redirect(self.redirect_url)
            
            sub_category.name = name
            sub_category.category = category
            sub_category.save()

            messages.success(request, "Success! Service sub category updated.")
            return redirect(self.success_url)                                                       
        
        except Exception as e:
            logger.error(f"Error in post function of UpdateServiceSubCategoryView in customer app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.redirect_url)
    

class DeleteServiceSubCategoryView(BaseServiceSubCategoryView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()
            messages.success(request, "Success! Deleted service sub category")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid service sub category")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteServiceSubCategoryView in customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class BaseServiceFaqBaseView(BaseCustomerView):
    model = ServiceFaq
    success_url = redirect_url = reverse_lazy('customer:service_faqs')
    slug_url_kwarg = 'slug'
        
    def get_service(self, service_slug):
        try:            
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["service_faq_page"] = True

        return context


class AddServiceFaqView(BaseServiceFaqBaseView, CreateView):    
    fields = ["company", "service", "question", "answer"]
    template_name = "customer_services/faq/add.html"    
    success_url = redirect_url = reverse_lazy('customer:add_service_faqs')    
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_service_faq_page"] = True
        context["categories"] = ServiceCategory.objects.filter(company = self.get_company()).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()

            service_slug = self.request.POST.get('service')
            question = request.POST.get("question")
            answer = request.POST.get("answer")

            service_slug = service_slug.strip() if service_slug else None
            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Service": service_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)

            service = self.get_service(service_slug)

            if not service:
                messages.error(request, "Invalid Service")
                return redirect(self.redirect_url)

            ServiceFaq.objects.update_or_create(company = company, service = service, question = question, defaults={"answer": answer})

            messages.success(request, f"Success! Created FAQ object for service: {service.name}")
            return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in get function of AddServiceFaqView of customer app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.redirect_url)
    

class ListServiceFaqView(BaseServiceFaqBaseView, ListView):
    template_name = "customer_services/faq/list.html"
    queryset = ServiceFaq.objects.none()
    context_object_name = "faqs"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["list_service_faqs"] = True

        return context

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
            
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListServiceFaqView in customer app: {e}")
            return self.queryset


class UpdateServiceFaqView(BaseServiceFaqBaseView, UpdateView):
    model = ServiceFaq
    fields = ["service", "question", "answer"]
    template_name = "customer_services/faq/update.html"
    context_object_name = "faq"

    def get_redirect_url(self):
        try:
            return reverse_lazy('customer:update_service_faq', kwargs = {'slug': self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url of UpdateServiceFaqView in customer app: {e}")
            return self.redirect_url
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company = self.get_company()

        context["update_service_faq_page"] = True

        context["categories"] = ServiceCategory.objects.filter(company = company).order_by("name")
        context["sub_categories"] = ServiceSubCategory.objects.filter(company = company, category = self.object.service.category).order_by("name")
        context["services"] = Service.objects.filter(company = company, category = self.object.service.category, sub_category = self.object.service.sub_category).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            service_slug = self.request.POST.get('service')
            question = request.POST.get("question")
            answer = request.POST.get("answer")

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Service": service_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            service = self.get_service(service_slug)

            if not service:
                messages.error(request, "Invalid Service")
                return redirect(self.get_redirect_url())

            similar_faq = self.model.objects.filter(company = self.object.company, service = service, question = question, answer = answer).first()

            if similar_faq:
                if similar_faq.slug == self.object.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar service FAQ already exists")
                return redirect(self.get_redirect_url())

            self.object.service = service
            self.object.question = question
            self.object.answer = answer
            self.object.save()

            messages.success(request, f"Success! Updated FAQ")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Invalid service FAQ object")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateServiceFaqView in customer app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteServiceFaqView(BaseServiceFaqBaseView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            service_name = self.object.service.name
            self.object.delete()

            messages.success(request, f"Success! Removed service FAQ object of: {service_name}")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Invalid Service FAQ")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteServiceFaqView in customer app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.redirect_url)
    

class BaseServiceEnquiryView(BaseCustomerView, View):
    model = ServiceEnquiry
    success_url = redirect_url = reverse_lazy('customer:service_enquiries')
    slug_url_kwarg = 'slug'    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["service_enquiry_page"] = True        

        return context


class ListServiceEnquiryView(BaseServiceEnquiryView, ListView):
    queryset = ServiceEnquiry.objects.none()
    context_object_name = "enquiries"
    template_name = "customer_services/enquiry/list.html"

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListServiceEnquiryView of customer app: {e}")
            return self.queryset


class DeleteServiceEnquiryView(BaseServiceEnquiryView, View):
    def post(self, request, *args, **kwargs):
        try:            
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()

            messages.success(request, "Success! Deleted Service Enquiry")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid Service Enquiry")
            return redirect(self.redirect_url)
        

# Registration Company
class BaseRegistrationView(BaseCustomerView, View):
    model = Registration
    success_url = redirect_url = reverse_lazy('customer:registrations')
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["company_list_page"] = True

        return context
    
    def get_sub_type(self, sub_type_slug):
        try:            
            return get_object_or_404(RegistrationSubType, slug = sub_type_slug)
        except Http404:
            None
        

class ListRegistrationView(BaseRegistrationView, ListView):    
    queryset = Registration.objects.none()
    context_object_name = "registrations"
    template_name = "customer_registrations/registration_detail/list.html"

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListRegistrationView of customer app: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["registration_page"] = True        

        return context

class AddRegistrationView(BaseRegistrationView, CreateView):
    model = Registration
    fields = ["company", "sub_type", "price", "time_required", "required_documents", "additional_info"]
    template_name = "customer_registrations/registration_detail/add.html"
    success_url = redirect_url = reverse_lazy('customer:add_registrations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company = self.get_company()
        context["types"] = RegistrationType.objects.filter(company = company).order_by("name")
        context["add_registration_page"] = True

        return context        

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()

            sub_type_slug = request.POST.get("sub_type")
            price = request.POST.get("price")
            time_required = request.POST.get("time_required")
            required_documents = request.POST.get("required_documents")
            additional_info = request.POST.get("additional_info")

            sub_type_slug = sub_type_slug.strip() if sub_type_slug else None
            price = price.strip() if price else None
            time_required = time_required.strip() if time_required else None
            required_documents = required_documents.strip() if required_documents else None
            additional_info = additional_info.strip() if additional_info else None

            required_fields = {
                "Sub Type": sub_type_slug,
                "Price": price,
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)            
            
            sub_type = self.get_sub_type(sub_type_slug)

            if not sub_type:
                messages.error(request, "Failed! Invalid Sub Type")
            
            if self.model.objects.filter(company=company, sub_type=sub_type).exists():
                messages.warning(request, "Similar registration already exists")
                return redirect(self.redirect_url)

            self.model.objects.create(
                company = company, sub_type = sub_type, price = price, 
                time_required = time_required, required_documents = required_documents, 
                additional_info = additional_info
                )
            
            messages.success(request, "Success! Registration Created.")
            return redirect(self.success_url)        

        except Exception as e:
            logger.exception(f"Error in post function of AddRegistrationView in customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class UpdateRegistrationView(BaseRegistrationView, UpdateView):
    fields = ["sub_type", "price", "time_required", "required_documents", "additional_info"]
    template_name = "customer_registrations/registration_detail/edit.html"    
    context_object_name = "registration"
        
    def get_redirect_url(self):
        try:
            return reverse_lazy("customer:update_registration", kwargs = {'slug': self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function in UpdateRegistrationView of customer app: {e}")
            return self.redirect_url    
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        current_company = self.get_company()
        registration = self.get_object()
        context["types"] = RegistrationType.objects.filter(company = current_company)
        context["sub_types"] = RegistrationSubType.objects.filter(company = current_company, type = registration.sub_type.type)

        return context 

    def post(self, request, *args, **kwargs):
        try:
            sub_type_slug = request.POST.get("sub_type")
            price = request.POST.get("price")
            time_required = request.POST.get("time_required")
            required_documents = request.POST.get("required_documents")
            additional_info = request.POST.get("additional_info")

            sub_type_slug = sub_type_slug.strip() if sub_type_slug else None
            price = price.strip() if price else None
            time_required = time_required.strip() if time_required else None
            required_documents = required_documents.strip() if required_documents else None
            additional_info = additional_info.strip() if additional_info else None

            required_fields = {
                "Sub Type": sub_type_slug,
                "Price": price,
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
            
            sub_type = self.get_sub_type(sub_type_slug)

            if not sub_type:
                messages.error(request, "Failed! Invalid Sub Type")
                return redirect(self.get_redirect_url())
            
            registration = self.get_object()
                        
            similar_registration = self.model.objects.filter(company = registration.company, sub_type=sub_type).first()
            
            if similar_registration:
                similar_error_msg = ""
                if similar_registration.slug == registration.slug:
                    if price == similar_registration.price and time_required == similar_registration.time_required and required_documents == similar_registration.required_documents and additional_info == similar_registration.additional_info:
                        similar_error_msg = "No changes detected"
                else:
                    similar_error_msg = "Similar registration already exists"

                if similar_error_msg:
                    messages.warning(request, similar_error_msg)
                    return redirect(self.get_redirect_url())

            registration.sub_type = sub_type
            registration.price = price
            registration.time_required = time_required
            registration.required_documents = required_documents
            registration.additional_info = additional_info
            registration.save()        
            
            messages.success(request, "Success! Registration Updated.")
            return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in post function of UpdateRegistrationView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class DeleteRegistrationView(BaseRegistrationView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()
            messages.success(request, "Success! Deleted registration")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid registration")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteRegistrationView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class BaseRegistrationTypeView(BaseCustomerView, View):
    model = RegistrationType
    template_name = "customer_registrations/type/list.html"
    success_url = redirect_url = reverse_lazy('customer:registration_types')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["registration_type_page"] = True

        return context


class ListRegistrationTypeView(BaseRegistrationTypeView, ListView):
    queryset = RegistrationType.objects.none()
    context_object_name = "types"    

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListRegistrationTypeView of customer app: {e}")
            return self.queryset
    

class AddRegistrationTypeView(BaseRegistrationTypeView, CreateView):
    fields = ["company", "name", "description"]    

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()

            name = request.POST.get("name")
            description = request.POST.get("description")

            name = name.strip() if name else None
            description = description.strip() if description else None

            if not name:
                messages.error(request, "Name of registration type is required.")
                return redirect(self.redirect_url)
            
            registration_type, created = self.model.objects.get_or_create(company = company, name = name, description = description)

            if not created:
                messages.warning(request, "Registration type already exists.")
                return redirect(self.redirect_url)

            messages.success(request, "Success! Registration type created.")
            return redirect(self.success_url)
        
        except Exception as e:
            logger.error(f"Error post function of AddRegistrationTypeView in customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.redirect_url)
        

class UpdateRegistrationTypeView(BaseRegistrationTypeView, UpdateView):
    fields = ["name", "description"]    

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            description = request.POST.get("description")
            description = description.strip() if description else None

            if not name:
                messages.error(request, "Name of registration type is required.")
                return redirect(self.redirect_url)
            
            registration_type = self.get_object()

            similar_registration_type = self.model.objects.filter(company = registration_type.company, name = name).first()

            if similar_registration_type:
                similar_error_msg = ''
                if similar_registration_type.slug == registration_type.slug:
                    if similar_registration_type.description == description:
                        similar_error_msg = "No changes detected"
                else:
                    similar_error_msg = "Similar registration type already exists"

                if similar_error_msg:
                    messages.warning(request, similar_error_msg)
                    return redirect(self.redirect_url)
            
            registration_type.name = name
            registration_type.description = description
            registration_type.save()

            messages.success(request, "Success! Registration type updated.")
            return redirect(self.success_url)
        
        except Exception as e:
            logger.error(f"Error in post function of UpdateRegistrationTypeView in customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.redirect_url)
        

class DeleteRegistrationTypeView(BaseRegistrationTypeView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()
            messages.success(request, "Success! Deleted registration type")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid registration type")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteRegistrationTypeView in customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class BaseRegistrationSubTypeView(BaseCustomerView, View):
    model = RegistrationSubType
    success_url = redirect_url = reverse_lazy('customer:registration_sub_types')
    template_name = "customer_registrations/sub_type/list.html"
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["registration_sub_type_page"] = True

        return context
    
    def get_type(self, type_slug):
        try:
            return get_object_or_404(RegistrationType, slug = type_slug)
        except Http404:
            return None


class ListRegistrationSubTypeView(BaseRegistrationSubTypeView, ListView):
    queryset = RegistrationSubType.objects.none()
    context_object_name = "sub_types"

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListRegistrationSubTypeView of customer app: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company = self.get_company()
        context["types"] = RegistrationType.objects.filter(company = company).order_by('name')

        return context
    
    
class AddRegistrationSubTypeView(BaseRegistrationSubTypeView, CreateView):
    fields = ["company", "name", "category", "description"]

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()

            name = request.POST.get("name")
            description = request.POST.get("description")

            type_slug = request.POST.get("type")

            type_slug = type_slug.strip() if type_slug else None
            name = name.strip() if name else None
            description = description.strip() if description else None

            if not type_slug or not name:
                error_msg = "Name of registration sub type is required."
                if not type_slug:
                    error_msg = "Registration type is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.redirect_url)
            
            type = self.get_type(type_slug)

            if not type:
                messages.error(request, "Failed! Invalid Type")
                return redirect(self.redirect_url)
            
            sub_type, created = self.model.objects.get_or_create(company = company, name = name, type = type, description = description)

            if not created:
                messages.warning(request, "Registration sub type already exists.")
                return redirect(self.redirect_url)

            messages.success(request, "Success! Registration sub type created.")
            return redirect(self.success_url)                                   
        
        except Exception as e:
            logger.error(f"Error in post function of AddRegistrationSubTypeView in customer: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class UpdateRegistrationSubTypeView(BaseRegistrationSubTypeView, UpdateView):
    fields = ["name", "category", "description"]

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            type_slug = request.POST.get("type")
            description = request.POST.get("description")

            name = name.strip() if name else None
            type_slug = type_slug.strip() if type_slug else None
            description = description.strip() if description else None

            if not type_slug or not name:
                error_msg = "Name of registration sub type is required."
                if not type_slug:
                    error_msg = "Registration type is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.redirect_url)
            
            type = self.get_type(type_slug)

            if not type:
                messages.error(request, "Invalid Type")
                return redirect(self.redirect_url)
            
            registration_sub_type = self.get_object()

            similar_registration_sub_type = self.model.objects.filter(
                company = registration_sub_type.company, name = name, type = type
                ).first()
            
            if similar_registration_sub_type:
                similar_error_msg = ''
                if similar_registration_sub_type.slug == registration_sub_type.slug:
                    if similar_registration_sub_type.description == description:
                        similar_error_msg = "No changes detected"
                else:
                    similar_error_msg = "Similar registration sub type already exists"

                if similar_error_msg:
                    messages.warning(request, similar_error_msg)
                    return redirect(self.redirect_url)
            
            registration_sub_type.name = name
            registration_sub_type.type = type
            registration_sub_type.description = description
            registration_sub_type.save()

            messages.success(request, "Success! Registration sub type updated.")
            return redirect(self.success_url)                                 
        
        except Exception as e:
            logger.error(f"Error in post function of UpdateRegistrationSubTypeView in customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class DeleteRegistrationSubTypeView(BaseRegistrationSubTypeView, View):
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()
            messages.success(request, "Success! Deleted registration sub type")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid registration sub type")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteRegistrationSubTypeView in customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)


class BaseRegistrationFaqView(BaseCustomerView, View):
    model = RegistrationFaq
    success_url = redirect_url = reverse_lazy("customer:registration_faqs")
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["registration_faq_page"] = True

        return context
    
    def get_registration_sub_type(self, registration_sUb_type_slug):
        try:            
            return get_object_or_404(RegistrationSubType, slug = registration_sUb_type_slug)
        except Http404:
            return None
    

class AddRegistrationFaqView(BaseRegistrationFaqView, CreateView):    
    fields = ["company", "registration_sub_type", "question", "answer"]
    template_name = "customer_registrations/faq/add.html"     
    success_url = redirect_url = reverse_lazy("customer:add_registration_faqs")       
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context["add_registration_faq_page"] = True
        company = self.get_company()
        context["types"] = RegistrationType.objects.filter(company = company).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            registration_sub_type_slug = self.request.POST.get('sub_type')
            question = request.POST.get("question")
            answer = request.POST.get("answer")

            registration_sub_type_slug = registration_sub_type_slug.strip() if registration_sub_type_slug else None
            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Registration Sub Type": registration_sub_type_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)

            company = self.get_company()
            registration_sub_type = self.get_registration_sub_type(registration_sub_type_slug)

            if not company or not registration_sub_type:
                invalid_msg = ""
                
                if not company:
                    invalid_msg = "Invalid Registration Company"
                else:
                    invalid_msg = "Invalid Registration Sub Type"

                messages.error(request, invalid_msg)
                return redirect(self.redirect_url)

            RegistrationFaq.objects.update_or_create(company = company, registration_sub_type = registration_sub_type, question = question, defaults={"answer": answer})

            messages.success(request, f"Success! Created FAQ object for registration sub type: {registration_sub_type.name}")
            return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in get function of AddRegistrationFaqView of customer app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.redirect_url)
    

class ListRegistrationFaqView(BaseRegistrationFaqView, ListView):
    template_name = "customer_registrations/faq/list.html"
    queryset = RegistrationFaq.objects.none()
    context_object_name = "faqs"

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
            
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListRegistrationFaqView in customer app: {e}")
            return self.queryset


class UpdateRegistrationFaqView(BaseRegistrationFaqView, UpdateView):
    fields = ["registration_sub_type", "question", "answer"]
    template_name = "customer_registrations/faq/update.html"
    context_object_name = "faq"    

    def get_redirect_url(self):
        try:
            return reverse_lazy('customer:update_registration_faq', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function of UpdateRegistrationFaqView in customer app: {e}")
            return self.redirect_url
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company = self.get_company()

        context["types"] = RegistrationType.objects.filter(company = company).order_by("name")
        context["sub_types"] = RegistrationSubType.objects.filter(company = company, type = self.object.registration_sub_type.type).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            registration_sub_type_slug = self.request.POST.get('sub_type')
            question = request.POST.get("question")
            answer = request.POST.get("answer")

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Registration Sub Type": registration_sub_type_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            registration_sub_type = self.get_registration_sub_type(registration_sub_type_slug)

            if not registration_sub_type:
                messages.error(request, "Invalid Registration Sub Type")
                return redirect(self.get_redirect_url())

            similar_faq = self.model.objects.filter(company = self.object.company, registration_sub_type = registration_sub_type, question = question).first()

            if similar_faq:
                if similar_faq.slug == self.object.slug:
                    if similar_faq.answer == answer:
                        messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar registration FAQ already exists")
                return redirect(self.get_redirect_url())

            self.object.registration_sub_type = registration_sub_type
            self.object.question = question
            self.object.answer = answer
            self.object.save()

            messages.success(request, f"Success! Updated FAQ")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Invalid registration FAQ object")

        except Exception as e:
            logger.exception(f"Error in get function of UpdateRegistrationFaqView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteRegistrationFaqView(BaseRegistrationFaqView, View):    

    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            registration_sub_type_name = self.object.registration_sub_type.name
            self.object.delete()

            messages.success(request, f"Success! Removed registration FAQ object of: {registration_sub_type_name}")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Invalid Registration FAQ")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteRegistrationFaqView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class BaseRegistrationEnquiryView(BaseCustomerView, View):
    model = RegistrationEnquiry
    success_url = redirect_url = reverse_lazy('customer:registration_enquiries')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["registration_enquiry_page"] = True

        return context


class ListRegistrationEnquiryView(BaseRegistrationEnquiryView, ListView):
    queryset = RegistrationEnquiry.objects.none()
    context_object_name = "enquiries"
    template_name = "customer_registrations/enquiry/list.html"

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListRegistrationEnquiryView of customer: {e}")
            return self.queryset


class DeleteRegistrationEnquiryView(BaseRegistrationEnquiryView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(RegistrationEnquiry, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()

            messages.success(request, "Success! Delete Registration Enquiry")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid Registration Enquiry")
            return redirect(self.redirect_url)
        

# Education Company
class BaseCourseView(BaseCustomerView, View):
    model = Course
    success_url = redirect_url = reverse_lazy("customer:courses")
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["course_page"] = True

        return context
    
    def get_program(self, program_slug):
        try:
            return get_object_or_404(Program, slug = program_slug)
        except Http404:
            return None
        
    def get_specialization(self, specialization_slug):
        try:
            return get_object_or_404(Specialization, slug = specialization_slug)
        except Http404:
            return None


class CourseListView(BaseCourseView, ListView):
    queryset = Course.objects.none()
    context_object_name = "courses"
    template_name = "customer_education/course/list.html"

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
        except Exception as e:
            logger.exception(f"Error in get_context_data function of CourseListView in customer app: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['list_course_page'] = True

        return context
    

class AddCourseView(BaseCourseView, CreateView): 
    fields = ["company", "image", "name", "program", "specialization", "mode", "duration", "price", "duration"]   
    template_name = "customer_education/course/add.html"
    success_url = redirect_url = reverse_lazy("customer:add_courses")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        company = self.get_company()
        context["add_course_page"] = True
        context["programs"] = Program.objects.filter(company = company)

        return context
    
    def post(self, request, *args, **kwargs):        
        try:
            company = self.get_company()

            image = request.FILES.get('image')
            name = request.POST.get("name")
            program_slug = request.POST.get("program")
            specialization_slug = request.POST.get("specialization")
            mode = request.POST.get("mode")
            duration = request.POST.get("duration")
            price = request.POST.get("price")

            program = self.get_program(program_slug)
            specialization = self.get_specialization(specialization_slug)
            
            if not program or not specialization:
                invalid_msg = "Failed! "

                if not program:
                    invalid_msg += "Invalid Program"
                else:
                    invalid_msg += "Invalid Specialization"

                messages.error(request, invalid_msg)
                return redirect(self.redirect_url)

            course, created = self.model.objects.get_or_create(
                company = company, image = image,
                name=name, program=program, specialization=specialization,
                mode=mode, duration=duration, price=price
                )
            
            if created:
                messages.success(request, "Success! Course created.")
                return redirect(self.success_url)
            
            messages.error(request, "Failed! Course already exists")

        except Exception as e:
            messages.error(request, "Failed! An unexpected error occurred")
            logger.exception(f"Error in post function of AddCourseView in customer app: {e}")

        return redirect(self.redirect_url)
    

class UpdateCourseView(BaseCourseView, UpdateView): 
    fields = ["image", "name", "program", "specialization", "mode", "duration", "price", "duration"]   
    template_name = "customer_education/course/edit.html"    
    
    def get_redirect_url(self):
        try:
            return reverse_lazy("customer:update_course", kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url of UpdateCourseView of customer app: {e}")
        
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   
                
        context["modes"] = ("Online", "Offline")
        company = self.get_company()
        current_course = self.get_object()
        context["programs"] = Program.objects.filter(company = company)
        context["specializations"] = Specialization.objects.filter(company = company, program = current_course.program)                        

        return context
    
    def post(self, request, *args, **kwargs):        
        try:
            image = request.FILES.get("image")

            name = request.POST.get("name")
            program_slug = request.POST.get("program")
            specialization_slug = request.POST.get("specialization")
            mode = request.POST.get("mode")
            duration = request.POST.get("duration")
            price = request.POST.get("price")
            description = request.POST.get("description")

            name = name.strip() if name else None
            program_slug = program_slug.strip() if program_slug else None
            specialization_slug = specialization_slug.strip() if specialization_slug else None
            mode = mode.strip() if mode else None
            duration = duration.strip() if duration else None
            price = price.strip() if price else None
            description = description.strip() if description else None


            required_fields = {
                "Name": name,
                "Program": program_slug,
                "Specialization": specialization_slug,
                "Mode": mode,
                "Price": price
            }
                
            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                
            
            program = self.get_program(program_slug)            
            specialization = self.get_specialization(specialization_slug)     

            if not program or not specialization:
                invalid_msg = "Failed! "

                if not program:
                    invalid_msg += "Invalid Program"
                else:
                    invalid_msg += "Invalid Specialization"

                messages.error(request, invalid_msg)
                return redirect(self.get_redirect_url())
                
            course = self.get_object()

            similar_course = self.model.objects.filter(
                company = course.company, name = name, program = program,
                specialization = specialization, mode = mode
                ).first()
            
            if similar_course:
                similar_error_msg = ""
                if similar_course.slug != course.slug:
                    similar_error_msg = "No changes detected"
                else:
                    similar_error_msg = "Similar course already exists"

                if similar_error_msg:
                    messages.warning(request, similar_error_msg)
                    return redirect(self.get_redirect_url())
            
            course.name = name
            course.program = program
            course.specialization = specialization
            course.mode = mode
            course.duration = duration
            course.price = price
            course.description = description
            if image:
                course.image = image
            course.save()
            
            messages.success(request, "Success! Course updated.")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Invalid Course")            
            
        except Exception as e:
            logger.exception(f"Error in post function of UpdateCourseView of customer app: {e}")
            messages.error(request, "Failed! An expected error occurred")

        return redirect(self.get_redirect_url())
    

class DeleteCourseView(BaseCourseView, View):
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()
            messages.success(request, "Success! Deleted course")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid Course")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteCourseView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)


class ListCourseProgramView(BaseCustomerView, ListView):
    model = Program
    queryset = model.objects.none()
    context_object_name = "programs"
    template_name = "customer_education/program/list.html"

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListCourseProgramView in customer app: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["course_program_page"] = True
        
        return context
    

class ListCourseSpecializationView(BaseCustomerView, ListView):
    model = Specialization
    queryset = model.objects.none()
    context_object_name = "specializations"
    template_name = "customer_education/specialization/list.html"

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListCourseSpecializationView in customer section: {e}")        
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["course_specialization_page"] = True
        context["programs"] = Program.objects.all()
        
        return context
    

class BaseEducationFaqView(BaseCustomerView, View):
    model = CourseFaq
    success_url = redirect_url = reverse_lazy("customer:course_faqs")
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["course_faq_page"] = True

        return context
    
    def get_course(self, course_slug):
        try:
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            return None
    

class ListCourseFaqView(BaseEducationFaqView, ListView):
    queryset = CourseFaq.objects.none()
    template_name = "customer_education/faq/list.html"
    context_object_name = "faqs"    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["list_course_faq_page"] = True

        return context

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
            
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListCourseFaqView in customer app: {e}")
            return self.queryset


class AddCourseFaqView(BaseEducationFaqView, CreateView):
    fields = ["company", "course", "question", "answer"]
    template_name = "customer_education/faq/add.html"
    success_url = redirect_url = reverse_lazy('customer:add_course_faqs')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company = self.get_company()
        context["add_course_faq_page"] = True
        context["programs"] = Program.objects.filter(company = company).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            course_slug = self.request.POST.get('course')
            question = request.POST.get("question")
            answer = request.POST.get("answer")

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Course": course_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)

            company = self.get_company()

            course = self.get_course(course_slug)

            if not course:
                messages.error(request, "Invalid Course")
                return redirect(self.redirect_url)

            CourseFaq.objects.update_or_create(company = company, course = course, question = question, defaults={"answer": answer})

            messages.success(request, f"Success! Created FAQ object for course: {course.name}")
            return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in post function of AddCourseFaqView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)


class UpdateCourseFaqView(BaseEducationFaqView, UpdateView):
    fields = ["course", "question", "answer"]
    template_name = "customer_education/faq/update.html"
    context_object_name = "faq"

    def get_redirect_url(self):
        try:
            return reverse_lazy('customer:update_course_faq', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url of UpdateCourseFaqView of customer app: {e}")
            return self.redirect_url
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company = self.get_company()
        self.object = self.get_object()
        context["programs"] = Program.objects.filter(company = company).order_by("name")
        context["courses"] = Course.objects.filter(company = company, program = self.object.course.program).order_by("name")

        return context    
        
    def post(self, request, *args, **kwargs):
        try:
            faq = self.get_object()

            course_slug = self.request.POST.get('course')
            question = request.POST.get("question")
            answer = request.POST.get("answer")

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Course": course_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            course = self.get_course(course_slug)

            if not course:
                messages.error(request, "Invalid Course")
                return redirect(self.get_redirect_url())

            similar_faq = self.model.objects.filter(company = faq.company, course = course, question = question, answer = answer).first()

            if similar_faq:
                if similar_faq.slug == faq.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar course FAQ already exists")
                return redirect(self.get_redirect_url())

            faq.course = course
            faq.question = question
            faq.answer = answer
            faq.save()

            messages.success(request, f"Success! Updated FAQ")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Invalid course FAQ object")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateCourseFaqView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteCourseFaqView(BaseEducationFaqView, View):
    def get_object(self):
        faq_slug = self.kwargs.get('course_faq_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = faq_slug, company__slug = company_slug)

    def post(self, request, *args, **kwargs):
        try:
            faq =  get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            course_name = faq.course.name
            faq.delete()

            messages.success(request, f"Success! Removed course FAQ object of: {course_name}")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Invalid Course FAQ")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteCourseFaqView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)


class ListCourseEnquiryView(BaseCustomerView, ListView):
    model = CourseEnquiry
    queryset = model.objects.none()
    context_object_name = "enquiries"
    template_name = "customer_education/enquiry/list.html"

    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company)
        except Exception as e:
            logger.exception(f"Error in get_queryset function of ListCourseEnquiryView of customer app: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["course_enquiry_page"] = True

        return context

class DeleteCourseEnquiryView(BaseCustomerView, View):
    model = CourseEnquiry
    success_url = redirect_url = reverse_lazy('customer:course_enquiries')        
    slug_url_kwarg = 'slug'

    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CourseEnquiry, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()

            messages.success(request, "Success! Delete Course Enquiry")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid Course Enquiry")

        except Exception as e:
            messages.error(request, "Failed! An unexpected error occurred")
            logger.exception(f"Error in post function of DeleteCourseEnquiryView of customer app: {e}")

        return redirect(self.redirect_url)
    

class BaseStudentTestimonialView(BaseCustomerView):
    model = StudentTestimonial
    success_url = redirect_url = reverse_lazy('customer:student_testimonials')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["testimonial_page"] = context["company_page"] = True

        return context    
    
    def get_course(self, course_slug):
        try:
            company = self.get_company()
            return get_object_or_404(Course, company = company, slug = course_slug)
        except Http404:
            return None
        
    def get_place(self, place_slug):
        try:
            return get_object_or_404(UniquePlace, slug = place_slug)
        except Http404:
            return None
    

class AddStudentTestimonialView(BaseStudentTestimonialView, CreateView):    
    template_name = "customer_education/testimonial/add.html"
    fields = ["company", "name", "image", "course", "place", "text", "rating", "order"]
    success_url = redirect_url = reverse_lazy('customer:add_student_testimonials')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["add_testimonial_page"] = True
        context["ratings"] = list(range(1,6))
        company = self.get_company()
        context["programs"] = Program.objects.filter(company = company)
        context["states"] = UniqueState.objects.all().order_by('name')
        
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            course_slug = request.POST.get("course")
            place_slug = request.POST.get("place")
            text = request.POST.get("testimonial")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            name = name.strip() if name else None
            course_slug = course_slug.strip() if course_slug else None
            place_slug = place_slug.strip() if place_slug else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Name": name,
                "Image": image,
                "Course": course_slug,
                "Place": place_slug,
                "Testimonal Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)
                

            course = self.get_course(course_slug)
            place = self.get_place(place_slug)

            if not course or not place:
                invalid_msg = ""
                if not course:
                    invalid_msg = "Invalid Course"
                else:
                    invalid_msg = "Invalid Place"

                messages.error(request, invalid_msg)
                return redirect(self.redirect_url)
                        
            if self.model.objects.filter(
                company = company, name = name, course = course, place = place
                ).exists():

                messages.warning(request, "Similar testimonial already exists")
                return redirect(self.redirect_url)
            
            self.model.objects.create(
                company = company, name = name, image = image, course = course, place = place,
                text = text, rating = rating, order = order
            )

            messages.success(request, "Success! Testimonial Created")
            return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in post function of AddStudentTestimonialView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.redirect_url)


class StudentTestimonialListView(BaseStudentTestimonialView, ListView):
    template_name = "customer_education/testimonial/list.html"
    context_object_name = "testimonials"
    queryset = StudentTestimonial.objects.none()
    
    def get_queryset(self):
        try:
            company = self.get_company()        
            return self.model.objects.filter(company = company).order_by("order")
        except Exception as e:
            logger.exception(f"Error in get_queryset function of StudentTestimonialListView in customer app: {e}")
            return self.queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["list_testimonial_page"] = True

        return context
    

class UpdateStudentTestimonialView(BaseStudentTestimonialView, UpdateView):    
    fields = ["name", "image", "course", "place", "text", "rating", "order"]
    template_name = "customer_education/testimonial/update.html"       

    def get_redirect_url(self):
        try:
            return reverse_lazy('customer:update_student_testimonial', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url of UpdateStudentTestimonialView of customer app: {e}")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["ratings"] = list(range(1,6))

        context["programs"] = Program.objects.filter(company = self.company).order_by("name")
        context["courses"] = Course.objects.filter(program = self.object.course.program).order_by("name")
        context["states"] = UniqueState.objects.all().order_by('name')
        context["districts"] = UniqueDistrict.objects.filter(state = self.object.place.state).order_by('name')
        context["places"] = UniquePlace.objects.filter(district = self.object.place.district).order_by('name')
        
        return context    

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            course_slug = request.POST.get("course")
            place_slug = request.POST.get("place")
            text = request.POST.get("testimonial")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            name = name.strip() if name else None
            course_slug = course_slug.strip() if course_slug else None
            place_slug = place_slug.strip() if place_slug else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Name": name,
                "Image": image,
                "Course": course_slug,
                "Place": place_slug,
                "Testimonal Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():
                if key == "Image" and self.object.image:
                    continue
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            course = self.get_course(course_slug)
            place = self.get_place(place_slug)

            if not course or not place:
                invalid_msg = ""
                if not course:
                    invalid_msg = "Invalid Course"
                else:
                    invalid_msg = "Invalid Place"

                messages.error(request, invalid_msg)
                return redirect(self.get_redirect_url())
            
            similar_client = self.model.objects.filter(
                company = self.object.company, name = name, course = course, place = place
                ).first()

            if similar_client:
                dublicate_error_msg = ""

                if similar_client.slug == self.object.slug:
                    if not (image or order or text or rating):
                        dublicate_error_msg = "No changes detected"
                else:
                    dublicate_error_msg = "Similar testimonial already exists"

                if dublicate_error_msg:
                    messages.warning(request, dublicate_error_msg)
                    return redirect(self.get_redirect_url())
            
            self.object.name = name
            self.object.course = course
            self.object.place = place
            self.object.text = text
            self.object.rating = rating
            self.object.order = order

            if image:
                self.object.image = image

            self.object.save()

            messages.success(request, "Success! Testimonial Updated")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateStudentTestimonialView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class DeleteStudentTestimonialView(BaseStudentTestimonialView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()
            messages.success(request, "Success! Testimonial Deleted")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in delete function of DeleteStudentTestimonialView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)


# Clients
class BaseClientView(BaseCustomerView):
    model = Client
    success_url = redirect_url = reverse_lazy('customer:clients')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["client_page"] = True

        return context
    

class AddClientView(BaseClientView, CreateView):    
    template_name = "customer_clients/add.html"
    fields = ["company", "name", "image", "order"]
    success_url = redirect_url = reverse_lazy('customer:add_clients')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_client_page"] = True        

        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()

            if company.type.name == "Education":
                obj = "Corporate Partner"
            else:
                obj = "Client"

            name = request.POST.get("name")
            image = request.FILES.get("image")
            order = request.POST.get("order", 0)

            name = name.strip() if name else None

            if not name or not image:
                message = "Failed! Name is required"
                if name:
                    message = "Failed! Image is required"
                
                messages.error(request, message)
                return redirect(self.redirect_url)
            
            if self.model.objects.filter(company = company, name = name).exists():                
                messages.warning(request, f"Similar {obj} already exists")
                return redirect(self.redirect_url)
            
            self.model.objects.create(company = company, name = name, image = image, order = order)
            messages.success(request, f"Success! {obj} Created")
            return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in post function of AddClientView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.redirect_url)


class ClientListView(BaseClientView, ListView):
    template_name = "customer_clients/list.html"
    context_object_name = "clients"
    queryset = Client.objects.none()
    
    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company).order_by("order")
        
        except Exception as e:
            logger.exception(f"Error in get_queryset of ClientListView in customer app: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["list_client_page"] = True

        return context


class UpdateClientView(BaseClientView, UpdateView):    
    fields = ["name", "image", "order"]

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            if self.object.company.type.name == "Education":
                obj = "Corporate Partner"
            else:
                obj = "Client"

            name = request.POST.get("name")
            image = request.FILES.get("image")
            order = request.POST.get("order", 0)

            name = name.strip() if name else None

            if not name:
                messages.error(request, "Failed! Name is required")
                return redirect(self.redirect_url)

            if not image and not self.object.image:
                messages.error(request, "Failed! Image is required")
                return redirect(self.redirect_url)     
            
            similar_client = self.model.objects.filter(company = self.object.company, name = name).first()

            if similar_client:
                dublicate_error_msg = ""

                if similar_client.slug == self.object.slug:
                    if not image and not order:
                        dublicate_error_msg = "No changes detected"
                else:
                    dublicate_error_msg = f"Similar {obj} already exists"

                if dublicate_error_msg:
                    messages.warning(request, dublicate_error_msg)
                    return redirect(self.redirect_url)
            
            self.object.name = name
            self.object.order = order

            if image:
                self.object.image = image

            self.object.save()

            messages.success(request, f"Success! {obj} Updated")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, f"Invalid {obj}")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateClientView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
        

class DeleteClientView(BaseClientView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()
            messages.success(request, "Success! Client Deleted")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Invalid client")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteClientView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

# General Testimonial
class BaseTestimonialView(BaseCustomerView):
    model = Testimonial
    success_url = redirect_url = reverse_lazy('customer:testimonials')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["testimonial_page"] = context["company_page"] = True

        return context    
        
    def get_place(self, place_slug):
        try:
            return get_object_or_404(UniquePlace, slug = place_slug)
        except Http404:
            return None
    

class AddTestimonialView(BaseTestimonialView, CreateView):    
    template_name = "customer_testimonials/add.html"
    fields = ["company", "name", "image", "company", "place", "text", "rating", "order"]
    success_url = redirect_url = reverse_lazy('customer:add_testimonials')    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["add_testimonial_page"] = True
        context["ratings"] = list(range(1,6))
        context["states"] = UniqueState.objects.all().order_by('name')
        
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            client_company = request.POST.get("company")
            place_slug = request.POST.get("place")
            text = request.POST.get("testimonial")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            name = name.strip() if name else None
            client_company = client_company.strip() if client_company else None
            place_slug = place_slug.strip() if place_slug else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Name": name,
                "Image": image,
                "Company": client_company,
                "Place": place_slug,
                "Testimonal Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)
                
            place = self.get_place(place_slug)

            if not place:                
                messages.error(request, "Invalid Place")
                return redirect(self.redirect_url)
                        
            if self.model.objects.filter(
                company = company, name = name, client_company = client_company, place = place
                ).exists():

                messages.warning(request, "Similar testimonial already exists")
                return redirect(self.redirect_url)
            
            self.model.objects.create(
                company = company, name = name, image = image, client_company = client_company, place = place,
                text = text, rating = rating, order = order
            )

            messages.success(request, "Success! Testimonial Created")
            return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in post function of AddTestimonialView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.redirect_url)


class TestimonialListView(BaseTestimonialView, ListView):
    template_name = "customer_testimonials/list.html"
    context_object_name = "testimonials"
    queryset = Testimonial.objects.none()
    
    def get_queryset(self):
        try:
            company = self.get_company()
            return self.model.objects.filter(company = company).order_by("order")        
        except Exception as e:
            logger.exception(f"Error in get_queryset function of TestimonialListView in customer app: {e}")
            return self.queryset
    

class UpdateTestimonialView(BaseTestimonialView, UpdateView):    
    fields = ["name", "image", "company", "place", "text", "rating", "order"]
    template_name = "customer_testimonials/update.html"
    slug_url_kwarg = 'slug'

    def get_redirect_url(self):
        try:
            return reverse_lazy('customer:update_testimonial', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url of UpdateTestimonialView of customer app: {e}")
            return self.redirect_url
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["ratings"] = list(range(1,6))
        
        context["states"] = UniqueState.objects.all().order_by('name')
        context["districts"] = UniqueDistrict.objects.filter(state = self.object.place.state).order_by('name')
        context["places"] = UniquePlace.objects.filter(district = self.object.place.district).order_by('name')
        
        return context    

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            client_company = request.POST.get("company")
            place_slug = request.POST.get("place")
            text = request.POST.get("testimonial")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            name = name.strip() if name else None
            client_company = client_company.strip() if client_company else None
            place_slug = place_slug.strip() if place_slug else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Name": name,
                "Image": image,
                "Company": client_company,
                "Place": place_slug,
                "Testimonal Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():
                if key == "Image" and self.object.image:
                    continue
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            place = self.get_place(place_slug)

            if not place:
                messages.error(request, "Invalid Place")
                return redirect(self.get_redirect_url())
            
            similar_client = self.model.objects.filter(
                company = self.object.company, name = name, client_company = client_company, place = place
                ).first()

            if similar_client:
                dublicate_error_msg = ""

                if similar_client.slug == self.object.slug:
                    if not (image or order or text or rating):
                        dublicate_error_msg = "No changes detected"
                else:
                    dublicate_error_msg = "Similar testimonial already exists"

                if dublicate_error_msg:
                    messages.warning(request, dublicate_error_msg)
                    return redirect(self.get_redirect_url())
            
            self.object.name = name
            self.object.client_company = client_company
            self.object.place = place
            self.object.text = text
            self.object.rating = rating
            self.object.order = order

            if image:
                self.object.image = image

            self.object.save()

            messages.success(request, "Success! Testimonial Updated")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateTestimonialView of customer app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class DeleteTestimonialView(BaseTestimonialView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()
            messages.success(request, "Success! Testimonial Deleted")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in delete function of DeleteTestimonialView of customer app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.redirect_url)