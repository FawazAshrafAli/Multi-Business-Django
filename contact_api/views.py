from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Enquiry
from .serializers import EnquirySerializer

class EnquiryViewSet(viewsets.ModelViewSet):
    queryset = Enquiry.objects.all().order_by("-created")
    serializer_class = EnquirySerializer    

    def create(self, request, *args, **kwargs):
        response_data = {
            "success": False,
            "message": "Validation failed"
        }

        form_data = request.data

        print(form_data)

        serializer = self.get_serializer(data = form_data)                

        if serializer.is_valid():            
                
            serializer.save()

            response_data["success"] = True
            response_data["message"] = "Success! Enquiry Submitted"

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        response_data["error"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)



from bs4 import BeautifulSoup
import mailbox
import re

def extract_fields_from_html(html_body, fallback_name=None):
    soup = BeautifulSoup(html_body, 'html.parser')
    text = soup.get_text(separator='\n')

    data = {
        'name': fallback_name,
        'email': None,
        'phone_number': None,
        'selected_services': None,
        'turnover': None,
        'location': None,
        'requirements': None
    }

    # Patterns to extract fields
    patterns = {
        'email': r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        'phone_number': r"(?:\+91[-\s]?)?[6-9]\d{9}",
        'selected_services': r"Selected Services\s*:\s*(.*)",
        'turnover': r"Turnover\s*:\s*(.*)",
        'location': r"Location\s*:\s*(.*)",
        'requirements': r"Requirements\s*:\s*(.*)",
        'name': r"Name\s*:\s*(.*)",
    }

    # Search each line
    for line in text.splitlines():
        line = line.strip()

        for key, pattern in patterns.items():
            if data[key]:  # already found
                continue

            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                value = match.group(1) if match.groups() else match.group(0)
                data[key] = value.strip()

    return {k: v for k, v in data.items() if v}


def test_import():
    mbox_path = r"C:/Users/HP/Downloads/takeout-20250803T085947Z-1-001/Takeout/Mail/All mail Including Spam and Trash.mbox"
    mbox = mailbox.mbox(mbox_path)

    for i, message in enumerate(mbox):
        if i >= 5:  # limit for testing
            break

        try:
            subject = message['subject']
            sender = message['from']
            recipients = message['to']

            print(f"\nEmail #{i + 1}")
            print(f"Subject   : {subject}")
            print(f"From      : {sender}")
            print(f"To        : {recipients}")

            html_body = ''
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    content_disposition = part.get('Content-Disposition', '')

                    if content_type == 'text/html' and not content_disposition.startswith('attachment'):
                        charset = part.get_content_charset() or 'utf-8'
                        html_body = part.get_payload(decode=True).decode(charset, errors='replace')
                        break  # stop after first html part
            else:
                if message.get_content_type() == 'text/html':
                    charset = message.get_content_charset() or 'utf-8'
                    html_body = message.get_payload(decode=True).decode(charset, errors='replace')

            if html_body:
                structured_data = extract_fields_from_html(html_body, fallback_name=sender.split("<")[0].strip())
                print("Structured data:", structured_data)
            else:
                print("No HTML body found.")

        except Exception as e:
            print(f"Failed to read email #{i + 1}: {e}")
