from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# Path to Brave executable
brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"  # Update this path if necessary

# Set up options to use Brave
chrome_options = Options()
chrome_options.binary_location = brave_path

# Initialize the WebDriver for Brave
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Function to retrieve the subjects of the emails
def retrieve_email_subjects(driver, num_emails=5):
    # Ensure the inbox is loaded
    driver.get("https://mail.google.com/mail/u/0/#inbox")
    time.sleep(5)
    
    # Find email subjects
    subjects = driver.find_elements_by_xpath("//span[@class='bog']")
    for i, subject in enumerate(subjects[:num_emails], 1):
        print(f"Email {i}: {subject.text}")

# Function to search for the word "Unsubscribe" in the first few emails
def search_for_unsubscribe(driver, num_emails=5):
    # Find the first few emails
    email_rows = driver.find_elements_by_xpath("//tr[@class='zA zE' or @class='zA yO']")  # Unread (zE) or Read (yO)
    
    for i, row in enumerate(email_rows[:num_emails]):
        row.click()  # Click to open the email
        time.sleep(3)  # Wait for the email to load
        
        try:
            # Check the body for 'Unsubscribe'
            body = driver.find_element_by_xpath("//div[@class='ii gt']//div[@dir='ltr']").text.lower()
            unsubscribe_count = body.count("unsubscribe")
            print(f"Email {i+1} contains 'Unsubscribe' {unsubscribe_count} time(s).")
        except Exception as e:
            print(f"Error processing email {i+1}: {e}")
        
        # Go back to inbox
        driver.back()
        time.sleep(3)

# Main function to automate Gmail
def automate_gmail():
    try:
        # Retrieve email subjects
        print("\nEmail Subjects:")
        retrieve_email_subjects(driver, num_emails=5)
        
        # Search for the word 'Unsubscribe' in the emails
        print("\nSearch for 'Unsubscribe':")
        search_for_unsubscribe(driver, num_emails=5)
    
    finally:
        # Close the WebDriver
        driver.quit()

if __name__ == "__main__":
    automate_gmail()
