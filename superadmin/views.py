from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, View, CreateView, ListView, UpdateView, DetailView, DeleteView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import Http404, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, logout
from django.db import IntegrityError
from django.db import transaction
from django.contrib.auth.models import User
import logging
from .tasks import send_company_created_email
from django.db import transaction
from queryset_sequence import QuerySetSequence
from utility.text import clean_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify

from .forms import (
    CourseMultiPageDescriptionForm, CourseDetailDescriptionForm, ServiceMultiPageDescriptionForm, RegistrationMultiPageDescriptionForm,
    ServiceDetailDescriptionForm, RegistrationDetailPageDescriptionForm, ProductMultiPageDescriptionForm, FaqForm,
    ProductDetailDescriptionForm, CompanyForm, BlogContentForm, MetaTagDescriptionForm, HomeContentForm, AboutUsContentForm,
    PrivacyPolicyForm, TermsAndConditionForm
    )

from custom_pages.models import (
    AboutUs, ContactUs, FAQ, PrivacyPolicy, TermsAndCondition,
    ShippingAndDeliveryPolicy, CancellationAndRefundPolicy
    )
from company.models import Company, CompanyType, Client, Testimonial, Testimonial, ContactEnquiry, Banner, ClientSlider
from locations.models import UniqueState, UniqueDistrict, UniquePlace

from product.models import (
    Product, Category as ProductCategory, SubCategory as ProductSubCategory, Color, Size, Brand,
    Faq as ProductFaq, Review as ProductReview, Enquiry as ProductEnquiry,
    SubCategoryFaq as ProductSubCategoryFaq,

    ProductDetailPage, Feature as ProductFeature,
    BulletPoint as ProductBulletPoint, Timeline as ProductTimeline,

    MultiPage as ProductMultiPage, MultiPageFeature as ProductMultiPageFeature,     
    MultiPageBulletPoint as ProductMultiPageBulletPoint, TextEditor as ProductTextEditor,
    MultiPageFaq as ProductMultiPageFaq, MultiPageTimeline as ProductMultiPageTimeline
    )

from educational.models import (
    Program, Course, Specialization, Enquiry as CourseEnquiry, CourseDetail, Feature as CourseFeature,
    VerticalTab as CourseVerticalTab, VerticalBullet as CourseVerticalBullet, HorizontalTab as CourseHorizontalTab,
    HorizontalBullet as CourseHorizontalBullet, TableData as CourseTableData, Table as CourseTable,
    BulletPoints as CourseBulletPoint, Timeline as CourseTimeline, Faq as CourseFaq,
    Testimonial as StudentTestimonial, MultiPage as CourseMultiPage, TextEditor as CourseTextEditor,

    MultiPageFeature as CourseMultiPageFeature, MultiPageVerticalTab as CourseMultiPageVerticalTab, 
    MultiPageVerticalBullet as CourseMultiPageVerticalBullet, MultiPageHorizontalTab as CourseMultiPageHorizontalTab,
    MultiPageHorizontalBullet as CourseMultiPageHorizontalBullet, MultiPageTableData as CourseMultiPageTableData, 
    MultiPageTable as CourseMultiPageTable, MultiPageBulletPoints as CourseMultiPageBulletPoint, 
    MultiPageTimeline as CourseMultiPageTimeline, MultiPageFaq as CourseMultiPageFaq,

     SpecializationFaq as CourseSpecializationFaq,
    )

from directory.models import PostOffice, PoliceStation, Bank, Court, Destination

from service.models import (
    Service, Category as ServiceCategory, SubCategory as ServiceSubCategory, Enquiry as ServiceEnquiry,
    Faq as ServiceFaq, ServiceDetail, Feature as ServiceFeature,
    VerticalTab as ServiceVerticalTab, VerticalBullet as ServiceVerticalBullet, HorizontalTab as ServiceHorizontalTab,
    HorizontalBullet as ServiceHorizontalBullet, TableData as ServiceTableData, Table as ServiceTable,
    BulletPoints as ServiceBulletPoint, Timeline as ServiceTimeline,

    TextEditor as ServiceTextEditor,

    MultiPage as ServiceMultiPage, MultiPageFeature as ServiceMultiPageFeature, MultiPageHorizontalTab as ServiceMultiPageHorizontalTab,
    MultiPageHorizontalBullet as ServiceMultiPageHorizontalBullet, MultiPageVerticalTab as ServiceMultiPageVerticalTab,
    MultiPageVerticalBullet as ServiceMultiPageVerticalBullet, MultiPageBulletPoint as ServiceMultiPageBulletPoint,
    MultiPageTimeline as ServiceMultiPageTimeline, MultiPageFaq as ServiceMultiPageFaq,
    MultiPageTable as ServiceMultiPageTable, MultiPageTableData as ServiceMultiPageTableData,
    )

from registration.models import (
    RegistrationType, RegistrationSubType, Registration, Faq as RegistrationFaq,
    Enquiry as RegistrationEnquiry,

    RegistrationDetailPage, Feature as RegistrationFeature, HorizontalTab as RegistrationHorizontalTab,
    HorizontalBullet as RegistrationHorizontalBullet, VerticalTab as RegistrationVerticalTab, VerticalBullet as RegistrationVerticalBullet, 
    Table as RegistrationTable, BulletPoint as RegistrationBulletPoint, TableData as RegistrationTableData,
    Timeline as RegistrationTimeline,

    MultiPage as RegistrationMultiPage, MultiPageFeature as RegistrationMultiPageFeature, MultiPageVerticalTab as RegistrationMultiPageVerticalTab,
    MultiPageVerticalBullet as RegistrationMultiPageVerticalBullet, MultiPageHorizontalTab as RegistrationMultiPageHorizontalTab,
    MultiPageHorizontalBullet as RegistrationMultiPageHorizontalBullet, MultiPageTable as RegistrationMultiPageTable,
    MultiPageTableData as RegistrationMultiPageTableData, MultiPageTimeline as RegistrationMultiPageTimeline,
    MultiPageFaq as RegistrationMultiPageFaq, MultiPageBulletPoint as RegistrationMultiPageBulletPoint,
    TextEditor as RegistrationTextEditor, SubTypeFaq
    )
from blog.models import Blog
from base.models import MetaTag
from home.models import HomeContent

logger = logging.getLogger(__name__)

def get_state(slug):
    try:
        return get_object_or_404(UniqueState, slug = slug)
    except Http404:
        return None
    
def get_district(slug):
        try:
            return get_object_or_404(UniqueDistrict, slug = slug)
        except Http404:
            return None
        
def get_place(slug):
        try:
            return get_object_or_404(UniquePlace, slug = slug)
        except Http404:
            return None  


@method_decorator(never_cache, name="dispatch")
class AdminBaseView(LoginRequiredMixin, View):
    login_url = reverse_lazy("authentication:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:

            companies = Company.objects.all().order_by("-updated")
            context["product_companies"] = companies.filter(type__name = "product").values("slug", "name").order_by("-updated")
            context["education_companies"] = companies.filter(type__name = "education").values("slug", "name").order_by("-updated")
            context["company_types"] = CompanyType.objects.all().order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin base view: {e}")
        return context
    

class HomeView(AdminBaseView, TemplateView):
    template_name = 'admin/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["home_page"] = True
        return context


# Company

class BaseCompanyView(AdminBaseView, View):
    model = Company

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get("slug"))
        except Http404:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # context['company_type_page'] = True
            context["current_company"] = self.get_current_company()
            context["company_page"] = True
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin base company view: {e}")
        return context

class CompanyView(BaseCompanyView, ListView):
    model = CompanyType
    template_name = "admin_company/company/list.html"
    context_object_name = "company_types"
    queryset = CompanyType.objects.all().order_by("-updated")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["company_types"] = CompanyType.objects.all().order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting context data of company view in superadmin: {e}")
        return context


class CompanyListView(CompanyView, ListView):
    model = Company
    queryset = Company.objects.none()
    context_object_name = "companies"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['company_list_page'] = True
            try:
                context['current_company_type'] = get_object_or_404(CompanyType, slug = self.kwargs.get("slug"))
            except Http404:
                pass

        except Exception as e:
            logger.exception(f"Error in fetching context data of admin company list view: {e}")
        return context
    
    def get_queryset(self):
        try:
            return Company.objects.filter(type__slug = self.kwargs.get("slug")).order_by("-updated")        
        except Exception as e:
            logger.exception(f"Error in fetching queryset in company list view: {e}")

        return self.queryset
    

class CompanyDetailView(BaseCompanyView, DetailView):
    template_name = "admin_company/company/detail.html"
    context_object_name = "company"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            try:
                current_company = get_object_or_404(Company, slug = self.kwargs.get("slug"))
                context["current_company"] = current_company

                if current_company.type.name == "Product":
                    products = Product.objects.filter(company = current_company).order_by("-updated")
                    context["products"] = products if products else None

                    types = ProductCategory.objects.filter(company = current_company).order_by("-updated")
                    context["types"] = types if types else None

                    sub_types = ProductSubCategory.objects.filter(company = current_company).order_by("-updated")
                    context["sub_types"] = sub_types if sub_types else None

            except Http404:
                messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of company detail view of superadmin: {e}")

        return context
    

class AddCompanyView(BaseCompanyView, CreateView):
    success_url = redirect_url = reverse_lazy('superadmin:add_company')
    form_class = CompanyForm
    template_name = "admin_company/company/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = MetaTag.objects.all().order_by("-updated")
        return context

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            name = request.POST.get("name")
            type = request.POST.get("type")
            sub_type = request.POST.get("sub_type")
            slug = request.POST.get("slug")
            favicon = request.FILES.get('favicon')
            logo = request.FILES.get('logo')
            phone1 = request.POST.get("phone1")
            phone2 = request.POST.get("phone2")
            whatsapp = request.POST.get("whatsapp")
            email = request.POST.get("email")

            summary = clean_string(request.POST.get("summary", ""))

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            add_on_company_types = request.POST.getlist("add_on_company_type")                        

            name = name.strip() if name else None
            type = type.strip() if type else None
            sub_type = sub_type.strip() if sub_type else None
            slug = slug.strip() if slug else None
            phone1 = phone1.strip() if phone1 else None
            phone2 = phone2.strip() if phone2 else None
            whatsapp = whatsapp.strip() if whatsapp else None
            email = email.strip() if email else None           

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]
            
            required_fields = {
                "Name": name, "Type": type, "Sub Type": sub_type, "Summary": summary,
                "Contact Number 1": phone1, "Contact Number 2": phone2, 
                "Whats App Number": whatsapp, "Email": email, "Meta Tags": meta_tags, 
                "Meta Description": meta_description
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)

            description = None
            if form.is_valid():
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")
                footer_content = cleaned_form.get("footer_content")

                description = description.strip() if description else None
                footer_content = footer_content.strip() if footer_content else None

            type = CompanyType.objects.get(slug = type)

            if self.model.objects.filter(type = type, sub_type = sub_type).exists():
                messages.error(request, "Failed! Company with provided sub type already exists.")
                return redirect(self.redirect_url)

            if slug:
                slug = slugify(slug)

                if Company.objects.filter(slug = slug).exists():
                    messages.error(request, "Failed! Company with similar slug already exists.")
                    return redirect(self.redirect_url)
            

            updating_meta_tags = []
            with transaction.atomic():

                company_obj = self.model.objects.create(
                    name = name, type=type, sub_type=sub_type, slug=slug,

                    favicon=favicon, logo=logo,
                    
                    phone1=phone1, phone2=phone2, whatsapp=whatsapp, email=email,
                    
                    summary = summary, description=description, 
                    
                    meta_title = meta_title, meta_description = meta_description, 
                    
                    footer_content = footer_content,
                    
                    )

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                company_obj.meta_tags.set(meta_tag_objects)

                if add_on_company_types:
                    company_type_ids = CompanyType.objects.filter(name__in = add_on_company_types).values_list("id", flat=True)
                    company_obj.add_on_company_types.set(company_type_ids)

                company_obj.save()
                
                User.objects.create_user(
                    username = company_obj.email,
                    email = company_obj.email,
                    password = company_obj.phone1
                )

                company = {
                    "name": company_obj.name,
                    "phone1": company_obj.phone1,
                    "email": company_obj.email
                }

                # send_company_created_email.delay(company)                
                messages.success(self.request, "Added Company")
                return redirect(self.success_url)
        
        except Exception as e:
            logger.exception(f"Error in adding company: {e}")
            return redirect(self.redirect_url)
        
    
