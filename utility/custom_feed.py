from django.utils.feedgenerator import Rss201rev2Feed

class ContentEncodedFeed(Rss201rev2Feed):
    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        if 'content_encoded' in item:
            handler.startElement("content:encoded", {})
            handler._write('<![CDATA[%s]]>' % item['content_encoded'])
            handler.endElement("content:encoded")
