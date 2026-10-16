import { CustomerEmail } from "./types.js";

export const SAMPLE_EMAILS: CustomerEmail[] = [
  // 1-10: HOW_TO Technical Questions
  {
    id: "email-001",
    from: "sarah.jenkins@example.com",
    customerName: "Sarah Jenkins",
    subject: "How do I process a refund for a member in Brilliant Directories?",
    body: "Hi team, one of our directory members accidentally purchased an annual subscription instead of monthly. Can you explain where in the admin panel I can issue a refund and cancel their plan?",
    receivedAt: "2026-10-14T09:15:00Z"
  },
  {
    id: "email-002",
    from: "mike.davies@localdirectory.org",
    customerName: "Mike Davies",
    subject: "Can I configure radius search and zip code filtering?",
    body: "Hello, our visitors want to filter members within a 25-mile radius of their zip code. Do we need custom coding for this or is there a built-in search setting?",
    receivedAt: "2026-10-14T09:30:00Z"
  },
  {
    id: "email-003",
    from: "linda.cho@meddirectory.com",
    customerName: "Linda Cho",
    subject: "Where do I connect my Stripe API keys and webhooks?",
    body: "We are ready to start charging members. Where do I enter our Stripe Publishable Key and Secret Key, and what webhook events do we need?",
    receivedAt: "2026-10-14T10:00:00Z"
  },
  {
    id: "email-004",
    from: "david.ross@lawyersgroup.net",
    customerName: "David Ross",
    subject: "Can I send a mass email campaign to my members?",
    body: "We have an announcement to make to all 1,200 registered attorneys. Does Brilliant Directories support sending mass newsletters or do I need Mailchimp?",
    receivedAt: "2026-10-14T10:45:00Z"
  },
  {
    id: "email-005",
    from: "elena.v@artisanregistry.com",
    customerName: "Elena Vance",
    subject: "How do I connect my custom domain name?",
    body: "We bought our domain on Namecheap. What DNS records (A record, CNAME) should we point to Brilliant Directories to make our site live?",
    receivedAt: "2026-10-14T11:15:00Z"
  },
  {
    id: "email-006",
    from: "tom.b@tradesmenhub.co.uk",
    customerName: "Tom Bradley",
    subject: "Where do I install the free SSL certificate?",
    body: "Our domain is pointing properly now, but Chrome says 'Not Secure'. Where in the dashboard do we install the free SSL certificate?",
    receivedAt: "2026-10-14T11:45:00Z"
  },
  {
    id: "email-007",
    from: "rachel.g@wellnesshub.io",
    customerName: "Rachel Green",
    subject: "How to configure membership plan post publishing privileges?",
    body: "We want Premium members to post events and classifieds, but Basic members should only have a profile. Where do we set post permissions?",
    receivedAt: "2026-10-14T12:30:00Z"
  },
  {
    id: "email-008",
    from: "kevin.n@petgroomers.org",
    customerName: "Kevin Nguyen",
    subject: "How does automatic lead matching work by category and location?",
    body: "When a customer submits a quote request, how can we automatically route that lead to groomers in the same zip code?",
    receivedAt: "2026-10-14T13:00:00Z"
  },
  {
    id: "email-009",
    from: "alicia.m@consultantsnetwork.com",
    customerName: "Alicia Miller",
    subject: "Where can I set member reviews to require admin moderation?",
    body: "We want all client reviews to be reviewed by our team before they appear publicly. Where is the moderation toggle located?",
    receivedAt: "2026-10-14T13:30:00Z"
  },
  {
    id: "email-010",
    from: "carlos.r@realtorsonline.org",
    customerName: "Carlos Ramirez",
    subject: "How to generate REST API keys for external Zapier integration?",
    body: "We want new member signups to sync to our HubSpot CRM via Zapier. Where do we generate API keys inside Brilliant Directories?",
    receivedAt: "2026-10-14T14:00:00Z"
  },

  // 11-20: BILLING_REFUND
  {
    id: "email-011",
    from: "george.k@contractors.biz",
    customerName: "George Klein",
    subject: "Accidental double charge on invoice #9012",
    body: "Hello, my card was charged twice for $149 yesterday. Please refund the duplicate transaction immediately.",
    receivedAt: "2026-10-14T14:15:00Z"
  },
  {
    id: "email-012",
    from: "anna.p@eventplanners.com",
    customerName: "Anna Petrov",
    subject: "Cancel subscription and refund unused period",
    body: "I am closing down my agency and would like to cancel my subscription and receive a pro-rated refund for the remaining 6 months.",
    receivedAt: "2026-10-14T14:45:00Z"
  },
  {
    id: "email-013",
    from: "brian.s@automechaniclist.com",
    customerName: "Brian Scott",
    subject: "Need VAT invoice and receipt for tax filing",
    body: "Can you send the formal PDF invoice and receipt with VAT breakdown for transaction #TX-8821?",
    receivedAt: "2026-10-14T15:00:00Z"
  },
  {
    id: "email-014",
    from: "diana.f@fitnesscoaches.net",
    customerName: "Diana Fox",
    subject: "Credit card expired - payment failed",
    body: "My recurring payment failed because my debit card expired. Where do I update my payment method so my account doesn't get suspended?",
    receivedAt: "2026-10-14T15:30:00Z"
  },
  {
    id: "email-015",
    from: "samuel.t@techfounders.io",
    customerName: "Samuel Taylor",
    subject: "Disputing charge from last week",
    body: "I see a charge of $399 that I did not authorize. Please explain what this is for or issue a full refund before I contact my bank.",
    receivedAt: "2026-10-14T16:00:00Z"
  },
  {
    id: "email-016",
    from: "clara.b@musicteachers.org",
    customerName: "Clara Bell",
    subject: "Partial refund requested for downgraded plan",
    body: "I downgraded from Enterprise to Standard halfway through the month. Can you please credit or refund the difference?",
    receivedAt: "2026-10-14T16:30:00Z"
  },
  {
    id: "email-017",
    from: "marcus.l@logisticsnetwork.com",
    customerName: "Marcus Lee",
    subject: "Billing receipt #4421 not received",
    body: "Our accounts department needs a copy of the receipt for payment #4421 from October 1st. Please resend it to this email.",
    receivedAt: "2026-10-14T17:00:00Z"
  },
  {
    id: "email-018",
    from: "olivia.w@wellnessdirectory.com",
    customerName: "Olivia Wright",
    subject: "Refund request for annual renewal",
    body: "My subscription renewed automatically yesterday but I meant to cancel last week. Please cancel the subscription and issue a full refund.",
    receivedAt: "2026-10-14T17:30:00Z"
  },
  {
    id: "email-019",
    from: "henry.c@craftbrewers.net",
    customerName: "Henry Clark",
    subject: "Wrong currency charged on Stripe invoice",
    body: "We were charged in USD instead of CAD. Please refund the transaction so we can re-bill in Canadian dollars.",
    receivedAt: "2026-10-14T18:00:00Z"
  },
  {
    id: "email-020",
    from: "jessica.m@mindfulness.org",
    customerName: "Jessica Morales",
    subject: "Cancel account and stop all recurring billing",
    body: "Please confirm that my recurring subscription is cancelled and no further charges will be billed to my Mastercard.",
    receivedAt: "2026-10-14T18:30:00Z"
  },

  // 21-28: PROJECT_REQUEST
  {
    id: "email-021",
    from: "mark.h@dentalnetwork.com",
    customerName: "Mark Hughes",
    subject: "Build a new custom directory for dental clinics",
    body: "We want to hire your team to build a new nationwide dental directory with custom appointment scheduling and patient reviews.",
    receivedAt: "2026-10-15T09:00:00Z"
  },
  {
    id: "email-022",
    from: "fiona.s@architectshub.com",
    customerName: "Fiona Stewart",
    subject: "Custom feature: interactive 3D map of architectural projects",
    body: "We need a custom Mapbox interactive widget embedded into member profiles displaying their building portfolios. Can you develop this?",
    receivedAt: "2026-10-15T09:30:00Z"
  },
  {
    id: "email-023",
    from: "robert.b@realtysyndicate.org",
    customerName: "Robert Burns",
    subject: "Migrate 25,000 members from WordPress to Brilliant Directories",
    body: "We have an existing WordPress site with 25,000 listings. We want to migrate all user accounts, images, and custom taxonomies over to BD.",
    receivedAt: "2026-10-15T10:00:00Z"
  },
  {
    id: "email-024",
    from: "valerie.d@yogastudiofinders.com",
    customerName: "Valerie Diaz",
    subject: "Redesign homepage and custom mobile responsive layout",
    body: "Our current homepage looks dated. We want a modern UI overhaul with hero video background and custom search filters.",
    receivedAt: "2026-10-15T10:30:00Z"
  },
  {
    id: "email-025",
    from: "patrick.k@irishbusiness.ie",
    customerName: "Patrick Kelly",
    subject: "Integrate custom multi-vendor booking and calendar sync",
    body: "Can you build a two-way sync between Brilliant Directories member listings and Google Calendar / Calendly for appointment bookings?",
    receivedAt: "2026-10-15T11:00:00Z"
  },
  {
    id: "email-026",
    from: "natalie.j@chefstable.org",
    customerName: "Natalie Jones",
    subject: "Custom verification badge system for verified culinary masters",
    body: "We want to award special verified badges to members who pass our safety audit. Is this a native setting or custom dev project?",
    receivedAt: "2026-10-15T11:30:00Z"
  },
  {
    id: "email-027",
    from: "greg.m@motorsportsregistry.com",
    customerName: "Greg Marshall",
    subject: "Develop custom vehicle VIN decoder integration",
    body: "When members list a car for sale, we want them to enter a VIN and automatically populate make, model, year, and engine specs from NHTSA API.",
    receivedAt: "2026-10-15T12:00:00Z"
  },
  {
    id: "email-028",
    from: "helen.t@tutorsguild.co.uk",
    customerName: "Helen Turner",
    subject: "Scope of work for student-tutor messaging portal",
    body: "We want to build a private direct messaging portal with file attachments between students and tutors. Please prepare a scope of work.",
    receivedAt: "2026-10-15T12:30:00Z"
  },

  // 29-36: QUOTE
  {
    id: "email-029",
    from: "eric.c@legalexperts.net",
    customerName: "Eric Campbell",
    subject: "How much to build a custom radius search widget?",
    body: "Could you give us an estimate and price quote for adding zip code radius search to our homepage?",
    receivedAt: "2026-10-15T13:00:00Z"
  },
  {
    id: "email-030",
    from: "monica.r@spadirectory.com",
    customerName: "Monica Rivera",
    subject: "Price quote for connecting custom webhook to HubSpot",
    body: "What is your hourly rate and estimated cost to build a webhook that pushes new directory signups to HubSpot?",
    receivedAt: "2026-10-15T13:30:00Z"
  },
  {
    id: "email-031",
    from: "andrew.w@contractorsguide.org",
    customerName: "Andrew Walsh",
    subject: "Estimate for custom CSS theme and brand styling",
    body: "We need our color palette, custom fonts, and logo implemented across all 15 template pages. What would the budget be?",
    receivedAt: "2026-10-15T14:00:00Z"
  },
  {
    id: "email-032",
    from: "danielle.s@weddingservices.com",
    customerName: "Danielle Stone",
    subject: "Cost to migrate 5,000 CSV member records",
    body: "Please quote us for cleaning and importing a 5,000-row CSV file of wedding vendors into Brilliant Directories with geocoding.",
    receivedAt: "2026-10-15T14:30:00Z"
  },
  {
    id: "email-033",
    from: "simon.p@freelancewriters.co",
    customerName: "Simon Price",
    subject: "Pricing for ongoing monthly technical maintenance",
    body: "Do you offer a monthly retainer for continuous BD maintenance, plugin updates, and troubleshooting? What are your pricing plans?",
    receivedAt: "2026-10-15T15:00:00Z"
  },
  {
    id: "email-034",
    from: "laura.k@childcarefinders.org",
    customerName: "Laura King",
    subject: "How much will custom SMS lead notifications cost?",
    body: "We want directory members to receive an SMS text via Twilio when a parent submits an inquiry. What is the estimated cost to build this?",
    receivedAt: "2026-10-15T15:30:00Z"
  },
  {
    id: "email-035",
    from: "bret.v@biketrails.net",
    customerName: "Bret Vance",
    subject: "Estimate for custom GPX trail map upload feature",
    body: "We want members to upload .gpx trail files and display the interactive elevation profile on their listing. Please send a price quote.",
    receivedAt: "2026-10-15T16:00:00Z"
  },
  {
    id: "email-036",
    from: "teresa.o@accountantshub.com",
    customerName: "Teresa Ortiz",
    subject: "Quote for custom multi-step member onboarding wizard",
    body: "What is your estimate in hours and dollars to build a 4-step wizard that guides new accountants through profile completion?",
    receivedAt: "2026-10-15T16:30:00Z"
  },

  // 37-43: COMPLAINT
  {
    id: "email-037",
    from: "jason.m@urgentcarelist.com",
    customerName: "Jason Miller",
    subject: "URGENT: Website down during product launch!",
    body: "Our website is showing a 500 Internal Server Error right in the middle of our press conference. This is totally unacceptable, fix it now!",
    receivedAt: "2026-10-15T17:00:00Z"
  },
  {
    id: "email-038",
    from: "karen.w@localretailers.org",
    customerName: "Karen Watson",
    subject: "Emails are not delivering to our members",
    body: "None of our welcome emails or invoice receipts have been sent for 48 hours. Members are complaining and we are losing business.",
    receivedAt: "2026-10-15T17:30:00Z"
  },
  {
    id: "email-039",
    from: "steve.b@boatingenthusiasts.net",
    customerName: "Steve Baker",
    subject: "Disappointed with support response times",
    body: "I submitted a high-priority ticket 3 days ago and have not received a single response. This is terrible service for an enterprise plan.",
    receivedAt: "2026-10-15T18:00:00Z"
  },
  {
    id: "email-040",
    from: "lisa.c@cleanersassociation.com",
    customerName: "Lisa Chen",
    subject: "Member search is broken on mobile devices",
    body: "Whenever visitors search on an iPhone, the search button is hidden behind the footer and impossible to tap. Please fix this bug immediately.",
    receivedAt: "2026-10-15T18:30:00Z"
  },
  {
    id: "email-041",
    from: "richard.g@securitypros.org",
    customerName: "Richard Gray",
    subject: "Spam bot accounts bypassing signup form",
    body: "We have had over 300 spam accounts created in the last 12 hours. The captcha is not working. Escalate to senior engineering right away.",
    receivedAt: "2026-10-15T19:00:00Z"
  },
  {
    id: "email-042",
    from: "miranda.h@beautysalons.io",
    customerName: "Miranda Hayes",
    subject: "Stripe payments failing for all checkout customers",
    body: "Every single customer who tries to pay receives an error 'Payment Gateway Not Configured'. We are losing thousands in revenue today.",
    receivedAt: "2026-10-15T19:30:00Z"
  },
  {
    id: "email-043",
    from: "victor.s@antiquedealers.net",
    customerName: "Victor Sanchez",
    subject: "Unacceptable downtime on directory search",
    body: "Our search results page has been timing out since this morning. If this is not resolved today we will demand a refund and switch platforms.",
    receivedAt: "2026-10-15T20:00:00Z"
  },

  // 44-50: FOLLOW_UP
  {
    id: "email-044",
    from: "ashley.t@photographersnet.com",
    customerName: "Ashley Taylor",
    subject: "Checking in on status of Ticket #4912",
    body: "Hi team, following up on ticket #4912 regarding the custom watermark feature. Any update on when this will be deployed?",
    receivedAt: "2026-10-16T08:00:00Z"
  },
  {
    id: "email-045",
    from: "brandon.k@fitnessgyms.org",
    customerName: "Brandon Kelly",
    subject: "Any update on our custom CSS styling proposal?",
    body: "Just checking in to see if your lead consultant has had time to review the Figma files we sent on Tuesday for the homepage styling.",
    receivedAt: "2026-10-16T08:30:00Z"
  },
  {
    id: "email-046",
    from: "carol.m@caterersnetwork.com",
    customerName: "Carol Murphy",
    subject: "Following up on DNS propagation for caterersnetwork.com",
    body: "We added the A record yesterday morning as instructed. Has DNS propagated on your end so we can install the SSL certificate?",
    receivedAt: "2026-10-16T09:00:00Z"
  },
  {
    id: "email-047",
    from: "dennis.w@plumbersunion.biz",
    customerName: "Dennis White",
    subject: "Status of CSV member import #782",
    body: "Hi, following up on the member import ticket from yesterday. Have the 1,500 plumber listings been geocoded and published?",
    receivedAt: "2026-10-16T09:30:00Z"
  },
  {
    id: "email-048",
    from: "emily.r@therapistsfinder.org",
    customerName: "Emily Robinson",
    subject: "Checking in on Stripe test mode issue",
    body: "Following up on our call regarding the Stripe webhook signing secret. Did you receive the new keys we shared in the secure portal?",
    receivedAt: "2026-10-16T10:00:00Z"
  },
  {
    id: "email-049",
    from: "frank.l@autodealersassociation.com",
    customerName: "Frank Lopez",
    subject: "Status update on custom search filter delivery",
    body: "Checking in to see if developer testing on the multi-category search filter is on track for Friday release.",
    receivedAt: "2026-10-16T10:30:00Z"
  },
  {
    id: "email-050",
    from: "gina.h@veterinarians.net",
    customerName: "Gina Howard",
    subject: "Following up on quote #Q-2024-88",
    body: "Hi, we reviewed the estimate for the emergency pet clinic filter. What are the next steps to kick off the project?",
    receivedAt: "2026-10-16T11:00:00Z"
  }
];
