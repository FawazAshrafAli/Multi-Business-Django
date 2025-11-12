import mailbox
import os
from email.utils import parsedate_to_datetime
from django.core.management.base import BaseCommand
from contact_api.models import Enquiry

class Command(BaseCommand):
    help = 'Import mbox file into Email model with resume support'

    def add_arguments(self, parser):
        parser.add_argument('mbox_path', type=str, help='Path to your .mbox file')
        parser.add_argument('--batch-size', type=int, default=10000)
        parser.add_argument('--progress-file', type=str, default='.mbox_progress')

    def handle(self, *args, **kwargs):
        mbox_path = kwargs['mbox_path']
        batch_size = kwargs['batch_size']
        progress_file = kwargs['progress_file']

        # Load mbox
        mbox = mailbox.mbox(mbox_path)

        # Resume support
        start_index = 0
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                start_index = int(f.read().strip())
            self.stdout.write(f"Resuming from index: {start_index}")
        else:
            self.stdout.write("Starting fresh import...")

        total_imported = 0
        buffer = []

        for i, message in enumerate(mbox):
            if i < start_index:
                continue  # skip already-imported emails

            try:
                subject = message['subject']
                sender = message['from']
                recipients = message['to']
                date = parsedate_to_datetime(message['date']) if message['date'] else None

                # Extract plain text body
                body = ''
                if message.is_multipart():
                    for part in message.walk():
                        if part.get_content_type() == 'text/plain' and not part.get('Content-Disposition', '').startswith('attachment'):
                            charset = part.get_content_charset() or 'utf-8'
                            body += part.get_payload(decode=True).decode(charset, errors='replace')
                else:
                    charset = message.get_content_charset() or 'utf-8'
                    body = message.get_payload(decode=True).decode(charset, errors='replace')

                buffer.append(Enquiry(
                    subject=subject,
                    sender=sender,
                    recipients=recipients,
                    date=date,
                    body=body
                ))

                if len(buffer) >= batch_size:
                    Enquiry.objects.bulk_create(buffer, batch_size=batch_size)
                    total_imported += len(buffer)
                    buffer = []

                    # Update progress
                    with open(progress_file, 'w') as f:
                        f.write(str(i + 1))

                    self.stdout.write(f"Imported: {total_imported} emails... (up to #{i})")

            except Exception as e:
                self.stderr.write(f"Failed at index {i}: {e}")
                continue

        # Final flush
        if buffer:
            Enquiry.objects.bulk_create(buffer, batch_size=batch_size)
            total_imported += len(buffer)
            with open(progress_file, 'w') as f:
                f.write(str(i + 1))
            self.stdout.write(f"Final batch: Imported {len(buffer)} emails.")

        self.stdout.write(self.style.SUCCESS(f"All done. Total imported: {total_imported}"))
