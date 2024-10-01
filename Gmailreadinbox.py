import imaplib
import email
from email.header import decode_header
import os
from collections import defaultdict
import dotenv
import logging
from multiprocessing import Pool, cpu_count

# Load environment variables securely
dotenv.load_dotenv()

# Gmail credentials from environment variables
EMAIL = os.getenv("GMAIL_USER")
PASSWORD = os.getenv("GMAIL_PASS")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to clean the subject (optional, for file naming)
def clean(text):
    return "".join(c if c.isalnum() else "_" for c in text)

# Function to fetch and process an email, establishing a new IMAP connection for each worker
def process_email_batch(email_ids):
    imap_host = "imap.gmail.com"
    unsubscribe_count = 0
    sender_count = defaultdict(int)
    
    # Each worker creates its own IMAP connection
    try:
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        for email_id in email_ids:
            try:
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                if status != "OK":
                    logging.warning(f"Failed to fetch email with ID {email_id}")
                    continue
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        # Parse the email content
                        msg = email.message_from_bytes(response_part[1])
                        # Decode the sender's email address
                        from_ = msg.get("From")
                        sender_count[from_] += 1

                        # Process email body and count 'Unsubscribe' occurrences
                        unsubscribe_count += process_email_body(msg)
            
            except Exception as e:
                logging.error(f"Error processing email {email_id}: {e}")

    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP connection failed: {e}")
    
    finally:
        mail.logout()  # Ensure the worker logs out properly
        logging.info("IMAP connection closed after batch processing.")

    return sender_count, unsubscribe_count

# Function to process the email body
def process_email_body(msg):
    unsubscribe_count = 0
    try:
        if msg.is_multipart():
            # Iterate over email parts
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors='ignore').lower()
                    unsubscribe_count += body.count("unsubscribe")
        else:
            # Non-multipart emails
            body = msg.get_payload(decode=True).decode(errors='ignore').lower()
            unsubscribe_count += body.count("unsubscribe")

    except Exception as e:
        logging.error(f"Error processing email body: {e}")

    return unsubscribe_count

# Batch email processing with multiprocessing
def process_emails_in_batches(email_ids):
    batch_size = 100
    # Split email_ids into batches
    batches = [email_ids[i:i + batch_size] for i in range(0, len(email_ids), batch_size)]
    
    # Use multiprocessing pool for parallel processing
    num_workers = min(cpu_count(), 4)  # Limit to 4 workers or CPU count
    with Pool(processes=num_workers) as pool:
        results = pool.map(process_email_batch, batches)

    # Aggregate results
    unsubscribe_count = 0
    sender_count = defaultdict(int)

    for result_sender_count, result_unsubscribe_count in results:
        unsubscribe_count += result_unsubscribe_count
        for sender, count in result_sender_count.items():
            sender_count[sender] += count

    return sender_count, unsubscribe_count

# Function to read emails and count senders and 'Unsubscribe' occurrences
def read_and_count_emails():
    imap_host = "imap.gmail.com"
    sender_count = defaultdict(int)
    unsubscribe_count = 0

    # Connect to the Gmail IMAP server
    try:
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(EMAIL, PASSWORD)
    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP login failed: {e}")
        return

    try:
        # Select the mailbox ('inbox' by default)
        mail.select("inbox")

        # Search for all emails in the mailbox
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            logging.error("Failed to retrieve email list.")
            return
        
        # Convert messages to a list of email IDs
        email_ids = messages[0].split()
        total_emails = len(email_ids)
        logging.info(f"Total emails found: {total_emails}")

        # Process emails in parallel batches
        sender_count, unsubscribe_count = process_emails_in_batches(email_ids)

    except Exception as e:
        logging.error(f"Error during IMAP operations: {e}")
    finally:
        mail.logout()

    # Write results to a file using a context manager
    with open("email_analysis.txt", "w") as f:
        f.write("Sender Email Count:\n")
        for sender, count in sender_count.items():
            f.write(f"{sender}: {count}\n")
        f.write(f"\nTotal occurrences of the word 'Unsubscribe': {unsubscribe_count}\n")

    logging.info("Email analysis complete. Results saved to 'email_analysis.txt'.")

# Call the function to read emails and count data
if __name__ == "__main__":
    read_and_count_emails()