class UpdateCompanyView(BaseCompanyView, UpdateView):
    form_class = CompanyForm
    template_name = "admin_company/company/update.html"
    success_url = redirect_url = reverse_lazy('superadmin:companies')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context["tags"] = MetaTag.objects.all().order_by("-updated")
        return context

    def get_success_url(self):
        try:
            slug = self.request.POST.get('slug')
            if slug:
                return reverse_lazy('superadmin:update_company',  kwargs = {'slug' : slug})    
            return reverse_lazy('superadmin:update_company',  kwargs = {'slug' : self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in getting success url of update company view: {e}")
            return self.success_url

    def get_redirect_url(self):
        try:
            self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of update company view: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            name = request.POST.get("name")
            type = request.POST.get("type")
            sub_type = request.POST.get("sub_type")
            slug = request.POST.get("slug")
            favicon = request.FILES.get('favicon')
            logo = request.FILES.get('logo')
            phone1 = request.POST.get("phone1")
            phone2 = request.POST.get("phone2")
            whatsapp = request.POST.get("whatsapp")
            email = request.POST.get("email")

            summary = clean_string(request.POST.get("summary", ""))

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            add_on_company_types = request.POST.getlist("add_on_company_type")

            name = name.strip() if name else None
            type = type.strip() if type else None
            sub_type = sub_type.strip() if sub_type else None
            slug = slug.strip() if slug else None
            phone1 = phone1.strip() if phone1 else None
            phone2 = phone2.strip() if phone2 else None
            whatsapp = whatsapp.strip() if whatsapp else None
            email = email.strip() if email else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            required_fields = {
                "Name": name, "Type": type, "Sub Type": sub_type, 
                "Summary": summary, "Contact Number 1": phone1,
                "Contact Number 2": phone2, "Whats App Number": whatsapp,
                "Email": email, "Meta Tags": meta_tags, 
                "Meta Description": meta_description
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)

            type = CompanyType.objects.get(slug = type)

            self.object = self.get_object()

            description = None

            if form.is_valid():
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")
                footer_content = cleaned_form.get("footer_content")

                description = description.strip() if description else None
                footer_content = footer_content.strip() if footer_content else None

            if self.model.objects.filter(type = type, sub_type = sub_type).exclude(slug = self.object.slug).exists():
                messages.error(request, "Company with the provided sub type already exists")
                return redirect(self.get_redirect_url())

            if slug:
                slug = slugify(slug)

                if Company.objects.filter(slug = slug).exclude(pk = self.object.pk).exists():
                    messages.error(request, "Failed! Company with similar slug already exists.")
                    return redirect(self.get_redirect_url())

            updating_meta_tags = []

            self.object.name = name
            self.object.type = type
            self.object.sub_type = sub_type
            self.object.summary = summary
            if slug:
                self.object.slug = slug
            self.object.favicon = favicon if favicon else self.object.favicon
            self.object.logo = logo if logo else self.object.logo
            self.object.phone1 = phone1
            self.object.phone2 = phone2
            self.object.whatsapp = whatsapp
            self.object.email = email
            self.object.description = description

            self.object.meta_title = meta_title
            self.object.meta_description = meta_description

            self.object.footer_content = footer_content

            for tag in meta_tags:
                if not MetaTag.objects.filter(slug = tag).exists():

                    new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                    if not new_tag.slug in updating_meta_tags:
                        updating_meta_tags.append(new_tag.slug)

                else:
                    if not tag in updating_meta_tags:
                        updating_meta_tags.append(tag)

            self.object.add_on_company_types.clear()
            if add_on_company_types:
                company_type_ids = CompanyType.objects.filter(name__in = add_on_company_types).values_list("id", flat=True)
                self.object.add_on_company_types.set(company_type_ids)

            self.object.save()

            meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
            self.object.meta_tags.set(meta_tag_objects)

            messages.success(request, "Company Updation Successfull.")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in updating company: {e}")
            return redirect(self.get_redirect_url())


class DeleteCompanyView(BaseCompanyView, UpdateView):
    success_url = redirect_url = reverse_lazy("superadmin:companies")
    slug_url_kwarg = 'slug'
            
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Company Deletion Successfull.")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in deleting company: {e}")

        return redirect(self.redirect_url)
        

class CompanyTypeListView(BaseCompanyView, ListView):
    queryset = CompanyType.objects.all().order_by("-updated")
    context_object_name = "types"
    template_name = "admin_company/types/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            pass
        except Exception as e:
            logger.exception(f"Error in fetching context data of company list view: {e}")
        return context
        

class AddCompanyTypeView(BaseCompanyView, CreateView):
    model = CompanyType
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("superadmin:company_types")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                company_type, created = self.model.objects.get_or_create(name = name)

                if created:
                    messages.success(request, "Success! Company type created.")
                    return redirect(self.success_url)

                else:
                    messages.warning(request, "Company type already exists.")

            else:
                messages.error(request, "Name is required.")            
        
        except Exception as e:
            logger.exception(f"Error in creating company type: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.redirect_url)
    

class UpdateCompanyTypeView(BaseCompanyView, View):
    model = CompanyType
    fields = ["name", "slug"]    
    success_url = redirect_url = reverse_lazy('superadmin:company_types')
        
    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("slug"))
        except Exception as e:
            logger.exception(f"Error in fetching the object in update company view: {e}")
        
        return None

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")            

            self.object = self.get_object()

            if self.object:
                self.object.name = name.strip()
                self.object.slug = None

                self.object.save()

                messages.success(request, "Company Type Updation Successfull.")
                return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in updating company type: {e}")
            return redirect(self.redirect_url())
    

class DeleteCompanyTypeView(BaseCompanyView, View):
    model = CompanyType
    success_url = redirect_url = reverse_lazy("superadmin:company_types")

    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Company Type")
        except Exception as e:
            logger.exception(f"Error in getting company type object: {e}")
            
        return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Company Type Deletion Successfull.")
            return redirect(self.success_url)
        except Exception as e:
            logger.exception(f"Error in deleting company type: {e}")
            return redirect(self.redirect_url)


# Product Company
class BaseProductCompanyView(BaseCompanyView, View):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try: 
            context["company_type"] = False
            context["product_company_page"] = True
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            logger.exception(f"Invalid product company in context of base product company view of superadmin.")
        except Exception as e:
            logger.exception(f"Error in fetching context data of base product company view of super admin: {e}")
        return context


class BaseProductView(BaseProductCompanyView, View):
    model = Product
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:products', kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of BaseProductView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_object(self):
        try:
            company_slug = self.kwargs.get(self.slug_url_kwarg)
            product_slug = self.kwargs.get('product_slug')

            return get_object_or_404(self.model, company__slug = company_slug, slug = product_slug)
        except Http404:
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company_page"] = True
        context["product_page"] = True        
        return context

class ListProductView(BaseProductView, ListView):
    model = Product
    queryset = model.objects.none()
    context_object_name = "products"
    template_name = "product_company/products/list.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
    
    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug')).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of list product view of superadmin side: {e}")
            return self.queryset    
    

class AddProductView(BaseProductView, CreateView):
    fields = "__all__"
    success_url = redirect_url = reverse_lazy("superadmin:home")
    template_name = "product_company/products/add.html"

    def get_success_url(self):        
        return reverse_lazy("superadmin:add_product", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["add_product_page"] = True

            context["sizes"] = Size.objects.all().order_by("-updated")
            context["colors"] = Color.objects.all().order_by("-updated")
            context["units"] = sorted(["mm", "cm", "m"])
            current_company = self.get_current_company()

            context["categories"] = ProductCategory.objects.filter(company = current_company).values("slug", "name").order_by("-updated")
            context["sub_categories"] = ProductSubCategory.objects.filter(company = current_company).values("slug", "name").order_by("-updated")
            context["colors"] = Color.objects.filter(company = current_company).values("slug", "name", "hexa").order_by("-updated")
            context["sizes"] = Size.objects.filter(company = current_company).values("slug", "name").order_by("-updated")
            context["brands"] = Brand.objects.filter(company = current_company).values("slug", "name").order_by("-updated")            

        except Exception as e:
            logger.warning(f"Error in loading context data of add product view: {e}")
        return context
    
    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."
        try:
            product_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
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
                    return redirect(self.get_redirect_url())
                
            try:
                stock = int(stock)
                if stock <= 0:
                    raise ValueError("Stock must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid stock number.")
                return redirect(self.get_redirect_url())                        
                
            category = get_object_or_404(ProductCategory, slug = category_slug)
            sub_category = get_object_or_404(ProductSubCategory, slug = sub_category_slug)
            brand = get_object_or_404(Brand, slug = brandSlug)

            product, created = self.model.objects.get_or_create(
                company = product_company,
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
                            logger.exception(f"Size object not found for slug: {sizeSlug}")
                            continue

                    product.sizes.set(size_list)

                if color and len(color) > 0:
                    color_list = []
                    for colorSlug in color:
                        try:
                            color_obj = get_object_or_404(Color, slug = colorSlug)
                            color_list.append(color_obj.pk)
                        except Http404:
                            logger.exception(f"Color object not found for slug: {sizeSlug}")
                            continue

                    product.colors.set(color_list)

                product.save()
            else:
                messages.warning(request, "Failed! Product already exists.")
                return redirect(self.get_redirect_url())

            messages.success(request, "Success! Product created.")
            return redirect(self.get_success_url())

        except Http404:
            error_msg = "Failed. Invalid Category."
            if category:
                error_msg = "Failed! Invalid sub category"

        except Exception as e:
            logger.exception(f"Error in adding product: {e}")

        messages.error(request, error_msg)
        return redirect(self.get_redirect_url())
    

class UpdateProductView(BaseProductView, UpdateView):
    fields = "__all__"    
    template_name = "product_company/products/update.html"
    slug_url_kwarg = "product_slug"
    context_object_name = "product"    

    def get_object(self):
        try:
            return get_object_or_404(self.model, company__slug = self.kwargs.get("slug"), slug = self.kwargs.get("product_slug"))
        except Http404:
            return None

    def get_redirect_url(self):
        try:
            return reverse_lazy("superadmin:update_product", kwargs = {"slug": self.kwargs.get("slug"), "product_slug": self.kwargs.get("product_slug")})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url of UpdateProductView: {e}")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["update_product_page"] = True            
            
            context["units"] = sorted(["mm", "cm", "m"])
            current_company = self.get_current_company()

            context["categories"] = ProductCategory.objects.filter(company = current_company).values("slug", "name").order_by("-updated")

            self.object = self.get_object()

            context["colors"] = Color.objects.filter(company = current_company).values("slug", "name", "hexa").order_by("-updated")            
            context["brands"] = Brand.objects.filter(company = current_company).values("slug", "name").order_by("-updated")            

            if self.object:
                context["sub_categories"] = ProductSubCategory.objects.filter(company = self.object.company, category = self.object.category).values("slug", "name").order_by("-updated")
                context["sizes"] = Size.objects.filter(company = self.object.company, category = self.object.category).values("slug", "name").order_by("-updated")

        except Exception as e:
            logger.warning(f"Error in loading context data of add product view: {e}")
        return context
    
    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."
        try:
            self.object = self.get_object()

            if not self.object:
                messages.error(request, "Failed! Invalid Product.")

            name = clean_string(request.POST.get("name", ""))
            category_slug = request.POST.get("category")
            sub_category_slug = request.POST.get("sub_category")
            brandSlug = request.POST.get("brand")
            image = request.FILES.get("image")
            sku = clean_string(request.POST.get("sku", ""))
            stock = clean_string(request.POST.get("stock", ""))
            price = clean_string(request.POST.get("price", ""))
            description = clean_string(request.POST.get("description", ""))
            size = request.POST.getlist("size")
            color = request.POST.getlist("color")
            length = request.POST.get("length")
            width = clean_string(request.POST.get("width", ""))
            height = clean_string(request.POST.get("height", ""))
            weight = clean_string(request.POST.get("weight", ""))
            unit = clean_string(request.POST.get("unit", ""))

            required_fields = {
                "Name": name,
                "Product Category": category_slug,
                "Product Sub Category": sub_category_slug,
                "Brand": brandSlug,
                "Product Image": image if not self.object.image else True,
                "Stock": stock,
                "Price": price                
            }

            if length or width or height:                
                required_fields["unit"] = unit

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed. {field_name.title()} is required.")
                    return redirect(self.get_redirect_url())
                
            try:
                stock = int(stock)
                if stock <= 0:
                    raise ValueError("Stock must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid stock number.")
                return redirect(self.get_redirect_url())            
                
            category = get_object_or_404(ProductCategory, slug = category_slug)
            sub_category = get_object_or_404(ProductSubCategory, slug = sub_category_slug)
            brand = get_object_or_404(Brand, slug = brandSlug)

            if not self.model.objects.filter(
                name = name, category = category, sub_category = sub_category, brand = brand,
                price = price
            ).exclude(pk = self.object.pk).exists():
            
                self.object.name = name
                self.object.category = category
                self.object.sub_category = sub_category
                
                self.object.brand = brand
                if image:
                    self.object.image = image
                self.object.sku = sku
                self.object.stock = stock
                self.object.price = price
                
                self.object.description = description
                self.object.length = length if length else 0
                self.object.width = width if width else 0
                
                self.object.height = height if height else 0
                self.object.weight = weight if weight else 0
                self.object.unit = unit if unit else None              

                self.object.save()
            
                if size and len(size) > 0:
                    size_list = []
                    for sizeSlug in size:
                        try:
                            size_obj = get_object_or_404(Size, slug = sizeSlug)
                            size_list.append(size_obj.pk)
                        except Http404:
                            logger.exception(f"Size object not found for slug: {sizeSlug}")
                            continue

                    self.object.sizes.set(size_list)

                if color and len(color) > 0:
                    color_list = []
                    for colorSlug in color:
                        try:
                            color_obj = get_object_or_404(Color, slug = colorSlug)
                            color_list.append(color_obj.pk)
                        except Http404:
                            logger.exception(f"Color object not found for slug: {sizeSlug}")
                            continue

                    self.object.colors.set(color_list)

            else:
                messages.warning(request, "Failed! Similar product already exists.")
                return redirect(self.get_redirect_url())

            messages.success(request, "Success! Product updated.")
            return redirect(self.get_success_url())

        except Http404:
            error_msg = "Failed. Invalid Category."
            if category:
                error_msg = "Failed! Invalid sub category"

        except Exception as e:
            logger.exception(f"Error in adding product: {e}")

        messages.error(request, error_msg)
        return redirect(self.get_redirect_url())
    


class DeleteProductView(BaseProductView, UpdateView):
    slug_url_kwarg = 'product_slug'

    def post(self, request, *args, **kwargs):
        try:
            products = self.model.objects.filter(company__slug = self.kwargs.get("slug"), slug = self.kwargs.get("product_slug"))
            if not products:
                messages.error(request, "Invalid product")
                return redirect(self.get_redirect_url())
            
            products.delete()
            messages.success(request, "Success! Product Deleted")
            return redirect(self.get_success_url())
        except Exception as e:
            logger.exception(f"Error in post function of DeleteProductView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")
            return redirect(self.get_redirect_url())


class BaseBrandView(BaseProductCompanyView, View):
    model = Brand
    success_url = redirect_url = reverse_lazy("superadmin:brands")

    def get_success_url(self):        
        return reverse_lazy("superadmin:brands", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()


class ListBrandView(BaseBrandView, ListView):
    queryset = Brand.objects.none()
    context_object_name = "brands"
    template_name = "product_company/brands/list.html"
    
    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug')).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of list brand view of superadmin side: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:                        
            context["product_brand_page"] = True        
        except Exception as e:
            logger.exception(f"Error in fetching context data of list brand view of superadmin: {e}")
        return context
    

class AddBrandView(BaseBrandView, CreateView):
    fields = ["company", "name"]    

    def post(self, request, *args, **kwargs):
        try:
            product_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                product, created = self.model.objects.get_or_create(company = product_company, name = name)

                if created:
                    messages.success(request, "Success! Product brand created.")
                    return redirect(self.get_success_url())

                else:
                    messages.warning(request, "Brand already exists.")

            else:
                messages.error(request, "Brand name is required.")            
        
        except Exception as e:
            logger.exception(f"Error in creating product brand: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())


class UpdateBrandView(BaseBrandView, CreateView):
    fields = ["name"]
    slug_url_kwarg = "brand_slug"

    def post(self, request, *args, **kwargs):
        try:
            name = clean_string(request.POST.get("name", ""))

            if not name:
                messages.error(request, "Name is required.")            
                return redirect(self.get_redirect_url())


            self.object = self.get_object()
        
            if not self.model.objects.filter(
                company = self.object.company, name = name
                ).exclude(
                    pk = self.object.pk
                    ).exists():
                
                self.object.name = name
                self.object.save()                
                            
                messages.success(request, "Success! Product brand updated.")
                return redirect(self.get_success_url())

            else:
                messages.warning(request, "Similar brand already exists.")
        
        except Exception as e:
            logger.exception(f"Error in UpdateBrandView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class DeleteBrandView(BaseBrandView, View):
    def post(self, request, *args, **kwargs):
        try:
            company_slug = self.kwargs.get("slug")
            brand_slug = self.kwargs.get("brand_slug")

            brands = self.model.objects.filter(company__slug = company_slug, slug = brand_slug)

            if brands.exists():
                brands.delete()
                messages.success(request, "Success! Category Deleted!")
                return redirect(self.get_success_url())

            else:
                messages.error(request, "Failed! Invalid company or brand.")                
        
        except Exception as e:
            logger.exception(f"Error in DeleteBrandView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.get_redirect_url())


class BaseProductCategoryView(BaseProductCompanyView, View):
    model = ProductCategory
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:categories", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url() 


@method_decorator(csrf_exempt, name="post")
class AddProductCategoryView(BaseProductCategoryView, CreateView):
    model = ProductCategory
    fields = ["name"]    

    def post(self, request, *args, **kwargs):
        try:
            product_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                product, created = self.model.objects.get_or_create(company = product_company, name = name)

                if created:
                    messages.success(request, "Success! Product category created.")
                    return redirect(self.get_success_url())

                else:
                    messages.warning(request, "Category already exists.")
            
            else:
                messages.error(request, "Category name is required.")            
        
        except Exception as e:
            logger.exception(f"Error in creating product category: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())


class ListProductCategoryView(BaseProductCategoryView, ListView):
    model = ProductCategory
    queryset = model.objects.none()
    template_name = "product_company/category/list.html"    
    context_object_name = "categories"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of list category view of superadmin side: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:            
            context["product_categories_page"] = True        
        except Exception as e:
            logger.exception(f"Error in fetching context data of list category view of superadmin: {e}")
        return context


class UpdateProductCategoryView(BaseProductCategoryView, UpdateView):
    model = ProductCategory
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("superadmin:home")
    slug_url_kwarg = "category_slug"

    def get_redirect_url(self):
        try:
            return reverse_lazy("superadmin:update_category", kwargs = {"slug": self.kwargs.get("slug"), "category_slug": self.kwargs.get("category_slug")})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function of UpdateProductCategoryView in superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            name = clean_string(request.POST.get("name", ""))
            
            if not name:
                messages.error(request, "Category name is required.")
                return redirect(self.get_redirect_url())

            self.object = self.get_object()
            
            if not self.model.objects.filter(name = name, company = self.object.company).exclude(
                pk = self.object.pk
            ).exists():

                self.object.name = name
                self.object.save()

                messages.success(request, "Success! Product category updated.")
                return redirect(self.get_success_url())

            else:
                messages.warning(request, "Category already exists.")
            
        except Exception as e:
            logger.exception(f"Error in updating product category: {e}")
            messages.error(request, "An unexpected error occured.")

        return redirect(self.get_redirect_url())


class DeleteProductCategoryView(BaseProductCategoryView, View):
    def post(self, request, *args, **kwargs):
        try:
            company_slug = self.kwargs.get("slug")
            category_slug = self.kwargs.get("category_slug")

            categories = self.model.objects.filter(company__slug = company_slug, slug = category_slug)

            if categories.exists():
                categories.delete()
                messages.success(request, "Success! Category Deleted!")
                return redirect(self.get_success_url())

            else:
                messages.error(request, "Failed! Invalid company or category.")                
        
        except Exception as e:
            logger.exception(f"Error in DeleteProductCategoryView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.get_redirect_url())


class BaseProductSubCategory(BaseProductCompanyView, View):
    model = ProductSubCategory
    success_url = redirect_url = reverse_lazy("superadmin:sub_categories")

    def get_success_url(self):        
        return reverse_lazy("superadmin:sub_categories", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url() 


class ListProductSubCategoryView(BaseProductSubCategory, ListView):
    queryset = ProductSubCategory.objects.none()
    template_name = "product_company/sub_category/list.html"    
    context_object_name = "sub_categories"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug')).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of list product sub category view of superadmin side: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:            
            context["product_sub_categories_page"] = True
            current_company = self.get_current_company()
            context["categories"] = ProductCategory.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in fetching context data of list sub category view of superadmin: {e}")
        return context


class AddProductSubCategoryView(BaseProductSubCategory, CreateView):
    fields = ["name", "category"]

    def post(self, request, *args, **kwargs):
        try:
            product_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None

            category_slug = request.POST.get("category")

            if not category_slug or not name:
                error_msg = "Name of sub category is required."
                if not category_slug:
                    error_msg = "Category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.get_redirect_url())
            
            category = get_object_or_404(ProductCategory, slug = category_slug)
            
            sub_category, created = self.model.objects.get_or_create(company = product_company, name = name, category = category)

            if created:
                messages.success(request, "Success! Product sub category created.")
                return redirect(self.get_success_url())

            else:
                messages.warning(request, "Sub Category already exists.")

        except Http404:
            messages.error(request, "Invalid category")                                    
        
        except Exception as e:
            logger.exception(f"Error in creating product sub category by superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())


class UpdateProductSubCategoryView(BaseProductSubCategory, UpdateView):
    fields = ["name", "category"]    
    slug_url_kwarg = "sub_category_slug"
    template_name = "product_company/sub_category/edit.html"
    context_object_name = "sub_category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_company = self.get_current_company()

        context["categories"] = ProductCategory.objects.filter(company = current_company).order_by("name")

        return context

    def handle_faqs(self, request, company, sub_category_slug):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]               

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                ProductSubCategoryFaq.objects.filter(company = company, sub_category_slug = sub_category_slug).delete()
                
                if question_list and answer_list:
                    creating_faqs = [ProductSubCategoryFaq(
                        company = company, sub_category_slug = sub_category_slug,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    ProductSubCategoryFaq.objects.bulk_create(creating_faqs)

                    product_faqs = ProductSubCategoryFaq.objects.filter(company = company, sub_category_slug = sub_category_slug)                
                                            
                    return product_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of UpdateProductSubCategoryView: {e}")

        return []

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            object_slug = self.object.slug or ""
        
            name = clean_string(request.POST.get("name", ""))
            category_slug = clean_string(request.POST.get("category", ""))
            description = clean_string(request.POST.get("description", ""))
            starting_title = clean_string(request.POST.get("starting_title", ""))
            slug = clean_string(request.POST.get("slug", object_slug))
            ending_title = clean_string(request.POST.get("ending_title", ""))
            content = request.POST.get("content")            
            hide_faqs = request.POST.get("hide_faqs")

            required_fields = {
                "Name": name,                
                "Product Category": category_slug
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required")
                    return redirect(self.get_redirect_url())

            slug_list = [starting_title, slug, ending_title]

            full_slug = slugify("-".join(filter(None, slug_list)))
            
            with transaction.atomic():
                category = get_object_or_404(ProductCategory, slug = category_slug)               

                if self.model.objects.filter(
                    company = self.object.company, name = name, category = category
                    ).exclude(pk = self.object.pk).exists():
                    
                    messages.error(request, "Failed! Similar sub category already exists.")
                    return redirect(self.get_redirect_url())
                
                slug = slugify(slug)

                if slug != self.object.slug:
                    
                    if self.model.objects.filter(slug = slug).exclude(pk = self.object.pk).exists():
                        messages.error(request, "Failed! Similar slug already exists for another product sub category.")
                        return redirect(self.get_redirect_url())
                    
                    self.object.slug = slug

                if full_slug != self.object.location_slug:                    
                    if self.model.objects.filter(location_slug = full_slug).exclude(pk = self.object.pk).exists():
                        messages.error(request, "Failed! Similar location slug already exists for another product sub category.")
                        return redirect(self.get_redirect_url())

                    self.object.location_slug = full_slug

                self.object.name = name
                self.object.category = category
                self.object.description = description
                self.object.starting_title = starting_title
                self.object.ending_title = ending_title
                self.object.hide_faqs = True if hide_faqs else False        
                self.object.content = content

                self.object.save()

                sub_category_faq_objs = self.handle_faqs(request, self.object.company, self.object.slug)
                self.object.faqs.set(sub_category_faq_objs)

                messages.success(request, "Success! Product sub category updated.")
                return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid category")                                    
        
        except Exception as e:
            logger.exception(f"Error in UpdateProductSubCategoryView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.get_redirect_url())


class DeleteProductSubCategoryView(BaseProductSubCategory, View):
    def post(self, request, *args, **kwargs):
        try:
            company_slug = self.kwargs.get("slug")
            sub_category_slug = self.kwargs.get("sub_category_slug")

            sub_categories = self.model.objects.filter(company__slug = company_slug, slug = sub_category_slug)

            if sub_categories.exists():
                sub_categories.delete()
                messages.success(request, "Success! Sub Category Deleted!")
                return redirect(self.get_success_url())

            else:
                messages.error(request, "Failed! Invalid company or sub category.")                
        
        except Exception as e:
            logger.exception(f"Error in DeleteProductSubCategoryView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.get_redirect_url())
    

class ListProductColorView(BaseProductSubCategory, ListView):
    model = Color
    queryset = model.objects.none()
    template_name = "product_company/colors/list.html"    
    context_object_name = "colors"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug')).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of list product colors view of superadmin side: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:            
            context["product_color_page"] = True
        except Exception as e:
            logger.exception(f"Error in fetching context data of list colors view of superadmin: {e}")
        return context

    

class BaseProductColorView(BaseProductCompanyView, View):
    model = Color
    success_url = redirect_url = reverse_lazy("superadmin:home")
    
    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:colors", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of BaseProductColorView of superadmin: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url() 
        

class AddProductColorView(BaseProductColorView, CreateView):
    fields = ["name", "hexa"]    

    def post(self, request, *args, **kwargs):
        try:
            product_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            
            name = request.POST.get("name")
            name = name.strip() if name else None

            hexa = request.POST.get("hexa")
            hexa = hexa.strip() if hexa else None

            if not name or not hexa:
                if not name:
                    error_msg = "Failed! Name is required."

                if not hexa:
                    error_msg = "Failed! Hexa is required."

                messages.error(request, error_msg)    
                return redirect(self.get_redirect_url())
            
            color, created = self.model.objects.get_or_create(company = product_company, name = name, hexa = hexa)

            if created:
                messages.success(request, "Success! Product color created.")
                return redirect(self.get_success_url())

            else:
                messages.warning(request, "Color already exists.")                                   
        
        except Exception as e:
            logger.exception(f"Error in creating product color by superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())


class UpdateProductColorView(BaseProductColorView, UpdateView):
    fields = ["name", "hexa"]
    slug_url_kwarg = "color_slug"          

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            
            name = request.POST.get("name")
            name = name.strip() if name else None

            hexa = request.POST.get("hexa")
            hexa = hexa.strip() if hexa else None

            if not name or not hexa:
                if not name:
                    error_msg = "Failed! Name is required."

                if not hexa:
                    error_msg = "Failed! Hexa is required."

                messages.error(request, error_msg)    
                return redirect(self.get_redirect_url())
            
            self.object.name = name
            self.object.hexa = hexa
            self.object.save()
            
            messages.success(request, "Success! Product color updated.")
            return redirect(self.get_success_url())                                            
        
        except Exception as e:
            logger.exception(f"Error in updating product color by superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())


class DeleteProductColorView(BaseProductColorView, View):
    def post(self, request, *args, **kwargs):
        try:
            company_slug = self.kwargs.get("slug")
            color_slug = self.kwargs.get("color_slug")

            colors = Color.objects.filter(company__slug = company_slug, slug = color_slug)

            if colors.exists():
                colors.delete()
                messages.success(request, "Success! Color Deleted!")
                return redirect(self.get_success_url())

            else:
                messages.error(request, "Failed! Invalid company or color.")                
        
        except Exception as e:
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.get_redirect_url())


class BaseSizeView(BaseProductCompanyView, View):
    model = Size
    success_url = redirect_url = reverse_lazy("superadmin:home")
    
    def get_success_url(self):
        try:
            print(self.kwargs.get("slug"))
            return reverse_lazy("superadmin:sizes", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of BaseSizeView of superadmin: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url() 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_size_page"] = True
        return context


class AddSizeView(BaseSizeView, CreateView):
    fields = ["name", "category", "standard"]
    

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

            company = self.get_current_company()

            category = get_object_or_404(ProductCategory, slug = category_slug, company = company)
            
            for name in names:
                name = name.strip()

                if name:
                    size, created = self.model.objects.get_or_create(company = company, name = name.upper(), category = category, standard = standard)

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
                return redirect(self.get_success_url())
            
            else:
                messages.warning(request, "Given size/sizes already exists in the database.")

        except Http404:
            error_msg = "Failed! Invalid category"
        
        except Exception as e:
            logger.exception(f"Error in creating product size: {e}")

        messages.error(request, error_msg)
        return redirect(self.get_redirect_url())
    

class UpdateSizeView(BaseSizeView, UpdateView):
    fields = ["name", "category", "standard", "slug"]
    slug_url_kwarg = "size_slug"

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

            if not self.model.objects.filter(name = name, category = category, standard = standard).exclude(pk = self.object.pk).exists():
                self.object.name = name
                self.object.category = category
                self.slug = None
                self.object.standard = standard if standard else None
                self.object.save()

                messages.success(request, "Success! Size Updated.")
                return redirect(self.get_success_url())

            else:
                messages.warning(request, "Failed! Size already exists.")        

        except Http404:
            error_msg = "Failed! Invalid category"
        
        except Exception as e:
            logger.exception(f"Error in updating product size: {e}")

        messages.error(request, error_msg)
        return redirect(self.get_redirect_url())
    

class ListSizeView(BaseSizeView, ListView):
    queryset = Size.objects.none()
    template_name = "product_company/sizes/list.html"    
    context_object_name = "sizes"

    def get_queryset(self):
        company_slug = self.kwargs.get("slug")
        if company_slug:
            return Size.objects.filter(company__slug = company_slug).order_by("-updated")

        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        company_slug = self.kwargs.get("slug")
        if company_slug:            
            context["categories"] = ProductCategory.objects.filter(company__slug = company_slug).order_by("-updated")

        return context

class DeleteSizeView(BaseSizeView, View):
    def post(self, request, *args, **kwargs):
        try:
            company_slug = self.kwargs.get("slug")
            size_slug = self.kwargs.get("size_slug")

            sizes = Size.objects.filter(company__slug = company_slug, slug = size_slug)

            if sizes.exists():
                sizes.delete()
                messages.success(request, "Success! Size Deleted!")
                return redirect(self.get_success_url())

            else:
                messages.error(request, "Failed! Invalid company or size.")                
        
        except Exception as e:
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.get_redirect_url())
    

# Product FAQ
class ProductFaqBaseView(BaseProductCompanyView):
    model = ProductFaq
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:product_faqs', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseProductFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()
        
    def get_product(self, product_slug):
        try:            
            return get_object_or_404(Product, slug = product_slug)
        except Http404:
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context["company_page"] = True
        context["product_faq_page"] = True

        return context


class AddProductFaqView(ProductFaqBaseView, CreateView):    
    fields = ["company", "product", "question", "answer", "dynamic_place_rendering"]
    template_name = "product_company/faqs/add.html"    

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_product_faq', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddProductFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()        
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["add_product_faq_page"] = True
        context["categories"] = ProductCategory.objects.filter(company__slug = company_slug).order_by("-updated")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            product_slug = self.request.POST.get('product')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            product_slug = product_slug.strip() if product_slug else None
            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Product": product_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            company = self.get_current_company()
            product = self.get_product(product_slug)

            if not company or not product:
                invalid_msg = ""
                
                if not company:
                    invalid_msg = "Invalid Product Company"
                else:
                    invalid_msg = "Invalid Product"

                messages.error(request, invalid_msg)
                return redirect(self.get_redirect_url())
            
            dynamic_place_rendering = True if dynamic_place_rendering else False

            ProductFaq.objects.update_or_create(
                company = company, product = product, question = question, dynamic_place_rendering = dynamic_place_rendering, 
                defaults={"answer": answer}
                )

            messages.success(request, "Success! Added FAQ")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in get function of AddProductFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class ListProductFaqView(ProductFaqBaseView, ListView):
    model = ProductFaq
    template_name = "product_company/faqs/list.html"
    queryset = model.objects.none()
    context_object_name = "faqs"

    def get_queryset(self):
        try:
            company_slug = self.kwargs.get(self.slug_url_kwarg)
            company = get_object_or_404(Company, slug = company_slug, type__name = "Product")
            return self.model.objects.filter(company = company)
            
        except Http404:
            messages.error(self.request, "Invalid product company")
            return redirect(self.redirect_url)


class UpdateProductFaqView(ProductFaqBaseView, UpdateView):
    model = ProductFaq
    fields = ["product", "question", "answer", "dynamic_place_rendering"]
    template_name = "product_company/faqs/update.html"
    context_object_name = "faq"

    def get_product(self, product_slug):
        try:
            return get_object_or_404(Product, slug = product_slug)
        except Http404:
            return None
        
    def get_object(self):
        company_slug = self.kwargs.get('slug') 
        product_faq_slug = self.kwargs.get('product_faq_slug') 

        self.object = get_object_or_404(ProductFaq, company__slug = company_slug, slug = product_faq_slug)

        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["update_product_faq_page"] = True

        context["categories"] = ProductCategory.objects.filter(company__slug = company_slug).order_by("-updated")
        context["sub_categories"] = ProductSubCategory.objects.filter(company__slug = company_slug, category = self.object.product.category).order_by("-updated")
        context["products"] = Product.objects.filter(company__slug = company_slug, category = self.object.product.category, sub_category = self.object.product.sub_category).order_by("-updated")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            product_slug = self.request.POST.get('product')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Product": product_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            product = self.get_product(product_slug)

            if not product:
                messages.error(request, "Invalid Product")
                return redirect(self.get_redirect_url())
            
            dynamic_place_rendering = True if dynamic_place_rendering else False

            similar_faq = self.model.objects.filter(
                company = self.object.company, product = product, question = question, answer = answer, dynamic_place_rendering = dynamic_place_rendering
                ).first()

            if similar_faq:
                if similar_faq.slug == self.object.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar product FAQ already exists")
                return redirect(self.get_redirect_url())

            self.object.product = product
            self.object.question = question
            self.object.answer = answer
            self.object.dynamic_place_rendering = dynamic_place_rendering
            self.object.save()

            messages.success(request, f"Success! Updated FAQ")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid product FAQ object")

        except Exception as e:
            logger.exception(f"Error in get function of UpdateProductFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteProductFaqView(ProductFaqBaseView, View):
    model = ProductFaq
        
    def get_object(self):
        faq_slug = self.kwargs.get('product_faq_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = faq_slug, company__slug = company_slug)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            product_name = str(self.object.product.name)[:25]
            if len(str(self.object.product.name)) > 25:
                product_name += "..."
            self.object.delete()

            messages.success(request, f"Success! Removed product FAQ object of: {product_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Product FAQ")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteProductFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


# Product Review
class BaseProductReviewView(BaseProductCompanyView):
    model = ProductReview
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_review_page"] = context["company_page"] = True
        context["current_company"] = self.get_current_company()
        context["company_type_page"] = False
        return context
    
    def get_success_url(self):
        try:
            if self.slug_url_kwarg:
                return reverse_lazy("superadmin:product_reviews", kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of BaseProductReviewView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_object(self):
        company_slug = self.kwargs.get(self.slug_url_kwarg)
        product_review_slug = self.kwargs.get('product_review_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = product_review_slug)
    
    def get_product(self, product_slug):
        try:
            company = self.get_current_company()
            return get_object_or_404(Product, company = company, slug = product_slug)
        except Http404:
            return None
    

class AddProductReviewView(BaseProductReviewView, CreateView):    
    template_name = "product_company/reviews/add.html"
    fields = ["company", "product", "user", "review_by", "text", "rating", "order"]

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_product_reviews", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of AddProductReviewView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["add_product_review_page"] = True
        context["ratings"] = list(range(1,6))

        context["categories"] = ProductCategory.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg)).order_by("-updated")
        
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

            product_slug = request.POST.get("product")
            review_by = request.POST.get("reviewed_by")
            text = request.POST.get("testimonial")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            product_slug = product_slug.strip() if product_slug else None
            review_by = review_by.strip() if review_by else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Product": product_slug,
                "Review By": review_by,
                "Review Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                

            product = self.get_product(product_slug)

            if not product:
                messages.error(request, "Invalid Product")
                return redirect(self.get_redirect_url())                          
                                   
            
            self.model.objects.create(
                company = company, user = request.user, product = product, review_by = review_by,
                text = text, rating = rating, order = order
            )

            messages.success(request, "Success! Review Added")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddProductReviewView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.get_redirect_url())


class ProductReviewListView(BaseProductReviewView, ListView):
    template_name = "product_company/reviews/list.html"
    context_object_name = "reviews"
    queryset = ProductReview.objects.none()
    
    def get_queryset(self):
        company_slug = self.kwargs.get('slug')
        if company_slug:
            return self.model.objects.filter(company__slug = company_slug).order_by("order")
        
        return self.queryset
    

class UpdateProductReviewView(BaseProductReviewView, UpdateView):    
    fields = ["review_by", "product", "text", "rating", "order"]
    template_name = "product_company/reviews/update.html"
    slug_url_kwarg = 'slug'
        
    def get_redirect_url(self):
        try:
            return reverse_lazy("superadmin:update_product_review", kwargs = {"slug": self.kwargs.get('slug'), "product_review_slug": self.kwargs.get('product_review_slug')})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of AddProductReviewView of superadmin app: {e}")
        
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["update_review_page"] = True
        context["ratings"] = list(range(1,6))

        context["categories"] = ProductCategory.objects.filter(company = self.get_current_company()).order_by("-updated")
        context["sub_categories"] = ProductSubCategory.objects.filter(
            company = self.get_current_company(), category = self.object.product.category
            ).order_by("-updated")
        context["products"] = Product.objects.filter(
            company = self.get_current_company(), category = self.object.product.category, sub_category = self.object.product.sub_category
            ).order_by("-updated")
        
        return context    

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            review_by = request.POST.get("review_by")
            product_slug = request.POST.get("product")
            text = request.POST.get("text")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            review_by = review_by.strip() if review_by else None
            product_slug = product_slug.strip() if product_slug else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Reviewer Name": review_by,
                "Product": product_slug,
                "Review Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():                
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            product = self.get_product(product_slug)

            if not product:
                messages.error(request, "Invalid Product")
                return redirect(self.get_redirect_url())                
            
            similar_client = self.model.objects.filter(
                company = self.object.company, review_by = review_by, product = product
                ).first()

            if similar_client:
                dublicate_error_msg = ""

                if similar_client.slug == self.object.slug:
                    if not (order or text or rating):
                        dublicate_error_msg = "No changes detected"
                else:
                    dublicate_error_msg = "Similar review already exists"

                if dublicate_error_msg:
                    messages.warning(request, dublicate_error_msg)
                    return redirect(self.get_redirect_url())
            
            self.object.review_by = review_by
            self.object.product = product
            self.object.text = text
            self.object.rating = rating
            self.object.order = order            

            self.object.save()

            messages.success(request, "Success! Review Updated")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid Review")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateProductReviewView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class DeleteProductReviewView(BaseProductReviewView, DeleteView):
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Review Deleted")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Review")

        except Exception as e:
            logger.exception(f"Error in delete function of DeleteProductReviewView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class BaseProductEnquiryView(BaseProductCompanyView, View):
    model = ProductEnquiry
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = self.get_current_company()
            context["product_enquiry_page"] = True

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseProductEnquiryView: {e}")

        return context


class ListProductEnquiryView(BaseProductEnquiryView, ListView):
    queryset = ProductEnquiry.objects.none()
    context_object_name = "enquiries"
    template_name = "product_company/enquiries/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListProductEnquiryView of superadmin: {e}")
            return self.queryset


class DeleteProductEnquiryView(BaseProductEnquiryView, View):
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:product_enquiries', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of DeleteProductEnquiryView of superadmin app: {e}")
            return self.success_url

    def get_redirect_url(self):
        return self.get_success_url()
            

    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(ProductEnquiry, company__slug = self.kwargs.get(self.slug_url_kwarg), slug = self.kwargs.get('enquiry_slug'))
            self.object.delete()

            messages.success(request, "Success! Delete Product Enquiry")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Product Enquiry")
            return redirect(self.get_redirect_url())


class BaseProductDetailPageView(BaseProductCompanyView):
    model = ProductDetailPage
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["product_detail_page"] = True
            
            current_company = self.get_current_company()

            context["current_company"] = current_company

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseProductDetailPageView of superadmin: {e}")
        
        return context
        
    def get_product(self, product_slug):
        try:
            return get_object_or_404(Product, slug = product_slug)
        except Http404:
            messages.error(self.request, "Invalid Product")
            return redirect(self.get_redirect_url())
        
    def get_current_product(self):
        try:
            product_slug = self.kwargs.get('product_slug')

            product =  get_object_or_404(Product, slug = product_slug)
            return product
        except Http404:
            messages.error(self.request, "Failed! Invalid Product")
            return redirect(self.redirect_url)

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:product_detail_pages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseProductDetailPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseProductDetailPageView of superadmin: {e}")
            return self.redirect_url

    def get_object(self):
        try:
            current_company = self.get_current_company()
            product_detail_slug = self.kwargs.get("product_detail_slug")
            # current_product = self.get_current_product()

            return get_object_or_404(self.model, company = current_company, slug = product_detail_slug)
        
        except Http404:
            messages.error(self.request, "Invalid product for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of BaseProductDetailPageView of superadmin: {e}")

        return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, product):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    ProductFeature.objects.filter(company = company, product = product).delete()

                    features = [ProductFeature(company=company, product=product, feature=feature) for feature in features_list]
                    ProductFeature.objects.bulk_create(features)

                    feature_objs = ProductFeature.objects.filter(company = company, product = product)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseProductDetailPageView: {e}")
        
        return []

    # def handle_vertical_tabs(self, request, company, product):
    #     try:
    #         vertical_tab_objects = []

    #         vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
    #         vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
    #         vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
    #         vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
    #         vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

    #         if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
    #             raise ValueError("Mismatch in the number of vertical fields.")            
            
    #         initial = 0


    #         with transaction.atomic():
    #             ProductVerticalTab.objects.filter(company = company, product = product).delete()
    #             ProductVerticalBullet.objects.filter(company = company, product = product).delete()

    #             for i in range(len(vertical_bullet_count_list)):
    #                 heading = vertical_heading_list[i]
    #                 sub_heading = vertical_sub_heading_list[i]

    #                 if heading:
    #                     vertical_tab_obj = ProductVerticalTab.objects.create(
    #                         company = company,
    #                         product = product,
    #                         heading = heading,
    #                         sub_heading = sub_heading,
    #                         summary = vertical_summary_list[i]
    #                     )

    #                     final = initial + vertical_bullet_count_list[i]
    #                     vertical_bullets = vertical_bullet_list[initial:final]
    #                     initial = final

    #                     if vertical_bullet_count_list[i] != 0:

    #                         creating_vertical_bullets = [ProductVerticalBullet(
    #                             company = company, product = product, heading = heading,
    #                             sub_heading = sub_heading, bullet = bullet
    #                         ) for bullet in vertical_bullets if bullet]

    #                         if creating_vertical_bullets:
    #                             ProductVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

    #                         created_vertical_bullets = ProductVerticalBullet.objects.filter(company = company, product = product, heading = heading, sub_heading = sub_heading)

    #                         vertical_tab_obj.bullets.set(created_vertical_bullets)

    #                     vertical_tab_objects.append(vertical_tab_obj)

    #         return vertical_tab_objects

    #     except (IntegrityError, IndexError, ValueError) as e:
    #         logger.exception(f"Error in handle_vertical_tabs function of BaseProductDetailPageView: {e}")

    #     return []
    
    # def handle_horizontal_tabs(self, request, company, product):
    #     try:
    #         horizontal_tab_objects = []

    #         horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
    #         horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
    #         horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
    #         horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

    #         if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
    #             raise ValueError("Mismatch in the number of horizontal fields.")                        
            
    #         initial = 0


    #         with transaction.atomic():
    #             ProductHorizontalTab.objects.filter(company = company, product = product).delete()
    #             ProductHorizontalBullet.objects.filter(company = company, product = product).delete()

    #             for i in range(len(horizontal_bullet_count_list)):
    #                 heading = horizontal_heading_list[i]

    #                 if heading:
    #                     horizontal_tab_obj = ProductHorizontalTab.objects.create(
    #                         company = company,
    #                         product = product,
    #                         heading = heading,
    #                         summary = horizontal_summary_list[i]
    #                     )

    #                     final = initial + horizontal_bullet_count_list[i]
    #                     horizontal_bullets = horizontal_bullet_list[initial:final]
    #                     initial = final
                        
    #                     if horizontal_bullet_count_list[i] != 0:
                        
    #                         creating_horizontal_bullets = [ProductHorizontalBullet(
    #                             company = company, product = product, heading = heading,
    #                             bullet = bullet
    #                         ) for bullet in horizontal_bullets if bullet]

    #                         if creating_horizontal_bullets:
    #                             ProductHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

    #                         created_horizontal_bullets = ProductHorizontalBullet.objects.filter(company = company, product = product, heading = heading)

    #                         horizontal_tab_obj.bullets.set(created_horizontal_bullets)

    #                     horizontal_tab_objects.append(horizontal_tab_obj)

    #         return horizontal_tab_objects

    #     except (IntegrityError, IndexError, ValueError) as e:
    #         logger.exception(f"Error in handle_horizontal_tabs function of BaseProductDetailPageView: {e}")

    #     return []
    
    # def handle_tables(self, request, company, product):
    #     try:
    #         product_tables = []

    #         heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
    #         data_list = [data.strip() for data in request.POST.getlist("table_data")]

    #         heading_length = len(heading_list)
    #         data_length = len(data_list)


    #         with transaction.atomic():
    #             ProductTableData.objects.filter(company = company, product = product).delete()
    #             ProductTable.objects.filter(company = company, product = product).delete()

    #             for index, heading in enumerate(heading_list):
    #                 product_table = ProductTable.objects.create(
    #                     company = company, product = product, heading = heading
    #                 )

    #                 data_positions  = list(range(index, data_length, heading_length))
    #                 data_list_of_heading = [data_list[i] for i in data_positions ]

    #                 table_data_objs  = [ProductTableData(
    #                         company = company, product = product,
    #                         heading = heading, data = data
    #                         ) for data in data_list_of_heading]

    #                 ProductTableData.objects.bulk_create(table_data_objs )

    #                 product_table_data_objs = ProductTableData.objects.filter(company = company, product = product, heading = heading)

    #                 product_table.datas.set(product_table_data_objs)

    #                 product_tables.append(product_table)

    #         return product_tables
        
    #     except Exception as e:
    #         logger.exception(f"Error in handle_tables function of BaseProductDetailPageView: {e}")

    #     return []
    
    def handle_bullet_points(self, request, company, product):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                ProductBulletPoint.objects.filter(company = company, product = product).delete()

                if bullet_point_list:
                    bullet_point_objects = [ProductBulletPoint(
                        company = company, product = product,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    ProductBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = ProductBulletPoint.objects.filter(company = company, product = product)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseProductDetailPageView: {e}")

        return []

    def handle_timelines(self, request, company, product):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                ProductTimeline.objects.filter(company = company, product = product).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [ProductTimeline(
                        company = company, product = product,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    ProductTimeline.objects.bulk_create(creating_timelines)

                    product_timelines = ProductTimeline.objects.filter(company = company, product = product)                
                                            
                    return product_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseProductDetailPageView: {e}")

        return []


class AddProductDetailPageView(BaseProductDetailPageView, CreateView):
    form_class = ProductDetailDescriptionForm
    template_name = "product_company/detail_page/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_product_detail_page"] = True

        current_company = self.get_current_company()        
        context["categories"] = ProductCategory.objects.filter(company = current_company).order_by("-updated")

        context["tags"] = MetaTag.objects.all().order_by("-updated")
        
        return context

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_product_detail_page', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseProductDetailPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseProductDetailPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            product_slug = request.POST.get('product')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            buy_now_action = request.POST.get("buy_now_action")
            whatsapp = request.POST.get("whatsapp")
            external_link = request.POST.get("external_link")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            # bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")
            
            hide_features = request.POST.get("hide_features")
            # hide_vertical_tab = request.POST.get("hide_vertical_tab")
            # hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            # hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")

            hide_support_languages = request.POST.get("hide_support_languages")

            summary = summary.strip() if summary else None
            
            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None
            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            buy_now_action = buy_now_action.strip() if buy_now_action else None
            whatsapp = whatsapp.strip() if whatsapp else None
            external_link = external_link.strip() if external_link else None

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            # bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Product": product_slug,
                "summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            buy_now_missing_field = ""
            if buy_now_action == "whatsapp" and not whatsapp:
                buy_now_missing_field = "Whatsapp Number"
            
            if buy_now_action == "external_link" and not external_link:
                buy_now_missing_field = "External Link"

            if buy_now_missing_field:
                messages.error(request, f"Failed! {buy_now_missing_field} is not provided")
                return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                # "hide_vertical_tab": hide_vertical_tab,
                # "hide_horizontal_tab": hide_horizontal_tab,
                # "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                }

            product = self.get_product(product_slug)

            updating_meta_tags = []
            with transaction.atomic():
                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                product_detail = self.model.objects.create(
                    company = company, product = product, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    buy_now_action = buy_now_action, whatsapp = whatsapp, external_link = external_link,                    
                 timeline_title = timeline_title, 
                    hide_support_languages = True if hide_support_languages else False
                )                

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(product_detail, key, True)

                product_detail.save()

                relationship_handlers = {
                    "features": self.handle_features,                    
                    "bullet_points": self.handle_bullet_points,                    
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, product)
                    getattr(product_detail, field).set(objects)

                if meta_tags:
                    meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                    product_detail.meta_tags.set(meta_tag_objects)  

                messages.success(request, "Success! Created product detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddProductDetailPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ProductDetailPageListView(BaseProductDetailPageView, ListView):
    template_name = "product_company/detail_page/list.html"
    queryset = ProductDetailPage.objects.none()
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "detail_pages"        
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting queryset of ProductDetailsListView of superadmin: {e}")
            return self.queryset


class ProductDetailPageView(BaseProductDetailPageView, DetailView):
    model = ProductDetailPage
    template_name = "product_company/detail_page/detail.html"
    redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "detail_page"

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:product_detail_pages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function of ProductDetailPageView: {e}")
            return self.redirect_url


class UpdateProductDetailPageView(BaseProductDetailPageView, UpdateView):    
    form_class = ProductDetailDescriptionForm
    template_name = "product_company/detail_page/update.html"
    context_object_name = "detail_page"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object()
        current_company = self.get_current_company()        
        context["categories"] = ProductCategory.objects.filter(company = current_company).order_by("-updated")
        context["sub_categories"] = ProductSubCategory.objects.filter(company = current_company, category = self.object.product.category).order_by("-updated")
        context["products"] = Product.objects.filter(company = current_company, category = self.object.product.category, sub_category = self.object.product.sub_category).order_by("-updated")

        context["tags"] = MetaTag.objects.all().order_by("-updated")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_product_detail_page', kwargs = {"slug": self.kwargs.get('slug'), "product_detail_slug": self.kwargs.get('product_detail_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateProductDetailPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateProductDetailPageView of superadmin: {e}")
            return self.redirect_url


    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            product_slug = request.POST.get('product')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            buy_now_action = request.POST.get("buy_now_action")
            whatsapp = request.POST.get("whatsapp")
            external_link = request.POST.get("external_link")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            # bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")   

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            buy_now_action = buy_now_action.strip() if buy_now_action else None
            whatsapp = whatsapp.strip() if whatsapp else None
            external_link = external_link.strip() if external_link else None

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            # bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            hide_features = request.POST.get("hide_features")
            # hide_vertical_tab = request.POST.get("hide_vertical_tab")
            # hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            # hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")

            hide_support_languages = request.POST.get("hide_support_languages")

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Product": product_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            buy_now_missing_field = ""
            if buy_now_action == "whatsapp" and not whatsapp:
                buy_now_missing_field = "Whatsapp Number"
            
            if buy_now_action == "external_link" and not external_link:
                buy_now_missing_field = "External Link"

            if buy_now_missing_field:
                messages.error(request, f"Failed! {buy_now_missing_field} is not provided")
                return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                # "hide_vertical_tab": hide_vertical_tab,
                # "hide_horizontal_tab": hide_horizontal_tab,
                # "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                }

            product = self.get_product(product_slug)

            updating_meta_tags = []
            with transaction.atomic():

                product_detail = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                product_detail.product = product
                product_detail.summary = summary

                product_detail.description = description

                product_detail.meta_title = meta_title
                product_detail.meta_description = meta_description

                product_detail.buy_now_action = buy_now_action

                if buy_now_action == "whatsapp":
                    product_detail.whatsapp = whatsapp 

                if buy_now_action == "external_link":
                    product_detail.external_link = external_link 

                # product_detail.vertical_title = vertical_title
                # product_detail.horizontal_title = horizontal_title
                # product_detail.table_title = table_title
                # product_detail.bullet_title = bullet_title                
                product_detail.timeline_title = timeline_title 

                product_detail.hide_support_languages = True if hide_support_languages else False                

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:                    
                        assigning_value = True

                    setattr(product_detail, key, assigning_value)
                
                product_detail.save()      

                meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                product_detail.meta_tags.set(meta_tag_objects)                       

                relationship_handlers = {
                    "features": self.handle_features,                    
                    "bullet_points": self.handle_bullet_points,                    
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, product)
                    getattr(product_detail, field).set(objects)

                product_detail.save()

                messages.success(request, "Success! Updated product detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateProductDetailPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())

class DeleteProductDetailPageView(BaseProductDetailPageView, View):
    def get_object(self, **kwargs):
        company_slug = self.kwargs.get('slug')
        detail_page_slug = self.kwargs.get('detail_page_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = detail_page_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            product_name = self.object.product.name
            self.object.delete()

            messages.success(request, f"Success! Removed product detail page of: {product_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Product Detail")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteProductDetailPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseProductMultiPageView(BaseProductCompanyView, View):
    model = ProductMultiPage
    success_url = redirect_url = reverse_lazy('superadmin:home')        
        
    def get_categories(self):
        return ProductCategory.objects.filter(company = self.current_company).order_by("-updated")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["product_multipage"] = True
            
            self.current_company = self.get_current_company()
            
            context["current_company"] = self.current_company            
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseProductMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:product_multipages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseProductMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseProductMultiPageView of superadmin: {e}")
            return self.redirect_url
        
    def get_product(self, product_slug):
        try:
            return get_object_or_404(Product, slug = product_slug)
        except Http404:
            messages.error(self.request, "Invalid Product")
            return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, title):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    ProductMultiPageFeature.objects.filter(company = company, title = title).delete()

                    features = [ProductMultiPageFeature(company=company, title=title, feature=feature) for feature in features_list]
                    ProductMultiPageFeature.objects.bulk_create(features)

                    feature_objs = ProductMultiPageFeature.objects.filter(company = company, title = title)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseProductMultiPageView: {e}")
        
        return []

    # def handle_vertical_tabs(self, request, company, title):
    #     try:
    #         vertical_tab_objects = []

    #         vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
    #         vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
    #         vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
    #         vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
    #         vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

    #         if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
    #             raise ValueError("Mismatch in the number of vertical fields.")            
            
    #         initial = 0


    #         with transaction.atomic():
    #             ProductMultiPageVerticalTab.objects.filter(company = company, title = title).delete()
    #             ProductMultiPageVerticalBullet.objects.filter(company = company, title = title).delete()

    #             for i in range(len(vertical_bullet_count_list)):
    #                 heading = vertical_heading_list[i]
    #                 sub_heading = vertical_sub_heading_list[i]

    #                 if heading:
    #                     vertical_tab_obj = ProductMultiPageVerticalTab.objects.create(
    #                         company = company,
    #                         title = title,
    #                         heading = heading,
    #                         sub_heading = sub_heading,
    #                         summary = vertical_summary_list[i]
    #                     )

    #                     final = initial + vertical_bullet_count_list[i]
    #                     vertical_bullets = vertical_bullet_list[initial:final]
    #                     initial = final

    #                     if vertical_bullet_count_list[i] != 0:

    #                         creating_vertical_bullets = [ProductMultiPageVerticalBullet(
    #                             company = company, title = title, heading = heading,
    #                             sub_heading = sub_heading, bullet = bullet
    #                         ) for bullet in vertical_bullets if bullet]

    #                         if creating_vertical_bullets:
    #                             ProductMultiPageVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

    #                         created_vertical_bullets = ProductMultiPageVerticalBullet.objects.filter(company = company, title = title, heading = heading, sub_heading = sub_heading)

    #                         vertical_tab_obj.bullets.set(created_vertical_bullets)


    #                     vertical_tab_objects.append(vertical_tab_obj)

    #         return vertical_tab_objects

    #     except (IntegrityError, IndexError, ValueError) as e:
    #         logger.exception(f"Error in handle_vertical_tabs function of BaseProductMultiPageView: {e}")

    #     return []
    
    # def handle_horizontal_tabs(self, request, company, title):
    #     try:
    #         horizontal_tab_objects = []

    #         horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
    #         horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
    #         horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
    #         horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

    #         if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
    #             raise ValueError("Mismatch in the number of horizontal fields.")                        
            
    #         initial = 0


    #         with transaction.atomic():
    #             ProductMultiPageHorizontalTab.objects.filter(company = company, title = title).delete()
    #             ProductMultiPageHorizontalBullet.objects.filter(company = company, title = title).delete()

    #             for i in range(len(horizontal_bullet_count_list)):
    #                 heading = horizontal_heading_list[i]

    #                 if heading:
    #                     horizontal_tab_obj = ProductMultiPageHorizontalTab.objects.create(
    #                         company = company,
    #                         title = title,
    #                         heading = heading,
    #                         summary = horizontal_summary_list[i]
    #                     )

    #                     final = initial + horizontal_bullet_count_list[i]
    #                     horizontal_bullets = horizontal_bullet_list[initial:final]
    #                     initial = final
                        
    #                     if horizontal_bullet_count_list[i] != 0:
                        
    #                         creating_horizontal_bullets = [ProductMultiPageHorizontalBullet(
    #                             company = company, title = title, heading = heading,
    #                             bullet = bullet
    #                         ) for bullet in horizontal_bullets if bullet]

    #                         if creating_horizontal_bullets:
    #                             ProductMultiPageHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

    #                         created_horizontal_bullets = ProductMultiPageHorizontalBullet.objects.filter(company = company, title = title, heading = heading)

    #                         horizontal_tab_obj.bullets.set(created_horizontal_bullets)

    #                     horizontal_tab_objects.append(horizontal_tab_obj)

    #         return horizontal_tab_objects

    #     except (IntegrityError, IndexError, ValueError) as e:
    #         logger.exception(f"Error in handle_horizontal_tabs function of BaseProductMultiPageView: {e}")

    #     return []
    
    # def handle_tables(self, request, company, title):
    #     try:
    #         product_tables = []

    #         heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
    #         data_list = [data.strip() for data in request.POST.getlist("table_data")]

    #         heading_length = len(heading_list)
    #         data_length = len(data_list)


    #         with transaction.atomic():
    #             ProductMultiPageTableData.objects.filter(company = company, title = title).delete()
    #             ProductMultiPageTable.objects.filter(company = company, title = title).delete()

    #             for index, heading in enumerate(heading_list):
    #                 product_table = ProductMultiPageTable.objects.create(
    #                     company = company, title = title, heading = heading
    #                 )

    #                 data_positions  = list(range(index, data_length, heading_length))
    #                 data_list_of_heading = [data_list[i] for i in data_positions ]

    #                 table_data_objs  = [ProductMultiPageTableData(
    #                         company = company, title = title,
    #                         heading = heading, data = data
    #                         ) for data in data_list_of_heading if data]

    #                 ProductMultiPageTableData.objects.bulk_create(table_data_objs )

    #                 product_table_data_objs = ProductMultiPageTableData.objects.filter(company = company, title = title, heading = heading)

    #                 product_table.datas.set(product_table_data_objs)
    #                 product_tables.append(product_table)

    #         return product_tables
        
    #     except Exception as e:
    #         logger.exception(f"Error in handle_tables function of BaseProductMultiPageView: {e}")

    #     return []
    
    def handle_bullet_points(self, request, company, title):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                ProductMultiPageBulletPoint.objects.filter(company = company, title = title).delete()

                if bullet_point_list:
                    bullet_point_objects = [ProductMultiPageBulletPoint(
                        company = company, title = title,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    ProductMultiPageBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = ProductMultiPageBulletPoint.objects.filter(company = company, title = title)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseProductMultiPageView: {e}")

        return []

    def handle_timelines(self, request, company, title):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                ProductMultiPageTimeline.objects.filter(company = company, title = title).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [ProductMultiPageTimeline(
                        company = company, title = title,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    ProductMultiPageTimeline.objects.bulk_create(creating_timelines)

                    product_timelines = ProductMultiPageTimeline.objects.filter(company = company, title = title)                
                                            
                    return product_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseProductMultiPageView: {e}")

        return []

    def handle_faqs(self, request, company, title):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]                        

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                ProductMultiPageFaq.objects.filter(company = company, title = title).delete()
                
                if question_list and answer_list:
                    creating_faqs = [ProductMultiPageFaq(
                        company = company, title = title,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    ProductMultiPageFaq.objects.bulk_create(creating_faqs)

                    product_faqs = ProductMultiPageFaq.objects.filter(company = company, title = title)                
                                            
                    return product_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of BaseProductMultiPageView: {e}")

        return []

    def handle_text_editors(self, request, company, title):
        try:
            text_editor_title_list = [title.strip() for title in request.POST.getlist("text_editor_title")]
            content_list = request.POST.getlist("text_editor_content")

            if len(text_editor_title_list) != len(content_list):
                raise ValueError("The number of titles does not match the number of contents.")

            with transaction.atomic():
                ProductTextEditor.objects.filter(company = company, title = title).delete()
                
                if text_editor_title_list and content_list:
                    creating_text_editors = [ProductTextEditor(
                        company = company, title = title,
                        text_editor_title = text_editor_title, content = content
                        ) for text_editor_title, content in zip(text_editor_title_list, content_list) if text_editor_title and content]

                    ProductTextEditor.objects.bulk_create(creating_text_editors)

                    service_text_editors = ProductTextEditor.objects.filter(company = company, title = title)                
                                            
                    return service_text_editors
        except Exception as e:
            logger.exception(f"Error in handle_text_editors function of BaseProductMultiPageView: {e}")

        return []


class AddProductMultiPageView(BaseProductMultiPageView, CreateView):
    form_class = ProductMultiPageDescriptionForm
    template_name = "product_company/multipage/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["categories"] = self.get_categories()        
        context["tags"] = MetaTag.objects.all().order_by("-updated")
        context["states"] = UniqueState.objects.all().order_by("-updated")

        return context

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_product_multipage', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddProductMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddProductMultiPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()

            form = self.get_form()

            title = clean_string(request.POST.get('title', ""))
            sub_title = request.POST.get('sub_title', "")
            product_slugs = [product.strip() for product in request.POST.getlist('product')]

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")
            product_region = request.POST.get("product_region")
            available_states = request.POST.getlist("available_states")

            buy_now_action = request.POST.get("buy_now_action")
            whatsapp = request.POST.get("whatsapp")
            external_link = request.POST.get("external_link")

            # vertical_title = request.POST.get("vertical_title")
            # horizontal_title = request.POST.get("horizontal_title")
            # table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            # hide_vertical_tab = request.POST.get("hide_vertical_tab")
            # hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            # hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None

            buy_now_action = buy_now_action.strip() if buy_now_action else None
            whatsapp = whatsapp.strip() if whatsapp else None
            external_link = external_link.strip() if external_link else None

            # vertical_title = vertical_title.strip() if vertical_title else None
            # horizontal_title = horizontal_title.strip() if horizontal_title else None
            # table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = current_company

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Title": title,
                "Products": product_slugs,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            if product_region != "all" and len(available_states) < 1:
                messages.error(request, "Failed! Selected 'Selected States' for product region without providing any available state")
                return redirect(self.get_redirect_url())
                
            buy_now_missing_field = ""
            if buy_now_action == "whatsapp" and not whatsapp:
                buy_now_missing_field = "Whatsapp Number"
            
            if buy_now_action == "external_link" and not external_link:
                buy_now_missing_field = "External Link"

            if buy_now_missing_field:
                messages.error(request, f"Failed! {buy_now_missing_field} is not provided")
                return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                # "hide_vertical_tab": hide_vertical_tab,
                # "hide_horizontal_tab": hide_horizontal_tab,
                # "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            products = Product.objects.filter(slug__in = product_slugs).order_by("-updated")

            if not products or len(products) == 0:
                messages.error(request, "Failed! Invalid Products.")
                return redirect(self.get_redirect_url())

            updating_meta_tags = []
            with transaction.atomic():                                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                product_multi_page = self.model.objects.create(
                    company = company, title = title, sub_title = sub_title, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    url_type = url_type, product_region = product_region,
                    buy_now_action = buy_now_action, whatsapp = whatsapp, external_link = external_link,                    
                    bullet_title = bullet_title, 
                    timeline_title = timeline_title
                )

                product_multi_page.products.set(products)                

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(product_multi_page, key, True)
                
                product_multi_page.save()

                relationship_handlers = {
                    "features": self.handle_features,                    
                    "bullet_points": self.handle_bullet_points,                    
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                    "text_editors": self.handle_text_editors,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, title)
                    getattr(product_multi_page, field).set(objects)

                if meta_tags:
                    meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                    product_multi_page.meta_tags.set(meta_tag_objects)

                available_states_objs = UniqueState.objects.all()
                if product_region != "all":
                    available_states_objs = UniqueState.objects.filter(slug__in = available_states)

                product_multi_page.available_states.set(available_states_objs)

                messages.success(request, "Success! Created product multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddProductMultiPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ProductMultiPageListView(BaseProductMultiPageView, ListView):
    template_name = "product_company/multipage/list.html"
    queryset = ProductMultiPage.objects.none()
    context_object_name = "multipages"    
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting queryset of ProductMultiPageListView of superadmin: {e}")
            return self.queryset
        
class ProductMultiPageDetailView(BaseProductMultiPageView, DetailView):
    template_name = "product_company/multipage/detail.html"
    context_object_name = "multipage"

    def get_object(self):
        try:
            current_company = self.get_current_company()
            return get_object_or_404(self.model, company = current_company, slug = self.kwargs.get("multipage_slug"))
        
        except Http404:
            messages.error(self.request, "Invalid product Multipage")

        except Exception as e:
            logger.exception(f"Error in get_object function of ProductMultipageDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object
        
        context[self.context_object_name] = self.object
        return context        
    

class UpdateProductMultiPageView(BaseProductMultiPageView, UpdateView):    
    form_class = ProductMultiPageDescriptionForm
    template_name = "product_company/multipage/update.html"
    context_object_name = "multipage"    

    def get_object(self):
        try:
            company_slug = self.kwargs.get('slug')
            multipage_slug = self.kwargs.get('multipage_slug')            
            
            return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)
        
        except Http404:
            messages.error(self.request, "Invalid product multipage object")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            self.object = self.get_object()
            context[self.context_object_name] = self.object

            context["categories"] = ProductCategory.objects.filter(company = current_company).order_by("-updated")

            if (self.object and self.object.products.count() > 0):
                category = self.object.products.first().category

                context["products"] = Product.objects.filter(company = current_company, category = category).order_by("-updated")

            context["tags"] = MetaTag.objects.all().order_by("-updated")
            context["states"] = UniqueState.objects.all().order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateMultiPageView of superadmin: {e}")
        
        return context        
        
    def get_redirect_url(self):
        try:
            object_slug = self.object.slug or  self.kwargs.get('multipage_slug')
            return reverse_lazy('superadmin:update_product_multipage', kwargs = {"slug": self.kwargs.get('slug'), "multipage_slug": object_slug})
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateMultiPageView of superadmin: {e}")
            return self.redirect_url
        
        
    def post(self, request, *args, **kwargs):
        try:            
            form = self.get_form()

            title = clean_string(request.POST.get("title", ""))
            sub_title = request.POST.get("sub_title", "")
            product_slugs = [product.strip() for product in request.POST.getlist('product')]

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")
            product_region = request.POST.get("product_region")
            available_states = request.POST.getlist("available_states")

            buy_now_action = request.POST.get("buy_now_action")
            whatsapp = request.POST.get("whatsapp")
            external_link = request.POST.get("external_link")
            
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")            
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None
            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None
            product_region = product_region.strip() if product_region else None
            available_states = [state.strip() for state in available_states if state.strip()]

            buy_now_action = buy_now_action.strip() if buy_now_action else None
            whatsapp = whatsapp.strip() if whatsapp else None
            external_link = external_link.strip() if external_link else None
            
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Title": title,
                "Products": product_slugs,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            if product_region != "all" and len(available_states) < 1:
                messages.error(request, "Failed! Selected 'Selected States' for product region without providing any available state")
                return redirect(self.get_redirect_url())

            buy_now_missing_field = ""
            if buy_now_action == "whatsapp" and not whatsapp:
                buy_now_missing_field = "Whatsapp Number"
            
            if buy_now_action == "external_link" and not external_link:
                buy_now_missing_field = "External Link"

            if buy_now_missing_field:
                messages.error(request, f"Failed! {buy_now_missing_field} is not provided")
                return redirect(self.get_redirect_url())
                
            checkbox_fields = {
                "hide_features": hide_features,                
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            products = Product.objects.filter(slug__in = product_slugs).order_by("-updated")

            if not products or len(products) == 0:
                messages.error(request, "Failed! Invalid Products.")
                return redirect(self.get_redirect_url())

            updating_meta_tags = []
            with transaction.atomic():

                multipage = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                multipage.title = title
                multipage.sub_title = sub_title
                multipage.summary = summary

                multipage.description = description

                multipage.meta_title = meta_title
                multipage.meta_description = meta_description

                multipage.url_type = url_type
                multipage.product_region = product_region

                multipage.buy_now_action = buy_now_action

                if buy_now_action == "whatsapp":
                    multipage.whatsapp = whatsapp 

                if buy_now_action == "external_link":
                    multipage.external_link = external_link 
                
                multipage.bullet_title = bullet_title                
                multipage.timeline_title = timeline_title                

                multipage.products.set(products)                

                multipage.available_states.clear()
                available_states_objs = UniqueState.objects.all()
                if product_region != "all":
                    available_states_objs = UniqueState.objects.filter(slug__in = available_states)
                    
                multipage.available_states.set(available_states_objs)         

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:
                        assigning_value = True

                    setattr(multipage, key, assigning_value)
                
                multipage.save()

                relationship_handlers = {
                    "features": self.handle_features,                    
                    "bullet_points": self.handle_bullet_points,                    
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                    "text_editors": self.handle_text_editors,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, title)
                    getattr(multipage, field).set(objects)

                multipage.save()

                meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                multipage.meta_tags.set(meta_tag_objects)

                messages.success(request, "Success! Updated product multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteProductMultiPageView(BaseProductMultiPageView, View):
    def get_object(self, **kwargs):
        company_slug = self.kwargs.get('slug')
        multipage_slug = self.kwargs.get('multipage_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            product_name = self.object.product.name
            self.object.delete()

            messages.success(request, f"Success! Removed product multipage of: {product_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Product Multipage")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteProductMultiPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseProductBannerView(BaseProductCompanyView, View):
    model = Banner

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:product_banners', kwargs ={"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseBannerView: {e}")

        return reverse_lazy('superadmin:home')

    def get_redirect_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_banner_page"] = True
        return context


class ProductBannerListView(BaseProductBannerView, ListView):
    context_object_name = "banners"
    template_name = "product_company/banner/list.html"

    def get_queryset(self):
        return Banner.objects.filter(company__slug = self.kwargs.get("slug"))


class CreateProductBannerView(BaseProductBannerView, CreateView):
    template_name = "product_company/banner/add.html"
    fields = ["company", "image", "title", "description", "link"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_banner_page"] = True
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

            if not company:
                messages.error(request, "Failed! Invalid Product Company.")
                return self.get_redirect_url()
            
            image = request.FILES.get("image" "")
            title = clean_string(request.POST.get("title", ""))
            description = clean_string(request.POST.get("description", ""))
            link = clean_string(request.POST.get("link", ""))

            required_fields = {
                "Title": title, "Description": description,
                "Image": image, "Link": link
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required.")
                    return redirect(self.get_redirect_url())

            if Banner.objects.filter(title = title, company = company).exists():
                messages.warning(request, f"Failed! Banner with similar heading already exists.")
                return redirect(self.get_redirect_url())
                
            Banner.objects.create(
                company = company, title = title, description = description,
                image = image, link = link
            )
            messages.success(request, "Success! Banner Created.")
            return redirect(self.get_success_url())

        except Exception as e:
            messages.error(request, "Failed! An unexpected error occurred.")
            logger.exception(f"Error in CreateProductBannerView of superadmin :{e}")

        return self.get_redirect_url()
    

class UpdateProductBannerView(BaseProductBannerView, UpdateView):
    fields = ["image", "title", "description", "link"]
    slug_url_kwarg = "banner_slug"

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:update_product_banner', kwargs={'slug': self.kwargs.get('slug'), 'banner_slug': self.kwargs.get('slug_url_kwarg')})
        except Exception as e:
            pass

        return self.get_success_url()

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()
            self.object = self.get_object()

            if not company:
                messages.error(request, "Failed! Invalid Product Company.")
                return self.get_redirect_url()
            
            image = request.FILES.get("image" "")
            title = clean_string(request.POST.get("title", ""))
            description = clean_string(request.POST.get("description", ""))
            link = clean_string(request.POST.get("link", ""))

            required_fields = {
                "Title": title, "Description": description, "Link": link
            }

            if not hasattr(self.object, "image"):
                required_fields["image"] = image            

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required.")
                    return redirect(self.get_redirect_url())
                
            if Banner.objects.filter(title = title, company = company).exclude(pk = self.object.pk).exists():
                messages.warning(request, f"Failed! Banner with similar heading already exists.")
                return redirect(self.get_redirect_url())
                
            self.object.title = title
            self.object.description = description
            self.object.link = link

            if image:
                self.object.image = image

            self.object.save()               
            messages.success(request, "Success! Banner Updated.")
            return redirect(self.get_success_url())

        except Exception as e:
            messages.error(request, "Failed! An unexpected error occurred.")
            logger.exception(f"Error in UpdateProductBannerView of superadmin :{e}")

        return self.get_redirect_url()


class DeleteProductBannerView(BaseProductBannerView, UpdateView):
    slug_url_kwarg = 'banner_slug'

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()
            self.object = self.get_object()

            if not company:
                messages.error(request, "Failed! Invalid Product Company.")
                return self.get_redirect_url()
            
            self.object.delete()
            messages.success(request, "Success! Banner Deleted.")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Banner.")
            return self.get_redirect_url()


# Education Company
class BaseEducationCompanyView(BaseCompanyView, View):
    model = Course
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:                        
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["company_page"] = True
        except Http404:
            logger.exception(f"Invalid education company in context of base education company view of superadmin.")
        except Exception as e:
            logger.exception(f"Error in fetching context data of base education company view of super admin: {e}")
        return context
    

class AddCourseView(BaseEducationCompanyView, CreateView): 
    fields = ["company", "image", "name", "program", "specialization", "mode", "duration", "price", "duration", "meta_tags", "meta_description", "subtitles"]
    template_name = "education_company/courses/add.html"
    success_url = redirect_url = reverse_lazy("superadmin:home")
    
    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:courses", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of add course view: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of add course view: {e}")

        return self.redirect_url


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   
        
        try:
            context["course_page"] = True
            context["add_course_page"] = True

            current_company = self.get_current_company()

            context["programs"] = Program.objects.filter(company = current_company).order_by("-updated")
            context["tags"] = MetaTag.objects.all().order_by("-updated")
                
        except Exception as e:
            logger.exception(f"Error in getting context data of AddCourseView in superadmin app: {e}")

        return context
    
    def post(self, request, *args, **kwargs):        
        try:
            company = self.get_current_company()

            image = request.FILES.get('image')
            name = request.POST.get("name")
            program_slug = request.POST.get("program")
            specialization_slug = request.POST.get("specialization")
            mode = request.POST.get("mode")
            duration = request.POST.get("duration")
            price = request.POST.get("price")

            meta_tags = request.POST.getlist("meta_tag")

            subtitles = request.POST.get("subtitles")
            meta_description = request.POST.get("meta_description")

            name = name.strip() if name else None
            program_slug = program_slug.strip() if program_slug else None
            specialization_slug = specialization_slug.strip() if specialization_slug else None
            mode = mode.strip() if mode else None
            duration = duration.strip() if duration else None
            price = price.strip() if price else None
            subtitles = subtitles.strip() if subtitles else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            required_fields = {
                "Name": name,
                "Program": program_slug,
                "Specialization": specialization_slug,
                "Mode": mode,
                "Price": price,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url)

            try:
                program = get_object_or_404(Program, slug = program_slug)
            except Http404:
                messages.error(request, "Failed! Invalid Program")
                return redirect(self.get_redirect_url())

            try:
                specialization = get_object_or_404(Specialization, slug = specialization_slug)
            except Http404:
                messages.error(request, "Failed! Invalid Specialization")
                return redirect(self.get_redirect_url())

            updating_meta_tags = []
            with transaction.atomic():

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                course, created = self.model.objects.get_or_create(
                    company = company, image = image,
                    name=name, program=program, specialization=specialization,
                    mode=mode, duration=duration, price=price, subtitles = subtitles,
                    meta_description = meta_description
                    )

                if meta_tags:
                    meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                    course.meta_tags.set(meta_tag_objects)  
                
                if created:
                    messages.success(request, "Success! Course created.")
                    return redirect(self.get_success_url())
                
                messages.error(request, "Failed! Course already exists")

        except Exception as e:
            messages.error(request, "Failed! Server Error.")
            logger.exception(f"Error in adding course in add course view: {e}")

        return redirect(self.get_redirect_url())
    

class UpdateCourseView(BaseEducationCompanyView, UpdateView): 
    fields = ["image", "name", "program", "specialization", "mode", "duration", "price", "duration", "subtitles", "meta_tags", "meta_description"]   
    template_name = "education_company/courses/edit.html"
    success_url = redirect_url = reverse_lazy("superadmin:home")    
    slug_url_kwarg = "course_slug"
    
    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:courses", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateCourseView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateCourseView of superadmin app: {e}")

        return self.redirect_url    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   
        
        try:
            context["course_page"] = True
            context["add_course_page"] = True
            context["modes"] = ("Online", "Offline")

            current_company = self.get_current_company()
            current_course = self.get_object()

            context["programs"] = Program.objects.filter(company = current_company).order_by("-updated")
            context["specializations"] = Specialization.objects.filter(company = current_company, program = current_course.program).order_by("-updated")

            context["tags"] = MetaTag.objects.all().order_by("-updated")
                
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateCourseView in superadmin app: {e}")

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

            meta_tags = request.POST.getlist("meta_tag")

            subtitles = request.POST.get("subtitles")
            meta_description = request.POST.get("meta_description")

            name = name.strip() if name else None
            program_slug = program_slug.strip() if program_slug else None
            specialization_slug = specialization_slug.strip() if specialization_slug else None
            mode = mode.strip() if mode else None
            duration = duration.strip() if duration else None
            price = price.strip() if price else None

            meta_tags = [tag.strip() for tag in meta_tags if tag and tag.strip()]

            subtitles = subtitles.strip() if subtitles else None
            meta_description = meta_description.strip() if meta_description else None

            required_fields = {
                "Name": name,
                "Program": program_slug,
                "Specialization": specialization_slug,
                "Mode": mode,
                "Price": price,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url)
                
            try:
                program = get_object_or_404(Program, slug = program_slug)
            except Http404:
                messages.error(request, "Failed! Invalid Program")
                return redirect(self.get_redirect_url())

            try:
                specialization = get_object_or_404(Specialization, slug = specialization_slug)
            except Http404:
                messages.error(request, "Failed! Invalid Specialization")
                return redirect(self.get_redirect_url())            

            course = self.get_object()

            updating_meta_tags = []
            with transaction.atomic():

                similar_course = self.model.objects.filter(
                    company = course.company, name = name, program = program,
                    specialization = specialization, mode = mode
                    ).exclude(pk = course.pk).first()
                
                if similar_course:                
                    messages.error(request, "Failed! Similar course already exists")
                    return redirect(self.get_redirect_url())

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)
                
                course.name = name
                course.program = program
                course.specialization = specialization
                course.mode = mode
                course.duration = duration
                course.price = price
                course.subtitles = subtitles
                course.meta_description = meta_description
                if image:
                    course.image = image
                course.save()
                
                meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                course.meta_tags.set(meta_tag_objects)

                messages.success(request, "Success! Course updated.")
                return redirect(self.get_success_url())
            
        except Exception as e:
            logger.exception(f"Error in UpdateCourseView of superadmin app: {e}")
            messages.error(request, "An expected error occurred")

        return redirect(self.get_redirect_url())
    

class RemoveCourseView(BaseEducationCompanyView, View):
    model = Course
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:courses", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveCourseView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveCourseView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("course_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted course")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid course")

        except Exception as e:
            logger.exception(f"Error in RemoveCourseView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())


class CourseListView(BaseEducationCompanyView, ListView):
    queryset = Course.objects.none()
    context_object_name = "courses"
    template_name = "education_company/courses/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get("slug")).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of course list view of admin section")
        
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_page"] = True
            context['course_list_page'] = True
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin course list view: {e}")
        return context
    

class CourseProgramListView(BaseEducationCompanyView, ListView):
    model = Program
    queryset = model.objects.none()
    context_object_name = "programs"
    template_name = "education_company/programs/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get("slug"))
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of course program list view of admin section")
        
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_program_page"] = True
            context['program_list_page'] = True
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin course program list view: {e}")
        return context
    

class AddCourseProgramView(BaseEducationCompanyView, CreateView):
    model = Program
    fields = ["company", "name"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:course_programs", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()  

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()

            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                program, created = self.model.objects.get_or_create(company = current_company, name = name)

                if created:
                    messages.success(request, "Success! Course program created.")
                    return redirect(self.get_success_url())

                else:
                    messages.warning(request, "Course program already exists.")
            
            else:
                messages.error(request, "Course program name is required.")            
        
        except Exception as e:
            logger.exception(f"Error in creating course program: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class UpdateCourseProgramView(BaseEducationCompanyView, UpdateView):
    model = Program
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:course_programs", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()
        
    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("program_slug"))
        except Http404:
            messages.error(self.request, "Invalid course program")
            return redirect(self.get_redirect_url())

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            if not name:
                messages.error(request, "Failed! Name is required")
                return redirect(self.get_redirect_url())
            
            program = self.get_object()

            similar_programs = self.model.objects.filter(company = program.company, name = name)
            
            if similar_programs.exists() and similar_programs.first() != program:
                messages.warning(request, "Similar course program already exists")
                return redirect(self.get_redirect_url())

            program.name = name
            program.save()
            messages.success(request, "Success! Course program updated.")
            return redirect(self.get_success_url())    
        
        except Exception as e:
            logger.exception(f"Error in UpdateCourseProgramView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class RemoveCourseProgramView(BaseEducationCompanyView, View):
    model = Program
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:course_programs", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveCourseProgramView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveCourseProgramView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("program_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted course program")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid course program")

        except Exception as e:
            logger.exception(f"Error in RemoveCourseProgramView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class CourseSpecializationListView(BaseEducationCompanyView, ListView):
    model = Specialization
    queryset = model.objects.none()
    context_object_name = "specializations"
    template_name = "education_company/specializations/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get("slug")).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of CourseSpecializationListView of admin section: {e}")
        
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_specialization_page"] = True
            context['program_list_page'] = True                
            context["programs"] = Program.objects.filter(company__slug = self.kwargs.get("slug")).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in fetching context data of CourseSpecializationListView of superadmin app: {e}")
        return context
    

class AddCourseSpecializationView(BaseEducationCompanyView, CreateView):
    model = Specialization
    fields = ["name", "program", "starting_title", "slug", "ending_title", "content", "faqs", "description"]
    success_url = redirect_url = reverse_lazy("superadmin:home")
    template_name = "education_company/specializations/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            context["course_specialization_page"] = True
            context["programs"] = Program.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateCourseSpecializationView of superadmin app: {e}")
        
        return context

    def get_success_url(self):        
        return reverse_lazy("superadmin:course_specializations", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()   

    def handle_faqs(self, request, company, specialization_slug):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]               

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                CourseSpecializationFaq.objects.filter(company = company, specialization_slug = specialization_slug).delete()
                
                if question_list and answer_list:
                    creating_faqs = [CourseSpecializationFaq(
                        company = company, specialization_slug = specialization_slug,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    CourseSpecializationFaq.objects.bulk_create(creating_faqs)

                    specialization_faqs = CourseSpecializationFaq.objects.filter(company = company, specialization_slug = specialization_slug)                
                                            
                    return specialization_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of AddCourseSpecializationView: {e}")

        return []  

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()

            name = clean_string(request.POST.get("name", ""))
            program_slug = clean_string(request.POST.get("program", ""))
            description = clean_string(request.POST.get("description", ""))
            starting_title = clean_string(request.POST.get("starting_title", ""))
            slug = clean_string(request.POST.get("slug", ""))
            ending_title = clean_string(request.POST.get("ending_title", ""))
            content = request.POST.get("content")
            hide_faqs = request.POST.get("hide_faqs")

            required_fields = {
                "Name": name,
                "Course Program": program_slug
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required")
                    return redirect(self.get_redirect_url())

            slug_list = [starting_title, slug, ending_title]

            full_slug = slugify("-".join(filter(None, slug_list)))

            with transaction.atomic():            
                program = get_object_or_404(Program, slug = program_slug)

                if self.model.objects.filter(slug = slug).exists():
                    messages.error(request, "Failed! Similar slug already exists for another course specialization.")
                    return redirect(self.get_redirect_url())

                if full_slug and self.model.objects.filter(location_slug = full_slug).exists():
                        messages.error(request, "Failed! Similar location slug already exists for another course specialization.")
                        return redirect(self.get_redirect_url())
                
                specialization, created = self.model.objects.get_or_create(
                    company = current_company, name = name, 
                    program = program, 
                    defaults={
                        "description": description,
                        "starting_title": starting_title,
                        "ending_title": ending_title,
                        "hide_faqs": True if hide_faqs else False,
                        "content": content,
                        "slug": slug if slug else None,
                        "location_slug": full_slug if full_slug else None,
                    })

                if not created:
                    messages.warning(request, "Course specialization already exists.")
                    return redirect(self.get_redirect_url())

                specialization_faq_objs = self.handle_faqs(request, specialization.company, specialization.slug)
                specialization.faqs.set(specialization_faq_objs)

                messages.success(request, "Success! Course specialization created.")
                return redirect(self.get_success_url())                

        except Http404:
            messages.error(request, "Invalid course program")                                    
        
        except Exception as e:
            logger.exception(f"Error in AddCourseSpecializationView in superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class UpdateCourseSpecializationView(BaseEducationCompanyView, UpdateView):
    model = Specialization
    fields = ["name", "program", "starting_title", "slug", "ending_title", "content", "faqs", "description"]
    success_url = redirect_url = reverse_lazy("superadmin:home")
    template_name = "education_company/specializations/edit.html"
    context_object_name = "specialization"

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:course_specializations", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of UpdateCourseSpecializationView in superadmin app: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()  
        except Exception as e:
            logger.exception(f"Error in getting redirect url of UpdateCourseSpecializationView in superadmin app: {e}")
            return self.redirect_url 
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            context["course_specialization_page"] = True
            context["programs"] = Program.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateCourseSpecializationView of superadmin app: {e}")
        
        return context
        
    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("specialization_slug"))
        except Http404:
            messages.error(self.request, "Invalid course specialization")
            return redirect(self.get_redirect_url())

    def handle_faqs(self, request, company, specialization_slug):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]               

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                CourseSpecializationFaq.objects.filter(company = company, specialization_slug = specialization_slug).delete()
                
                if question_list and answer_list:
                    creating_faqs = [CourseSpecializationFaq(
                        company = company, specialization_slug = specialization_slug,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    CourseSpecializationFaq.objects.bulk_create(creating_faqs)

                    product_faqs = CourseSpecializationFaq.objects.filter(company = company, specialization_slug = specialization_slug)                
                                            
                    return product_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of UpdateCourseSpecializationView: {e}")

        return []


    def post(self, request, *args, **kwargs):
        try:
            specialization = self.get_object()
            object_slug = specialization.slug or ""

            name = clean_string(request.POST.get("name", ""))
            program_slug = clean_string(request.POST.get("program", ""))
            description = clean_string(request.POST.get("description", ""))
            starting_title = clean_string(request.POST.get("starting_title", ""))
            slug = clean_string(request.POST.get("slug", object_slug))
            ending_title = clean_string(request.POST.get("ending_title", ""))
            content = request.POST.get("content")            
            hide_faqs = request.POST.get("hide_faqs")

            required_fields = {
                "Name": name,                
                "Course Program": program_slug
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required")
                    return redirect(self.get_redirect_url())
                
            slug_list = [starting_title, slug, ending_title]

            full_slug = slugify("-".join(filter(None, slug_list)))
            
            with transaction.atomic():
                program = get_object_or_404(Program, slug = program_slug)

                if self.model.objects.filter(
                    company = specialization.company, name = name, program = program
                    ).exclude(pk = specialization.pk).exists():

                    messages.warning(request, "Failed! Similar course specialization already exists")
                    return redirect(self.get_redirect_url())

                slug = slugify(slug)

                if slug != specialization.slug:
                    
                    if self.model.objects.filter(slug = slug).exclude(pk = specialization.pk).exists():
                        messages.error(request, "Failed! Similar slug already exists for another course specialization.")
                        return redirect(self.get_redirect_url())
                    
                    specialization.slug = slug

                if full_slug != specialization.location_slug:                    
                    if self.model.objects.filter(location_slug = full_slug).exclude(pk = specialization.pk).exists():
                        messages.error(request, "Failed! Similar location slug already exists for another course specialization.")
                        return redirect(self.get_redirect_url())

                    specialization.location_slug = full_slug

                specialization.name = name
                specialization.program = program
                specialization.description = description
                specialization.starting_title = starting_title
                specialization.ending_title = ending_title
                specialization.hide_faqs = True if hide_faqs else False        
                specialization.content = content

                specialization.save()
                
                specialization_faq_objs = self.handle_faqs(request, specialization.company, specialization.slug)
                specialization.faqs.set(specialization_faq_objs)

                messages.success(request, "Success! Course specialization updated.")
                return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid course program")                                    
        
        except Exception as e:
            logger.exception(f"Error in UpdateCourseSpecializationView in superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class RemoveCourseSpecializationView(BaseEducationCompanyView, View):
    model = Specialization
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:course_specializations", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveCourseSpecializationView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveCourseSpecializationView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("specialization_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted course specialization")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid course specialization")

        except Exception as e:
            logger.exception(f"Error in RemoveCourseSpecializationView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    
# Course Detail
class AddCourseDetailView(BaseEducationCompanyView, CreateView):
    model = CourseDetail
    form_class = CourseDetailDescriptionForm
    template_name = "education_company/course_detail/add.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_detail_page"] = True
            
            current_company = self.get_current_company()
            
            context["current_company"] = current_company

            context["tags"] = MetaTag.objects.all().order_by("-updated")

            context["programs"] = Program.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting context data of AddCourseDetailView of superadmin: {e}")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_course_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddCourseDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddCourseDetailView of superadmin: {e}")
            return self.redirect_url
        
    def get_course(self, course_slug):
        try:
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Invalid Course")
            return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, course):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    CourseFeature.objects.filter(company = company, course = course).delete()

                    features = [CourseFeature(company=company, course=course, feature=feature) for feature in features_list]
                    CourseFeature.objects.bulk_create(features)

                    feature_objs = CourseFeature.objects.filter(company = company, course = course)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of AddCourseDetailView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, course):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                CourseVerticalTab.objects.filter(company = company, course = course).delete()
                CourseVerticalBullet.objects.filter(company = company, course = course).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = CourseVerticalTab.objects.create(
                            company = company,
                            course = course,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [CourseVerticalBullet(
                                company = company, course = course, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                CourseVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = CourseVerticalBullet.objects.filter(company = company, course = course, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)

                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of AddCourseDetailView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, course):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                CourseHorizontalTab.objects.filter(company = company, course = course).delete()
                CourseHorizontalBullet.objects.filter(company = company, course = course).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = CourseHorizontalTab.objects.create(
                            company = company,
                            course = course,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [CourseHorizontalBullet(
                                company = company, course = course, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                CourseHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = CourseHorizontalBullet.objects.filter(company = company, course = course, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of AddCourseDetailView: {e}")

        return []
    
    def handle_tables(self, request, company, course):
        try:
            course_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                CourseTableData.objects.filter(company = company, course = course).delete()
                CourseTable.objects.filter(company = company, course = course).delete()

                for index, heading in enumerate(heading_list):
                    course_table = CourseTable.objects.create(
                        company = company, course = course, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [CourseTableData(
                            company = company, course = course,
                            heading = heading, data = data
                            ) for data in data_list_of_heading]

                    CourseTableData.objects.bulk_create(table_data_objs )

                    course_table_data_objs = CourseTableData.objects.filter(company = company, course = course, heading = heading)

                    course_table.datas.set(course_table_data_objs)

                    course_tables.append(course_table)

            return course_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of AddCourseDetailView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, course):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                CourseBulletPoint.objects.filter(company = company, course = course).delete()

                if bullet_point_list:
                    bullet_point_objects = [CourseBulletPoint(
                        company = company, course = course,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    CourseBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = CourseBulletPoint.objects.filter(company = company, course = course)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of AddCourseDetailView: {e}")

        return []

    def handle_timelines(self, request, company, course):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                CourseTimeline.objects.filter(company = company, course = course).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [CourseTimeline(
                        company = company, course = course,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    CourseTimeline.objects.bulk_create(creating_timelines)

                    course_timelines = CourseTimeline.objects.filter(company = company, course = course)                
                                            
                    return course_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of AddCourseDetailView: {e}")

        return []

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            course_slug = request.POST.get('course')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")

            hide_support_languages = request.POST.get("hide_support_languages")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company or company.type.name != "Education" :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Course": course_slug,
                "summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                
            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                }

            course = self.get_course(course_slug)

            updating_meta_tags = []
            with transaction.atomic():

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                course_detail = self.model.objects.create(
                    company = company, course = course, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, 
                    timeline_title = timeline_title, hide_support_languages = True if hide_support_languages else False
                )                

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(course_detail, key, True)

                course_detail.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, course)
                    getattr(course_detail, field).set(objects)

                if meta_tags:
                    meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                    course_detail.meta_tags.set(meta_tag_objects)  

                messages.success(request, "Success! Created course detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class CourseDetailsListView(BaseEducationCompanyView, ListView):
    model = CourseDetail
    template_name = "education_company/course_detail/list.html"
    queryset = model.objects.none()
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "course_details"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_detail_page"] = True
            
            current_company = self.get_current_company()
            
            context["current_company"] = current_company

        except Exception as e:
            logger.exception(f"Error in getting context data of AddCompanyDetailView of superadmin: {e}")
        
        return context
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting queryset of CourseDetailsListView of superadmin: {e}")
            return self.queryset
        

class CourseDetailView(BaseEducationCompanyView, DetailView):
    model = CourseDetail
    template_name = "education_company/course_detail/detail.html"
    redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "course_detail"

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:course_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function of CourseDetailView: {e}")
            return self.redirect_url
        
    def get_current_course(self):
        try:
            course_slug = self.kwargs.get('course_slug')
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Course")
            return redirect(self.redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_detail_page"] = True
            
            current_company = self.get_current_company()
            
            context["current_company"] = current_company

        except Exception as e:
            logger.exception(f"Error in getting context data of AddCompanyDetailView of superadmin: {e}")
        
        return context
    
    def get_object(self):
        try:
            current_company = self.get_current_company()
            current_course = self.get_current_course()
            return get_object_or_404(self.model, company = current_company, course = current_course)
        
        except Http404:
            messages.error(self.request, "Invalid course for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of CourseDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())
    

class UpdateCourseDetailView(BaseEducationCompanyView, UpdateView):
    model = CourseDetail
    form_class = CourseDetailDescriptionForm
    template_name = "education_company/course_detail/update.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "course_detail"
    
    def get_object(self):
        try:
            company_slug = self.kwargs.get('slug')
            course_detail_slug = self.kwargs.get('course_detail_slug')
            
            return get_object_or_404(CourseDetail, company__slug = company_slug, slug = course_detail_slug)
        
        except Http404:
            messages.error(self.request, "Invalid course detail object")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_detail_page"] = True
            
            current_company = self.get_current_company()
            
            context["current_company"] = current_company 
            context["tags"] = MetaTag.objects.all().order_by("-updated")  

            self.object = self.get_object()         

            context["programs"] = Program.objects.filter(company = current_company).order_by("-updated")
            context["courses"] = Course.objects.filter(company = current_company, program = self.object.course.program).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateCourseDetailView of superadmin: {e}")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:course_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateCourseDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:update_course_details', kwargs = {"slug": self.kwargs.get('slug'), "course_detail_slug": self.kwargs.get('course_detail_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateCourseDetailView of superadmin: {e}")
            return self.redirect_url
        
    def get_course(self, course_slug):
        try:
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Invalid Course")
            return redirect(self.get_redirect_url())
    
    def handle_features(self, request, company, course):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    CourseFeature.objects.filter(company = company, course = course).delete()

                    features = [CourseFeature(company=company, course=course, feature=feature) for feature in features_list]
                    CourseFeature.objects.bulk_create(features)

                    feature_objs = CourseFeature.objects.filter(company = company, course = course)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of UpdateCourseDetailView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, course):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")

            initial = 0

            with transaction.atomic():
                CourseVerticalTab.objects.filter(company = company, course = course).delete()
                CourseVerticalBullet.objects.filter(company = company, course = course).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = CourseVerticalTab.objects.create(
                            company = company,
                            course = course,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )                    

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [CourseVerticalBullet(
                                company = company, course = course, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                CourseVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = CourseVerticalBullet.objects.filter(company = company, course = course, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)

                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of UpdateCourseDetailView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, course):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")

            initial = 0

            with transaction.atomic():
                CourseHorizontalTab.objects.filter(company = company, course = course).delete()
                CourseHorizontalBullet.objects.filter(company = company, course = course).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = CourseHorizontalTab.objects.create(
                            company = company,
                            course = course,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:

                            creating_horizontal_bullets = [CourseHorizontalBullet(
                                company = company, course = course, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                CourseHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = CourseHorizontalBullet.objects.filter(company = company, course = course, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)                                        

            return horizontal_tab_objects

        except Exception as e:
            logger.exception(f"Error in handle_horizontal_tabs function of UpdateCourseDetailView: {e}")

        return []
    
    def handle_tables(self, request, company, course):
        try:
            course_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)

            with transaction.atomic():
                CourseTableData.objects.filter(company = company, course = course).delete()
                CourseTable.objects.filter(company = company, course = course).delete()

                for index, heading in enumerate(heading_list):
                    course_table = CourseTable.objects.create(
                        company = company, course = course, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [CourseTableData(
                            company = company, course = course,
                            heading = heading, data = data
                            ) for data in data_list_of_heading]

                    CourseTableData.objects.bulk_create(table_data_objs )

                    course_table_data_objs = CourseTableData.objects.filter(company = company, course = course, heading = heading)

                    course_table.datas.set(course_table_data_objs)

                    course_tables.append(course_table)

            return course_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of UpdateCourseDetailView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, course):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                CourseBulletPoint.objects.filter(company = company, course = course).delete()

                if bullet_point_list:
                    bullet_point_objects = [CourseBulletPoint(
                        company = company, course = course,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    CourseBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = CourseBulletPoint.objects.filter(company = company, course = course)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of UpdateCourseDetailView: {e}")

        return []

    def handle_timelines(self, request, company, course):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                CourseTimeline.objects.filter(company = company, course = course).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [CourseTimeline(
                        company = company, course = course,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    CourseTimeline.objects.bulk_create(creating_timelines)

                    course_timelines = CourseTimeline.objects.filter(company = company, course = course)

                    return course_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of UpdateCourseDetailView: {e}")

        return []
        
    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            course_slug = request.POST.get('course')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")
            
            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title") 

            hide_support_languages = request.POST.get("hide_support_languages")  

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")

            # Fetch current company
            company = self.get_current_company()

            if not company or company.type.name != "Education" :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Course": course_slug,
                "summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                }

            course = self.get_course(course_slug)

            updating_meta_tags = []
            with transaction.atomic():

                course_detail = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                course_detail.course = course
                course_detail.summary = summary

                course_detail.description = description

                course_detail.meta_title = meta_title
                course_detail.meta_description = meta_description

                course_detail.vertical_title = vertical_title
                course_detail.horizontal_title = horizontal_title
                course_detail.table_title = table_title
                course_detail.bullet_title = bullet_title                
                course_detail.timeline_title = timeline_title

                course_detail.hide_support_languages = True if hide_support_languages else False                
                
                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:                    
                        assigning_value = True

                    setattr(course_detail, key, assigning_value)
                
                course_detail.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, course)
                    getattr(course_detail, field).set(objects)

                course_detail.save()

                meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                course_detail.meta_tags.set(meta_tag_objects)

                messages.success(request, "Success! Updated course detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())



class DeleteCourseDetailView(BaseEducationCompanyView, View):
    model = CourseDetail
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:course_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of DeleteCourseDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of DeleteCourseDetailView of superadmin: {e}")
            return self.redirect_url
        
    def get_object(self):
        course_slug = self.kwargs.get('course_detail_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = course_slug, company__slug = company_slug)

    def get(self, request, *args, **kwargs):
        try:
            course_detail = self.get_object()
            course_name = course_detail.course.name
            course_detail.delete()

            messages.success(request, f"Success! Removed course detail page of: {course_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Course Detail")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteCourseDetailView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())

class AddCourseFaqView(BaseEducationCompanyView, CreateView):
    model = CourseFaq
    fields = ["company", "dynamic_place_rendering", "course", "question", "answer"]
    template_name = "education_company/course_faqs/add.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_course_faq', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddCourseFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddCourseFaqView of superadmin: {e}")
            return self.redirect_url

    def get_course(self, course_slug):
        try:
            
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Invalid Course")
            return redirect(self.get_redirect_url())
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["course_faq_page"] = context["add_course_faq_page"] = True
        context["programs"] = Program.objects.filter(company__slug = company_slug).order_by("-updated")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            course_slug = self.request.POST.get('course')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

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

            company = self.get_current_company()
            course = self.get_course(course_slug)

            dynamic_place_rendering = True if dynamic_place_rendering else False

            CourseFaq.objects.update_or_create(company = company, course = course, question = question, dynamic_place_rendering = dynamic_place_rendering, defaults={"answer": answer})

            messages.success(request, f"Success! Created FAQ object for course: {course.name}")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in get function of AddCourseFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class UpdateCourseFaqView(BaseEducationCompanyView, UpdateView):
    model = CourseFaq
    fields = ["course", "dynamic_place_rendering", "question", "answer"]
    template_name = "education_company/course_faqs/update.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "faq"

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_course_faq', kwargs = {"slug": self.kwargs.get('slug'), "course_faq_slug": self.kwargs.get('course_faq_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateCourseFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateCourseFaqView of superadmin: {e}")
            return self.redirect_url

    def get_course(self, course_slug):
        try:
            
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Invalid Course")
            return redirect(self.get_redirect_url())
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["course_faq_page"] = context["update_course_faq_page"] = True
        context["programs"] = Program.objects.filter(company__slug = company_slug).order_by("-updated")

        return context
    
    def get_object(self):
        company_slug = self.kwargs.get('slug') 
        course_faq_slug = self.kwargs.get('course_faq_slug') 

        return get_object_or_404(CourseFaq, company__slug = company_slug, slug = course_faq_slug)
        
    def post(self, request, *args, **kwargs):
        try:
            faq = self.get_object()

            course_slug = self.request.POST.get('course')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

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

            dynamic_place_rendering = True if dynamic_place_rendering else False

            similar_faq = self.model.objects.filter(
                company = faq.company, course = course, question = question, answer = answer, dynamic_place_rendering = dynamic_place_rendering
                ).first()

            if similar_faq:
                if similar_faq.slug == faq.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar course FAQ already exists")
                return redirect(self.get_redirect_url())

            faq.course = course
            faq.question = question
            faq.answer = answer
            faq.dynamic_place_rendering = dynamic_place_rendering
            faq.save()

            messages.success(request, f"Success! Updated FAQ")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid course FAQ object")

        except Exception as e:
            logger.exception(f"Error in get function of UpdateCourseFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteCourseFaqView(BaseEducationCompanyView, View):
    model = CourseFaq
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:course_faqs', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of DeleteCourseFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of DeleteCourseFaqView of superadmin: {e}")
            return self.redirect_url
        
    def get_object(self):
        faq_slug = self.kwargs.get('course_faq_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = faq_slug, company__slug = company_slug)

    def get(self, request, *args, **kwargs):
        try:
            faq = self.get_object()
            course_name = faq.course.name
            faq.delete()

            messages.success(request, f"Success! Removed course FAQ object of: {course_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Course FAQ")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteCourseFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ListCourseFaqView(BaseEducationCompanyView, ListView):
    model = CourseFaq
    template_name = "education_company/course_faqs/list.html"
    queryset = model.objects.none()
    context_object_name = "faqs"
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["course_faq_page"] = True

        return context

    def get_queryset(self):
        try:
            company_slug = self.kwargs.get('slug')
            company = get_object_or_404(Company, slug = company_slug, type__name = "Education")
            return self.model.objects.filter(company = company)
            
        except Http404:
            messages.error(self.request, "Invalid educational company")
            return redirect(self.redirect_url)           


class BaseCourseEnquiryView(BaseEducationCompanyView, View):
    model = CourseEnquiry
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = self.get_current_company()
            context["education_enquiry_page"] = True

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseCourseEnquiryView: {e}")

        return context

class ListCourseEnquiryView(BaseCourseEnquiryView, ListView):
    context_object_name = "enquiries"
    template_name = "education_company/enquiries/list.html"

    def get_queryset(self):
        try:
            course_enquiries = CourseEnquiry.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg))
            contact_enquiries = ContactEnquiry.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg))
            return QuerySetSequence(course_enquiries, contact_enquiries).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListCourseEnquiryView of superadmin: {e}")
            return QuerySetSequence().none()

    def get_template_names(self):
        return [self.template_name]


class DeleteCourseEnquiryView(BaseCourseEnquiryView, View):
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:course_enquiries', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of DeleteCourseEnquiryView of superadmin app: {e}")
            return self.success_url

    def get_redirect_url(self):
        return self.get_success_url()
            

    def post(self, request, *args, **kwargs):
        try:
            CourseEnquiry.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg), slug = self.kwargs.get('enquiry_slug')).delete()

            messages.success(request, "Success! Delete Course Enquiry")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Course Enquiry")
            return redirect(self.get_redirect_url())


class BaseCourseMultiPageView(BaseEducationCompanyView, View):
    model = CourseMultiPage
    success_url = redirect_url = reverse_lazy('superadmin:home')    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_multipage"] = True
            
            self.current_company = self.get_current_company()
            
            context["current_company"] = self.current_company            
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseCourseMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:course_multipages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseCourseMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseCourseMultiPageView of superadmin: {e}")
            return self.redirect_url
        
    def get_course(self, course_slug):
        try:
            return get_object_or_404(Course, slug = course_slug)
        except Http404:            
            return None
        
    def handle_features(self, request, company, title):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    CourseMultiPageFeature.objects.filter(company = company, title = title).delete()

                    features = [CourseMultiPageFeature(company=company, title=title, feature=feature) for feature in features_list]
                    CourseMultiPageFeature.objects.bulk_create(features)

                    feature_objs = CourseMultiPageFeature.objects.filter(company = company, title = title)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseCourseMultiPageView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, title):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                CourseMultiPageVerticalTab.objects.filter(company = company, title = title).delete()
                CourseMultiPageVerticalBullet.objects.filter(company = company, title = title).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = CourseMultiPageVerticalTab.objects.create(
                            company = company,
                            title = title,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [CourseMultiPageVerticalBullet(
                                company = company, title = title, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                CourseMultiPageVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = CourseMultiPageVerticalBullet.objects.filter(company = company, title = title, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)


                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseCourseMultiPageView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, title):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                CourseMultiPageHorizontalTab.objects.filter(company = company, title = title).delete()
                CourseMultiPageHorizontalBullet.objects.filter(company = company, title = title).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = CourseMultiPageHorizontalTab.objects.create(
                            company = company,
                            title = title,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [CourseMultiPageHorizontalBullet(
                                company = company, title = title, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                CourseMultiPageHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = CourseMultiPageHorizontalBullet.objects.filter(company = company, title = title, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseCourseMultiPageView: {e}")

        return []
    
    def handle_tables(self, request, company, title):
        try:
            course_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                CourseMultiPageTableData.objects.filter(company = company, title = title).delete()
                CourseMultiPageTable.objects.filter(company = company, title = title).delete()

                for index, heading in enumerate(heading_list):
                    course_table = CourseMultiPageTable.objects.create(
                        company = company, title = title, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [CourseMultiPageTableData(
                            company = company, title = title,
                            heading = heading, data = data
                            ) for data in data_list_of_heading if data]

                    CourseMultiPageTableData.objects.bulk_create(table_data_objs )

                    course_table_data_objs = CourseMultiPageTableData.objects.filter(company = company, title = title, heading = heading)

                    course_table.datas.set(course_table_data_objs)
                    course_tables.append(course_table)

            return course_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseCourseMultiPageView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, title):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                CourseMultiPageBulletPoint.objects.filter(company = company, title = title).delete()

                if bullet_point_list:
                    bullet_point_objects = [CourseMultiPageBulletPoint(
                        company = company, title = title,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    CourseMultiPageBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = CourseMultiPageBulletPoint.objects.filter(company = company, title = title)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseCourseMultiPageView: {e}")

        return []

    def handle_timelines(self, request, company, title):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                CourseMultiPageTimeline.objects.filter(company = company, title = title).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [CourseMultiPageTimeline(
                        company = company, title = title,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    CourseMultiPageTimeline.objects.bulk_create(creating_timelines)

                    course_timelines = CourseMultiPageTimeline.objects.filter(company = company, title = title)                
                                            
                    return course_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseCourseMultiPageView: {e}")

        return []

    def handle_faqs(self, request, company, title):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]                        

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                CourseMultiPageFaq.objects.filter(company = company, title = title).delete()
                
                if question_list and answer_list:
                    creating_faqs = [CourseMultiPageFaq(
                        company = company, title = title,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    CourseMultiPageFaq.objects.bulk_create(creating_faqs)

                    course_faqs = CourseMultiPageFaq.objects.filter(company = company, title = title)                
                                            
                    return course_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of BaseCourseMultiPageView: {e}")

        return []

    def handle_text_editors(self, request, company, title):
        try:
            text_editor_title_list = [title.strip() for title in request.POST.getlist("text_editor_title")]
            content_list = request.POST.getlist("text_editor_content")

            if len(text_editor_title_list) != len(content_list):
                raise ValueError("The number of titles does not match the number of contents.")

            with transaction.atomic():
                CourseTextEditor.objects.filter(company = company, title = title).delete()
                
                if text_editor_title_list and content_list:
                    creating_text_editors = [CourseTextEditor(
                        company = company, title = title,
                        text_editor_title = text_editor_title, content = content
                        ) for text_editor_title, content in zip(text_editor_title_list, content_list) if text_editor_title and content]

                    CourseTextEditor.objects.bulk_create(creating_text_editors)

                    course_text_editors = CourseTextEditor.objects.filter(company = company, title = title)                
                                            
                    return course_text_editors
        except Exception as e:
            logger.exception(f"Error in handle_text_editors function of BaseCourseMultiPageView: {e}")

        return []

class AddCourseMultiPageView(BaseCourseMultiPageView, CreateView):
    form_class = CourseMultiPageDescriptionForm
    template_name = "education_company/multipage/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        company = self.get_current_company()

        context["programs"] = Program.objects.filter(company = company).order_by("-updated")
        context["courses"] = Course.objects.filter(company = company).order_by("-updated")
        context["tags"] = MetaTag.objects.all().order_by("-updated")
        context["states"] = UniqueState.objects.all().order_by("-updated")

        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_course_multipage', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseCourseMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseCourseMultiPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()
            form = self.get_form()

            title = clean_string(request.POST.get('title'))
            sub_title = request.POST.get('sub_title')
            course_slug = clean_string(request.POST.get("course"))

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")
            course_region = request.POST.get("course_region")
            available_states = request.POST.getlist("available_states")

            slider_course_details = [item.strip() for item in request.POST.getlist("course_details", [])]

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None
            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None
            course_region = course_region.strip() if course_region else None
            available_states = [state.strip() for state in available_states if state.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = current_company

            if not company or company.type.name != "Education" :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Title": title,
                "Course": course_slug,
                "summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                
            if course_region != "all" and len(available_states) < 1:
                messages.error(request, "Failed! Selected 'Selected States' for course region without providing any available state")
                return redirect(self.get_redirect_url())

            course = self.get_course(course_slug)

            if not course:
                messages.error(request, "Failed! Invalid Course")
                return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            updating_meta_tags = []
            with transaction.atomic():
                if self.model.objects.filter(company = company, title = title).exists():
                    messages.error(request, "Multipage for this course already exists")
                    return redirect(self.get_redirect_url())

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                course_multi_page = self.model.objects.create(
                    company = company, title = title, sub_title = sub_title, course = course, summary = summary, 
                    description = description, meta_title = meta_title, meta_description = meta_description,
                    url_type = url_type, course_region = course_region, vertical_title = vertical_title, 
                    horizontal_title = horizontal_title, table_title = table_title, bullet_title = bullet_title, 
                    timeline_title = timeline_title
                )                           

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(course_multi_page, key, True)
                
                course_multi_page.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,                    
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                    "text_editors": self.handle_text_editors,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, title)
                    getattr(course_multi_page, field).set(objects)                

                if meta_tags:
                    meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                    course_multi_page.meta_tags.set(meta_tag_objects)  

                available_states_objs = UniqueState.objects.all()
                if course_region != "all":
                    available_states_objs = UniqueState.objects.filter(slug__in = available_states)

                course_multi_page.available_states.set(available_states_objs)

                slider_course_objs = CourseDetail.objects.filter(slug__in = slider_course_details)
                course_multi_page.slider_courses.set(slider_course_objs)

                messages.success(request, "Success! Created course multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddCourseMultiPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class CourseMultiPageListView(BaseCourseMultiPageView, ListView):
    template_name = "education_company/multipage/list.html"
    queryset = CourseMultiPage.objects.none()
    context_object_name = "multipages"    
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting queryset of CourseMultiPageListView of superadmin: {e}")
            return self.queryset
        
class CourseMultiPageDetailView(BaseCourseMultiPageView, DetailView):
    template_name = "education_company/multipage/detail.html"
    context_object_name = "multipage"

    def get_object(self):
        try:
            current_company = self.get_current_company()
            return get_object_or_404(self.model, company = current_company, slug = self.kwargs.get("multipage_slug"))
        
        except Http404:
            messages.error(self.request, "Invalid course for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of CourseMultipageDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object
        
        context[self.context_object_name] = self.object
        return context
        
    def get_current_course(self):
        try:
            course_slug = self.kwargs.get('course_slug')
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Course")
            return redirect(self.redirect_url)        
    

class UpdateCourseMultiPageView(BaseCourseMultiPageView, UpdateView):    
    form_class = CourseMultiPageDescriptionForm
    template_name = "education_company/multipage/update.html"
    context_object_name = "multipage"    

    def get_object(self):
        try:
            company_slug = self.kwargs.get('slug')
            multipage_slug = self.kwargs.get('multipage_slug')            
            
            return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)
        
        except Http404:
            messages.error(self.request, "Invalid course multipage object")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            self.object = self.get_object()
            context[self.context_object_name] = self.object
            
            company = self.get_current_company()

            context["programs"] = Program.objects.filter(company = company).order_by("-updated")            
            context["course_details"] = CourseDetail.objects.filter(company = company, course__program__slug = self.object.slider_course_program_slug).order_by("-updated")
            context["courses"] = Course.objects.filter(company = company).order_by("-updated")
            context["tags"] = MetaTag.objects.all().order_by("-updated")
            context["states"] = UniqueState.objects.all().order_by("-updated")

        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateMultiPageView of superadmin: {e}")
        
        return context        
        
    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:update_course_multipage', kwargs = {"slug": self.kwargs.get('slug'), "multipage_slug": self.kwargs.get('multipage_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateMultiPageView of superadmin: {e}")
            return self.redirect_url
        
        
    def post(self, request, *args, **kwargs):
        try:            
            form = self.get_form()

            title = clean_string(request.POST.get('title'))
            sub_title = request.POST.get('sub_title')

            course_slug = clean_string(request.POST.get("course"))

            summary = request.POST.get("summary")
            
            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")
            course_region = request.POST.get("course_region")
            available_states = request.POST.getlist("available_states")

            slider_course_details = [item.strip() for item in request.POST.getlist("course_details", [])]

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None
            course_region = course_region.strip() if course_region else None
            available_states = [state.strip() for state in available_states if state.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company or company.type.name != "Education" :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Title": title,
                "Course": course_slug,
                "summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            if course_region != "all" and len(available_states) < 1:
                messages.error(request, "Failed! Selected 'Selected States' for course region without providing any available state")
                return redirect(self.get_redirect_url())

            course = self.get_course(course_slug)

            if not course:
                messages.error(request, "Failed! Invalid Course")
                return redirect(self.get_redirect_url())
                
            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            updating_meta_tags = []
            with transaction.atomic():

                multipage = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                multipage.title = title
                multipage.sub_title = sub_title
                multipage.course = course
                multipage.summary = summary

                multipage.description = description

                multipage.meta_title = meta_title
                multipage.meta_description = meta_description

                multipage.url_type = url_type
                multipage.course_region = course_region

                multipage.vertical_title = vertical_title
                multipage.horizontal_title = horizontal_title
                multipage.table_title = table_title
                multipage.bullet_title = bullet_title                
                multipage.timeline_title = timeline_title                

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:
                        assigning_value = True

                    setattr(multipage, key, assigning_value)
                
                multipage.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                    "text_editors": self.handle_text_editors,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, title)
                    getattr(multipage, field).set(objects)                    

                multipage.save()

                meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                multipage.meta_tags.set(meta_tag_objects)

                multipage.available_states.clear()
                available_states_objs = UniqueState.objects.all()
                if course_region != "all":
                    available_states_objs = UniqueState.objects.filter(slug__in = available_states)
                    
                multipage.available_states.set(available_states_objs)

                slider_course_objs = CourseDetail.objects.filter(slug__in = slider_course_details)
                multipage.slider_courses.set(slider_course_objs)

                messages.success(request, "Success! Updated course multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteCourseMultiPageView(BaseCourseMultiPageView, View):
    def get_object(self):
        multipage_slug = self.kwargs.get('multipage_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = multipage_slug, company__slug = company_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            course_name = self.object.title
            self.object.delete()

            messages.success(request, f"Success! Removed course multipage of: {course_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Course Multipage")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteCourseMultiPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class BaseEducationBannerView(BaseEducationCompanyView, View):
    model = Banner

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:education_banners', kwargs ={"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseBannerView: {e}")

        return reverse_lazy('superadmin:home')

    def get_redirect_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["education_banner_page"] = True
        return context


class EducationBannerListView(BaseEducationBannerView, ListView):
    context_object_name = "banners"
    template_name = "education_company/banner/list.html"

    def get_queryset(self):
        return Banner.objects.filter(company__slug = self.kwargs.get("slug"))


class CreateEducationBannerView(BaseEducationBannerView, CreateView):
    template_name = "education_company/banner/add.html"
    fields = ["company", "image", "title", "description", "link"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_banner_page"] = True
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

            if not company:
                messages.error(request, "Failed! Invalid Education Company.")
                return self.get_redirect_url()
            
            image = request.FILES.get("image" "")
            title = clean_string(request.POST.get("title", ""))
            description = clean_string(request.POST.get("description", ""))
            link = clean_string(request.POST.get("link", ""))

            required_fields = {
                "Title": title, "Description": description,
                "Image": image, "Link": link
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required.")
                    return redirect(self.get_redirect_url())

            if Banner.objects.filter(title = title, company = company).exists():
                messages.warning(request, f"Failed! Banner with similar heading already exists.")
                return redirect(self.get_redirect_url())
                
            Banner.objects.create(
                company = company, title = title, description = description,
                image = image, link = link
            )
            messages.success(request, "Success! Banner Created.")
            return redirect(self.get_success_url())

        except Exception as e:
            messages.error(request, "Failed! An unexpected error occurred.")
            logger.exception(f"Error in CreateEducationBannerView of superadmin :{e}")

        return self.get_redirect_url()
    

class UpdateEducationBannerView(BaseEducationBannerView, UpdateView):
    fields = ["image", "title", "description", "link"]
    slug_url_kwarg = "banner_slug"

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:update_education_banner', kwargs={'slug': self.kwargs.get('slug'), 'banner_slug': self.kwargs.get('slug_url_kwarg')})
        except Exception as e:
            pass

        return self.get_success_url()

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()
            self.object = self.get_object()

            if not company:
                messages.error(request, "Failed! Invalid Education Company.")
                return self.get_redirect_url()
            
            image = request.FILES.get("image" "")
            title = clean_string(request.POST.get("title", ""))
            description = clean_string(request.POST.get("description", ""))
            link = clean_string(request.POST.get("link", ""))

            required_fields = {
                "Title": title, "Description": description, "Link": link
            }

            if not hasattr(self.object, "image"):
                required_fields["image"] = image            

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required.")
                    return redirect(self.get_redirect_url())
                
            if Banner.objects.filter(title = title, company = company).exclude(pk = self.object.pk).exists():
                messages.warning(request, f"Failed! Banner with similar heading already exists.")
                return redirect(self.get_redirect_url())
                
            self.object.title = title
            self.object.description = description
            self.object.link = link

            if image:
                self.object.image = image

            self.object.save()               
            messages.success(request, "Success! Banner Updated.")
            return redirect(self.get_success_url())

        except Exception as e:
            messages.error(request, "Failed! An unexpected error occurred.")
            logger.exception(f"Error in UpdateEducationBannerView of superadmin :{e}")

        return self.get_redirect_url()


class DeleteEducationBannerView(BaseEducationBannerView, UpdateView):
    slug_url_kwarg = 'banner_slug'

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()
            self.object = self.get_object()

            if not company:
                messages.error(request, "Failed! Invalid Education Company.")
                return self.get_redirect_url()
            
            self.object.delete()
            messages.success(request, "Success! Banner Deleted.")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Banner.")
            return self.get_redirect_url()
    

# Service Company
class BaseServiceCompanyView(BaseCompanyView, View):
    success_url = redirect_url = reverse_lazy('superadmin:home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["company_list_page"] = True
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in getting context data of base service company view: {e}")

        return context


    def get_service_category(self, category_slug):
        try:
            return get_object_or_404(ServiceCategory, slug = category_slug)
        except Http404:
            pass

        return None


    def get_service_sub_category(self, sub_category_slug):
        try:
            return get_object_or_404(ServiceSubCategory, slug = sub_category_slug.strip())
        except Http404:
            pass

        return None
    

class ListServiceView(BaseServiceCompanyView, ListView):
    model = Service
    queryset = model.objects.none()
    context_object_name = "services"
    template_name = "service_company/services/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of list service view of superadmin: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["service_page"] = True

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of list service view: {e}")

        return context
    
class AddServiceView(BaseServiceCompanyView, CreateView):
    model = Service
    fields = ["company", "name", "category", "sub_category", "is_active", "duration", "price"]
    template_name = "service_company/services/add.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_service", kwargs = {'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in getting success url of add service view in superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url in add service view of superadmin: {e}")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["categories"] = ServiceCategory.objects.filter(company = self.get_current_company()).order_by("-updated")
            context["service_page"] = True
        except Exception as e:
            logger.exception(f"Error in getting context data of add service view: {e}")

        return context

    def post(self, request, *args, **kwargs):
        try:
            name = clean_string(request.POST.get("name", ""))
            category_slug = clean_string(request.POST.get("category", ""))
            sub_category_slug = clean_string(request.POST.get("sub_category", ""))
            image = request.FILES.get("image")

            description = clean_string(request.POST.get("description", ""))

            price = clean_string(request.POST.get("price", ""))
            duration = clean_string(request.POST.get("duration", ""))
            is_active = request.POST.get("is_active")

            required_fields = {
                "Service Name": name,
                "Image": image,
                "Category": category_slug,
                "Sub Category": sub_category_slug,                
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            company = self.get_current_company()

            if not company:
                messages.error(request, "Failed! Invalid company")
                return redirect(self.redirect_url)

            category = self.get_service_category(category_slug)

            if not category:
                messages.error(request, "Failed! Invalid Category")
                return redirect(self.get_redirect_url())            
            
            sub_category = self.get_service_sub_category(sub_category_slug)

            if not sub_category:         
                messages.error(request, "Failed! Invalid Sub Category")
                return redirect(self.get_redirect_url())
            
            if Service.objects.filter(company=company, name=name, category=category, sub_category=sub_category).exists():
                messages.warning(request, "Service already exists")
                return redirect(self.get_redirect_url())

            Service.objects.create(
                company = company, name = name, category = category, sub_category = sub_category, 
                description = description, price = price, duration = duration, 
                is_active = bool(is_active), image = image
                )
            
            messages.success(request, "Success! Service Created.")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in adding service in add service view of superadmin: {e}")
            messages.error(request, "Server Error")
            return redirect(self.get_redirect_url())
        

class UpdateServiceView(BaseServiceCompanyView, UpdateView):
    model = Service
    fields = ["name", "category", "sub_category", "description", "price", "duration", "is_active"]
    success_url = redirect_url = reverse_lazy("superadmin:home")
    template_name = "service_company/services/edit.html"

    def get_success_url(self):
        try:  
            return reverse_lazy("superadmin:services", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting succes url of UpdateServiceView of superadmin app: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of UpdateServiceView of superadmin app: {e}")
            return self.redirect_url
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            context["categories"] = ServiceCategory.objects.filter(company = current_company).order_by("-updated")
            context["sub_categories"] = ServiceSubCategory.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateServiceView of superadmin app: {e}")
        
        return context
        
    def get_object(self):
        try:
            current_company = self.get_current_company()
            return get_object_or_404(self.model, company = current_company, slug = self.kwargs.get("service_slug"))
        
        except Http404:
            messages.error(self.request, "Invalid service")
            return redirect(self.get_redirect_url())        

    def post(self, request, *args, **kwargs):
        try:            
            name = clean_string(request.POST.get("name", ""))
            image = request.FILES.get("image")
            category_slug = clean_string(request.POST.get("category", ""))
            sub_category_slug = clean_string(request.POST.get("sub_category", ""))

            description = clean_string(request.POST.get("description", ""))

            price = clean_string(request.POST.get("price", ""))
            duration = clean_string(request.POST.get("duration", ""))
            is_active = request.POST.get("is_active")
            
            service = self.get_object()

            required_fields = {
                "Service Name": name,
                "Image": image if not service.image else service.image,
                "Category": category_slug,
                "Sub Category": sub_category_slug,                
            }


            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            category = self.get_service_category(category_slug)

            if not category:
                messages.error(request, "Failed! Invalid Category")
                return redirect(self.get_redirect_url())            
            
            sub_category = self.get_service_sub_category(sub_category_slug)

            if not sub_category:         
                messages.error(request, "Failed! Invalid Sub Category")
                return redirect(self.get_redirect_url())
            
            similar_service = self.model.objects.filter(
                company = service.company, name = name, category = category, sub_category = sub_category
                ).first()

            if similar_service and similar_service != service:           
                messages.warning(request, "Similar service already exists")
                return redirect(self.get_redirect_url())

            service.name = name

            if image:
                service.image = image

            service.category = category
            service.sub_category = sub_category
            service.description = description
            service.price = price
            service.duration = duration
            service.is_active = bool(is_active)
            service.save()
            
            messages.success(request, "Success! Service Updated")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in UpdateServiceView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")
            return redirect(self.get_redirect_url())
        

class RemoveServiceView(BaseServiceCompanyView, View):
    model = Service
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:services", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveServiceView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveServiceView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("category_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted service")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid service")

        except Exception as e:
            logger.exception(f"Error in RemoveServiceView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ListServiceCategoryView(BaseServiceCompanyView, ListView):
    model = ServiceCategory
    queryset = model.objects.none()
    context_object_name = "categories"
    template_name = "service_company/categories/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of list service category view of superadmin: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["service_category_page"] = True

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of list service category view: {e}")

        return context
    

class AddServiceCategoryView(BaseServiceCompanyView, CreateView):
    model = ServiceCategory
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:service_categories", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def post(self, request, *args, **kwargs):
        try:
            current_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                product, created = self.model.objects.get_or_create(company = current_company, name = name)

                if created:
                    messages.success(request, "Success! Service category created.")
                    return redirect(self.get_success_url())

                else:
                    messages.warning(request, "Service category already exists.")
            
            else:
                messages.error(request, "Service category name is required.")            
        
        except Exception as e:
            logger.exception(f"Error in creating service category: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class UpdateServiceCategoryView(BaseServiceCompanyView, UpdateView):
    model = ServiceCategory
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:  
            return reverse_lazy("superadmin:service_categories", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting succes url of UpdateServiceCategoryView of superadmin app: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of UpdateServiceCategoryView of superadmin app: {e}")
            return self.redirect_url
        
    def get_object(self):
        try:
            current_company = self.get_current_company()
            return get_object_or_404(self.model, company = current_company, slug = self.kwargs.get("category_slug"))
        
        except Http404:
            messages.error(self.request, "Invalid service category")
            return redirect(self.get_redirect_url())        

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            if not name:
                messages.error(request, f"Failed! Name of service category is required")
                return redirect(self.get_redirect_url())
            
            category = self.get_object()

            updating_name = name if name else category.name
            
            if self.model.objects.filter(company = category.company, name = updating_name).exists():
                messages.warning(request, "Category with the given name already exists")
                return redirect(self.get_redirect_url())
            
            category.name = updating_name
            category.save()

            messages.success(request, "Success! Service category updated.")
            return redirect(self.get_success_url())                                                       
        
        except Exception as e:
            logger.exception(f"Error in updating service category by superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class RemoveServiceCategoryView(BaseServiceCompanyView, View):
    model = ServiceCategory
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:service_categories", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveServiceCategoryView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveServiceCategoryView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("category_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted service category")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid service category")

        except Exception as e:
            logger.exception(f"Error in RemoveServiceCategoryView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class ListServiceSubCategoryView(BaseServiceCompanyView, ListView):
    model = ServiceSubCategory
    queryset = model.objects.none()
    context_object_name = "sub_categories"
    template_name = "service_company/sub_categories/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of list service sub category view of superadmin: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            company = self.get_current_company()
            context["current_company"] = company
            context["service_sub_category_page"] = True
            context["categories"] = ServiceCategory.objects.filter(company = company).order_by("-updated")

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of list service sub category view: {e}")

        return context
    

class ListServiceEnquiryView(BaseServiceCompanyView, ListView):
    model = ServiceEnquiry
    queryset = model.objects.none()
    context_object_name = "enquiries"
    template_name = "service_company/enquiries/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListServiceEnquiryView of superadmin: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["service_enquiry_page"] = True

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of ListServiceEnquiryView: {e}")

        return context
    

class AddServiceSubCategoryView(BaseServiceCompanyView, CreateView):
    model = ServiceSubCategory
    fields = ["name", "category"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:service_sub_categories", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def post(self, request, *args, **kwargs):
        try:
            current_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None

            category_slug = request.POST.get("category")

            if not category_slug or not name:
                error_msg = "Name of service sub category is required."
                if not category_slug:
                    error_msg = "Service category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.get_redirect_url())
            
            category = get_object_or_404(ServiceCategory, slug = category_slug)
            
            sub_category, created = self.model.objects.get_or_create(company = current_company, name = name, category = category)

            if created:
                messages.success(request, "Success! Service sub category created.")
                return redirect(self.get_success_url())

            else:
                messages.warning(request, "Service sub category already exists.")

        except Http404:
            messages.error(request, "Invalid service category")                                    
        
        except Exception as e:
            logger.exception(f"Error in creating service sub category by superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class UpdateServiceSubCategoryView(BaseServiceCompanyView, UpdateView):
    model = ServiceSubCategory
    fields = ["name", "category"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:  
            return reverse_lazy("superadmin:service_sub_categories", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting succes url of UpdateServiceSubCategoryView of superadmin app: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of UpdateServiceSubCategoryView of superadmin app: {e}")
            return self.redirect_url

    def get_object(self):
        try:
            current_company = self.get_current_company()
            return get_object_or_404(self.model, company = current_company, slug = self.kwargs.get("sub_category_slug"))
        
        except Http404:
            messages.error(self.request, "Invalid service sub category")
            return redirect(self.get_redirect_url())        

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            category_slug = request.POST.get("category")

            if not category_slug or not name:
                error_msg = "Name of service sub category is required."
                if not category_slug:
                    error_msg = "Service category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.get_redirect_url())
            
            category = get_object_or_404(ServiceCategory, slug = category_slug)
            
            sub_category = self.get_object()

            updating_name = name if name else sub_category.name
            updating_category = category if category else sub_category.category
            
            if self.model.objects.filter(company = sub_category.company, name = updating_name, category = updating_category).exists():
                messages.warning(request, "Sub category with the given data already exists")
                return redirect(self.get_redirect_url())
            
            sub_category.name = updating_name
            sub_category.category = updating_category
            sub_category.save()

            messages.success(request, "Success! Service sub category updated.")
            return redirect(self.get_success_url())                                                       
        
        except Exception as e:
            logger.exception(f"Error in updating service sub category by superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class RemoveServiceSubCategoryView(BaseServiceCompanyView, View):
    model = ServiceSubCategory
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:service_sub_categories", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveServiceSubCategoryView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveServiceSubCategoryView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("sub_category_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted service sub category")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid service sub category")

        except Exception as e:
            logger.exception(f"Error in RemoveServiceSubCategoryView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    
# Service FAQ
class ServiceFaqBaseView(BaseServiceCompanyView):
    model = ServiceFaq
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:service_faqs', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseServiceFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()
        
    def get_service(self, service_slug):
        try:            
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context["service_faq_page"] = True

        return context


class AddServiceFaqView(ServiceFaqBaseView, CreateView):    
    fields = ["company", "service", "question", "answer", "dynamic_place_rendering"]
    template_name = "service_company/faqs/add.html"    

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_service_faq', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddServiceFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()        
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["add_service_faq_page"] = True
        context["categories"] = ServiceCategory.objects.filter(company__slug = company_slug).order_by("-updated")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            service_slug = self.request.POST.get('service')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

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
                    return redirect(self.get_redirect_url())

            company = self.get_current_company()
            service = self.get_service(service_slug)

            if not company or not service:
                invalid_msg = ""
                
                if not company:
                    invalid_msg = "Invalid Service Company"
                else:
                    invalid_msg = "Invalid Service"

                messages.error(request, invalid_msg)
                return redirect(self.get_redirect_url())
            
            dynamic_place_rendering = True if dynamic_place_rendering else False

            ServiceFaq.objects.update_or_create(
                company = company, service = service, question = question, dynamic_place_rendering = dynamic_place_rendering, 
                defaults={"answer": answer}
                )

            messages.success(request, f"Success! Created FAQ object for service: {service.name}")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in get function of AddServiceFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class ListServiceFaqView(ServiceFaqBaseView, ListView):
    model = ServiceFaq
    template_name = "service_company/faqs/list.html"
    queryset = model.objects.none()
    context_object_name = "faqs"

    def get_queryset(self):
        try:
            company_slug = self.kwargs.get(self.slug_url_kwarg)
            company = get_object_or_404(Company, slug = company_slug, type__name = "Service")
            return self.model.objects.filter(company = company)
            
        except Http404:
            messages.error(self.request, "Invalid service company")
            return redirect(self.redirect_url)


class UpdateServiceFaqView(ServiceFaqBaseView, UpdateView):
    model = ServiceFaq
    fields = ["service", "question", "answer", "dynamic_place_rendering"]
    template_name = "service_company/faqs/update.html"
    context_object_name = "faq"

    def get_service(self, service_slug):
        try:
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            return None
        
    def get_object(self):
        company_slug = self.kwargs.get('slug') 
        service_faq_slug = self.kwargs.get('service_faq_slug') 

        self.object = get_object_or_404(ServiceFaq, company__slug = company_slug, slug = service_faq_slug)

        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["update_service_faq_page"] = True

        context["categories"] = ServiceCategory.objects.filter(company__slug = company_slug).order_by("-updated")
        context["sub_categories"] = ServiceSubCategory.objects.filter(company__slug = company_slug, category = self.object.service.category).order_by("-updated")
        context["services"] = Service.objects.filter(company__slug = company_slug, category = self.object.service.category, sub_category = self.object.service.sub_category).order_by("-updated")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            service_slug = self.request.POST.get('service')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

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

            dynamic_place_rendering = True if dynamic_place_rendering else False

            similar_faq = self.model.objects.filter(
                company = self.object.company, service = service, question = question, answer = answer, dynamic_place_rendering = dynamic_place_rendering
                ).first()

            if similar_faq:
                if similar_faq.slug == self.object.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar service FAQ already exists")
                return redirect(self.get_redirect_url())

            self.object.service = service
            self.object.question = question
            self.object.answer = answer
            self.object.dynamic_place_rendering = dynamic_place_rendering
            self.object.save()

            messages.success(request, f"Success! Updated FAQ")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid service FAQ object")

        except Exception as e:
            logger.exception(f"Error in get function of UpdateServiceFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteServiceFaqView(ServiceFaqBaseView, View):
    model = ServiceFaq
        
    def get_object(self):
        faq_slug = self.kwargs.get('service_faq_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = faq_slug, company__slug = company_slug)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            service_name = self.object.service.name
            self.object.delete()

            messages.success(request, f"Success! Removed service FAQ object of: {service_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Service FAQ")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteServiceFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseServiceEnquiryView(BaseServiceCompanyView, View):
    model = ServiceEnquiry
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = self.get_current_company()
            context["service_enquiry_page"] = True

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseServiceEnquiryView: {e}")

        return context

class ListServiceEnquiryView(BaseServiceEnquiryView, ListView):
    queryset = ServiceEnquiry.objects.none()
    context_object_name = "enquiries"
    template_name = "service_company/enquiries/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListServiceEnquiryView of superadmin: {e}")
            return self.queryset


class DeleteServiceEnquiryView(BaseServiceEnquiryView, View):
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:service_enquiries', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of DeleteServiceEnquiryView of superadmin app: {e}")
            return self.success_url

    def get_redirect_url(self):
        return self.get_success_url()
            

    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(ServiceEnquiry, company__slug = self.kwargs.get(self.slug_url_kwarg), slug = self.kwargs.get('enquiry_slug'))
            self.object.delete()

            messages.success(request, "Success! Delete Service Enquiry")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Service Enquiry")
            return redirect(self.get_redirect_url())


# Service Detail
class BaseServiceDetailView(BaseServiceCompanyView):
    model = ServiceDetail
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["service_detail_page"] = True
            
            current_company = self.get_current_company()

            context["current_company"] = current_company

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseServiceDetailView of superadmin: {e}")
        
        return context    

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:service_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseServiceDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseServiceDetailView of superadmin: {e}")
            return self.redirect_url
        
    def get_service(self, service_slug):
        try:
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            messages.error(self.request, "Invalid Service")
            return redirect(self.get_redirect_url())
        
    def get_current_service(self):
        try:
            service_slug = self.kwargs.get('service_slug')   
            service =  get_object_or_404(Service, slug = service_slug)
            return service
        except Http404:
            messages.error(self.request, "Failed! Invalid Service")
            return redirect(self.redirect_url)

    def get_object(self):
        try:
            current_company = self.get_current_company()
            # current_service = self.get_current_service()
            detail_page_slug = self.kwargs.get("detail_page_slug")
            return get_object_or_404(self.model, company = current_company, slug = detail_page_slug)
        
        except Http404:
            messages.error(self.request, "Invalid service for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of BaseServiceDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, service):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    ServiceFeature.objects.filter(company = company, service = service).delete()

                    features = [ServiceFeature(company=company, service=service, feature=feature) for feature in features_list]
                    ServiceFeature.objects.bulk_create(features)

                    feature_objs = ServiceFeature.objects.filter(company = company, service = service)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseServiceDetailView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, service):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                ServiceVerticalTab.objects.filter(company = company, service = service).delete()
                ServiceVerticalBullet.objects.filter(company = company, service = service).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = ServiceVerticalTab.objects.create(
                            company = company,
                            service = service,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [ServiceVerticalBullet(
                                company = company, service = service, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                ServiceVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = ServiceVerticalBullet.objects.filter(company = company, service = service, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)

                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseServiceDetailView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, service):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                ServiceHorizontalTab.objects.filter(company = company, service = service).delete()
                ServiceHorizontalBullet.objects.filter(company = company, service = service).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = ServiceHorizontalTab.objects.create(
                            company = company,
                            service = service,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [ServiceHorizontalBullet(
                                company = company, service = service, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                ServiceHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = ServiceHorizontalBullet.objects.filter(company = company, service = service, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseServiceDetailView: {e}")

        return []
    
    def handle_tables(self, request, company, service):
        try:
            service_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                ServiceTableData.objects.filter(company = company, service = service).delete()
                ServiceTable.objects.filter(company = company, service = service).delete()

                for index, heading in enumerate(heading_list):
                    service_table = ServiceTable.objects.create(
                        company = company, service = service, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [ServiceTableData(
                            company = company, service = service,
                            heading = heading, data = data
                            ) for data in data_list_of_heading]

                    ServiceTableData.objects.bulk_create(table_data_objs )

                    service_table_data_objs = ServiceTableData.objects.filter(company = company, service = service, heading = heading)

                    service_table.datas.set(service_table_data_objs)

                    service_tables.append(service_table)

            return service_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseServiceDetailView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, service):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                ServiceBulletPoint.objects.filter(company = company, service = service).delete()

                if bullet_point_list:
                    bullet_point_objects = [ServiceBulletPoint(
                        company = company, service = service,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    ServiceBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = ServiceBulletPoint.objects.filter(company = company, service = service)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseServiceDetailView: {e}")

        return []

    def handle_timelines(self, request, company, service):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                ServiceTimeline.objects.filter(company = company, service = service).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [ServiceTimeline(
                        company = company, service = service,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    ServiceTimeline.objects.bulk_create(creating_timelines)

                    service_timelines = ServiceTimeline.objects.filter(company = company, service = service)                
                                            
                    return service_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseServiceDetailView: {e}")

        return []


class AddServiceDetailView(BaseServiceDetailView, CreateView):
    form_class = ServiceDetailDescriptionForm
    template_name = "service_company/service_detail/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_service_detail_page"] = True

        current_company = self.get_current_company()        
        context["categories"] = ServiceCategory.objects.filter(company = current_company).order_by("-updated")
        context["tags"] = MetaTag.objects.all().order_by("-updated")
        
        return context

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_service_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddServiceDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddServiceDetailView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            service_slug = request.POST.get('service')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_description = request.POST.get("meta_description")

            meta_tags = request.POST.getlist("meta_tag")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")
            
            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")

            summary = summary.strip() if summary else None
            
            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Service": service_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                }

            service = self.get_service(service_slug)

            updating_meta_tags = []
            with transaction.atomic():
                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                service_detail = self.model.objects.create(
                    company = company, service = service, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, 
                    timeline_title = timeline_title
                )                           

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(service_detail, key, True)

                service_detail.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, service)
                    getattr(service_detail, field).set(objects)

                if meta_tags:
                    meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                    service_detail.meta_tags.set(meta_tag_objects)  

                messages.success(request, "Success! Created service detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddServiceDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ServiceDetailsListView(BaseServiceDetailView, ListView):
    template_name = "service_company/service_detail/list.html"
    queryset = ServiceDetail.objects.none()
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "service_details"        
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting queryset of ServiceDetailsListView of superadmin: {e}")
            return self.queryset


class ServiceDetailView(BaseServiceDetailView, DetailView):
    model = ServiceDetail
    template_name = "service_company/service_detail/detail.html"
    redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "service_detail"

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:service_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function of ServiceDetailView: {e}")
            return self.redirect_url


class UpdateServiceDetailView(BaseServiceDetailView, UpdateView):    
    form_class = ServiceDetailDescriptionForm
    template_name = "service_company/service_detail/update.html"
    context_object_name = "service_detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object()
        current_company = self.get_current_company()        
        context["categories"] = ServiceCategory.objects.filter(company = current_company).order_by("-updated")
        context["sub_categories"] = ServiceSubCategory.objects.filter(company = current_company, category = self.object.service.category).order_by("-updated")
        context["services"] = Service.objects.filter(company = current_company, category = self.object.service.category, sub_category = self.object.service.sub_category).order_by("-updated")
        context["tags"] = MetaTag.objects.all().order_by("-updated")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_service_details', kwargs = {"slug": self.kwargs.get('slug'), "detail_page_slug": self.kwargs.get('detail_page_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateServiceDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateServiceDetailView of superadmin: {e}")
            return self.redirect_url


    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            service_slug = request.POST.get('service')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_description = request.POST.get("meta_description")

            meta_tags = request.POST.getlist("meta_tag")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")   

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Service": service_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                }

            service = self.get_service(service_slug)

            updating_meta_tags = []
            with transaction.atomic():

                service_detail = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                service_detail.service = service
                service_detail.summary = summary

                service_detail.description = description

                service_detail.meta_title = meta_title
                service_detail.meta_description = meta_description

                service_detail.vertical_title = vertical_title
                service_detail.horizontal_title = horizontal_title
                service_detail.table_title = table_title
                service_detail.bullet_title = bullet_title                
                service_detail.timeline_title = timeline_title                

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:                    
                        assigning_value = True

                    setattr(service_detail, key, assigning_value)
                
                service_detail.save()                             

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, service)
                    getattr(service_detail, field).set(objects)

                service_detail.save()

                meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                service_detail.meta_tags.set(meta_tag_objects)

                messages.success(request, "Success! Updated service detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateServiceDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteServiceDetailPageView(BaseServiceDetailView, View):
    def get_object(self, **kwargs):
        company_slug = self.kwargs.get('slug')
        detail_page_slug = self.kwargs.get('detail_page_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = detail_page_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            service_name = self.object.service.name
            self.object.delete()

            messages.success(request, f"Success! Removed service detail page of: {service_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Service Detail")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteServiceDetailPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseServiceMultiPageView(BaseServiceCompanyView, View):
    model = ServiceMultiPage
    success_url = redirect_url = reverse_lazy('superadmin:home')        
        
    def get_categories(self):
        return ServiceCategory.objects.filter(company = self.current_company).order_by("-updated")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["service_multipage"] = True
            
            self.current_company = self.get_current_company()
            
            context["current_company"] = self.current_company            
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseServiceMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:service_multipages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseServiceMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseServiceMultiPageView of superadmin: {e}")
            return self.redirect_url
        
    def get_service(self, service_slug):
        try:
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            messages.error(self.request, "Invalid Service")
            return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, title):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    ServiceMultiPageFeature.objects.filter(company = company, title = title).delete()

                    features = [ServiceMultiPageFeature(company=company, title=title, feature=feature) for feature in features_list]
                    ServiceMultiPageFeature.objects.bulk_create(features)

                    feature_objs = ServiceMultiPageFeature.objects.filter(company = company, title = title)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseServiceMultiPageView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, title):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                ServiceMultiPageVerticalTab.objects.filter(company = company, title = title).delete()
                ServiceMultiPageVerticalBullet.objects.filter(company = company, title = title).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = ServiceMultiPageVerticalTab.objects.create(
                            company = company,
                            title = title,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [ServiceMultiPageVerticalBullet(
                                company = company, title = title, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                ServiceMultiPageVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = ServiceMultiPageVerticalBullet.objects.filter(company = company, title = title, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)


                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseServiceMultiPageView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, title):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                ServiceMultiPageHorizontalTab.objects.filter(company = company, title = title).delete()
                ServiceMultiPageHorizontalBullet.objects.filter(company = company, title = title).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = ServiceMultiPageHorizontalTab.objects.create(
                            company = company,
                            title = title,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [ServiceMultiPageHorizontalBullet(
                                company = company, title = title, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                ServiceMultiPageHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = ServiceMultiPageHorizontalBullet.objects.filter(company = company, title = title, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseServiceMultiPageView: {e}")

        return []
    
    def handle_tables(self, request, company, title):
        try:
            service_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                ServiceMultiPageTableData.objects.filter(company = company, title = title).delete()
                ServiceMultiPageTable.objects.filter(company = company, title = title).delete()

                for index, heading in enumerate(heading_list):
                    service_table = ServiceMultiPageTable.objects.create(
                        company = company, title = title, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [ServiceMultiPageTableData(
                            company = company, title = title,
                            heading = heading, data = data
                            ) for data in data_list_of_heading if data]

                    ServiceMultiPageTableData.objects.bulk_create(table_data_objs )

                    service_table_data_objs = ServiceMultiPageTableData.objects.filter(company = company, title = title, heading = heading)

                    service_table.datas.set(service_table_data_objs)
                    service_tables.append(service_table)

            return service_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseServiceMultiPageView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, title):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                ServiceMultiPageBulletPoint.objects.filter(company = company, title = title).delete()

                if bullet_point_list:
                    bullet_point_objects = [ServiceMultiPageBulletPoint(
                        company = company, title = title,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    ServiceMultiPageBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = ServiceMultiPageBulletPoint.objects.filter(company = company, title = title)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseServiceMultiPageView: {e}")

        return []

    def handle_timelines(self, request, company, title):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                ServiceMultiPageTimeline.objects.filter(company = company, title = title).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [ServiceMultiPageTimeline(
                        company = company, title = title,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    ServiceMultiPageTimeline.objects.bulk_create(creating_timelines)

                    service_timelines = ServiceMultiPageTimeline.objects.filter(company = company, title = title)                
                                            
                    return service_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseServiceMultiPageView: {e}")

        return []

    def handle_faqs(self, request, company, title):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]                        

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                ServiceMultiPageFaq.objects.filter(company = company, title = title).delete()
                
                if question_list and answer_list:
                    creating_faqs = [ServiceMultiPageFaq(
                        company = company, title = title,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    ServiceMultiPageFaq.objects.bulk_create(creating_faqs)

                    service_faqs = ServiceMultiPageFaq.objects.filter(company = company, title = title)                
                                            
                    return service_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of BaseServiceMultiPageView: {e}")

        return []


    def handle_text_editors(self, request, company, title):
        try:
            text_editor_title_list = [title.strip() for title in request.POST.getlist("text_editor_title")]
            content_list = request.POST.getlist("text_editor_content")

            if len(text_editor_title_list) != len(content_list):
                raise ValueError("The number of titles does not match the number of contents.")

            with transaction.atomic():
                ServiceTextEditor.objects.filter(company = company, title = title).delete()
                
                if text_editor_title_list and content_list:
                    creating_text_editors = [ServiceTextEditor(
                        company = company, title = title,
                        text_editor_title = text_editor_title, content = content
                        ) for text_editor_title, content in zip(text_editor_title_list, content_list) if text_editor_title and content]

                    ServiceTextEditor.objects.bulk_create(creating_text_editors)

                    service_text_editors = ServiceTextEditor.objects.filter(company = company, title = title)                
                                            
                    return service_text_editors
        except Exception as e:
            logger.exception(f"Error in handle_text_editors function of BaseServiceMultiPageView: {e}")

        return []


class AddServiceMultiPageView(BaseServiceMultiPageView, CreateView):
    form_class = ServiceMultiPageDescriptionForm
    template_name = "service_company/multipage/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_company = self.get_current_company()

        context["categories"] = ServiceCategory.objects.filter(company = current_company).order_by("-updated")
        context["services"] = Service.objects.filter(company = current_company).order_by("-updated")
        context["tags"] = MetaTag.objects.all().order_by("-updated")
        context["states"] = UniqueState.objects.all().order_by("-updated")

        return context

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_service_multipage', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddServiceMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddServiceMultiPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()

            form = self.get_form()

            title = clean_string(request.POST.get("title", ""))
            sub_title = request.POST.get("sub_title", "")
            service_slug = clean_string(request.POST.get('service', ""))

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")
            service_region = request.POST.get("service_region")
            available_states = request.POST.getlist("available_states")

            slider_service_details = [item.strip() for item in request.POST.getlist("service_details", [])]

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None
            service_region = service_region.strip() if service_region else None
            available_states = [state.strip() for state in available_states if state.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = current_company

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Title": title,
                "Service": service_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            if service_region != "all" and len(available_states) < 1:
                messages.error(request, "Failed! Selected 'Selected States' for service region without providing any available state")
                return redirect(self.get_redirect_url())

            service = self.get_service(service_slug)

            if not service:
                messages.error(request, "Failed! Invalid service")
                return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }
            
            updating_meta_tags = []
            with transaction.atomic():
                if self.model.objects.filter(company = company, title = title).exists():
                    messages.error(request, "Multipage with this title already exists")
                    return redirect(self.get_redirect_url())
                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                service_multi_page = self.model.objects.create(
                    company = company, title = title, sub_title = sub_title, service = service, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    url_type = url_type, service_region = service_region,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, 
                    timeline_title = timeline_title
                )

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(service_multi_page, key, True)
                
                service_multi_page.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                    "text_editors": self.handle_text_editors,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, title)
                    getattr(service_multi_page, field).set(objects)

                if meta_tags:
                    meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                    service_multi_page.meta_tags.set(meta_tag_objects)

                available_states_objs = UniqueState.objects.all()
                if service_region != "all":
                    available_states_objs = UniqueState.objects.filter(slug__in = available_states)

                service_multi_page.available_states.set(available_states_objs)

                slider_service_objs = ServiceDetail.objects.filter(slug__in = slider_service_details)
                service_multi_page.slider_services.set(slider_service_objs)

                messages.success(request, "Success! Created service multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddServiceMultiPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ServiceMultiPageListView(BaseServiceMultiPageView, ListView):
    template_name = "service_company/multipage/list.html"
    queryset = ServiceMultiPage.objects.none()
    context_object_name = "multipages"    
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting queryset of ServiceMultiPageListView of superadmin: {e}")
            return self.queryset
        
class ServiceMultiPageDetailView(BaseServiceMultiPageView, DetailView):
    template_name = "service_company/multipage/detail.html"
    context_object_name = "multipage"

    def get_object(self):
        try:
            current_company = self.get_current_company()
            # current_service = self.get_current_service()
            return get_object_or_404(self.model, company = current_company, slug = self.kwargs.get("multipage_slug"))
        
        except Http404:
            messages.error(self.request, "Invalid service for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of ServiceMultipageDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object
        
        context[self.context_object_name] = self.object
        return context
        
    def get_current_service(self):
        try:
            service_slug = self.kwargs.get('service_slug')
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Service")
            return redirect(self.redirect_url)        
    

class UpdateServiceMultiPageView(BaseServiceMultiPageView, UpdateView):    
    form_class = ServiceMultiPageDescriptionForm
    template_name = "service_company/multipage/update.html"
    context_object_name = "multipage"    

    def get_object(self):
        try:
            company_slug = self.kwargs.get('slug')
            multipage_slug = self.kwargs.get('multipage_slug')            
            
            return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)
        
        except Http404:
            messages.error(self.request, "Invalid service multipage object")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            self.object = self.get_object()
            context[self.context_object_name] = self.object
            
            company = self.get_current_company()
            
            context["categories"] = ServiceCategory.objects.filter(company = company).order_by("-updated")            
            context["service_details"] = ServiceDetail.objects.filter(
                company = company, service__category__slug = self.object.slider_service_category_slug
                ).order_by("-updated")
            context["services"] = Service.objects.filter(company = company).order_by("-updated")
            context["tags"] = MetaTag.objects.all().order_by("-updated")
            context["states"] = UniqueState.objects.all().order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_redirect_url(self, redirect_slug = None):
        try:
            if not redirect_slug:
                redirect_slug = self.kwargs.get('multipage_slug')
            return reverse_lazy('superadmin:update_service_multipage', kwargs = {"slug": self.kwargs.get('slug'), "multipage_slug": redirect_slug})
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateServiceMultiPageView of superadmin: {e}")
            return self.success_url
        
    def post(self, request, *args, **kwargs):
        redirect_slug = None
        try: 
            form = self.get_form()            
            
            title = clean_string(request.POST.get('title', ''))
            sub_title = request.POST.get('sub_title', '')
            service_slug = clean_string(request.POST.get('service', ''))

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")
            service_region = request.POST.get("service_region")
            available_states = request.POST.getlist("available_states")

            slider_service_details = [item.strip() for item in request.POST.getlist("service_details", [])]

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None
            service_region = service_region.strip() if service_region else None
            available_states = [state.strip() for state in available_states if state.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Title": title,
                "Service": service_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                
            if service_region != "all" and len(available_states) < 1:
                messages.error(request, "Failed! Selected 'Selected States' for service region without providing any available state")
                return redirect(self.get_redirect_url())

            service = self.get_service(service_slug)

            if not service:
                messages.error(request, "Failed! Invalid service")
                return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }


            updating_meta_tags = []
            with transaction.atomic():

                self.object = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                self.object.title = title
                self.object.sub_title = sub_title
                self.object.service = service
                self.object.summary = summary

                self.object.description = description

                self.object.meta_title = meta_title
                self.object.meta_description = meta_description

                self.object.url_type = url_type
                self.object.service_region = service_region

                self.object.vertical_title = vertical_title
                self.object.horizontal_title = horizontal_title
                self.object.table_title = table_title
                self.object.bullet_title = bullet_title                
                self.object.timeline_title = timeline_title                

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:
                        assigning_value = True

                    setattr(self.object, key, assigning_value)
                
                self.object.save()

                redirect_slug = self.object.slug

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                    "text_editors": self.handle_text_editors,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, title)
                    getattr(self.object, field).set(objects)

                self.object.save()

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)                
                self.object.meta_tags.set(meta_tag_objs)

                self.object.available_states.clear()
                available_states_objs = UniqueState.objects.all()
                if service_region != "all":
                    available_states_objs = UniqueState.objects.filter(slug__in = available_states)
                    
                self.object.available_states.set(available_states_objs)
                
                slider_service_objs = ServiceDetail.objects.filter(slug__in = slider_service_details)
                self.object.slider_services.set(slider_service_objs)

                messages.success(request, "Success! Updated service multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteServiceMultiPageView(BaseServiceMultiPageView, View):
    def get_object(self, **kwargs):
        company_slug = self.kwargs.get('slug')
        multipage_slug = self.kwargs.get('multipage_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            service_name = self.object.service.name
            self.object.delete()

            messages.success(request, f"Success! Removed service multipage of: {service_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Service Multipage")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteServiceMultiPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseServiceBannerView(BaseServiceCompanyView, View):
    model = Banner

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:service_banners', kwargs ={"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseBannerView: {e}")

        return reverse_lazy('superadmin:home')

    def get_redirect_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_banner_page"] = True
        return context


class ServiceBannerListView(BaseServiceBannerView, ListView):
    context_object_name = "banners"
    template_name = "service_company/banner/list.html"

    def get_queryset(self):
        return Banner.objects.filter(company__slug = self.kwargs.get("slug"))


class CreateServiceBannerView(BaseServiceBannerView, CreateView):
    template_name = "service_company/banner/add.html"
    fields = ["company", "image", "title", "description", "link"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_banner_page"] = True
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

            if not company:
                messages.error(request, "Failed! Invalid Service Company.")
                return self.get_redirect_url()
            
            image = request.FILES.get("image" "")
            title = clean_string(request.POST.get("title", ""))
            description = clean_string(request.POST.get("description", ""))
            link = clean_string(request.POST.get("link", ""))

            required_fields = {
                "Title": title, "Description": description,
                "Image": image, "Link": link
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required.")
                    return redirect(self.get_redirect_url())

            if Banner.objects.filter(title = title, company = company).exists():
                messages.warning(request, f"Failed! Banner with similar heading already exists.")
                return redirect(self.get_redirect_url())
                
            Banner.objects.create(
                company = company, title = title, description = description,
                image = image, link = link
            )
            messages.success(request, "Success! Banner Created.")
            return redirect(self.get_success_url())

        except Exception as e:
            messages.error(request, "Failed! An unexpected error occurred.")
            logger.exception(f"Error in CreateServiceBannerView of superadmin :{e}")

        return self.get_redirect_url()
    

class UpdateServiceBannerView(BaseServiceBannerView, UpdateView):
    fields = ["image", "title", "description", "link"]
    slug_url_kwarg = "banner_slug"

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:update_service_banner', kwargs={'slug': self.kwargs.get('slug'), 'banner_slug': self.kwargs.get('slug_url_kwarg')})
        except Exception as e:
            pass

        return self.get_success_url()

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()
            self.object = self.get_object()

            if not company:
                messages.error(request, "Failed! Invalid Service Company.")
                return self.get_redirect_url()
            
            image = request.FILES.get("image" "")
            title = clean_string(request.POST.get("title", ""))
            description = clean_string(request.POST.get("description", ""))
            link = clean_string(request.POST.get("link", ""))

            required_fields = {
                "Title": title, "Description": description, "Link": link
            }

            if not hasattr(self.object, "image"):
                required_fields["image"] = image            

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required.")
                    return redirect(self.get_redirect_url())
                
            if Banner.objects.filter(title = title, company = company).exclude(pk = self.object.pk).exists():
                messages.warning(request, f"Failed! Banner with similar heading already exists.")
                return redirect(self.get_redirect_url())
                
            self.object.title = title
            self.object.description = description
            self.object.link = link

            if image:
                self.object.image = image

            self.object.save()               
            messages.success(request, "Success! Banner Updated.")
            return redirect(self.get_success_url())

        except Exception as e:
            messages.error(request, "Failed! An unexpected error occurred.")
            logger.exception(f"Error in UpdateServiceBannerView of superadmin :{e}")

        return self.get_redirect_url()


class DeleteServiceBannerView(BaseServiceBannerView, UpdateView):
    slug_url_kwarg = 'banner_slug'

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()
            self.object = self.get_object()

            if not company:
                messages.error(request, "Failed! Invalid Service Company.")
                return self.get_redirect_url()
            
            self.object.delete()
            messages.success(request, "Success! Banner Deleted.")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Banner.")
            return self.get_redirect_url()


# Registration Company
class BaseRegistrationCompanyView(BaseCompanyView, View):
    success_url = redirect_url = reverse_lazy('superadmin:home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["company_list_page"] = True
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))

        except Http404:
            messages.error(self.request, "Invalid Company")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in getting context data of base registration company view: {e}")

        return context

    def get_registration_type(self, registration_type_slug):
        try:
            return get_object_or_404(RegistrationType, slug = registration_type_slug)          
        except Http404:
            return None
                
    def get_registration_sub_type(self, registration_sub_type_slug):
        try:
            return get_object_or_404(RegistrationSubType, slug = registration_sub_type_slug)          
        except Http404:
            return None 

    def get_registration(self, registration_slug):
        try:
            return get_object_or_404(Registration, slug = registration_slug)          
        except Http404:
            return None                
    

class ListRegistrationView(BaseRegistrationCompanyView, ListView):
    model = Registration
    queryset = model.objects.none()
    context_object_name = "registrations"
    template_name = "registration_company/registration/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListRegistrationView of superadmin app: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:            
            context["registration_page"] = True        
        except Exception as e:
            logger.exception(f"Error in getting context data of ListRegistrationView of superadmin app: {e}")

        return context

class AddRegistrationView(BaseRegistrationCompanyView, CreateView):
    model = Registration
    fields = ["title", "image", "company", "sub_type", "registration_type", "price", "time_required", "required_documents", "additional_info"]
    template_name = "registration_company/registration/add.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_registration", kwargs = {'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in getting success url in AddRegistrationView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url in AddRegistrationView of superadmin app: {e}")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["types"] = RegistrationType.objects.filter(company = self.get_current_company()).order_by("-updated")
            context["registration_page"] = True
            context["add_registration_page"] = True
        except Exception as e:
            logger.exception(f"Error in getting context data in AddRegistrationView of superadmin app: {e}")

        return context
    
    def get_company(self):
        try:
            company_slug = self.kwargs.get('slug')
            return get_object_or_404(Company, slug = company_slug.strip())
        except Http404:
            messages.error(self.request, "Invalid Company")
            return redirect(self.redirect_url)        

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()
            title = clean_string(request.POST.get("title", ""))
            registration_type_slug = clean_string(request.POST.get("type", ""))
            image = request.FILES.get("image")

            sub_type_slug = clean_string(request.POST.get("sub_type"))
            price = clean_string(request.POST.get("price"))
            time_required = clean_string(request.POST.get("time_required"))
            required_documents = clean_string(request.POST.get("required_documents"))
            additional_info = clean_string(request.POST.get("additional_info"))

            required_fields = {
                "Title": title,
                "Type": registration_type_slug,
                "Sub Type": sub_type_slug,
                "Image": image,
                "Price": price,
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
      
            registration_type = self.get_registration_type(registration_type_slug)
            registration_sub_type = self.get_registration_sub_type(sub_type_slug)

            if not registration_type:
                messages.error(request, "Failed! Invalid Registration Type")
                return redirect(self.get_redirect_url())

            if not registration_sub_type:
                messages.error(request, "Failed! Invalid Registration Sub Type")
                return redirect(self.get_redirect_url())
            
            if self.model.objects.filter(company=company, title=title, sub_type = registration_sub_type).exists():
                messages.warning(request, "Registration already exists")
                return redirect(self.get_redirect_url())

            self.model.objects.create(
                title = title, image = image, company = company, 
                registration_type = registration_type, sub_type = registration_sub_type, price = price,
                time_required = time_required, required_documents = required_documents, 
                additional_info = additional_info
                )
            
            messages.success(request, "Success! Registration Created.")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in adding registration in AddRegistrationView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class UpdateRegistrationView(BaseRegistrationCompanyView, UpdateView):
    model = Registration
    fields = ["sub_type", "price", "time_required", "required_documents", "additional_info"]
    template_name = "registration_company/registration/edit.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "registration"

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:registrations", kwargs = {'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in getting success url in EditRegistrationView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url in EditRegistrationView of superadmin app: {e}")
            return self.redirect_url

    def get_company(self):
        try:
            company_slug = self.kwargs.get('slug')
            return get_object_or_404(Company, slug = company_slug.strip())
        except Http404:
            messages.error(self.request, "Invalid Company")
            return redirect(self.redirect_url)    

    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get('registration_slug'))
        except Http404:
            messages.error(self.request, "Invalid registration")   
            return redirect(self.get_redirect_url())
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_company()
            registration = self.get_object()
            context["types"] = RegistrationType.objects.filter(company = current_company).order_by("-updated")
            context["sub_types"] = RegistrationSubType.objects.filter(company = current_company, type = registration.sub_type.type).order_by("-updated")
            context["registration_page"] = True            
        except Exception as e:
            logger.exception(f"Error in getting context data in EditRegistrationView of superadmin app: {e}")

        return context 

    def post(self, request, *args, **kwargs):
        try:
            title = clean_string(request.POST.get("title", ""))
            registration_type_slug = clean_string(request.POST.get("type", ""))
            image = request.FILES.get("image")

            sub_type_slug = clean_string(request.POST.get("sub_type"))
            price = clean_string(request.POST.get("price"))
            time_required = clean_string(request.POST.get("time_required"))
            required_documents = clean_string(request.POST.get("required_documents"))
            additional_info = clean_string(request.POST.get("additional_info"))

            required_fields = {
                "Title": title,
                "Type": registration_type_slug,
                "Sub Type": sub_type_slug,
                "Price": price,
            }

            registration = self.get_object()
            
            if not image and not registration.image:
                required_fields["Image"] = image

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())            
            
            registration_type = self.get_registration_type(registration_type_slug)
            registration_sub_type = self.get_registration_sub_type(sub_type_slug)            

            if not registration_type:
                messages.error(request, "Failed! Invalid Registration Type")
                return redirect(self.get_redirect_url())

            if not registration_sub_type:
                messages.error(request, "Failed! Invalid Registration Sub Type")
                return redirect(self.get_redirect_url())
                        
            similar_registrations = self.model.objects.filter(company = registration.company, title = title, sub_type=registration_sub_type)
            
            if similar_registrations.exists() and similar_registrations.first() != registration:
                messages.warning(request, "similar registration already exists")
                return redirect(self.get_redirect_url())
        
            registration.title = title
            if image:
                registration.image = image
            registration.registration_type = registration_type
            registration.sub_type = registration_sub_type
            registration.price = price.strip()
            registration.time_required = time_required.strip() if time_required else None
            registration.required_documents = required_documents.strip() if required_documents else None
            registration.additional_info = additional_info.strip() if additional_info else None
            registration.save()        
            
            messages.success(request, "Success! Registration Updated.")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in updating registration in EditRegistrationView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class RemoveRegistrationView(BaseRegistrationCompanyView, View):
    model = Registration
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:registrations", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveRegistrationView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveRegistrationView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("registration_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted registration")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid registration")

        except Exception as e:
            logger.exception(f"Error in RemoveRegistrationView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class ListRegistrationTypeView(BaseRegistrationCompanyView, ListView):
    model = RegistrationType
    queryset = model.objects.none()
    context_object_name = "types"
    template_name = "registration_company/types/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListRegistrationTypeView of superadmin app: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["registration_type_page"] = True

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of ListRegistrationTypeView of superadmin app: {e}")

        return context
    

class AddRegistrationTypeView(BaseRegistrationCompanyView, CreateView):
    model = RegistrationType
    fields = ["name", "description"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:registration_types", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def post(self, request, *args, **kwargs):
        try:
            current_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None

            description = request.POST.get("description")
            description = description.strip() if description else None

            if not name:
                messages.error(request, "Name of registration type is required.")
                return redirect(self.get_redirect_url())
            
            registration_type, created = self.model.objects.get_or_create(company = current_company, name = name, description = description)

            if not created:
                messages.warning(request, "Registration type already exists.")
                return redirect(self.get_redirect_url())

            messages.success(request, "Success! Registration type created.")
            return redirect(self.get_success_url())
        
        except Exception as e:
            logger.exception(f"Error in creating registration type: {e}")
            messages.error(request, "Failed! An unexpected error occured")
            return redirect(self.get_redirect_url())
        

class UpdateRegistrationTypeView(BaseRegistrationCompanyView, UpdateView):
    model = RegistrationType
    fields = ["name", "description"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:registration_types", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("registration_type_slug"))
        except Http404:
            messages.error(self.request, "Invalid registration type")
            return redirect(self.get_redirect_url())

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            description = request.POST.get("description")
            description = description.strip() if description else None

            if not name:
                messages.error(request, "Name of registration type is required.")
                return redirect(self.get_redirect_url())
            
            registration_type = self.get_object()

            similar_registration_types = self.model.objects.filter(company = registration_type.company, name = name)

            if similar_registration_types.exists() and similar_registration_types.first() != registration_type:
                messages.warning(request, "Similar registration type already exists")
                return redirect(self.get_redirect_url())
            
            registration_type.name = name
            registration_type.description = description
            registration_type.save()

            messages.success(request, "Success! Registration type updated.")
            return redirect(self.get_success_url())
        
        except Exception as e:
            logger.exception(f"Error in updating registration type: {e}")
            messages.error(request, "An unexpected error occurred")
            return redirect(self.get_redirect_url())
        

class RemoveRegistrationTypeView(BaseRegistrationCompanyView, View):
    model = RegistrationType
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:registration_types", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveRegistrationTypeView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveRegistrationTypeView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("registration_type_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted registration type")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid registration type")

        except Exception as e:
            logger.exception(f"Error in RemoveRegistrationTypeView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ListRegistrationSubTypeView(BaseRegistrationCompanyView, ListView):
    model = RegistrationSubType
    queryset = model.objects.none()
    context_object_name = "sub_types"
    template_name = "registration_company/sub_types/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug')).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListRegistrationSubTypeView of superadmin app: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["registration_sub_type_page"] = True
            context["types"] = RegistrationType.objects.filter(company = self.get_current_company()).order_by("-updated")

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of ListRegistrationSubTypeView of superadmin app: {e}")

        return context
    
    
class AddRegistrationSubTypeView(BaseRegistrationCompanyView, CreateView):
    model = RegistrationSubType
    fields = ["name", "type", "starting_title", "slug", "ending_title", "content", "faqs", "description"]
    success_url = redirect_url = reverse_lazy("superadmin:home")
    template_name = "registration_company/sub_types/add.html"

    def get_success_url(self):        
        return reverse_lazy("superadmin:add_registration_sub_types", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            context["types"] = RegistrationType.objects.filter(company = current_company).order_by("name")
        except Exception as e:
            logger.exception(f"Error in getting context data of AddRegistrationSubTypeView of superadmin app: {e}")
        
        return context    

    def handle_faqs(self, request, company, sub_type_slug):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]               

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                SubTypeFaq.objects.filter(company = company, sub_type_slug = sub_type_slug).delete()
                
                if question_list and answer_list:
                    creating_faqs = [SubTypeFaq(
                        company = company, sub_type_slug = sub_type_slug,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    SubTypeFaq.objects.bulk_create(creating_faqs)

                    registration_faqs = SubTypeFaq.objects.filter(company = company, sub_type_slug = sub_type_slug)                
                                            
                    return registration_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of BaseRegistrationSubTypeView: {e}")

        return [] 

    def post(self, request, *args, **kwargs):
        try:
            current_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            
            name = clean_string(request.POST.get("name", ""))
            type_slug = clean_string(request.POST.get("type", ""))
            description = clean_string(request.POST.get("description", ""))
            starting_title = clean_string(request.POST.get("starting_title", ""))
            slug = clean_string(request.POST.get("slug", ""))
            ending_title = clean_string(request.POST.get("ending_title", ""))
            content = request.POST.get("content")
            hide_faqs = request.POST.get("hide_faqs")

            required_fields = {
                "Name": name,
                "Registration Type": type_slug
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required")
                    return redirect(self.get_redirect_url())

            slug_list = [starting_title, slug, ending_title]

            full_slug = slugify("-".join(filter(None, slug_list)))
            
            with transaction.atomic():
                main_type = get_object_or_404(RegistrationType, slug = type_slug)

                slug = slugify(slug)

                if self.model.objects.filter(slug = slug).exists():
                    messages.error(request, "Failed! Similar slug already exists for another registration sub type.")
                    return redirect(self.get_redirect_url())

                if full_slug and self.model.objects.filter(location_slug = full_slug).exists():
                        messages.error(request, "Failed! Similar location slug already exists for another registration sub type.")
                        return redirect(self.get_redirect_url())
                
                sub_type, created = self.model.objects.get_or_create(
                    company = current_company, name = name, 
                    type = main_type, 
                    defaults={
                        "description": description,
                        "starting_title": starting_title,
                        "ending_title": ending_title,
                        "hide_faqs": True if hide_faqs else False,
                        "content": content,
                        "slug": slug if slug else None,
                        "location_slug": full_slug if full_slug else None,
                    })

                if not created:
                    messages.warning(request, "Registration sub type already exists.")
                    return redirect(self.get_redirect_url())

                sub_type_faq_objs = self.handle_faqs(request, sub_type.company, sub_type.slug)
                sub_type.faqs.set(sub_type_faq_objs)

                messages.success(request, "Success! Registration sub type created.")
                return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid registration sub type")                                   
        
        except Exception as e:
            logger.exception(f"Error in creating registration sub type by superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class UpdateRegistrationSubTypeView(BaseRegistrationCompanyView, UpdateView):
    model = RegistrationSubType
    fields = ["name", "type", "starting_title", "slug", "ending_title", "content", "faqs", "description"]
    success_url = redirect_url = reverse_lazy("superadmin:home")
    template_name = "registration_company/sub_types/edit.html"
    context_object_name = "sub_type"

    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("registration_sub_type_slug"))
        except Http404:
            messages.error(self.request, "Invalid registration sub type")
            return redirect(self.get_redirect_url())

    def get_success_url(self):
        try:  
            return reverse_lazy("superadmin:registration_sub_types", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of UpdateRegistrationSubTypeView of superadmin app: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of UpdateRegistrationSubTypeView of superadmin app: {e}")
            return self.redirect_url
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            context["types"] = RegistrationType.objects.filter(company = current_company).order_by("name")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateRegistrationSubTypeView of superadmin app: {e}")
        
        return context    
    
    def handle_faqs(self, request, company, sub_type_slug):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]               

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                SubTypeFaq.objects.filter(company = company, sub_type_slug = sub_type_slug).delete()
                
                if question_list and answer_list:
                    creating_faqs = [SubTypeFaq(
                        company = company, sub_type_slug = sub_type_slug,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    SubTypeFaq.objects.bulk_create(creating_faqs)

                    registration_faqs = SubTypeFaq.objects.filter(company = company, sub_type_slug = sub_type_slug)                
                                            
                    return registration_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of UpdateRegistrationSubTypeView: {e}")

        return []

    def post(self, request, *args, **kwargs):
        try:
            registration_sub_type = self.get_object()
            object_slug = registration_sub_type.slug or ""

            name = clean_string(request.POST.get("name", ""))
            type_slug = clean_string(request.POST.get("type", ""))
            description = clean_string(request.POST.get("description", ""))
            starting_title = clean_string(request.POST.get("starting_title", ""))
            slug = clean_string(request.POST.get("slug", object_slug))
            ending_title = clean_string(request.POST.get("ending_title", ""))
            content = request.POST.get("content")            
            hide_faqs = request.POST.get("hide_faqs")

            required_fields = {
                "Name": name,                
                "Registration Type": type_slug
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required")
                    return redirect(self.get_redirect_url())

            slug_list = [starting_title, slug, ending_title]

            full_slug = slugify("-".join(filter(None, slug_list)))

            with transaction.atomic():            
                type = get_object_or_404(RegistrationType, slug = type_slug)
                
                if self.model.objects.filter(
                    company = registration_sub_type.company, name = name, type = type
                    ).exclude(pk = registration_sub_type.pk).exists():
                    messages.warning(request, "Similar registration sub type already exists")
                    return redirect(self.get_redirect_url())
                
                slug = slugify(slug)

                if slug != registration_sub_type.slug:
                    
                    if self.model.objects.filter(slug = slug).exclude(pk = registration_sub_type.pk).exists():
                        messages.error(request, "Failed! Similar slug already exists for another registration sub type.")
                        return redirect(self.get_redirect_url())
                    
                    registration_sub_type.slug = slug
                
                if full_slug != registration_sub_type.location_slug:                    
                    if self.model.objects.filter(location_slug = full_slug).exclude(pk = registration_sub_type.pk).exists():
                        messages.error(request, "Failed! Similar location slug already exists for another registration sub type.")
                        return redirect(self.get_redirect_url())

                    registration_sub_type.location_slug = full_slug                                        

                registration_sub_type.name = name
                registration_sub_type.type = type
                registration_sub_type.description = description
                registration_sub_type.starting_title = starting_title
                registration_sub_type.ending_title = ending_title
                registration_sub_type.hide_faqs = True if hide_faqs else False        
                registration_sub_type.content = content

                registration_sub_type.save()

                sub_type_faq_objs = self.handle_faqs(request, registration_sub_type.company, registration_sub_type.slug)
                registration_sub_type.faqs.set(sub_type_faq_objs) 

                messages.success(request, "Success! Registration sub type updated.")
                return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid registration sub type")                                   
        
        except Exception as e:
            logger.exception(f"Error in updating registration sub type by superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class RemoveRegistrationSubTypeView(BaseRegistrationCompanyView, View):
    model = RegistrationSubType
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:registration_sub_types", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveRegistrationSubTypeView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveRegistrationSubTypeView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("registration_sub_type_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted registration sub type")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid registration sub type")

        except Exception as e:
            logger.exception(f"Error in RemoveRegistrationSubTypeView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())


# Registration FAQ
class RegistrationFaqBaseView(BaseRegistrationCompanyView):
    model = RegistrationFaq
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:registration_faqs', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseRegistrationFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()
        
    # def get_registration_sub_type(self, registration_SUb_type_slug):
    #     try:            
    #         return get_object_or_404(RegistrationSubType, slug = registration_SUb_type_slug)
    #     except Http404:
    #         return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context["registration_faq_page"] = True

        return context


class AddRegistrationFaqView(RegistrationFaqBaseView, CreateView):    
    fields = ["company", "registration", "question", "answer", "dynamic_place_rendering"]
    template_name = "registration_company/faqs/add.html"    

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_registration_faq', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddRegistrationFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()        
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["add_registration_faq_page"] = True
        context["types"] = RegistrationType.objects.filter(company__slug = company_slug).order_by("-updated")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            registration_slug = self.request.POST.get('registration')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            registration_slug = registration_slug.strip() if registration_slug else None
            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Registration": registration_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            company = self.get_current_company()
            registration = self.get_registration(registration_slug)

            if not company or not registration:
                invalid_msg = ""
                
                if not company:
                    invalid_msg = "Invalid Registration Company"
                else:
                    invalid_msg = "Invalid Registration Sub Type"

                messages.error(request, invalid_msg)
                return redirect(self.get_redirect_url())
            
            dynamic_place_rendering = True if dynamic_place_rendering else False

            RegistrationFaq.objects.update_or_create(
                company = company, registration = registration, question = question, dynamic_place_rendering = dynamic_place_rendering, 
                defaults={"answer": answer}
                )

            messages.success(request, f"Success! Created FAQ object for registration sub type: {registration.title}")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in get function of AddRegistrationFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class ListRegistrationFaqView(RegistrationFaqBaseView, ListView):
    model = RegistrationFaq
    template_name = "registration_company/faqs/list.html"
    queryset = model.objects.none()
    context_object_name = "faqs"

    def get_queryset(self):
        try:
            company_slug = self.kwargs.get(self.slug_url_kwarg)
            company = get_object_or_404(Company, slug = company_slug, type__name = "Registration")
            return self.model.objects.filter(company = company)
            
        except Http404:
            messages.error(self.request, "Invalid registration company")
            return redirect(self.redirect_url)


class UpdateRegistrationFaqView(RegistrationFaqBaseView, UpdateView):
    model = RegistrationFaq
    fields = ["registration", "question", "answer", "dynamic_place_rendering"]
    template_name = "registration_company/faqs/update.html"
    context_object_name = "faq"    
        
    def get_object(self):
        company_slug = self.kwargs.get('slug') 
        registration_faq_slug = self.kwargs.get('registration_faq_slug') 

        self.object = get_object_or_404(RegistrationFaq, company__slug = company_slug, slug = registration_faq_slug)

        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["update_registration_faq_page"] = True

        context["types"] = RegistrationType.objects.filter(company__slug = company_slug).order_by("-updated")
        registration_type = self.object.registration.registration_type
        sub_registration_type = self.object.registration.sub_type

        context["sub_types"] = RegistrationSubType.objects.filter(company__slug = company_slug, type = registration_type).order_by("-updated")
        context["registrations"] = Registration.objects.filter(company__slug = company_slug, sub_type = sub_registration_type).order_by("-updated")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            registration_slug = request.POST.get('registration')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Registration": registration_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            registration = self.get_registration(registration_slug)

            if not registration:
                messages.error(request, "Invalid Registration")
                return redirect(self.get_redirect_url())

            dynamic_place_rendering = True if dynamic_place_rendering else False

            similar_faq = self.model.objects.filter(
                company = self.object.company, registration = registration, question = question, answer = answer, dynamic_place_rendering = dynamic_place_rendering
                ).first()

            if similar_faq:
                if similar_faq.slug == self.object.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar registration FAQ already exists")
                return redirect(self.get_redirect_url())

            self.object.registration = registration
            self.object.question = question
            self.object.answer = answer
            self.object.dynamic_place_rendering = dynamic_place_rendering
            self.object.save()

            messages.success(request, f"Success! Updated FAQ")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid registration FAQ object")

        except Exception as e:
            logger.exception(f"Error in get function of UpdateRegistrationFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteRegistrationFaqView(RegistrationFaqBaseView, View):
    model = RegistrationFaq
        
    def get_object(self):
        faq_slug = self.kwargs.get('registration_faq_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = faq_slug, company__slug = company_slug)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            registration = self.object.registration
            self.object.delete()

            messages.success(request, f"Success! Removed registration FAQ object of: {registration}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Registration FAQ")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteRegistrationFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseRegistrationEnquiryView(BaseRegistrationCompanyView, View):
    model = RegistrationEnquiry
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = self.get_current_company()
            context["registration_enquiry_page"] = True

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseRegistrationEnquiryView: {e}")

        return context


class ListRegistrationEnquiryView(BaseRegistrationEnquiryView, ListView):
    queryset = RegistrationEnquiry.objects.none()
    context_object_name = "enquiries"
    template_name = "registration_company/enquiries/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListRegistrationEnquiryView of superadmin: {e}")
            return self.queryset


class DeleteRegistrationEnquiryView(BaseRegistrationEnquiryView, View):
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:registration_enquiries', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of DeleteRegistrationEnquiryView of superadmin app: {e}")
            return self.success_url

    def get_redirect_url(self):
        return self.get_success_url()
            

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()            
            RegistrationEnquiry.objects.filter(company = current_company, slug = self.kwargs.get('enquiry_slug')).delete()

            messages.success(request, "Success! Delete Registration Enquiry")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Registration Enquiry")
            return redirect(self.get_redirect_url())


class BaseRegistrationDetailPageView(BaseRegistrationCompanyView):
    model = RegistrationDetailPage
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["registration_detail_page"] = True
            
            current_company = self.get_current_company()

            context["current_company"] = current_company

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseRegistrationDetailPageView of superadmin: {e}")
        
        return context    
        
    def get_registration_sub_type(self, registration_sub_type_slug):
        try:
            return get_object_or_404(RegistrationSubType, slug = registration_sub_type_slug)
        except Http404:
            messages.error(self.request, "Invalid Registration Sub Type")
            return redirect(self.get_redirect_url())
        
    def get_current_registration_sub_type(self):
        try:
            registration_sub_type_slug = self.kwargs.get('registration_sub_type_slug')   
            registration = get_object_or_404(RegistrationSubType, slug = registration_sub_type_slug)
            return registration
        except Http404:
            messages.error(self.request, "Failed! Invalid Registration Sub Type")
            return redirect(self.redirect_url)

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:registration_detail_pages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function of RegistrationDetailPageView: {e}")
            return self.redirect_url

    def get_success_url(self):
        return self.get_redirect_url()

    def get_object(self):
        try:
            current_company = self.get_current_company()
            detail_page_slug = self.kwargs.get("detail_page_slug")
            # current_registration_sub_type = self.get_current_registration_sub_type()
            return get_object_or_404(self.model, company = current_company, slug = detail_page_slug)
        
        except Http404:
            messages.error(self.request, "Invalid registration sub type")

        except Exception as e:
            logger.exception(f"Error in get_object function of BaseRegistrationDetailPageView of superadmin: {e}")

        return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, registration):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    RegistrationFeature.objects.filter(company = company, registration = registration).delete()

                    features = [RegistrationFeature(company=company, registration=registration, feature=feature) for feature in features_list]
                    RegistrationFeature.objects.bulk_create(features)

                    feature_objs = RegistrationFeature.objects.filter(company = company, registration = registration)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseRegistrationDetailPageView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, registration):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                RegistrationVerticalTab.objects.filter(company = company, registration = registration).delete()
                RegistrationVerticalBullet.objects.filter(company = company, registration = registration).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = RegistrationVerticalTab.objects.create(
                            company = company,
                            registration = registration,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [RegistrationVerticalBullet(
                                company = company, registration = registration, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                RegistrationVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = RegistrationVerticalBullet.objects.filter(company = company, registration = registration, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)

                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseRegistrationDetailPageView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, registration):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                RegistrationHorizontalTab.objects.filter(company = company, registration = registration).delete()
                RegistrationHorizontalBullet.objects.filter(company = company, registration = registration).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = RegistrationHorizontalTab.objects.create(
                            company = company,
                            registration = registration,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [RegistrationHorizontalBullet(
                                company = company, registration = registration, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                RegistrationHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = RegistrationHorizontalBullet.objects.filter(company = company, registration = registration, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseRegistrationDetailPageView: {e}")

        return []
    
    def handle_tables(self, request, company, registration):
        try:
            registration_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                RegistrationTableData.objects.filter(company = company, registration = registration).delete()
                RegistrationTable.objects.filter(company = company, registration = registration).delete()

                for index, heading in enumerate(heading_list):
                    registration_table = RegistrationTable.objects.create(
                        company = company, registration = registration, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [RegistrationTableData(
                            company = company, registration = registration,
                            heading = heading, data = data
                            ) for data in data_list_of_heading]

                    RegistrationTableData.objects.bulk_create(table_data_objs )

                    registration_table_data_objs = RegistrationTableData.objects.filter(company = company, registration = registration, heading = heading)

                    registration_table.datas.set(registration_table_data_objs)

                    registration_tables.append(registration_table)

            return registration_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseRegistrationDetailPageView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, registration):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                RegistrationBulletPoint.objects.filter(company = company, registration = registration).delete()

                if bullet_point_list:
                    bullet_point_objects = [RegistrationBulletPoint(
                        company = company, registration = registration,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    RegistrationBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = RegistrationBulletPoint.objects.filter(company = company, registration = registration)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseRegistrationDetailPageView: {e}")

        return []

    def handle_timelines(self, request, company, registration):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                RegistrationTimeline.objects.filter(company = company, registration = registration).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [RegistrationTimeline(
                        company = company, registration = registration,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    RegistrationTimeline.objects.bulk_create(creating_timelines)

                    registration_timelines = RegistrationTimeline.objects.filter(company = company, registration = registration)                
                                            
                    return registration_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseRegistrationDetailPageView: {e}")

        return []


class AddRegistrationDetailPageView(BaseRegistrationDetailPageView, CreateView):
    form_class = RegistrationDetailPageDescriptionForm
    template_name = "registration_company/detail_page/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_registration_detail_page"] = True

        current_company = self.get_current_company()        
        context["types"] = RegistrationType.objects.filter(company = current_company).order_by("-updated")
        context["tags"] = MetaTag.objects.all().order_by("-updated")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_registration_detail_page', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseRegistrationDetailPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseRegistrationDetailPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            registration_slug = clean_string(request.POST.get("registration", ""))

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")
            
            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")

            summary = summary.strip() if summary else None
            
            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None
            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Registration": registration_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                }

            registration = self.get_registration(registration_slug)

            if not registration:
                messages.error(request, "Failed! Invalid Registration.")
                return redirect(self.get_redirect_url())

            updating_meta_tags = []
            with transaction.atomic():
                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                if RegistrationDetailPage.objects.filter(company = company, registration = registration).exists():
                    messages.warning(request, "This registration already have an detail page.")
                    return redirect(self.get_redirect_url())

                registration_detail = self.model.objects.create(
                    company = company, registration = registration, 
                    summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, 
                    timeline_title = timeline_title
                )                                

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(registration_detail, key, True)

                registration_detail.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,                    
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, registration)
                    getattr(registration_detail, field).set(objects)

                if meta_tags:
                    meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                    registration_detail.meta_tags.set(meta_tag_objects)  

                messages.success(request, "Success! Created registration detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddRegistrationDetailPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class RegistrationDetailPageListView(BaseRegistrationDetailPageView, ListView):
    template_name = "registration_company/detail_page/list.html"
    queryset = Registration.objects.none()
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "detail_pages"        
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting queryset of RegistrationDetailsListView of superadmin: {e}")
            return self.queryset


class RegistrationDetailPageView(BaseRegistrationDetailPageView, DetailView):
    template_name = "registration_company/detail_page/detail.html"
    redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "detail_page"    


class UpdateRegistrationDetailPageView(BaseRegistrationDetailPageView, UpdateView):    
    form_class = RegistrationDetailPageDescriptionForm
    template_name = "registration_company/detail_page/update.html"
    context_object_name = "detail_page"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object()
        current_company = self.get_current_company()
        registration_type = self.object.registration.registration_type
        registration_sub_type = self.object.registration.sub_type
        context["types"] = RegistrationType.objects.filter(company = current_company).order_by("-updated")
        context["sub_types"] = RegistrationSubType.objects.filter(company = current_company, type = registration_type).order_by("-updated")
        context["registrations"] = Registration.objects.filter(company = current_company, sub_type = registration_sub_type).order_by("-updated")
        context["tags"] = MetaTag.objects.all().order_by("-updated")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_registration_detail_page', kwargs = {"slug": self.kwargs.get('slug'), "detail_page_slug": self.kwargs.get('detail_page_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateRegistrationDetailPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateRegistrationDetailPageView of superadmin: {e}")
            return self.redirect_url


    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()
            
            registration_slug = clean_string(request.POST.get("registration", ""))

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")   

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None
            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Registration": registration_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                }

            registration = self.get_registration(registration_slug)

            if not registration:
                messages.error(request, "Failed! Invalid Registration.")
                return redirect(self.get_redirect_url())

            updating_meta_tags = []
            with transaction.atomic():

                registration_detail = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                if RegistrationDetailPage.objects.filter(company = registration_detail.company, registration = registration).exclude(pk = registration_detail.pk).exists():
                    messages.warning(request, "This registration already have an detail page.")
                    return redirect(self.get_redirect_url())                

                registration_detail.registration = registration
                registration_detail.summary = summary

                registration_detail.description = description

                registration_detail.meta_title = meta_title
                registration_detail.meta_description = meta_description

                registration_detail.vertical_title = vertical_title
                registration_detail.horizontal_title = horizontal_title
                registration_detail.table_title = table_title
                registration_detail.bullet_title = bullet_title                
                registration_detail.timeline_title = timeline_title                

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:                    
                        assigning_value = True

                    setattr(registration_detail, key, assigning_value)
                
                registration_detail.save()                             

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,                    
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, registration)
                    getattr(registration_detail, field).set(objects)

                registration_detail.save()

                meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                registration_detail.meta_tags.set(meta_tag_objects)

                messages.success(request, "Success! Updated registration detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateRegistrationDetailPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteRegistrationDetailPageView(BaseRegistrationDetailPageView, View):

    def post(self, request, *args, **kwargs):
        try:
            company_slug = self.kwargs.get('slug')
            detail_page_slug = self.kwargs.get('detail_page_slug')
            RegistrationDetailPage.objects.filter(company__slug = company_slug, slug = detail_page_slug).delete()            

            messages.success(request, f"Success! Removed registration detail page.")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Registration Detail")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteRegistrationDetailPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseRegistrationMultiPageView(BaseRegistrationCompanyView, View):
    model = RegistrationMultiPage
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = "slugf" 
        
    def get_registration_types(self):
        return RegistrationType.objects.filter(company = self.current_company).order_by("-updated")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["registration_multipage"] = True
            
            self.current_company = self.get_current_company()
            
            context["current_company"] = self.current_company            
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseRegistrationMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:registration_multipages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseRegistrationMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseRegistrationMultiPageView of superadmin: {e}")
            return self.redirect_url
        
    def get_registration_sub_type(self, registration_sub_type_slug):
        try:
            return get_object_or_404(RegistrationSubType, slug = registration_sub_type_slug)
        except Http404:
            messages.error(self.request, "Invalid Registration Sub Type")
            return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, title):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    RegistrationMultiPageFeature.objects.filter(company = company, title = title).delete()

                    features = [RegistrationMultiPageFeature(company=company, title=title, feature=feature) for feature in features_list]
                    RegistrationMultiPageFeature.objects.bulk_create(features)

                    feature_objs = RegistrationMultiPageFeature.objects.filter(company = company, title = title)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseRegistrationMultiPageView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, title):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                RegistrationMultiPageVerticalTab.objects.filter(company = company, title = title).delete()
                RegistrationMultiPageVerticalBullet.objects.filter(company = company, title = title).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = RegistrationMultiPageVerticalTab.objects.create(
                            company = company,
                            title = title,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [RegistrationMultiPageVerticalBullet(
                                company = company, title = title, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                RegistrationMultiPageVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = RegistrationMultiPageVerticalBullet.objects.filter(company = company, title = title, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)


                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseRegistrationMultiPageView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, title):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                RegistrationMultiPageHorizontalTab.objects.filter(company = company, title = title).delete()
                RegistrationMultiPageHorizontalBullet.objects.filter(company = company, title = title).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = RegistrationMultiPageHorizontalTab.objects.create(
                            company = company,
                            title = title,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [RegistrationMultiPageHorizontalBullet(
                                company = company, title = title, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                RegistrationMultiPageHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = RegistrationMultiPageHorizontalBullet.objects.filter(company = company, title = title, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseRegistrationMultiPageView: {e}")

        return []
    
    def handle_tables(self, request, company, title):
        try:
            registration_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                RegistrationMultiPageTableData.objects.filter(company = company, title = title).delete()
                RegistrationMultiPageTable.objects.filter(company = company, title = title).delete()

                for index, heading in enumerate(heading_list):
                    registration_table = RegistrationMultiPageTable.objects.create(
                        company = company, title = title, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [RegistrationMultiPageTableData(
                            company = company, title = title,
                            heading = heading, data = data
                            ) for data in data_list_of_heading if data]

                    RegistrationMultiPageTableData.objects.bulk_create(table_data_objs )

                    registration_table_data_objs = RegistrationMultiPageTableData.objects.filter(company = company, title = title, heading = heading)

                    registration_table.datas.set(registration_table_data_objs)
                    registration_tables.append(registration_table)

            return registration_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseRegistrationMultiPageView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, title):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                RegistrationMultiPageBulletPoint.objects.filter(company = company, title = title).delete()

                if bullet_point_list:
                    bullet_point_objects = [RegistrationMultiPageBulletPoint(
                        company = company, title = title,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    RegistrationMultiPageBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = RegistrationMultiPageBulletPoint.objects.filter(company = company, title = title)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseRegistrationMultiPageView: {e}")

        return []

    def handle_timelines(self, request, company, title):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                RegistrationMultiPageTimeline.objects.filter(company = company, title = title).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [RegistrationMultiPageTimeline(
                        company = company, title = title,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    RegistrationMultiPageTimeline.objects.bulk_create(creating_timelines)

                    registration_timelines = RegistrationMultiPageTimeline.objects.filter(company = company, title = title)                
                                            
                    return registration_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseRegistrationMultiPageView: {e}")

        return []

    def handle_faqs(self, request, company, title):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]                        

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                RegistrationMultiPageFaq.objects.filter(company = company, title = title).delete()
                
                if question_list and answer_list:
                    creating_faqs = [RegistrationMultiPageFaq(
                        company = company, title = title,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    RegistrationMultiPageFaq.objects.bulk_create(creating_faqs)

                    registration_faqs = RegistrationMultiPageFaq.objects.filter(company = company, title = title)                
                                            
                    return registration_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of BaseRegistrationMultiPageView: {e}")

        return []
    
    def handle_text_editors(self, request, company, title):
        try:
            text_editor_title_list = [title.strip() for title in request.POST.getlist("text_editor_title")]
            content_list = request.POST.getlist("text_editor_content")

            if len(text_editor_title_list) != len(content_list):
                raise ValueError("The number of titles does not match the number of contents.")

            with transaction.atomic():
                RegistrationTextEditor.objects.filter(company = company, title = title).delete()
                
                if text_editor_title_list and content_list:
                    creating_text_editors = [RegistrationTextEditor(
                        company = company, title = title,
                        text_editor_title = text_editor_title, content = content
                        ) for text_editor_title, content in zip(text_editor_title_list, content_list) if text_editor_title and content]

                    RegistrationTextEditor.objects.bulk_create(creating_text_editors)

                    registration_text_editors = RegistrationTextEditor.objects.filter(company = company, title = title)                
                                            
                    return registration_text_editors
        except Exception as e:
            logger.exception(f"Error in handle_text_editors function of BaseRegistrationMultiPageView: {e}")

        return []


class AddRegistrationMultiPageView(BaseRegistrationMultiPageView, CreateView):
    form_class = RegistrationMultiPageDescriptionForm
    template_name = "registration_company/multipage/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company = self.get_current_company()

        context["registration_types"] = RegistrationType.objects.filter(company = company).order_by("-updated")
        context["registrations"] = Registration.objects.filter(company = company).order_by("-updated")
        context["tags"] = MetaTag.objects.all().order_by("-updated")
        context["states"] = UniqueState.objects.all().order_by("-updated")

        return context

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_registration_multipage', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddRegistrationMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddRegistrationMultiPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()

            form = self.get_form()

            title = clean_string(request.POST.get("title", ""))
            sub_title = request.POST.get("sub_title", "")
            registration_slug = clean_string(request.POST.get("registration", ""))

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")
            registration_region = request.POST.get("registration_region")
            available_states = request.POST.getlist("available_states")

            slider_registration_details = [item.strip() for item in request.POST.getlist("registration_details", [])]

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None
            registration_region = registration_region.strip() if registration_region else None
            available_states = [state.strip() for state in available_states if state.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = current_company

            if not company or company.type.name != "Registration" :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Title": title,
                "Registration": registration_slug,
                "Summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            if registration_region != "all" and len(available_states) < 1:
                messages.error(request, "Failed! Selected 'Selected States' for registration region without providing any available state")
                return redirect(self.get_redirect_url())

            registration = self.get_registration(registration_slug)

            if not registration:
                messages.error(request, "Failed! Invalid registration")
                return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            updating_meta_tags = []
            with transaction.atomic():
                if self.model.objects.filter(company = company, title = title).exists():
                    messages.error(request, "Similar multipage already exists")
                    return redirect(self.get_redirect_url())
                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                registration_multi_page = self.model.objects.create(
                    company = company, title = title, sub_title = sub_title, registration = registration, 
                    summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    url_type = url_type, registration_region = registration_region,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, 
                    timeline_title = timeline_title
                )                

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(registration_multi_page, key, True)
                
                registration_multi_page.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,                    
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                    "text_editors": self.handle_text_editors,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, title)
                    getattr(registration_multi_page, field).set(objects)

                if meta_tags:
                    meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                    registration_multi_page.meta_tags.set(meta_tag_objects)

                available_states_objs = UniqueState.objects.all()
                if registration_region != "all":
                    available_states_objs = UniqueState.objects.filter(slug__in = available_states)

                registration_multi_page.available_states.set(available_states_objs)

                slider_registration_objs = RegistrationDetailPage.objects.filter(slug__in = slider_registration_details)
                registration_multi_page.slider_registrations.set(slider_registration_objs)                

                messages.success(request, "Success! Created registration multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddRegistrationMultiPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class RegistrationMultiPageListView(BaseRegistrationMultiPageView, ListView):
    template_name = "registration_company/multipage/list.html"
    queryset = RegistrationMultiPage.objects.none()
    context_object_name = "multipages"    
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company).order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting queryset of RegistrationMultiPageListView of superadmin: {e}")
            return self.queryset
        
class RegistrationMultiPageDetailView(BaseRegistrationMultiPageView, DetailView):
    template_name = "registration_company/multipage/detail.html"
    context_object_name = "multipage"
    slug_url_kwarg = 'multipage_slug'

    def get_current_registration_sub_type(self):
        try:
            registration_sub_type_slug = self.kwargs.get('registration_sub_type_slug')
            return get_object_or_404(RegistrationSubType, slug = registration_sub_type_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Registration Sub Type")
            return redirect(self.redirect_url)   

    def get_object(self):
        try:
            current_company = self.get_current_company()
            return get_object_or_404(self.model, company = current_company, slug = self.kwargs.get(self.slug_url_kwarg))
        
        except Http404:
            messages.error(self.request, "Invalid registration for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of RegistrationMultipageDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object
        
        context[self.context_object_name] = self.object
        return context     
    

class UpdateRegistrationMultiPageView(BaseRegistrationMultiPageView, UpdateView):    
    form_class = RegistrationMultiPageDescriptionForm
    template_name = "registration_company/multipage/update.html"
    context_object_name = "multipage"    

    def get_object(self):
        try:
            company_slug = self.kwargs.get('slug')
            multipage_slug = self.kwargs.get('multipage_slug')            
            
            return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)
        
        except Http404:
            messages.error(self.request, "Invalid registration multipage object")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            self.object = self.get_object()
            context[self.context_object_name] = self.object
            
            company = self.get_current_company()

            context["registration_types"] = RegistrationType.objects.filter(company = company).order_by("-updated")            

            context["registration_details"] = RegistrationDetailPage.objects.filter(
                company = company, registration__registration_type__slug = self.object.slider_registration_type_slug
                ).order_by("-updated")
            context["registrations"] = Registration.objects.filter(company = company).order_by("-updated")


            context["tags"] = MetaTag.objects.all().order_by("-updated")
            context["states"] = UniqueState.objects.all().order_by("-updated")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_redirect_url(self):
        try:
            object_slug = self.object.slug or self.kwargs.get('multipage_slug')
            return reverse_lazy('superadmin:update_registration_multipage', kwargs = {"slug": self.kwargs.get('slug'), "multipage_slug": object_slug})
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateRegistrationMultiPageView of superadmin: {e}")
            return self.success_url
        
    def post(self, request, *args, **kwargs):
        try:            
            form = self.get_form()

            title = clean_string(request.POST.get('title', ''))
            sub_title = request.POST.get('sub_title', '')
            registration_slug = clean_string(request.POST.get("registration", ""))

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")
            registration_region = request.POST.get("registration_region")
            available_states = request.POST.getlist("available_states")

            slider_registration_details = [item.strip() for item in request.POST.getlist("registration_details", [])]

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")            
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")            
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None
            registration_region = registration_region.strip() if registration_region else None
            available_states = [state.strip() for state in available_states if state.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None            
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Title": title,
                "Registration": registration_slug,
                "Summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            if registration_region != "all" and len(available_states) < 1:
                messages.error(request, "Failed! Selected 'Selected States' for registration region without providing any available state")
                return redirect(self.get_redirect_url())

            registration = self.get_registration(registration_slug)

            if not registration:
                messages.error(request, "Failed! Invalid registration")
                return redirect(self.get_redirect_url())
                
            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,                
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            updating_meta_tags = []
            with transaction.atomic():

                self.object = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                self.object.title = title
                self.object.sub_title = sub_title
                self.object.registration = registration
                self.object.summary = summary

                self.object.description = description

                self.object.meta_title = meta_title
                self.object.meta_description = meta_description

                self.object.url_type = url_type
                self.object.registration_region = registration_region

                self.object.vertical_title = vertical_title
                self.object.horizontal_title = horizontal_title
                self.object.table_title = table_title
                self.object.bullet_title = bullet_title                
                self.object.timeline_title = timeline_title                

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:
                        assigning_value = True

                    setattr(self.object, key, assigning_value)
                
                self.object.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,                    
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                    "text_editors": self.handle_text_editors,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, title)
                    getattr(self.object, field).set(objects)

                self.object.save()

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)                
                self.object.meta_tags.set(meta_tag_objs)

                self.object.available_states.clear()
                available_states_objs = UniqueState.objects.all()
                if registration_region != "all":
                    available_states_objs = UniqueState.objects.filter(slug__in = available_states)
                    
                self.object.available_states.set(available_states_objs)         

                slider_registration_objs = RegistrationDetailPage.objects.filter(slug__in = slider_registration_details)
                self.object.slider_registrations.set(slider_registration_objs)                

                messages.success(request, "Success! Updated registration multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteRegistrationMultiPageView(BaseRegistrationMultiPageView, View):
    def get_object(self, **kwargs):
        company_slug = self.kwargs.get('slug')
        multipage_slug = self.kwargs.get('multipage_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            registration = self.object.registration
            self.object.delete()

            messages.success(request, f"Success! Removed registration multipage of: {registration.title}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Registration Multipage")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteRegistrationMultiPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseRegistrationBannerView(BaseRegistrationCompanyView, View):
    model = Banner

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:registration_banners', kwargs ={"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseBannerView: {e}")

        return reverse_lazy('superadmin:home')

    def get_redirect_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registration_banner_page"] = True
        return context


class RegistrationBannerListView(BaseRegistrationBannerView, ListView):
    context_object_name = "banners"
    template_name = "registration_company/banner/list.html"

    def get_queryset(self):
        return Banner.objects.filter(company__slug = self.kwargs.get("slug"))


class CreateRegistrationBannerView(BaseRegistrationBannerView, CreateView):
    template_name = "registration_company/banner/add.html"
    fields = ["company", "image", "title", "description", "link"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_banner_page"] = True
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

            if not company:
                messages.error(request, "Failed! Invalid Registration Company.")
                return self.get_redirect_url()
            
            image = request.FILES.get("image" "")
            title = clean_string(request.POST.get("title", ""))
            description = clean_string(request.POST.get("description", ""))
            link = clean_string(request.POST.get("link", ""))

            required_fields = {
                "Title": title, "Description": description,
                "Image": image, "Link": link
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required.")
                    return redirect(self.get_redirect_url())

            if Banner.objects.filter(title = title, company = company).exists():
                messages.warning(request, f"Failed! Banner with similar heading already exists.")
                return redirect(self.get_redirect_url())
                
            Banner.objects.create(
                company = company, title = title, description = description,
                image = image, link = link
            )
            messages.success(request, "Success! Banner Created.")
            return redirect(self.get_success_url())

        except Exception as e:
            messages.error(request, "Failed! An unexpected error occurred.")
            logger.exception(f"Error in CreateRegistrationBannerView of superadmin :{e}")

        return self.get_redirect_url()
    

class UpdateRegistrationBannerView(BaseRegistrationBannerView, UpdateView):
    fields = ["image", "title", "description", "link"]
    slug_url_kwarg = "banner_slug"

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:update_registration_banner', kwargs={'slug': self.kwargs.get('slug'), 'banner_slug': self.kwargs.get('slug_url_kwarg')})
        except Exception as e:
            pass

        return self.get_success_url()

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()
            self.object = self.get_object()

            if not company:
                messages.error(request, "Failed! Invalid Registration Company.")
                return self.get_redirect_url()
            
            image = request.FILES.get("image" "")
            title = clean_string(request.POST.get("title", ""))
            description = clean_string(request.POST.get("description", ""))
            link = clean_string(request.POST.get("link", ""))

            required_fields = {
                "Title": title, "Description": description, "Link": link
            }

            if not hasattr(self.object, "image"):
                required_fields["image"] = image            

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required.")
                    return redirect(self.get_redirect_url())
                
            if Banner.objects.filter(title = title, company = company).exclude(pk = self.object.pk).exists():
                messages.warning(request, f"Failed! Banner with similar heading already exists.")
                return redirect(self.get_redirect_url())
                
            self.object.title = title
            self.object.description = description
            self.object.link = link

            if image:
                self.object.image = image

            self.object.save()               
            messages.success(request, "Success! Banner Updated.")
            return redirect(self.get_success_url())

        except Exception as e:
            messages.error(request, "Failed! An unexpected error occurred.")
            logger.exception(f"Error in UpdateRegistrationBannerView of superadmin :{e}")

        return self.get_redirect_url()


class DeleteRegistrationBannerView(BaseRegistrationBannerView, UpdateView):
    slug_url_kwarg = 'banner_slug'

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()
            self.object = self.get_object()

            if not company:
                messages.error(request, "Failed! Invalid Registration Company.")
                return self.get_redirect_url()
            
            self.object.delete()
            messages.success(request, "Success! Banner Deleted.")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Banner.")
            return self.get_redirect_url()


# Directory
class BaseDirectoryView(AdminBaseView, ListView):
    model = Bank
    template_name = "directory/list.html"    
    queryset = model.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["directory_page"] = True
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseDirectoryView in superadmin app: {e}")
        return context


class ListBankView(BaseDirectoryView, ListView):
    model = Bank
    queryset = model.objects.all().order_by("name")
    context_object_name = "banks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_directory"] = "Bank"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListBankView in superadmin app: {e}")
        return context
    

class ListCourtView(BaseDirectoryView, ListView):
    model = Court
    queryset = model.objects.all().order_by("name")
    context_object_name = "courts"
    ordering = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_directory"] = "Court"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListCourtView in superadmin app: {e}")
        return context


class ListDestinationView(BaseDirectoryView, ListView):
    model = Destination
    queryset = model.objects.all().order_by("name")
    context_object_name = "destinations"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_directory"] = "Destination"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListDestinationView in superadmin app: {e}")
        return context


class ListPoliceStationView(BaseDirectoryView, ListView):
    model = PoliceStation
    queryset = model.objects.all().order_by("name")
    context_object_name = "police_stations"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_directory"] = "Police Station"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListPoliceStationView in superadmin app: {e}")
        return context


class ListPostOfficeView(BaseDirectoryView, ListView):
    model = PostOffice
    queryset = model.objects.all().order_by("pincode")
    context_object_name = "post_offices"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_directory"] = "Post Office"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListPostOfficeView in superadmin app: {e}")
        return context
    

# Settings

class SettingsView(AdminBaseView, TemplateView):
    model = User
    template_name = "settings/settings.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UpdatePasswordView(SettingsView, UpdateView):
    model = User
    success_url = reverse_lazy('authentication:login')
    redirect_url = reverse_lazy('superadmin:settings')

    def validate_password(self, password):
        password = str(password)

        if len(password) < 8:
            return "Password must contain at least 8 characters"
        
        if " " in password:
            return "Password cannot have any white spaces"
        
        if password.isalpha():
            return "Password must contain at least one digit"
        
        if password.isnumeric():
            return "Password must contain at least one alphabet"
        
        if password == password.lower() or password == password.upper():
            return "Password must contain at least one uppercase and one lowercase alphabet"
        
        if password.isalnum():
            return "Password must contain at least one special character"
        
        return None        

    def post(self, request, *args, **kwargs):
        try:
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            required_fields = {
                "Current password": current_password,
                "New password": new_password,
                "Confirm password": confirm_password
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! Field '{key}' is required")
                    return redirect(self.redirect_url)

            user = authenticate(request, username = request.user.username, password = current_password)

            if not user:
                messages.error(request, "The current password you entered is incorrect")
                return redirect(self.redirect_url)
            
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect(self.redirect_url)
            
            validation_error_msg = self.validate_password(new_password)

            if validation_error_msg is not None:
                messages.warning(request, validation_error_msg)
                return redirect(self.redirect_url)
            
            user.set_password(new_password)
            user.save()

            logout(request)
            messages.success(request, "Success! Password changed")
            return redirect(self.success_url)
            
        except Exception as e:
            logger.exception(f"Error in UpdatePasswordView of superadmin app: {e}")
            return redirect(self.redirect_url)
        

class UpdateUserDetailView(SettingsView, UpdateView):
    model = User
    success_url = redirect_url = reverse_lazy('superadmin:settings')

    def post(self, request, *args, **kwargs):
        try:
            username = request.POST.get("username")
            email = request.POST.get("email")

            username = username.strip() if username else None
            email = email.strip() if email else None    
            
            required_fields = {
                "Username": username,
                "Email": email
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! Field {key} is required")
                    return redirect(self.redirect_url)
                
            user = request.user

            user.username = username
            user.email = email
            user.save()

            messages.success(request, "Success! User detail updation successfull")
            return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in UpdateUserDetailView in superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")
            return redirect(self.redirect_url)
        

# Custome Pages
class AddCustomPageView(AdminBaseView, TemplateView):
    template_name = "custom_pages/add.html"    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["page_types"] = ("About Us", "Contact Us", "FAQ", "Privacy Policy", "Terms And Conditions", "Shipping And Delivery Policy", "Cancellation And Refund Policy")
            context["companies"] = Company.objects.all().order_by("-updated")
            context["states"] = UniqueState.objects.all().order_by("-updated")
            context["custom_page"] = True
            context["about_us_form"] = AboutUsContentForm
        except Exception as e:
            logger.exception(f"Error in getting context data of AddCustomPageView of superadmin app: {e}")
        
        return context
    

class AddAboutUsPageView(AddCustomPageView, CreateView):
    model = AboutUs
    # fields = ["company", "content"]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')
    form_class = AboutUsContentForm

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            company_slug = request.POST.get("company")
            content = request.POST.get("content")        

            company_slug = company_slug.strip() if company_slug else None
            content = content.strip() if content else None                      

            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)

            company = get_object_or_404(Company, slug = company_slug) if company_slug else None

            self.model.objects.update_or_create(
                company = company, 
                defaults = {"content": content}
                )
            
            messages.success(request, f"Success! Created About Us")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddAboutUsPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred.")

        return redirect(self.redirect_url)
    

class UpdateAboutUsPageView(AdminBaseView, UpdateView):
    model = AboutUs
    redirect_url = success_url = reverse_lazy("superadmin:about_us")
    slug_url_kwarg = "about_us_slug"
    form_class = AboutUsContentForm
    template_name = "custom_pages/update_about_us.html"
    context_object_name = "about_us"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["current_custom_page"] = "About Us"

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        content = None

        if form.is_valid():
            cleaned_form = form.cleaned_data
            content = cleaned_form.get("content")

        if not content:
            messages.error(self.request, "Failed! Content is required")
            return redirect(self.redirect_url)

        self.object = self.get_object()

        self.object.content = content
        self.object.save()

        company_name = self.object.company.name if self.object.company else "BZIndia"

        messages.success(
            self.request, f"Success! Updated About Us page of company: {company_name}"
        )
        return redirect(self.success_url)


class DeleteAboutUsPageView(AddCustomPageView, UpdateView):
    model = AboutUs
    redirect_url = success_url = reverse_lazy("superadmin:about_us")
    slug_url_kwarg = "about_us_slug"
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()

            messages.success(request, "Success! About Us Deleted.")
            return redirect(self.success_url)
        except Http404:
            messages.error(request, "Failed! Invalid About Us.")

        except Exception as e:
            logger.exception(f"Error in DeleteAboutUsPageView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.redirect_url)

    

class AddContactUsPageView(AddCustomPageView, CreateView):
    model = ContactUs
    fields = [
        "company", "email", "tel", "mobile", "address", 
        "provide_query", "place", "district",
        "state", "pincode", "web", "lat", "lon"
        ]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')    

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")

            email = request.POST.get("email")
            tel = request.POST.get("tel")
            mobile = clean_string(request.POST.get("mobile", ""))

            web = clean_string(request.POST.get("web", ""))

            provide_query = request.POST.get("provide_query")

            address = clean_string(request.POST.get("address", ""))

            place_slug = request.POST.get("place")
            district_slug = request.POST.get("district")
            state_slug = request.POST.get("state")
            pincode = request.POST.get("pincode")

            lat = request.POST.get("lat")
            lon = request.POST.get("lon")

            company_slug = company_slug.strip() if company_slug else None

            email = email.strip() if email else None
            tel = tel.strip() if tel else None

            pincode = pincode.strip() if pincode else None            

            lat = lat.strip() if lat else None
            lon = lon.strip() if lon else None

            if not email:
                messages.error(request, "Failed! Email is required")
                return redirect(self.redirect_url)
            
            if not tel:
                messages.error(request, "Failed! Phone is required")
                return redirect(self.redirect_url)

            company = get_object_or_404(Company, slug = company_slug) if company_slug else None

            state = district = place = None

            if state_slug:
                state = get_state(state_slug)

                if not state:
                    messages.error(self.request, "Invalid State")
                    return redirect(self.redirect_url)

            if district_slug:
                district = get_district(district_slug)

                if not district:
                    messages.error(self.request, "Invalid District")
                    return redirect(self.redirect_url)

            if place_slug:
                place = get_place(place_slug)

                if not place:
                    messages.error(self.request, "Invalid Place")
                    return redirect(self.redirect_url)

            self.model.objects.create(
                company = company, email = email, tel = tel, mobile = mobile, 
                provide_query = True if provide_query else False,
                place = place, district = district, state = state, pincode = pincode,
                lat = lat, lon = lon, address = address, web = web
                )
            
            messages.success(request, f"Success! Created Contact Us")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddContactUsPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred.")

        return redirect(self.redirect_url)


class UpdateContactUsPageView(AdminBaseView, UpdateView):
    model = ContactUs
    redirect_url = success_url = reverse_lazy("superadmin:contact_us")
    slug_url_kwarg = "contact_us_slug"
    template_name = "custom_pages/update_contact_us.html"
    context_object_name = "contact_us"
    fields = [
        "company", "email", "tel", "mobile", "address", 
        "provide_query", "place", "district",
        "state", "pincode", "web", "lat", "lon"
        ]  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()

        context["current_custom_page"] = "Contact Us"
        context["states"] = UniqueState.objects.all()
        context["districts"] = UniqueDistrict.objects.filter(state = self.object.state)
        context["places"] = UniquePlace.objects.filter(state = self.object.state, district = self.object.district)

        return context

    def post(self, request, *args, **kwargs):
        try:
            email = clean_string(request.POST.get("email", ""))
            tel = clean_string(request.POST.get("tel", ""))
            mobile = clean_string(request.POST.get("mobile", ""))

            web = clean_string(request.POST.get("web", ""))

            provide_query = request.POST.get("provide_query")

            address = clean_string(request.POST.get("address", ""))

            place_slug = clean_string(request.POST.get("place", ""))
            district_slug = clean_string(request.POST.get("district", ""))
            state_slug = clean_string(request.POST.get("state", ""))
            pincode = clean_string(request.POST.get("pincode", ""))

            lat = clean_string(request.POST.get("lat", ""))
            lon = clean_string(request.POST.get("lon", ""))

            if not email:
                messages.error(request, "Failed! Email is required")
                return redirect(self.redirect_url)
            
            if not tel:
                messages.error(request, "Failed! Phone is required")
                return redirect(self.redirect_url)

            state = district = place = None

            if state_slug:
                state = get_state(state_slug)

                if not state:
                    messages.error(self.request, "Invalid State")
                    return redirect(self.redirect_url)

            if district_slug:
                district = get_district(district_slug)

                if not district:
                    messages.error(self.request, "Invalid District")
                    return redirect(self.redirect_url)

            if place_slug:
                place = get_place(place_slug)

                if not place:
                    messages.error(self.request, "Invalid Place")
                    return redirect(self.redirect_url)

            self.object = self.get_object()

            self.object.email = email
            self.object.tel = tel
            self.object.mobile = mobile
            self.object.provide_query = True if provide_query else False
            self.object.place = place
            self.object.district = district
            self.object.state = state
            self.object.pincode = pincode
            self.object.lat = lat
            self.object.lon = lon
            self.object.address = address
            self.object.web = web

            self.object.save()
            
            messages.success(request, f"Success! Updated Contact Us")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in UpdateContactUsPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred.")

        return redirect(self.redirect_url)


class DeleteContactUsPageView(AddCustomPageView, UpdateView):
    model = ContactUs
    redirect_url = success_url = reverse_lazy("superadmin:contact_us")
    slug_url_kwarg = "contact_us_slug"
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()

            messages.success(request, "Success! Contact Us Deleted.")
            return redirect(self.success_url)
        except Http404:
            messages.error(request, "Failed! Invalid Contact Us.")

        except Exception as e:
            logger.exception(f"Error in DeleteContactUsPageView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.redirect_url)
    

class AddFaqPageView(AddCustomPageView, CreateView):
    model = FAQ
    form_class = FaqForm
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            company_slug = request.POST.get("company")

            question = clean_string(request.POST.get("question", ""))
            short_answer = clean_string(request.POST.get("short_answer", ""))
            answer = clean_string(request.POST.get("answer", ""))

            company_slug = company_slug.strip() if company_slug else None           

            if not question:
                messages.error(request, "Failed! Question is required")
                return redirect(self.redirect_url)
            
            if not short_answer:
                messages.error(request, "Failed! Short Answer is required")
                return redirect(self.redirect_url)                    

            if not answer:
                messages.error(request, "Failed! Answer is required")
                return redirect(self.redirect_url)            

            company = get_object_or_404(Company, slug = company_slug) if company_slug else None

            self.model.objects.update_or_create(
                company = company, question = question,
                defaults = {"answer": answer, "short_answer": short_answer}
                )
            
            messages.success(request, f"Success! Created FAQ.")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddFaqPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred.")

        return redirect(self.redirect_url)


class UpdateFaqPageView(AdminBaseView, UpdateView):
    model = FAQ
    redirect_url = success_url = reverse_lazy("superadmin:faq")
    slug_url_kwarg = "faq_slug"
    template_name = "custom_pages/update_faq.html"
    context_object_name = "faq"
    form_class = FaqForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()

        context["current_custom_page"] = "FAQ"        

        return context    

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        question = clean_string(self.request.POST.get("question", ""))
        short_answer = clean_string(self.request.POST.get("short_answer", ""))

        answer = None

        if form.is_valid():
            cleaned_form = form.cleaned_data
            answer = cleaned_form.get("answer")

        if not question:
            messages.error(self.request, "Failed! Question is required")
            return redirect(self.redirect_url)

        if not short_answer:
            messages.error(self.request, "Failed! Short Answer is required")
            return redirect(self.redirect_url)

        if not answer:
            messages.error(self.request, "Failed! Answer is required")
            return redirect(self.redirect_url)

        self.object = self.get_object()

        self.object.question = question
        self.object.short_answer = short_answer
        self.object.answer = answer
        self.object.save()

        company_name = self.object.company.name if self.object.company else "BZIndia"

        messages.success(
            self.request, f"Success! Updated FAQ page of company: {company_name}"
        )
        return redirect(self.success_url)


class DeleteFaqPageView(AddCustomPageView, UpdateView):
    model = FAQ
    redirect_url = success_url = reverse_lazy("superadmin:faq")
    slug_url_kwarg = "faq_slug"
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()

            messages.success(request, "Success! FAQ Deleted.")
            return redirect(self.success_url)
        except Http404:
            messages.error(request, "Failed! Invalid FAQ.")

        except Exception as e:
            logger.exception(f"Error in DeleteFaqPageView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.redirect_url)
    

class AddPrivacyPolicyPageView(AddCustomPageView, CreateView):
    model = PrivacyPolicy
    fields = [
        "company", "content", "support_email", "effective_date"        
        ]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")

            content = request.POST.get("content")
            support_email = request.POST.get("support_email")
            effective_date = request.POST.get("effective_date")        

            company_slug = company_slug.strip() if company_slug else None

            content = content.strip() if content else None
            support_email = support_email.strip() if support_email else None
            effective_date = effective_date.strip() if effective_date else None            
            
            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)

            if not effective_date:
                messages.error(request, "Failed! Effective date is required")
                return redirect(self.redirect_url)            

            company = get_object_or_404(Company, slug = company_slug) if company_slug else None

            self.model.objects.update_or_create(
                company = company, 
                defaults = {
                    "effective_date": effective_date, "content": content,
                    "support_email": support_email
                    }
                )
            
            messages.success(request, f"Success! Created Privacy Policy.")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddPrivacyPolicyPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred.")

        return redirect(self.redirect_url)


class UpdatePrivacyPolicyPageView(AdminBaseView, UpdateView):
    model = PrivacyPolicy
    redirect_url = success_url = reverse_lazy("superadmin:privacy_policies")
    slug_url_kwarg = "privacy_policy_slug"
    template_name = "custom_pages/update_privacy_policy.html"
    context_object_name = "privacy_policy"
    form_class = PrivacyPolicyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["current_custom_page"] = "Privacy Policy"        

        return context    

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            support_email = request.POST.get("support_email")
            effective_date = clean_string(request.POST.get("effective_date", ""))                      
            
            content = None
            if form.is_valid():
                cleaned_form = form.cleaned_data
                content = cleaned_form.get("content")

            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)

            if not effective_date:
                messages.error(request, "Failed! Effective date is required")
                return redirect(self.redirect_url)   

            self.object = self.get_object()
            self.object.content = content
            self.object.effective_date = effective_date
            self.object.support_email = support_email
            self.object.save()
            
            messages.success(request, f"Success! Updated Privacy Policy.")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in UpdatePrivacyPolicyPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred.")

        return redirect(self.redirect_url)
    

class DeletePrivacyPolicyPageView(AddCustomPageView, UpdateView):
    model = PrivacyPolicy
    redirect_url = success_url = reverse_lazy("superadmin:privacy_policies")
    slug_url_kwarg = "privacy_policy_slug"
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()

            messages.success(request, "Success! Privacy Policy Deleted.")
            return redirect(self.success_url)
        except Http404:
            messages.error(request, "Failed! Invalid Privacy Policy.")

        except Exception as e:
            logger.exception(f"Error in DeletePrivacyPolicyPageView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.redirect_url)


class AddTermsAndConditionsPageView(AddCustomPageView, CreateView):
    model = TermsAndCondition
    fields = ["company", "content", "version", "effective_date"]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")

            content = request.POST.get("content")
            version = request.POST.get("version")
            effective_date = request.POST.get("effective_date")

            company_slug = company_slug.strip() if company_slug else None

            content = content.strip() if content else None
            version = version.strip() if version else None

            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)
            
            if not version:
                messages.error(request, "Failed! Version is required")
                return redirect(self.redirect_url)
            
            if not effective_date:
                messages.error(request, "Failed! Effective date is required")
                return redirect(self.redirect_url)

            company = get_object_or_404(Company, slug = company_slug) if company_slug else None

            self.model.objects.update_or_create(
                company = company,
                defaults = {
                    "content": content,
                    "version": version,
                    "effective_date": effective_date
                    }
                )
            
            messages.success(request, f"Success! Created Terms and Conditions.")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddTermsAndConditionsPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred.")

        return redirect(self.redirect_url)


class UpdateTermsAndConditionsPageView(AdminBaseView, UpdateView):
    model = TermsAndCondition
    redirect_url = success_url = reverse_lazy("superadmin:terms_and_conditions")
    slug_url_kwarg = "terms_and_condition_slug"
    template_name = "custom_pages/update_terms_and_conditions.html"
    context_object_name = "terms_and_conditions"
    form_class = TermsAndConditionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["current_custom_page"] = "Terms And Conditions"        

        return context    

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            version = clean_string(request.POST.get("version", ""))
            effective_date = clean_string(request.POST.get("effective_date", ""))            

            content = None

            if form.is_valid():
                cleaned_form = form.cleaned_data
                content = cleaned_form.get("content")

            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)
            
            if not version:
                messages.error(request, "Failed! Version is required")
                return redirect(self.redirect_url)
            
            if not effective_date:
                messages.error(request, "Failed! Effective date is required")
                return redirect(self.redirect_url)
            
            self.object = self.get_object()

            self.object.content = content
            self.object.version = version
            self.object.effective_date = effective_date
            self.object.save()
            
            messages.success(request, f"Success! Updated Terms And Conditions.")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in UpdateTermsAndConditionsPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred.")

        return redirect(self.redirect_url)


class DeleteTermsAndConditionPageView(AddCustomPageView, UpdateView):
    model = TermsAndCondition
    redirect_url = success_url = reverse_lazy("superadmin:terms_and_conditions")
    slug_url_kwarg = "terms_and_condition_slug"
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()

            messages.success(request, "Success! Terms And Condition Deleted.")
            return redirect(self.success_url)
        except Http404:
            messages.error(request, "Failed! Invalid Terms And Condition.")

        except Exception as e:
            logger.exception(f"Error in DeleteTermsAndConditionPageView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.redirect_url)
    

class BaseCustomPageView(AdminBaseView, ListView):
    model = AboutUs
    template_name = "custom_pages/list.html"    
    queryset = model.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["custom_page"] = True
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseCustomPageView in superadmin app: {e}")
        return context
    

class ListAboutUsView(BaseCustomPageView, ListView):
    model = AboutUs
    queryset = model.objects.all().order_by("-updated")
    context_object_name = "about_us_objects"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "About Us"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListAboutUsView in superadmin app: {e}")
        return context
    

class ListContactUsView(BaseCustomPageView, ListView):
    model = ContactUs
    queryset = model.objects.all().order_by("-updated")
    context_object_name = "contact_us_objects"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Contact Us"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListContactUsView in superadmin app: {e}")
        return context
    

class ListFaqView(BaseCustomPageView, ListView):
    model = FAQ
    queryset = model.objects.all().order_by("-updated")
    context_object_name = "faqs"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "FAQ"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListFaqView in superadmin app: {e}")
        return context
    

class ListPrivacyPolicyView(BaseCustomPageView, ListView):
    model = PrivacyPolicy
    queryset = model.objects.all().order_by("-updated")
    context_object_name = "privacy_policies"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Privacy Policy"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListPrivacyPolicyView in superadmin app: {e}")
        return context
    

class ListPrivacyPolicyView(BaseCustomPageView, ListView):
    model = PrivacyPolicy
    queryset = model.objects.all().order_by("-updated")
    context_object_name = "privacy_policies"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Privacy Policy"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListPrivacyPolicyView in superadmin app: {e}")
        return context


class ListTermsAndConditionsView(BaseCustomPageView, ListView):
    model = TermsAndCondition
    queryset = model.objects.all()
    context_object_name = "terms_and_conditions"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Terms And Conditions"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListTermsAndConditionsView in superadmin app: {e}")
        return context
    

class AddShippingAndDeliveryPolicyPageView(AddCustomPageView, CreateView):
    model = ShippingAndDeliveryPolicy
    fields = ["company", "content"]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")
            content = request.POST.get("content")        

            company_slug = company_slug.strip() if company_slug else None
            content = content.strip() if content else None                      

            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)

            company = get_object_or_404(Company, slug = company_slug) if company_slug else None

            self.model.objects.update_or_create(
                company = company, 
                defaults = {"content": content}
                )
            
            messages.success(request, f"Success! Created Shipping and Delivery Policy")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddShippingAndDeliveryPolicyPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred.")

        return redirect(self.redirect_url)


class DeleteShippingAndDeliveryPolicyPageView(AddCustomPageView, UpdateView):
    model = ShippingAndDeliveryPolicy
    redirect_url = success_url = reverse_lazy("superadmin:shipping_and_delivery_policies")
    slug_url_kwarg = "shipping_and_delivery_policy_slug"
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()

            messages.success(request, "Success! Shipping And Delivery Policy Deleted.")
            return redirect(self.success_url)
        except Http404:
            messages.error(request, "Failed! Invalid Shipping And Delivery Policy.")

        except Exception as e:
            logger.exception(f"Error in DeleteShippingAndDeliveryPolicyPageView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.redirect_url)
    

class ListShippingAndDeliveryPolicyView(BaseCustomPageView, ListView):
    model = ShippingAndDeliveryPolicy
    queryset = model.objects.all().order_by("-updated")
    context_object_name = "shipping_and_delivery_policies"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Shipping And Delivery Policy"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListShippingAndDeliveryPolicyView in superadmin app: {e}")
        return context
    

class AddCancellationAndRefundPolicyPageView(AddCustomPageView, CreateView):
    model = CancellationAndRefundPolicy
    fields = ["company", "content"]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")
            content = request.POST.get("content")        

            company_slug = company_slug.strip() if company_slug else None
            content = content.strip() if content else None

            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)

            company = get_object_or_404(Company, slug = company_slug) if company_slug else None

            self.model.objects.update_or_create(
                company = company, 
                defaults = {"content": content}
                )
            
            messages.success(request, f"Success! Created Cancellation and Refund Policy")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddCancellationAndRefundPolicyPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred.")

        return redirect(self.redirect_url)


class DeleteCancellationAndRefundPolicyPageView(AddCustomPageView, UpdateView):
    model = CancellationAndRefundPolicy
    redirect_url = success_url = reverse_lazy("superadmin:cancellation_and_refund_policies")
    slug_url_kwarg = "cancellation_and_refund_policy_slug"
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()

            messages.success(request, "Success! Cancellation And Refund Policy Deleted.")
            return redirect(self.success_url)
        except Http404:
            messages.error(request, "Failed! Invalid Cancellation And Refund Policy.")

        except Exception as e:
            logger.exception(f"Error in DeleteCancellationAndRefundPolicyPageView of superadmin: {e}")
            messages.error(request, "Failed! An unexpected error occured.")

        return redirect(self.redirect_url)


class ListCancellationAndRefundPolicyView(BaseCustomPageView, ListView):
    model = CancellationAndRefundPolicy
    queryset = model.objects.all().order_by("-updated")
    context_object_name = "Cancellation_and_refund_policies"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Cancellation And Refund Policy"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListCancellationAndRefundPolicyView in superadmin app: {e}")
        return context


# Clients
class BaseClientView(BaseCompanyView, View):
    model = Client
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["client_page"] = context["company_page"] = True
        context["current_company"] = self.get_current_company()
        context["company_type_page"] = False
        return context
    
    def get_success_url(self):
        try:
            if self.slug_url_kwarg:
                return reverse_lazy("superadmin:clients", kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of BaseClientView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_object(self):
        company_slug = self.kwargs.get(self.slug_url_kwarg)
        client_slug = self.kwargs.get('client_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = client_slug)
    

class AddClientView(BaseClientView, CreateView):    
    template_name = "clients/add.html"
    fields = ["company", "name", "image", "order"]

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_client", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of AddClientView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_client_page"] = True        
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            order = request.POST.get("order", 0)

            name = name.strip() if name else None

            if not name or not image:
                message = "Failed! Name is required"
                if name:
                    message = "Failed! Image is required"
                
                messages.error(request, message)
                return redirect(self.get_redirect_url())
            
            if self.model.objects.filter(company = company, name = name).exists():
                messages.warning(request, "Similar client already exists")
                return redirect(self.get_redirect_url())
            
            self.model.objects.create(company = company, name = name, image = image, order = order)
            messages.success(request, "Success! Client Created")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddClientView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.get_redirect_url())
        

class ClientListView(BaseClientView, ListView):
    template_name = "clients/list.html"
    context_object_name = "clients"
    queryset = Client.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["client_slider"] = ClientSlider.objects.filter(company__slug = self.kwargs.get('slug')).first()
        return context
    
    def get_queryset(self):
        company_slug = self.kwargs.get('slug')
        if company_slug:
            return self.model.objects.filter(company__slug = company_slug).order_by("order")
        
        return self.queryset


class UpdateClientView(BaseClientView, UpdateView):    
    fields = ["name", "image", "order"]
    slug_url_kwarg = 'slug'        

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            order = request.POST.get("order", 0)

            name = name.strip() if name else None

            if not name:
                messages.error(request, "Failed! Name is required")
                return redirect(self.get_redirect_url())

            if not image and not self.object.image:
                messages.error(request, "Failed! Image is required")
                return redirect(self.get_redirect_url())     
            
            similar_client = self.model.objects.filter(company = self.object.company, name = name).first()

            if similar_client:
                dublicate_error_msg = ""

                if similar_client.slug == self.object.slug:
                    if not image and not order:
                        dublicate_error_msg = "No changes detected"
                else:
                    dublicate_error_msg = "Similar client already exists"

                if dublicate_error_msg:
                    messages.warning(request, dublicate_error_msg)
                    return redirect(self.get_redirect_url())
            
            self.object.name = name
            self.object.order = order

            if image:
                self.object.image = image

            self.object.save()

            messages.success(request, "Success! Client Updated")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid Client")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateClientView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
        

class DeleteClientView(BaseClientView, DeleteView):
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Client Deleted")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid client")

        except Exception as e:
            logger.exception(f"Error in delete function of DeleteClientView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class UpdateClientSliderHeadingView(BaseCompanyView, CreateView):    
    model = ClientSlider
    fields = ["heading"]
    slug_url_kwarg = 'slug'
    redirect_url = success_url = reverse_lazy("superadmin:home")       

    def get_success_url(self):
        try:
            if self.slug_url_kwarg:
                return reverse_lazy("superadmin:clients", kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of UpdateClientSliderHeadingView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()

    def post(self, request, *args, **kwargs):
        try:            

            heading = clean_string(request.POST.get("heading", ""))            

            if not heading:
                messages.error(request, "Failed! Heading is required")
                return redirect(self.get_redirect_url())

            company = self.get_current_company()

            if not company:
                messages.error(request, "Failed! Invalid Company")
                return redirect(self.get_redirect_url())

            self.model.objects.create(
                company = company, heading = heading
            )

            messages.success(request, "Success! Client Slider Heading Updated")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid Client")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateClientSliderHeadingView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

# Student Testimonials
class BaseStudentTestimonialView(BaseEducationCompanyView):
    model = StudentTestimonial
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["testimonial_page"] = context["company_page"] = True
        context["current_company"] = self.get_current_company()
        context["company_type_page"] = False
        return context
    
    def get_success_url(self):
        try:
            if self.slug_url_kwarg:
                return reverse_lazy("superadmin:student_testimonials", kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of BaseStudentTestimonialView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_object(self):
        company_slug = self.kwargs.get(self.slug_url_kwarg)
        testimonial_slug = self.kwargs.get('testimonial_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = testimonial_slug)
    
    def get_course(self, course_slug):
        try:
            company = self.get_current_company()
            return get_object_or_404(Course, company = company, slug = course_slug)
        except Http404:
            return None
        
    def get_place(self, place_slug):
        try:
            return get_object_or_404(UniquePlace, slug = place_slug)
        except Http404:
            return None
    

class AddStudentTestimonialView(BaseStudentTestimonialView, CreateView):    
    template_name = "admin_student_testimonials/add.html"
    fields = ["company", "name", "image", "course", "place", "text", "rating", "order"]

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_student_testimonial", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of AddStudentTestimonialView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["add_testimonial_page"] = True
        context["ratings"] = list(range(1,6))

        context["programs"] = Program.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg)).order_by("-updated")
        context["states"] = UniqueState.objects.all().order_by('name')
        
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

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
                        
            if self.model.objects.filter(
                company = company, name = name, course = course, place = place
                ).exists():

                messages.warning(request, "Similar testimonial already exists")
                return redirect(self.get_redirect_url())
            
            self.model.objects.create(
                company = company, name = name, image = image, course = course, place = place,
                text = text, rating = rating, order = order
            )

            messages.success(request, "Success! Testimonial Created")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddStudentTestimonialView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.get_redirect_url())


class StudentTestimonialListView(BaseStudentTestimonialView, ListView):
    template_name = "admin_student_testimonials/list.html"
    context_object_name = "testimonials"
    queryset = StudentTestimonial.objects.none()
    
    def get_queryset(self):
        company_slug = self.kwargs.get('slug')
        if company_slug:
            return self.model.objects.filter(company__slug = company_slug).order_by("order")
        
        return self.queryset
    

class UpdateStudentTestimonialView(BaseStudentTestimonialView, UpdateView):    
    fields = ["name", "image", "course", "place", "text", "rating", "order"]
    template_name = "admin_student_testimonials/update.html"
    slug_url_kwarg = 'slug'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["update_testimonial_page"] = True
        context["ratings"] = list(range(1,6))

        context["programs"] = Program.objects.filter(company = self.company).order_by("-updated")
        context["courses"] = Course.objects.filter(program = self.object.course.program).order_by("-updated")
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
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateStudentTestimonialView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class DeleteStudentTestimonialView(BaseStudentTestimonialView, DeleteView):
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Testimonial Deleted")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in delete function of DeleteStudentTestimonialView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    
# General Testimonial
class BaseTestimonialView(BaseCompanyView):
    model = Testimonial
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["testimonial_page"] = context["company_page"] = True
        context["current_company"] = self.get_current_company()
        context["company_type_page"] = False
        return context
    
    def get_success_url(self):
        try:
            if self.slug_url_kwarg:
                return reverse_lazy("superadmin:testimonials", kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of BaseTestimonialView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_object(self):
        company_slug = self.kwargs.get(self.slug_url_kwarg)
        testimonial_slug = self.kwargs.get('testimonial_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = testimonial_slug)    
        
    def get_place(self, place_slug):
        try:
            return get_object_or_404(UniquePlace, slug = place_slug)
        except Http404:
            return None
    

class AddTestimonialView(BaseTestimonialView, CreateView):    
    template_name = "admin_testimonials/add.html"
    fields = ["company", "name", "image", "company", "place", "text", "rating", "order"]

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_testimonial", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of AddTestimonialView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["add_testimonial_page"] = True
        context["ratings"] = list(range(1,6))

        context["states"] = UniqueState.objects.all().order_by('name')
        
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

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
                    return redirect(self.get_redirect_url())
                
            place = self.get_place(place_slug)

            if not place:                
                messages.error(request, "Invalid Place")
                return redirect(self.get_redirect_url())
                        
            if self.model.objects.filter(
                company = company, name = name, client_company = client_company, place = place
                ).exists():

                messages.warning(request, "Similar testimonial already exists")
                return redirect(self.get_redirect_url())
            
            self.model.objects.create(
                company = company, name = name, image = image, client_company = client_company, place = place,
                text = text, rating = rating, order = order
            )

            messages.success(request, "Success! Testimonial Created")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddTestimonialView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.get_redirect_url())


class TestimonialListView(BaseTestimonialView, ListView):
    template_name = "admin_testimonials/list.html"
    context_object_name = "testimonials"
    queryset = Testimonial.objects.none()
    
    def get_queryset(self):
        company_slug = self.kwargs.get('slug')

        if company_slug:
            return self.model.objects.filter(company = self.get_current_company()).order_by("order")        
        
        return self.queryset
    

class UpdateTestimonialView(BaseTestimonialView, UpdateView):    
    fields = ["name", "image", "company", "place", "text", "rating", "order"]
    template_name = "admin_testimonials/update.html"
    slug_url_kwarg = 'slug'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["update_testimonial_page"] = True
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
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateTestimonialView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class DeleteTestimonialView(BaseTestimonialView, DeleteView):
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Testimonial Deleted")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in delete function of DeleteTestimonialView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

# Blogs
class BaseBlogView(AdminBaseView):
    model = Blog
    success_url = redirect_url = reverse_lazy('superadmin:blogs')
    slug_url_kwarg = 'slug'    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blog_page"] = True
        return context    

    def get_company(self, company_slug, company_type):
        try:
            return get_object_or_404(Company, slug = company_slug, type__name = company_type)
        except Http404:
            return None    


class AddBlogView(BaseBlogView, CreateView):
    template_name = "admin_blogs/add.html"
    success_url = redirect_url = reverse_lazy('superadmin:add_blogs')
    form_class = BlogContentForm    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_blog_page"] = True
        context["types"] = ("General", "Education", "Product", "Registration", "Service")
        context["tags"] = MetaTag.objects.all().order_by("-updated")

        return context

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            title = clean_string(request.POST.get("title", ""))
            image = request.FILES.get("image")
            blog_type = clean_string(request.POST.get("type", ""))

            company_slug = request.POST.get("company")          

            meta_tags = request.POST.getlist("meta_tag")
            meta_description = clean_string(request.POST.get("meta_description", ""))
            summary = clean_string(request.POST.get("summary", ""))
            
            content = None

            if form.is_valid():
                cleaned_form = form.cleaned_data
                content = cleaned_form.get("content")

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]            

            required_fields = {
                "Title": title,
                "Image": image,
                "Type": blog_type,
                "Company": company_slug if blog_type != "General" else True,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description,
                "Summary": summary,
                "Content": content,
            }                    

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)

            company = self.get_company(company_slug, blog_type) if blog_type != "General" else None                                
                
            updating_meta_tags = []
            with transaction.atomic():
                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)                

                blog = Blog.objects.create(
                            title = title, image = image, blog_type = blog_type, company = company,
                            content = content, summary = summary, meta_description = meta_description
                        )                

                if blog:
                    if meta_tags:
                        meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                        blog.meta_tags.set(meta_tag_objects)

                    messages.success(request, "Success! Created Blog")
                    return redirect(self.success_url)
        
        except Exception as e:
            logger.exception(f"Error in post function of AddBlogView in superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)


class ListBlogView(BaseBlogView, ListView):
    template_name = "admin_blogs/list.html"
    context_object_name = "blogs"
    queryset = Blog.objects.all().order_by("-updated")


class UpdateBlogView(BaseBlogView, UpdateView):
    template_name = "admin_blogs/update.html"
    success_url = redirect_url = reverse_lazy('superadmin:blogs')
    context_object_name = "blog"
    form_class = BlogContentForm    

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:update_blog', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url of UpdateBlogView in superadmin app: {e}")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["types"] = ("General", "Education", "Product", "Registration", "Service")

        self.object = self.get_object()

        context["companies"] = Company.objects.filter(type__name = self.object.blog_type).order_by("-updated") if self.object.blog_type != "General" else None        

        context["tags"] = MetaTag.objects.all().order_by("-updated")
 
        return context

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            title = clean_string(request.POST.get("title", ""))
            image = request.FILES.get("image")
            blog_type = clean_string(request.POST.get("type", ""))

            company_slug = request.POST.get("company")            

            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")
            summary = request.POST.get("summary")

            content = None

            if form.is_valid():
                cleaned_form = form.cleaned_data
                content = cleaned_form.get("content")

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            self.object = self.get_object()

            required_fields = {
                "Title": title,
                "Image": image if not self.object.image else True, 
                "Type": blog_type,
                "Company": company_slug if blog_type != "General" else True,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description,
                "Summary": summary,
                "Content": content,
            }

            if blog_type != "General":
                required_fields["Company"] = company_slug            

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            company = self.get_company(company_slug, blog_type) if blog_type != "General" else None

            if blog_type != "General" and not company:
                messages.error(request, "Invalid Company")
                return redirect(self.get_redirect_url())

            if blog_type != "General":
                invalid_message = ""                

                if invalid_message:
                    messages.error(request, invalid_message)
                    return redirect(self.get_redirect_url())

            updating_meta_tags = []
            with transaction.atomic():
                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                self.object.title = title
                self.object.blog_type = blog_type

                self.object.summary = summary
                self.object.content = content
                self.object.meta_description = meta_description
                self.object.company = company

                if image:
                    self.object.image = image                

                if Blog.objects.filter(
                    title = title, blog_type = blog_type, company = company
                    ).exclude(slug = self.object.slug).exists():
                    messages.warning(request, "Similar blog already exists")
                    return redirect(self.get_redirect_url())   

                self.object.save()                

                meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                self.object.meta_tags.set(meta_tag_objects)

                messages.success(request, "Success! Blog Updated")
                return redirect(self.success_url)   

            raise Exception                

        except Http404:
            messages.error(request, "Invalid Blog")        
        
        except Exception as e:
            logger.exception(f"Error in post function of UpdateBlogView in superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
        
        return redirect(self.get_redirect_url())


class DeleteBlogView(BaseBlogView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(Blog, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()
            messages.success(request, "Success! Blog Deleted")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Blog")
            return redirect(self.redirect_url)
        

class PublishBlogView(BaseBlogView, UpdateView):
    fields = ["is_published"]

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.is_published = True
            self.object.save()

            messages.success(request, "Success! Blog Published")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Blog")

        except Exception as e:
            logger.exception(f"Error in post function of PublishBlogView in superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)


class UnPublishBlogView(BaseBlogView, UpdateView):
    fields = ["is_published"]

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.is_published = False
            self.object.save()

            messages.success(request, "Success! Blog Unpublished")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Blog")

        except Exception as e:
            logger.exception(f"Error in post function of UnPublishBlogView in superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class BaseMetaTagView(AdminBaseView):
    model = MetaTag
    success_url = redirect_url = reverse_lazy("superadmin:meta_tags")
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["meta_tag_page"] = True

        return context


class AddMetaTagView(BaseMetaTagView, CreateView):
    template_name = "meta_tag/add.html"
    form_class = MetaTagDescriptionForm

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")            
            meta_title = request.POST.get("meta_title")
            meta_description = request.POST.get("meta_description")

            name = name.strip() if name else None
            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            if not name or not meta_description:
                required_field = "Meta Description" if "Name" else "Name"

                messages.error(request, f"Failed! {required_field} is required")
                return redirect(self.redirect_url)
            
            form = self.get_form()

            description = form.cleaned_data.get("description").strip() if form.is_valid() else None            

            with transaction.atomic():

                meta_tag, created = self.model.objects.get_or_create(name = name, defaults = {"description": description, "meta_title": meta_title, "meta_description": meta_description})

                if not created:
                    messages.warning(request, "Failed! Similar meta tag already exists")
                    return redirect(self.redirect_url)

                messages.success(request, "Success! Created Meta Tag")
                return redirect(self.success_url)
            
        except Exception as e:
            logger.exception(f"Error in post function of AddMetaTagView")
            
        messages.error(request, "Failed! An unexpected error occurred")
        return redirect(self.redirect_url)
    

class MetaTagListView(BaseMetaTagView, ListView):
    queryset = MetaTag.objects.all().order_by("-updated")
    template_name = "meta_tag/list.html"
    context_object_name = "meta_tags"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["list_meta_tag_page"] = True

        return context


class UpdateMetaTagView(BaseMetaTagView, UpdateView):
    template_name = "meta_tag/update.html"
    form_class = MetaTagDescriptionForm
    context_object_name = "meta_tag"

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")            
            meta_title = request.POST.get("meta_title")
            meta_description = request.POST.get("meta_description")

            name = name.strip() if name else None
            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            if not name or not meta_description:
                required_field = "Meta Description" if "Name" else "Name"

                messages.error(request, f"Failed! {required_field} is required")
                return redirect(self.redirect_url)

            form = self.get_form()
            description = form.cleaned_data.get("description").strip() if form.is_valid() else None            

            self.object = self.get_object()
            
            with transaction.atomic():
                if MetaTag.objects.filter(name = name).exclude(slug = self.object.slug).exists():
                    messages.warning(request, "Failed! Similar meta tag already exists")
                    return redirect(self.redirect_url)

                self.object.name = name
                self.object.meta_title = meta_title
                self.object.meta_description = meta_description
                self.object.description = description
                self.object.save()    

                messages.success(request, "Success! Updated Meta Tag")
                return redirect(self.success_url)
            
        except Exception as e:
            logger.exception(f"Error in post function of UpdateMetaTagView: {e}")

        messages.error(request, "Failed! An unexpected error occurred")
        return redirect(self.redirect_url)


class DeleteMetaTagView(BaseMetaTagView, UpdateView):
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()

            messages.success(request, "Success! Deleted Meta Tag")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid Meta Tag")
            return redirect(self.redirect_url)
    

class HomeContentView(AdminBaseView, UpdateView):
    model = HomeContent
    template_name = "home_content/main_content.html"
    form_class = HomeContentForm
    success_url = redirect_url = reverse_lazy('superadmin:home_main_content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["home_content_page"] = True

        return context

    def get_object(self):
        existing_obj = self.model.objects.all().first()

        return existing_obj if existing_obj else None

    def post(self, request, *args, **kwargs):
        try:            
            self.object = self.get_object()

            form = self.get_form()

            if not form.is_valid():
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
                        return redirect(self.redirect_url)

            cleaned_form = form.cleaned_data

            title = clean_string(cleaned_form.get("title", ""))
            description = clean_string(cleaned_form.get("description"))
            meta_title = clean_string(cleaned_form.get("meta_title"))
            meta_description = clean_string(cleaned_form.get("meta_description"))
            footer_text = clean_string(cleaned_form.get("footer_text"))

            required_fields = {
                "Title": title,
                "Description": description,
                "Meta Title": meta_title,
                "Meta Description": meta_description
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed! {field_name} is required")
                    return redirect(self.redirect_url)

            with transaction.atomic():
                self.model.objects.all().delete()

                self.model.objects.create(
                    title = title, description = description, meta_title = meta_title, meta_description = meta_description, footer_text = footer_text
                )

                messages.success(request, "Success! Updated main content of home page")
                return redirect(self.success_url)


        except Exception as e:
            messages.error(request, "Failed! An expected error occurred")
            logger.exception(f"Error in post function of HomeContentView of superadmin app: {e}")

        return redirect(self.redirect_url)



# Functions
class UpdateCheckedServiceMultipageView(AdminBaseView, UpdateView):

    def post(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != 'XMLHttpRequest':
                return JsonResponse({"error": "Method not allowed"}, status=403)
            
            multipage_slug = request.POST.get("multipage_slug")

            if not multipage_slug:
                return JsonResponse({"error": "Bad Request."}, status=400)
            
            try:
                multipage = get_object_or_404(ServiceMultiPage, slug = multipage_slug)
            except Http404:
                return JsonResponse({"error": "Bad Request."}, status=400)

            with transaction.atomic():        
                ServiceMultiPage.objects.filter(company = multipage.company).update(home_footer_visibility = False)
                multipage.home_footer_visibility = True
                multipage.save()

                return JsonResponse({"success": True}, status=200)

            return JsonResponse({"error": "Internal Server Error."}, status=500)
            
        except Exception as e:
            logger.exception(f"Erron in UpdateCheckedServiceMultipageView: {e}")
            return JsonResponse({"error": "An unexpected error occured."}, status=500)

        
class UpdateCheckedCourseMultipageView(AdminBaseView, UpdateView):

    def post(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != 'XMLHttpRequest':
                return JsonResponse({"error": "Method not allowed"}, status=403)
            
            multipage_slug = request.POST.get("multipage_slug")

            if not multipage_slug:
                return JsonResponse({"error": "Bad Request."}, status=400)
            
            try:
                multipage = get_object_or_404(CourseMultiPage, slug = multipage_slug)
            except Http404:
                return JsonResponse({"error": "Bad Request."}, status=400)

            with transaction.atomic():        
                CourseMultiPage.objects.filter(company = multipage.company).update(home_footer_visibility = False)
                multipage.home_footer_visibility = True
                multipage.save()

                return JsonResponse({"success": True}, status=200)

            return JsonResponse({"error": "Internal Server Error."}, status=500)
            
        except Exception as e:
            logger.exception(f"Erron in UpdateCheckedCourseMultipageView: {e}")
            return JsonResponse({"error": "An unexpected error occured."}, status=500)


class UpdateCheckedRegistrationMultipageView(AdminBaseView, UpdateView):

    def post(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != 'XMLHttpRequest':
                return JsonResponse({"error": "Method not allowed"}, status=403)
            
            multipage_slug = request.POST.get("multipage_slug")

            if not multipage_slug:
                return JsonResponse({"error": "Bad Request."}, status=400)
            
            try:
                multipage = get_object_or_404(RegistrationMultiPage, slug = multipage_slug)
            except Http404:
                return JsonResponse({"error": "Bad Request."}, status=400)
            
            if multipage.registration_region != "all":
                return JsonResponse({"error": "Bad Request."}, status=400)

            with transaction.atomic():        
                RegistrationMultiPage.objects.filter(company = multipage.company).update(home_footer_visibility = False)

                multipage.home_footer_visibility = True
                multipage.save()

                return JsonResponse({"success": True}, status=200)

            return JsonResponse({"error": "Internal Server Error."}, status=500)
            
        except Exception as e:
            logger.exception(f"Erron in UpdateCheckedRegistrationMultipageView: {e}")
            return JsonResponse({"error": "An unexpected error occured."}, status=500)


class UpdateCheckedProductMultipageView(AdminBaseView, UpdateView):

    def post(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != 'XMLHttpRequest':
                return JsonResponse({"error": "Method not allowed"}, status=403)
            
            multipage_slug = request.POST.get("multipage_slug")

            if not multipage_slug:
                return JsonResponse({"error": "Bad Request."}, status=400)
            
            try:
                multipage = get_object_or_404(ProductMultiPage, slug = multipage_slug)
            except Http404:
                return JsonResponse({"error": "Bad Request."}, status=400)

            with transaction.atomic():        
                ProductMultiPage.objects.filter(company = multipage.company).update(home_footer_visibility = False)
                multipage.home_footer_visibility = True
                multipage.save()

                return JsonResponse({"success": True}, status=200)

            return JsonResponse({"error": "Internal Server Error."}, status=500)
            
        except Exception as e:
            logger.exception(f"Erron in UpdateCheckedProductMultipageView: {e}")
            return JsonResponse({"error": "An unexpected error occured."}, status=500)