"""Curated seed articles representing core Brilliant Directories documentation."""

SEED_ARTICLES = [
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/5000558357-can-i-send-a-mass-email-campaign-using-brilliant-directories-",
        "title": "Can I Send A Mass Email Campaign Using Brilliant Directories?",
        "category": "Emails",
        "folder": "Email Marketing",
        "content": (
            "Brilliant Directories allows sending newsletters and email campaigns directly from the admin dashboard. "
            "Navigate to Emails > Send Newsletter to compose, schedule, and send mass campaigns to your registered members. "
            "You can segment your audience by Membership Plan, Status (Active, Inactive, Past Due), or Category. "
            "Third-party integrations with Mailchimp, Constant Contact, and SendGrid are also supported via webhook or Zapier. "
            "Important: Sending limits depend on your hosting package. For large lists exceeding 5,000 recipients, "
            "integrating an external SMTP relay or third-party email provider is recommended to maintain high deliverability."
        ),
        "images": [
            {
                "url": "https://support.brilliantdirectories.com/images/send-newsletter-menu.png",
                "alt": "Send Newsletter menu option under Emails navigation in Admin Dashboard",
                "caption": "Admin Panel: Emails > Send Newsletter workflow"
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/5000558363-emails-email-accounts",
        "title": "Emails & Custom Email Accounts Setup",
        "category": "Emails",
        "folder": "Email Accounts",
        "content": (
            "You can create professional domain-based email accounts (e.g., info@yourdomain.com) directly through cPanel or your hosting DNS settings. "
            "In Brilliant Directories, navigate to Settings > General Settings > Localization tab to set the Default Website Email Address. "
            "This email will receive system notifications, contact form submissions, and billing alerts. "
            "To prevent outgoing emails from landing in spam folders, configure SPF, DKIM, and DMARC TXT records in your DNS zone."
        ),
        "images": [
            {
                "url": "https://support.brilliantdirectories.com/images/email-settings-general.png",
                "alt": "General Settings Localization tab showing Default Website Email field",
                "caption": "Settings > General Settings > Localization tab"
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/5000684120-how-to-process-refunds-and-handle-cancellations",
        "title": "How to Process Member Refunds and Subscription Cancellations",
        "category": "Finance & Billing",
        "folder": "Transaction Processing",
        "content": (
            "To process a refund for a member in Brilliant Directories: "
            "1. Go to Finance > Transaction History in the admin dashboard. "
            "2. Locate the specific invoice or transaction using the member search or transaction ID. "
            "3. Click the 'Action' dropdown on the right side of the transaction row and select 'Refund'. "
            "4. Choose between 'Full Refund' or 'Partial Refund'. If partial, specify the exact dollar amount to return. "
            "5. If you also want to cancel the recurring billing, check the option 'Cancel Subscription'. "
            "Refunds processed through Brilliant Directories are automatically sent to your payment gateway (Stripe or PayPal). "
            "Note: Processing a refund does not automatically delete the member's account; their status switches to Cancelled or Inactive based on your settings."
        ),
        "images": [
            {
                "url": "https://support.brilliantdirectories.com/images/finance-refund-action.png",
                "alt": "Transaction History action dropdown showing Refund option",
                "caption": "Finance > Transaction History > Action > Refund modal"
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/5000684135-payment-gateway-credentials-setup-stripe-paypal",
        "title": "Connecting Payment Gateways: Stripe and PayPal Setup",
        "category": "Finance & Billing",
        "folder": "Payment Gateways",
        "content": (
            "Brilliant Directories natively supports Stripe, PayPal, and eWay for automated recurring subscription billing and one-time payments. "
            "To connect Stripe: "
            "1. Navigate to Settings > Payment Settings in the Admin Dashboard. "
            "2. Select 'Stripe' from the Payment Gateway selector. "
            "3. Enter your Stripe Publishable Key and Stripe Secret Key. "
            "4. Copy the Webhook Endpoint URL provided in the BD dashboard and paste it into your Stripe Developer Webhooks section. "
            "Ensure events `invoice.payment_succeeded`, `invoice.payment_failed`, and `customer.subscription.deleted` are enabled. "
            "5. Click 'Save Changes' and run a test transaction in Stripe Test Mode before switching live."
        ),
        "images": [
            {
                "url": "https://support.brilliantdirectories.com/images/payment-gateway-setup.png",
                "alt": "Payment Settings screen with Stripe API keys and Webhook URL",
                "caption": "Settings > Payment Settings: Stripe Configuration"
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/5000712390-search-results-radius-filtering-and-zip-code-search",
        "title": "Configuring Location Search, Radius Filtering, and Zip Code Search",
        "category": "Design & Search Settings",
        "folder": "Search Settings",
        "content": (
            "To enable radius and zip code location search without custom coding: "
            "1. Navigate to Settings > General Settings > Localization tab. "
            "2. Set the 'Distance Measurement' to either Miles or Kilometers. "
            "3. Navigate to My Members > Member Search Results > Search Settings. "
            "4. Enable 'Radius Search' and configure the default radius (e.g., 25, 50, or 100 miles). "
            "5. Connect your Google Maps API Key or OpenStreetMap integration under Settings > General Settings > Integrations. "
            "The search widget will automatically display a location input with autocomplete for city, state, and zip code. "
            "No custom developer code is required—this is a built-in platform configuration setting."
        ),
        "images": [
            {
                "url": "https://support.brilliantdirectories.com/images/radius-search-settings.png",
                "alt": "General Settings Localization distance measurement and radius options",
                "caption": "Settings > General Settings > Localization: Distance & Radius Options"
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/5000723411-membership-plan-privileges-and-feature-access",
        "title": "Managing Membership Plan Privileges and Feature Access",
        "category": "Members & Accounts",
        "folder": "Membership Plans",
        "content": (
            "Membership plans control what members can post and access on your website. "
            "To configure privileges: "
            "1. Go to Finance > Membership Plans. "
            "2. Click 'Edit' on the desired membership plan (e.g. Premium Member or Free Directory Listing). "
            "3. Navigate to the 'Post Publishing' tab to specify which post types the plan can create (Articles, Coupons, Events, Classifieds, Jobs, Properties). "
            "4. Navigate to the 'Search Visibility' tab to control whether members in this plan appear in search results. "
            "5. You can set maximum post limits per member or require admin moderation before posts go live. "
            "Changes apply immediately to all active members assigned to that tier."
        ),
        "images": [
            {
                "url": "https://support.brilliantdirectories.com/images/membership-plan-privileges.png",
                "alt": "Membership plan editor showing Post Publishing permission toggles",
                "caption": "Finance > Membership Plans > Post Publishing settings"
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/5000734502-lead-generation-and-automatic-lead-matching",
        "title": "Automatic Lead Matching and Buyer-Seller Lead Routing",
        "category": "Leads",
        "folder": "Lead Settings",
        "content": (
            "Brilliant Directories includes an automated lead routing system that connects visitors looking for services with qualified directory members. "
            "To configure lead matching rules: "
            "1. Go to Leads > Lead Settings in the admin panel. "
            "2. Under 'Auto-Match Leads', choose whether leads match members by Category only, Location only, or both Category and Location. "
            "3. Set the maximum number of members who can receive a single lead (e.g. 1 to 5 members). "
            "4. Choose whether leads are free for members to accept or require payment (lead purchasing monetization). "
            "5. Members receive an instant SMS/email alert with lead details upon submission."
        ),
        "images": [
            {
                "url": "https://support.brilliantdirectories.com/images/lead-routing-config.png",
                "alt": "Lead routing settings showing category and location match toggles",
                "caption": "Leads > Lead Settings: Auto-Match Configuration"
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/5000745610-custom-domain-pointing-and-ssl-activation",
        "title": "Connecting a Custom Domain and Activating Free SSL Certificate",
        "category": "Domain & Hosting",
        "folder": "Domain Setup",
        "content": (
            "To connect your custom domain to your Brilliant Directories website: "
            "1. Log in to your domain registrar (GoDaddy, Namecheap, Google Domains/Squarespace). "
            "2. Create an A Record pointing `@` (or your root domain) to the Brilliant Directories IP address provided in your Admin Welcome email. "
            "3. Create a CNAME Record for `www` pointing to your root domain or directory URL. "
            "4. In the Brilliant Directories admin panel, go to Settings > Domain Manager and enter your domain name. "
            "5. Once DNS propagates (typically 1 to 24 hours), click 'Install Free SSL Certificate' in Domain Manager. "
            "Brilliant Directories will automatically provision a Let's Encrypt SSL certificate and redirect all HTTP traffic to HTTPS."
        ),
        "images": [
            {
                "url": "https://support.brilliantdirectories.com/images/domain-manager-ssl.png",
                "alt": "Domain Manager showing DNS A Record status and Install SSL button",
                "caption": "Settings > Domain Manager: DNS validation & SSL installation"
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/5000756720-member-reviews-and-rating-settings",
        "title": "Configuring Member Reviews, Star Ratings, and Moderation",
        "category": "Reviews",
        "folder": "Review Settings",
        "content": (
            "Customer reviews and star ratings can be enabled or restricted on a per-membership plan basis. "
            "To manage review settings: "
            "1. Navigate to Settings > General Settings > Reviews tab. "
            "2. Enable or disable member reviews site-wide. "
            "3. Select moderation preference: 'Auto-Approve Reviews' or 'Hold for Admin Approval'. "
            "4. Choose whether reviewers must enter an email verification code before submitting a review to prevent spam. "
            "5. Members can respond publicly to reviews from within their member dashboard."
        ),
        "images": [
            {
                "url": "https://support.brilliantdirectories.com/images/reviews-moderation-settings.png",
                "alt": "General Settings Reviews tab with approval toggles and star rating controls",
                "caption": "Settings > General Settings > Reviews: Moderation & Anti-Spam Controls"
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/5000767830-webhooks-and-zapier-integration-api",
        "title": "Brilliant Directories API, Webhooks, and Zapier Integrations",
        "category": "Developer Tools & API",
        "folder": "Integrations",
        "content": (
            "Brilliant Directories provides a REST API and real-time outbound webhooks for connecting external CRM and marketing tools. "
            "To generate API keys: "
            "1. Navigate to Developer Tools > API Keys. "
            "2. Click 'Generate API Key', give it a label, and store the private key securely. "
            "3. Navigate to Developer Tools > Webhook Manager to listen for events such as `member.created`, `member.updated`, `transaction.completed`, and `lead.submitted`. "
            "4. Use the Brilliant Directories Zapier App to connect your directory to over 5,000 apps without writing code."
        ),
        "images": [
            {
                "url": "https://support.brilliantdirectories.com/images/api-key-manager.png",
                "alt": "Developer Tools API Key Manager screen showing generated secret keys",
                "caption": "Developer Tools > API Keys & Webhook Manager"
            }
        ]
    }
]

def chunk_text(text: str, max_chunk_chars: int = 500, overlap: int = 80) -> list[str]:
    """Split text into overlapping semantic chunks."""
    text = text.strip()
    if len(text) <= max_chunk_chars:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_chars
        if end >= len(text):
            chunks.append(text[start:].strip())
            break
        
        # Try to break on sentence or space boundary
        split_at = text.rfind(". ", start, end)
        if split_at != -1 and split_at > start + 100:
            chunk = text[start:split_at + 1].strip()
            start = split_at + 2
        else:
            space_at = text.rfind(" ", start, end)
            if space_at != -1 and space_at > start + 100:
                chunk = text[start:space_at].strip()
                start = space_at + 1
            else:
                chunk = text[start:end].strip()
                start = end - overlap
        
        if chunk:
            chunks.append(chunk)
    return chunks
