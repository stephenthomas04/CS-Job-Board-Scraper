"""Configuration for the job scraper: boards, keywords, and heuristic phrases.

All company tokens are public, unauthenticated Greenhouse / Lever board slugs.
Unknown or retired tokens simply 404 and are skipped by the scraper, so this
list is safe to edit freely.
"""

# --- Greenhouse boards --------------------------------------------------------
# token -> board metadata. Endpoint:
#   https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true
GREENHOUSE: dict[str, dict[str, str]] = {
    "twosigma": {"company_name": "Two Sigma", "company_url": "https://www.twosigma.com"},
    "stripe": {"company_name": "Stripe", "company_url": "https://stripe.com"},
    "databricks": {"company_name": "Databricks", "company_url": "https://databricks.com"},
    "ramp": {"company_name": "Ramp", "company_url": "https://ramp.com"},
    "brex": {"company_name": "Brex", "company_url": "https://brex.com"},
    "robinhood": {"company_name": "Robinhood", "company_url": "https://robinhood.com"},
    "airbnb": {"company_name": "Airbnb", "company_url": "https://airbnb.com"},
    "coinbase": {"company_name": "Coinbase", "company_url": "https://coinbase.com"},
    "cloudflare": {"company_name": "Cloudflare", "company_url": "https://cloudflare.com"},
    "gustohq": {"company_name": "Gusto", "company_url": "https://gusto.com"},
    "affirm": {"company_name": "Affirm", "company_url": "https://affirm.com"},
    "flexport": {"company_name": "Flexport", "company_url": "https://flexport.com"},
}

# --- Lever boards -------------------------------------------------------------
# token -> board metadata. Endpoint:
#   https://api.lever.co/v0/postings/{token}?mode=json
LEVER: dict[str, dict[str, str]] = {
    "voleon": {"company_name": "The Voleon Group", "company_url": "https://voleon.com"},
    "hudsonrivertrading": {
        "company_name": "Hudson River Trading",
        "company_url": "https://www.hudsonrivertrading.com",
    },
    "plaid": {"company_name": "Plaid", "company_url": "https://plaid.com"},
    "netflix": {"company_name": "Netflix", "company_url": "https://netflix.com"},
    "palantir": {"company_name": "Palantir", "company_url": "https://palantir.com"},
    "matchgroup": {"company_name": "Match Group", "company_url": "https://mtch.com"},
    "attentive": {"company_name": "Attentive", "company_url": "https://attentive.com"},
}

# --- Title filter -------------------------------------------------------------
# Case-insensitive substring match against the posting title.
KEYWORDS = [
    "software",
    "swe",
    "data science",
    "data engineer",
    "quantitative",
    "quant",
    "developer",
    "systems",
    "trading",
    "infrastructure",
    "intern",
]

# --- Sponsorship heuristics ---------------------------------------------------
# Matched (case-insensitive) against the plaintext job description.
# NEGATIVE_PHRASES  -> "Does Not Offer Sponsorship"
# CITIZENSHIP_PHRASES -> "U.S. Citizenship is Required"
# Citizenship is checked first (more specific), then negative phrases.
NEGATIVE_PHRASES = [
    "does not offer sponsorship",
    "will not sponsor",
    "unable to sponsor",
    "not able to sponsor",
    "no sponsorship",
    "without sponsorship",
    "cannot provide sponsorship",
    "not provide visa sponsorship",
    "not offer visa sponsorship",
    "sponsorship is not available",
    "not eligible for sponsorship",
]

CITIZENSHIP_PHRASES = [
    "u.s. citizen",
    "us citizen",
    "united states citizen",
    "citizenship is required",
    "must be a citizen",
    "security clearance",
    "active clearance",
    "itar",
    "export control",
    "green card holder",
    "permanent resident",
]

# --- HTTP ---------------------------------------------------------------------
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
REQUEST_TIMEOUT = 20  # seconds
MAX_RETRIES = 2
