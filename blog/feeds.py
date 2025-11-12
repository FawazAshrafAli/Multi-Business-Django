from django.http import HttpResponse
from django.contrib.syndication.views import Feed
from .models import Blog
from utility.custom_feed import ContentEncodedFeed
from home.models import HomeContent
from django.utils.text import Truncator
from django.utils.html import strip_tags
from django.shortcuts import get_object_or_404

class BlogFeed(Feed):
    feed_type = ContentEncodedFeed
    title = "BZ India - Find the top companies in India"
    link = "/blog/feed/"
    description = "BZ India blog feed updates."

    def get_title(self):
        detail = HomeContent.objects.first()
        return detail.meta_title if detail else self.title
    
    def get_description(self):
        detail = HomeContent.objects.first()
        return detail.meta_description if detail else self.description

    def items(self):
        return Blog.objects.filter(is_published=True).order_by("-created")[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary or item.short_description or "No summary available."

    def item_link(self, item):
        return f"/{item.company.slug}/blog/{item.slug}" if item.company else f"/blog/{item.slug}"

    def item_pubdate(self, item):
        return item.updated or item.created

    def item_guid(self, item):
        return str(item.pk) + "-" + item.slug

    def item_enclosure_url(self, item):
        return item.image.url if item.image else None

    def item_enclosure_length(self, item):
        return str(item.image.size) if item.image else "0"

    def item_enclosure_mime_type(self, item):
        return "image/jpeg" if item.image else None

    def item_categories(self, item):
        return [item.category if item else None]

    def item_author_name(self, item):
        return "BZ India"

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.content 
        }

# Optional: Serve with XML stylesheet
class StyledBlogFeed(BlogFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response


class BlogDetailFeed(Feed):
    feed_type = ContentEncodedFeed    

    def get_object(self, request, blog_slug):
        blog = get_object_or_404(Blog, slug=blog_slug)
        return blog

    def title(self, obj):
        return f"Updates on: {obj.title}"

    def link(self, obj):
        return f"/blog/{obj.slug}/feed/"

    def description(self, obj):
        return strip_tags(obj.content)[:200]  # Or obj.meta_description if available

    def items(self, obj):
        # You could use this to list related updates, comments, or just return the blog itself
        return [obj]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return Truncator(strip_tags(item.content)).words(50)

    def item_link(self, item):
        return f"/blog/{item.slug}/"

    def item_pubdate(self, item):
        return item.updated or item.created

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.content
        }

# Optional: Serve with XML stylesheet
class StyledBlogDetailFeed(BlogDetailFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
