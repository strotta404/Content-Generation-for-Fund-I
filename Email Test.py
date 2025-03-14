# Automated content workflow with real Gmail (Google Workspace) for approval
import random
import smtplib
from email.mime.text import MIMEText

# Topic list for PlasTech Machining
companies = {
    "PlasTech Machining": [
        "Precision Techniques for Small Parts", "Cost-Saving Tips for CNC Projects", "Industry Trends in Machining",
        "Prototyping with Plastics", "Optimizing CNC Tooling", "Reducing Waste in Machining",
        "Advanced CNC Software", "Material Selection for Precision", "Machining for Aerospace", "Quality Control in CNC"
    ]
}

# Function to send real email
def send_to_approver(company, prompt, article):
    sender_email = "STrotta@delcamcapital.com"
    sender_password = "cqsg vspr tsot zqql"  # Your App Password
    approver_email = "STrotta@delcamcapital.com"  # Same for testing

    msg = MIMEText(f"Prompt: {prompt}\n\nArticle Preview (first 100 words):\n{article[:100]}...\n\nFull article attached (imagine 1,000 words). Reply 'yes' to approve.")
    msg["Subject"] = f"Approve {company} Article"
    msg["From"] = sender_email
    msg["To"] = approver_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email sent to {approver_email} for {company} approval!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    
    approval = input("Type 'yes' if approved (check your email too): ")
    return approval == "yes"

# Simulate CMS and social
def post_to_cms(company, article):
    print(f"Posting to {company} CMS: [1,000-word article]")
    print(f"{article[:100]}... [Full text posted]")
    return f"https://{company.lower().replace(' ', '')}.com/{topic.lower().replace(' ', '-')}"

def post_to_social(company, topic, url):
    print(f"Social Media: New at {company}: {topic} - {url}")

# Main workflow
print("Office Manager Started Weekly Content...")
company = "PlasTech Machining"
topics = companies[company]
topic = random.choice(topics)
prompt = f"Write a 1,000-word article for {company} about {topic}, with detailed insights, examples, and actionable advice."

article = f"Title: {topic} at {company}\n\n" \
          f"At {company}, we’re redefining excellence with {topic.lower()}. This in-depth article explores " \
          f"every angle—how we implement {topic.lower()}, real-world examples, and practical steps for " \
          f"your business. Picture a 20% efficiency gain, like one client achieved, thanks to {topic.lower()}. " \
          f"[Imagine 950+ words of detailed analysis, case studies, and tips here!] Full story on our site."

if send_to_approver(company, prompt, article):
    url = post_to_cms(company, article)
    post_to_social(company, topic, url)
    print("Content processed successfully!")
else:
    print("Content not approved.")
