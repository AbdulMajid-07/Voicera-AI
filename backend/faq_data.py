"""Industry-specific FAQ datasets.

Each industry maps to a list of FAQ entries. Every entry has:
  - questions   : list[str]  — natural phrasings users actually say
  - answer      : str         — the spoken reply (2-3 sentences max for TTS speed)
  - keywords    : list[str]   — intent words, synonyms, and common paraphrases
  - audio_file  : str         — filename under faq_audio/<industry>/ for cached WAV
"""

HOSPITAL: list[dict] = [
    {
        "questions": [
            "what are your visiting hours",
        ],
        "answer": "Visiting hours are 10 AM to 8 PM daily. ICU visiting is limited to 11 AM–12 PM and 5 PM–6 PM.",
        "keywords": [
            "visiting", "hours", "visitor", "visit", "patient", "time",
            "allowed", "evening", "morning", "when", "open", "come",
            "close", "closing", "close time", "what time",
        ],
        "audio_file": "0.wav",
    },
    {
        "questions": [
            "how do i book an appointment",
        ],
        "answer": "I can help you book one right now — just tell me the department or doctor you'd like to see, and your preferred date.",
        "keywords": [
            "book", "booking", "appointment", "schedule", "visit", "see",
            "doctor", "consultation", "need", "make", "arrange", "set up",
            "register", "slot", "reserve",
        ],
        "audio_file": "1.wav",
    },
    {
        "questions": [
            "do you have an emergency department",
        ],
        "answer": "Yes, our emergency department is open 24/7 with doctors on call at all times.",
        "keywords": [
            "emergency", "department", "er", "accident", "urgent", "24/7",
            "open", "doctor", "on call", "critical", "immediate",
        ],
        "audio_file": "2.wav",
    },
    {
        "questions": [
            "what is the emergency contact number",
        ],
        "answer": "Our emergency line is 108 — available 24/7. If this is a medical emergency right now, please call it immediately.",
        "keywords": [
            "emergency", "contact", "number", "phone", "call", "108", "112",
            "urgent", "help", "ambulance", "reach", "hotline",
        ],
        "audio_file": "3.wav",
    },
    {
        "questions": [
            "which specialties are available at your hospital",
        ],
        "answer": "We have specialists in cardiology, orthopedics, pediatrics, gynecology, general medicine, and dermatology. Tell me which one you need and I'll check availability.",
        "keywords": [
            "specialties", "departments", "cardiology", "orthopedics",
            "pediatrics", "gynecology", "dermatology", "specialist",
            "doctor", "available", "offer", "have", "departments",
            "neurology", "ENT", "ophthalmology", "what",
        ],
        "audio_file": "4.wav",
    },
    {
        "questions": [
            "do you accept health insurance",
        ],
        "answer": "Yes, we accept most major health insurance providers — please have your insurance card and ID ready at admission.",
        "keywords": [
            "insurance", "health", "accept", "plan", "coverage", "claim",
            "cashless", "billing", "card", "provider", "star health",
            "hdfc", "icici", "payment",
        ],
        "audio_file": "5.wav",
    },
    {
        "questions": [
            "how can i get my test reports",
        ],
        "answer": "Reports are usually ready within 24-48 hours. I can check the status for you if you give me your patient ID.",
        "keywords": [
            "test", "reports", "results", "lab", "blood", "diagnostic",
            "check", "status", "patient id", "portal", "online",
            "download", "ready", "lab results", "check results",
        ],
        "audio_file": "6.wav",
    },
    {
        "questions": [
            "is parking available at the hospital",
        ],
        "answer": "Yes, visitor parking is available at the main entrance, free for the first 2 hours.",
        "keywords": [
            "parking", "car", "vehicle", "park", "main entrance",
            "valet", "free", "cost", "charge", "where", "available",
        ],
        "audio_file": "7.wav",
    },
    {
        "questions": [
            "do you have a pharmacy on-site",
        ],
        "answer": "Yes, our in-house pharmacy is open 24/7 for both inpatients and outpatients.",
        "keywords": [
            "pharmacy", "medicine", "drug", "24/7", "night", "buy",
            "medication", "prescription", "store", "open", "on-site",
            "in-house", "chemist", "medicines", "get medicine",
            "where medicine", "go", "get",
        ],
        "audio_file": "8.wav",
    },
    {
        "questions": [
            "how do i reach a specific department",
        ],
        "answer": "I can guide you there directly — tell me which department you're looking for.",
        "keywords": [
            "department", "reach", "find", "direction", "location",
            "floor", "where", "go", "navigate", "lost", "opd", "lab",
            "radiology", "pharmacy", "guide",
        ],
        "audio_file": "9.wav",
    },
    {
        "questions": [
            "can i get a doctor's appointment today",
        ],
        "answer": "Let me check today's availability — which doctor or department did you need?",
        "keywords": [
            "today", "appointment", "doctor", "available", "same day",
            "urgent", "see", "consultation", "slot", "now", "immediate",
            "schedule",
        ],
        "audio_file": "10.wav",
    },
    {
        "questions": [
            "what should i bring for my first visit",
        ],
        "answer": "Please bring a valid ID, any previous medical records, your insurance details, and a list of current medications.",
        "keywords": [
            "first", "visit", "bring", "documents", "id", "records",
            "insurance", "medications", "prepare", "before", "need",
            "carry", "required",
        ],
        "audio_file": "11.wav",
    },
    {
        "questions": [
            "do you offer telemedicine or video consultations",
        ],
        "answer": "Yes, for select departments. Tell me which specialist you need and I'll confirm if video consultation is available.",
        "keywords": [
            "telemedicine", "video", "consultation", "online", "remote",
            "virtual", "doctor", "home", "video call", "from home",
            "distance", "digital",
        ],
        "audio_file": "12.wav",
    },
    {
        "questions": [
            "what are the billing and payment options",
        ],
        "answer": "We accept cash, card, UPI, and insurance-based cashless billing where applicable.",
        "keywords": [
            "billing", "payment", "cash", "card", "upi", "pay",
            "how", "options", "methods", "online", "insurance",
            "cashless", "settle", "bill",
        ],
        "audio_file": "13.wav",
    },
    {
        "questions": [
            "how long is the wait time for the emergency room",
        ],
        "answer": "Emergency cases are triaged by urgency, not arrival order, so wait times vary based on your condition.",
        "keywords": [
            "wait", "time", "emergency", "room", "er", "long",
            "queue", "how much", "delay", "busy", "crowded",
        ],
        "audio_file": "14.wav",
    },
    {
        "questions": [
            "can i get a second opinion from another doctor here",
        ],
        "answer": "Absolutely — I can set up a consultation with another specialist for you.",
        "keywords": [
            "second", "opinion", "another", "doctor", "different",
            "specialist", "consult", "alternative", "review",
        ],
        "audio_file": "15.wav",
    },
    {
        "questions": [
            "do you have covid-19 testing available",
        ],
        "answer": "Yes, we offer COVID-19 testing here, with results typically ready within 24 hours.",
        "keywords": [
            "covid", "covid-19", "coronavirus", "test", "testing",
            "pcr", "rapid", "antigen", "result", "pandemic",
        ],
        "audio_file": "16.wav",
    },
    {
        "questions": [
            "what is your policy on visitor numbers per patient",
        ],
        "answer": "Generally up to 2 visitors per patient at a time, though ICU and isolation wards have stricter limits.",
        "keywords": [
            "visitor", "number", "how many", "allowed", "policy",
            "limit", "per patient", "icu", "isolation", "restrict",
        ],
        "audio_file": "17.wav",
    },
    {
        "questions": [
            "how do i request my medical records",
        ],
        "answer": "I can help start that request — I'll just need your ID and patient details. It usually takes 1-2 business days.",
        "keywords": [
            "medical", "records", "request", "history", "file",
            "documents", "patient", "id", "how", "get", "obtain",
            "copy",
        ],
        "audio_file": "18.wav",
    },
    {
        "questions": [
            "do you have ambulance services",
        ],
        "answer": "Yes, we run a 24/7 ambulance service. If you need one dispatched now, let me know your location right away.",
        "keywords": [
            "ambulance", "dispatch", "emergency", "transport", "24/7",
            "need", "send", "location", "pickup", "pick up", "come",
            "get me",
        ],
        "audio_file": "19.wav",
    },
    {
        "questions": [
            "are there any age restrictions for visitors",
        ],
        "answer": "Children under 12 are generally discouraged from visiting patient wards for hygiene and safety, though exceptions can be made.",
        "keywords": [
            "age", "restriction", "children", "kids", "under 12",
            "visitor", "allowed", "minor", "young", "policy",
        ],
        "audio_file": "20.wav",
    },
    {
        "questions": [
            "what is the process for hospital admission",
        ],
        "answer": "Admission needs a doctor's referral or emergency evaluation, followed by registration with your ID and insurance details — I can start that for you.",
        "keywords": [
            "admission", "admit", "process", "procedure", "referral",
            "register", "registration", "inpatient", "stay", "bed",
            "how",
        ],
        "audio_file": "21.wav",
    },
    {
        "questions": [
            "do you provide maternity and delivery services",
        ],
        "answer": "Yes, our maternity team handles prenatal care, delivery, and postnatal support. Would you like me to set up a consultation?",
        "keywords": [
            "maternity", "delivery", "baby", "birth", "pregnancy",
            "prenatal", "postnatal", "obstetric", "gynecology",
            "pregnant", "labor",
        ],
        "audio_file": "22.wav",
    },
    {
        "questions": [
            "can i pay my hospital bill online",
        ],
        "answer": "Yes, I can guide you to pay online, or you can settle it here directly.",
        "keywords": [
            "pay", "bill", "online", "payment", "settle", "balance",
            "how", "digitally", "upi", "card", "internet banking",
        ],
        "audio_file": "23.wav",
    },
    {
        "questions": [
            "how do i file a complaint or feedback about my visit",
        ],
        "answer": "You can share it with me directly right now, and I'll make sure it's logged and reviewed.",
        "keywords": [
            "complaint", "feedback", "file", "report", "issue",
            "problem", "bad", "experience", "service", "review",
            "suggest",
        ],
        "audio_file": "24.wav",
    },
]

