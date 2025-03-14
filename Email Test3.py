# Workflow with real email, auto-approved for testing
import random
import smtplib
from email.mime.text import MIMEText

companies = {
    "PlasTech Machining": [
        "Precision Techniques for Small Parts", "Cost-Saving Tips for CNC Projects", "Industry Trends in Machining",
        "Prototyping with Plastics", "Optimizing CNC Tooling", "Reducing Waste in Machining",
        "Advanced CNC Software", "Material Selection for Precision", "Machining for Aerospace", "Quality Control in CNC"
    ],
    "Plastic Injection Molding": [
        "Molding Efficiency Hacks", "Material Choices for Durability", "Design Tips for Molded Parts",
        "Reducing Cycle Times", "Injection Molding for Prototypes", "Sustainable Molding Practices",
        "Tooling Maintenance Strategies", "High-Volume Molding Tips", "Precision in Mold Design", "Cost-Effective Molding"
    ],
    "Sheet Metal Fabrication": [
        "Bending Methods for Complex Shapes", "Custom Parts on a Budget", "Cost Reduction in Fabrication",
        "Sheet Metal for Automotive", "Welding Techniques Unveiled", "Fabrication for Construction",
        "Laser Cutting Precision", "Designing Durable Metal Parts", "Scaling Fabrication Projects", "Metal Finishing Tips"
    ],
    "Shortening Shuttle": [
        "Waste Oil Solutions for Restaurants", "Recycling Benefits for Kitchens", "Sustainability Tips for Oil Management",
        "Efficient Oil Collection", "Reducing Restaurant Waste", "Cooking Oil Lifecycle",
        "Eco-Friendly Disposal Methods", "Oil Recycling Innovations", "Cost Savings in Waste Oil", "Green Practices for Dining"
    ]
}

def send_to_approver(company, prompt, article):
    sender_email = "STrotta@delcamcapital.com"
    sender_password = "cqsg vspr tsot zqql"
    approver_email = "STrotta@delcamcapital.com"

    msg = MIMEText(f"Prompt: {prompt}\n\nArticle Preview:\n{article[:100]}...\n\nFull 1,000 words imagined. Reply 'yes' to approve.")
    msg["Subject"] = f"Approve {company} Article"
    msg["From"] = sender_email
    msg["To"] = approver_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email sent to {approver_email} for {company}!")
        return True  # Auto-approve
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def post_to_cms(company, article):
    print(f"Posting to {company} CMS: {article[:100]}... [1,000 words]")
    return f"https://{company.lower().replace(' ', '')}.com/{topic.lower().replace(' ', '-')}"

def post_to_social(company, topic, url):
    print(f"Social Media: New at {company}: {topic} - {url}")

print("Office Manager Started Weekly Content...")
for company, topics in companies.items():
    topic = random.choice(topics)
    prompt = f"Write a 1,000-word article for {company} about {topic}, with detailed insights, examples, and actionable advice."
    article = f"Title: {topic} at {company}\n\n" \
              f"At {company}, we’re redefining excellence with {topic.lower()}. This in-depth article explores " \
              f"every angle—how we implement {topic.lower()}, real-world examples, and practical steps. " \
              f"[Imagine 950+ words here!] Full story on our site."
    
    if send_to_approver(company, prompt, article):
        url = post_to_cms(company, article)
        post_to_social(company, topic, url)
    else:
        print(f"{company} content not approved.")
