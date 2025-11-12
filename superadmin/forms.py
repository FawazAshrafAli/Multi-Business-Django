from django import forms
from ckeditor.widgets import CKEditorWidget

from educational.models import MultiPage as CourseMultiPage, CourseDetail
from service.models import MultiPage as ServiceMultiPage, ServiceDetail
from product.models import MultiPage as ProductMultiPage, ProductDetailPage
from registration.models import MultiPage as RegistrationMultiPage, RegistrationDetailPage
from company.models import Company
from blog.models import Blog
from base.models import MetaTag
from home.models import HomeContent
from custom_pages.models import AboutUs, FAQ, PrivacyPolicy, TermsAndCondition

from ckeditor.widgets import CKEditorWidget

class HomeContentForm(forms.ModelForm):
    class Meta:
        model = HomeContent
        fields = ["title", "description", "meta_title", "meta_description", "footer_text"]

        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Title"}),
            "meta_title": forms.TextInput(attrs={"placeholder": "Meta Title"}),
            "meta_description": forms.Textarea(attrs={"placeholder": "Meta Description", "rows": 3})
        }


class CourseMultiPageDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = CourseMultiPage
        fields = ["description"]


class ServiceMultiPageDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = ServiceMultiPage
        fields = ["description"]


class ProductMultiPageDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = ProductMultiPage
        fields = ["description"]


class RegistrationMultiPageDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = RegistrationMultiPage
        fields = ["description"]


class CourseDetailDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = CourseDetail
        fields = ["description"]


class ServiceDetailDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = ServiceDetail
        fields = ["description"]


class ProductDetailDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = ProductDetailPage
        fields = ["description"]


class RegistrationDetailPageDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = RegistrationDetailPage
        fields = ["description"]


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["description", "footer_content"]


class BlogContentForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["content"]


class MetaTagDescriptionForm(forms.ModelForm):
    class Meta:
        model = MetaTag
        fields = ["description"]


class AboutUsContentForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = AboutUs
        fields = ["content"]


class FaqForm(forms.ModelForm):
    answer = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = FAQ
        fields = ["answer"]


class PrivacyPolicyForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = PrivacyPolicy
        fields = ["content"]


class TermsAndConditionForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = TermsAndCondition
        fields = ["content"]