ENTERPRISE: list[dict] = [
    {
        "questions": [
            "what are your business hours",
        ],
        "answer": "We're open Monday to Friday, 9 AM to 6 PM, closed on weekends and public holidays.",
        "keywords": [
            "business", "hours", "open", "close", "office", "timing",
            "when", "schedule", "available", "weekend", "holiday",
        ],
        "audio_file": "0.wav",
    },
    {
        "questions": [
            "what services do you offer",
        ],
        "answer": "We offer various services. Tell me what you're looking for and I'll walk you through the right fit.",
        "keywords": [
            "services", "offer", "solutions", "what do you do",
            "company", "provide", "capabilities", "products",
            "offerings", "help",
        ],
        "audio_file": "1.wav",
    },
    {
        "questions": [
            "how can i get a price quote",
        ],
        "answer": "Share your requirements with me and I'll get you a customized quote.",
        "keywords": [
            "price", "quote", "pricing", "cost", "how much", "charge",
            "estimate", "proposal", "budget", "fee", "rates",
        ],
        "audio_file": "2.wav",
    },
    {
        "questions": [
            "how do i contact customer support",
        ],
        "answer": "You're talking to support right now — tell me what's going on and I'll help.",
        "keywords": [
            "support", "contact", "customer", "help", "reach",
            "phone", "email", "talk", "speak", "agent", "team",
        ],
        "audio_file": "3.wav",
    },
    {
        "questions": [
            "can i schedule a demo or meeting",
        ],
        "answer": "Yes, tell me your preferred date and time and I'll get that scheduled for you.",
        "keywords": [
            "demo", "meeting", "schedule", "book", "appointment",
            "demo", "walkthrough", "product", "presentation",
            "call", "session",
        ],
        "audio_file": "4.wav",
    },
    {
        "questions": [
            "do you offer technical support",
        ],
        "answer": "Yes, I can help troubleshoot right now — describe the issue you're running into.",
        "keywords": [
            "technical", "support", "troubleshoot", "issue", "problem",
            "error", "bug", "fix", "help", "not working", "broken",
            "assist", "look into", "something wrong",
        ],
        "audio_file": "5.wav",
    },
    {
        "questions": [
            "how do i reset my account password",
        ],
        "answer": "Use the \"Forgot Password\" link on the login page — if you're still stuck, tell me and I'll help you further.",
        "keywords": [
            "password", "reset", "forgot", "account", "login",
            "signin", "access", "locked", "credentials", "change",
            "recover",
        ],
        "audio_file": "6.wav",
    },
    {
        "questions": [
            "are you hiring currently",
        ],
        "answer": "We periodically post openings on our careers page. Tell me what role you're interested in and I can point you to it.",
        "keywords": [
            "hiring", "job", "career", "opening", "vacancy", "recruit",
            "work", "employment", "apply", "position", "role",
        ],
        "audio_file": "7.wav",
    },
    {
        "questions": [
            "where are your offices located",
        ],
        "answer": "Our main office is in Hyderabad. Let me know your location and I'll tell you the nearest branch.",
        "keywords": [
            "office", "location", "address", "branch", "where",
            "hyderabad", "nearest", "find", "visit", "directions",
        ],
        "audio_file": "8.wav",
    },
    {
        "questions": [
            "do you offer partnership or reseller opportunities",
        ],
        "answer": "Yes, we're open to that — tell me a bit about your proposal and I'll get it to the right team.",
        "keywords": [
            "partnership", "partner", "reseller", "collaborate",
            "channel", "alliance", "business", "proposal", "work together",
        ],
        "audio_file": "9.wav",
    },
    {
        "questions": [
            "what industries do you typically work with",
        ],
        "answer": "We work with clients across [your target industries], tailoring our approach to each sector's needs.",
        "keywords": [
            "industries", "sectors", "clients", "work with",
            "healthcare", "retail", "finance", "manufacturing",
            "technology", "who",
        ],
        "audio_file": "10.wav",
    },
    {
        "questions": [
            "do you offer a free trial",
        ],
        "answer": "Yes, I can get you started on a free trial right now if you'd like.",
        "keywords": [
            "free", "trial", "try", "test", "demo account",
            "before buy", "sample", "preview", "no cost",
        ],
        "audio_file": "11.wav",
    },
    {
        "questions": [
            "how long does onboarding typically take",
        ],
        "answer": "Onboarding usually takes around 2-3 weeks, depending on your setup's complexity.",
        "keywords": [
            "onboarding", "implementation", "setup", "how long",
            "getting started", "integration", "timeline", "deploy",
            "rollout",
        ],
        "audio_file": "12.wav",
    },
    {
        "questions": [
            "what payment terms do you offer",
        ],
        "answer": "We offer flexible monthly and annual billing — I can walk you through the options.",
        "keywords": [
            "payment", "terms", "billing", "monthly", "annual",
            "subscription", "invoice", "pay", "plan", "flexible",
        ],
        "audio_file": "13.wav",
    },
    {
        "questions": [
            "can i get an invoice for my purchase",
        ],
        "answer": "Yes, invoices are sent automatically to your registered email after each transaction.",
        "keywords": [
            "invoice", "receipt", "billing", "purchase", "transaction",
            "email", "copy", "get", "download",
        ],
        "audio_file": "14.wav",
    },
    {
        "questions": [
            "how do i cancel or downgrade my subscription",
        ],
        "answer": "I can help with that right now — tell me your account details and what change you'd like.",
        "keywords": [
            "cancel", "downgrade", "unsubscribe", "subscription",
            "stop", "end", "terminate", "change plan", "modify",
        ],
        "audio_file": "15.wav",
    },
    {
        "questions": [
            "do you provide dedicated account managers",
        ],
        "answer": "Yes, enterprise-tier clients get a dedicated account manager for ongoing support.",
        "keywords": [
            "account", "manager", "dedicated", "enterprise",
            "point of contact", "personal", "support",
        ],
        "audio_file": "16.wav",
    },
    {
        "questions": [
            "what is your data security policy",
        ],
        "answer": "We follow industry-standard security practices to protect client data — I can share detailed documentation if you'd like.",
        "keywords": [
            "security", "data", "privacy", "policy", "protection",
            "encrypt", "compliance", "ISO", "SOC", "GDPR", "safe",
        ],
        "audio_file": "17.wav",
    },
    {
        "questions": [
            "can i integrate your service with other tools we use",
        ],
        "answer": "Yes, we support several integrations — tell me which tools you're using and I'll confirm compatibility.",
        "keywords": [
            "integrate", "integration", "API", "connect", "tools",
            "compatibility", "third party", "plugin", "webhook",
            "compatible",
        ],
        "audio_file": "18.wav",
    },
    {
        "questions": [
            "how do i escalate an unresolved issue",
        ],
        "answer": "I can escalate this for you right now — just give me a summary of the issue.",
        "keywords": [
            "escalate", "escalation", "unresolved", "issue", "problem",
            "ticket", "manager", "priority", "not resolved", "stuck",
            "complaint",
        ],
        "audio_file": "19.wav",
    },
    {
        "questions": [
            "do you offer training or onboarding sessions",
        ],
        "answer": "Yes, I can get one scheduled for your team — what time works best?",
        "keywords": [
            "training", "onboarding", "session", "workshop", "teach",
            "team", "learn", "how to", "guide", "setup", "trainer",
            "educate",
        ],
        "audio_file": "20.wav",
    },
    {
        "questions": [
            "what is your typical response time for support tickets",
        ],
        "answer": "We aim to respond within 24 business hours, faster for urgent issues.",
        "keywords": [
            "response", "time", "support", "ticket", "how long",
            "wait", "SLA", "turnaround", "fast", "urgent",
        ],
        "audio_file": "21.wav",
    },
    {
        "questions": [
            "can i request a custom feature or service",
        ],
        "answer": "Yes, tell me what you need and I'll pass it along for feasibility review.",
        "keywords": [
            "custom", "feature", "service", "request", "bespoke",
            "tailored", "specific", "unique", "build", "develop",
        ],
        "audio_file": "22.wav",
    },
    {
        "questions": [
            "do you have a mobile app",
        ],
        "answer": "It will be out soon — let me know what you are looking for",
        "keywords": [
            "mobile", "app", "iOS", "android", "phone", "application",
            "download", "available",
        ],
        "audio_file": "23.wav",
    },
    {
        "questions": [
            "how do i provide feedback about your service",
        ],
        "answer": "You can tell me right now — I'll make sure it gets logged and reviewed.",
        "keywords": [
            "feedback", "survey", "review", "suggestion", "opinion",
            "rate", "improve", "experience", "tell",
        ],
        "audio_file": "24.wav",
    },
]

STORE: list[dict] = [
    {
        "questions": [
            "what are your store hours",
        ],
        "answer": "We're open Monday to Saturday, 10 AM to 9 PM, and Sunday 11 AM to 7 PM.",
        "keywords": [
            "hours", "open", "close", "store", "time", "sunday",
            "when", "timing", "weekend", "schedule", "available",
        ],
        "audio_file": "0.wav",
    },
    {
        "questions": [
            "what is your return and exchange policy",
        ],
        "answer": "You can return or exchange items within 7 days of purchase with the original receipt and tags intact — I can help start that now.",
        "keywords": [
            "return", "exchange", "policy", "refund", "money back",
            "receipt", "bring back", "send back", "swap", "change",
            "7 days",
        ],
        "audio_file": "1.wav",
    },
    {
        "questions": [
            "how can i track my order",
        ],
        "answer": "Give me your order number and I'll check the status for you right now.",
        "keywords": [
            "track", "order", "delivery", "status", "where",
            "shipping", "shipped", "dispatch", "package", "ETA",
            "number", "ordered", "something",
        ],
        "audio_file": "2.wav",
    },
    {
        "questions": [
            "is this product currently in stock",
        ],
        "answer": "Tell me the product name and I'll check availability for you.",
        "keywords": [
            "stock", "available", "availability", "in stock",
            "out of stock", "inventory", "have", "product",
            "sold out", "check",
        ],
        "audio_file": "3.wav",
    },
    {
        "questions": [
            "what are your delivery options and timelines",
        ],
        "answer": "We offer standard delivery (3-5 business days) and express delivery (1-2 business days), depending on your location.",
        "keywords": [
            "delivery", "shipping", "options", "timeline", "how long",
            "standard", "express", "fast", "days", "time",
            "shipping",
        ],
        "audio_file": "4.wav",
    },
    {
        "questions": [
            "what payment methods do you accept",
        ],
        "answer": "We accept cash, all major cards, UPI, and popular digital wallets.",
        "keywords": [
            "payment", "methods", "cash", "card", "credit", "debit",
            "upi", "wallet", "google pay", "phonepe", "paytm",
            "net banking", "pay",
        ],
        "audio_file": "5.wav",
    },
    {
        "questions": [
            "do you have any ongoing discounts or offers",
        ],
        "answer": "Yes, let me check what's currently running for you.",
        "keywords": [
            "discount", "offer", "sale", "deal", "promo", "coupon",
            "code", "save", "reduction", "percentage", "off",
        ],
        "audio_file": "6.wav",
    },
    {
        "questions": [
            "how do i know what size fits me",
        ],
        "answer": "I can guide you through our size chart, or describe your measurements and I'll suggest the right fit.",
        "keywords": [
            "size", "fit", "chart", "measurement", "large", "small",
            "guide", "right", "choose", "pick", "recommend",
        ],
        "audio_file": "7.wav",
    },
    {
        "questions": [
            "does this product come with a warranty",
        ],
        "answer": "Tell me which item you mean and I'll confirm the warranty details.",
        "keywords": [
            "warranty", "guarantee", "repair", "replace", "claim",
            "electronics", "period", "coverage", "protect",
        ],
        "audio_file": "8.wav",
    },
    {
        "questions": [
            "where is your store located",
        ],
        "answer": "We're located in Hyderabad Let me know your area and I'll point you to the nearest branch.",
        "keywords": [
            "store", "location", "address", "branch", "where",
            "nearest", "find", "direction", "map", "hyderabad",
        ],
        "audio_file": "9.wav",
    },
    {
        "questions": [
            "can i place an order over the phone",
        ],
        "answer": "Yes, I can take your order right now — just tell me what you'd like.",
        "keywords": [
            "order", "phone", "call", "place", "buy", "purchase",
            "over phone", "telephone", "remote",
        ],
        "audio_file": "10.wav",
    },
    {
        "questions": [
            "do you offer home delivery",
        ],
        "answer": "Yes, within our serviceable areas. Tell me your location and I'll confirm.",
        "keywords": [
            "home", "delivery", "ship", "send", "address",
            "serviceable", "area", "doorstep", "deliver",
        ],
        "audio_file": "11.wav",
    },
    {
        "questions": [
            "can i cancel my order after placing it",
        ],
        "answer": "If it hasn't shipped yet, yes — give me your order number and I'll process the cancellation.",
        "keywords": [
            "cancel", "order", "stop", "withdraw", "not want",
            "change mind", "number",
        ],
        "audio_file": "12.wav",
    },
    {
        "questions": [
            "do you have a loyalty or rewards program",
        ],
        "answer": "Yes, you earn points on every purchase, redeemable on future orders. Want me to check your current balance?",
        "keywords": [
            "loyalty", "rewards", "program", "points", "earn",
            "redeem", "balance", "membership", "vip", "benefits",
        ],
        "audio_file": "13.wav",
    },
    {
        "questions": [
            "what happens if i receive a damaged product",
        ],
        "answer": "I'm sorry to hear that — send me the order details and a photo if you can, and I'll arrange a replacement or refund.",
        "keywords": [
            "damaged", "broken", "defective", "wrong", "replacement",
            "refund", "return", "complaint", "issue", "problem",
            "photo", "faulty", "not working", "arrived",
        ],
        "audio_file": "14.wav",
    },
    {
        "questions": [
            "do you offer gift wrapping",
        ],
        "answer": "Yes, for a small additional charge. Want me to add that to your order?",
        "keywords": [
            "gift", "wrapping", "wrap", "packaging", "present",
            "box", "birthday", "surprise",
        ],
        "audio_file": "15.wav",
    },
    {
        "questions": [
            "can i exchange an item for a different size or color",
        ],
        "answer": "Yes, within our 7-day window, subject to availability — I can check that for you now.",
        "keywords": [
            "exchange", "different", "size", "color", "swap",
            "another", "fit", "wrong", "replace",
        ],
        "audio_file": "16.wav",
    },
    {
        "questions": [
            "do you ship internationally",
        ],
        "answer": "[Customize based on actual capability] — tell me your country and I'll confirm shipping options and costs.",
        "keywords": [
            "international", "ship", "abroad", "overseas", "country",
            "global", "worldwide", "outside", "export",
        ],
        "audio_file": "17.wav",
    },
    {
        "questions": [
            "how do i use a discount code at checkout",
        ],
        "answer": "Enter it in the promo code field at checkout — I can also apply it for you if you tell me the code.",
        "keywords": [
            "discount", "code", "promo", "coupon", "apply",
            "checkout", "enter", "use", "voucher",
        ],
        "audio_file": "18.wav",
    },
    {
        "questions": [
            "what is your policy on refunds",
        ],
        "answer": "Refunds are processed within 5-7 business days after we receive and inspect the returned item.",
        "keywords": [
            "refund", "policy", "money back", "return", "how long",
            "process", "inspected", "received", "days",
        ],
        "audio_file": "19.wav",
    },
    {
        "questions": [
            "do you have a physical fitting room in-store",
        ],
        "answer": "Yes, fitting rooms are available in-store for trying items on before purchase.",
        "keywords": [
            "fitting", "room", "try on", "trial", "changing room",
            "in-store", "physical", "before buy", "try", "before",
        ],
        "audio_file": "20.wav",
    },
    {
        "questions": [
            "can i reserve an item to pick up in-store",
        ],
        "answer": "Yes, I can reserve it for you now — which item and which store location?",
        "keywords": [
            "reserve", "pick up", "in-store", "click collect",
            "hold", "save", "collect", "reservation",
        ],
        "audio_file": "21.wav",
    },
    {
        "questions": [
            "are your products authentic or original",
        ],
        "answer": "Yes, all our products are 100% authentic, sourced directly from authorized suppliers.",
        "keywords": [
            "authentic", "original", "genuine", "real", "fake",
            "counterfeit", "legit", "brand", "authorized", "knockoff",
        ],
        "audio_file": "22.wav",
    },
    {
        "questions": [
            "how do i file a complaint",
        ],
        "answer": "You can tell me right now, and I'll make sure it's logged and followed up on.",
        "keywords": [
            "complaint", "file", "report", "issue", "problem",
            "bad", "experience", "service", "unsatisfied", "review",
        ],
        "audio_file": "23.wav",
    },
    {
        "questions": [
            "do you offer bulk or wholesale pricing",
        ],
        "answer": "Yes, tell me the quantity and item you're interested in and I'll work out a custom quote.",
        "keywords": [
            "bulk", "wholesale", "quantity", "large", "order",
            "corporate", "bulk order", "discount", "custom quote",
            "many", "bunch", "lot", "buy", "purchase", "business",
        ],
        "audio_file": "24.wav",
    },
]

FAQ_DB: dict[str, list[dict]] = {
    "hospital": HOSPITAL,
    "enterprise": ENTERPRISE,
    "store": STORE,
}
