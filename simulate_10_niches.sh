#!/bin/bash
set -e

# AgentBloom 10-Niche End-to-End Simulation
# Uses Bearer token auth
BASE="http://localhost:8000/api/v1"
AUTH="Authorization: Bearer 1dae59372e51dbf2fcc584450906d9119bcd86fe"
CT="Content-Type: application/json"
ORG="X-Org-Id: 64d0636f-361e-4178-afd5-a3ee8c1eed3d"

# Counters
PASS=0
FAIL=0
TOTAL=0
FAILURES=""

check() {
    TOTAL=$((TOTAL + 1))
    local label="$1"
    local response="$2"
    local id=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null || echo "")
    if [ -n "$id" ] && [ "$id" != "" ] && [ "$id" != "None" ]; then
        PASS=$((PASS + 1))
        echo "  ✓ $label (id=$id)"
        echo "$id"
    else
        FAIL=$((FAIL + 1))
        local err=$(echo "$response" | head -c 200)
        FAILURES="$FAILURES\n  ✗ $label: $err"
        echo "  ✗ $label: $err" >&2
        echo ""
    fi
}

check_list() {
    TOTAL=$((TOTAL + 1))
    local label="$1"
    local response="$2"
    local count=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); r=d if isinstance(d,list) else d.get('results',[]); print(len(r))" 2>/dev/null || echo "0")
    if [ "$count" -gt 0 ] 2>/dev/null; then
        PASS=$((PASS + 1))
        echo "  ✓ $label (count=$count)"
    else
        FAIL=$((FAIL + 1))
        FAILURES="$FAILURES\n  ✗ $label: empty or error"
        echo "  ✗ $label" >&2
    fi
}

check_ok() {
    TOTAL=$((TOTAL + 1))
    local label="$1"
    local response="$2"
    if echo "$response" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        PASS=$((PASS + 1))
        echo "  ✓ $label"
    else
        FAIL=$((FAIL + 1))
        FAILURES="$FAILURES\n  ✗ $label"
        echo "  ✗ $label" >&2
    fi
}

echo "============================================"
echo "  AgentBloom 10-Niche Simulation"
echo "============================================"
echo ""

# Verify auth first
echo "--- Verifying auth ---"
ME=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/auth/me/")
echo "$ME" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Logged in as: {d[\"email\"]}')"
echo ""

###############################################################################
# NICHE 1: Fitness Coach
###############################################################################
echo "=== NICHE 1: Fitness Coach ==="

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"FitPro Studio","slug":"fitpro-studio"}' "$BASE/sites/sites/")
SITE1=$(check "Create site" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"email":"john@fitclient.com","first_name":"John","last_name":"Smith","phone":"+1555100001","tags":["fitness","vip"]}' "$BASE/crm/contacts/")
C1=$(check "Create contact" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"January Fitness Challenge","subject":"Start Your Fitness Journey!","from_name":"FitPro","from_email":"coach@fitpro.com","html_content":"<h1>New Year Fitness</h1><p>Join our challenge!</p>","campaign_type":"email"}' "$BASE/crm/campaigns/")
check "Create campaign" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Personal Training Package","contact":"'"$C1"'","value":"2500.00","stage":"proposal"}' "$BASE/crm/deals/")
check "Create deal" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"12-Week Body Transformation","slug":"12week-transform","description":"Complete body transformation program","status":"draft","price":"299.00"}' "$BASE/courses/courses/")
check "Create course" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"1-on-1 PT Session","duration_minutes":60,"price":"85.00","description":"Personal training session"}' "$BASE/calendar/services/")
SVC1=$(check "Create service" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Training Session Pack","description":"10-session package","price":"750.00","product_type":"service"}' "$BASE/payments/products/")
check "Create product" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Workout FAQ","content":"## Common Questions\n\nQ: How often should I train?\nA: 3-5 times per week\n\nQ: Best diet plan?\nA: High protein, moderate carbs","doc_type":"faq","source_type":"text","status":"published"}' "$BASE/kb/documents/")
check "Create KB doc" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Stripe Fitness Webhook","url":"https://fitpro.com/webhooks/stripe","events":["payment.completed"],"is_active":true}' "$BASE/webhooks/endpoints/")
check "Create webhook" "$R"

echo ""

###############################################################################
# NICHE 2: Real Estate Agent
###############################################################################
echo "=== NICHE 2: Real Estate Agent ==="

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"HomeFinder Realty","slug":"homefinder-realty"}' "$BASE/sites/sites/")
SITE2=$(check "Create site" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"email":"sarah@homebuyer.com","first_name":"Sarah","last_name":"Johnson","phone":"+1555200001","tags":["buyer","pre-approved"]}' "$BASE/crm/contacts/")
C2=$(check "Create contact" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"New Listings Alert","subject":"Hot New Properties This Week!","from_name":"HomeFinder","from_email":"listings@homefinder.com","html_content":"<h1>New Listings</h1><p>Check out these amazing properties</p>","campaign_type":"email"}' "$BASE/crm/campaigns/")
check "Create campaign" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"123 Oak St Purchase","contact":"'"$C2"'","value":"450000.00","stage":"qualified"}' "$BASE/crm/deals/")
check "Create deal" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"First-Time Homebuyer Guide","slug":"first-homebuyer","description":"Everything you need to know","status":"draft","price":"0.00"}' "$BASE/courses/courses/")
check "Create course" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Property Showing","duration_minutes":45,"price":"0.00","description":"Guided property showing"}' "$BASE/calendar/services/")
SVC2=$(check "Create service" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Premium Listing Package","description":"Featured listing placement","price":"499.00","product_type":"service"}' "$BASE/payments/products/")
check "Create product" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Buying Process Guide","content":"## Steps to Buy a Home\n\n1. Get pre-approved\n2. Find an agent\n3. Search properties\n4. Make an offer","doc_type":"guide","source_type":"text","status":"published"}' "$BASE/kb/documents/")
check "Create KB doc" "$R"

echo ""

###############################################################################
# NICHE 3: Restaurant
###############################################################################
echo "=== NICHE 3: Restaurant ==="

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Bella Cucina Italian","slug":"bella-cucina"}' "$BASE/sites/sites/")
check "Create site" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"email":"mike@foodlover.com","first_name":"Mike","last_name":"Chen","phone":"+1555300001","tags":["regular","vip-dining"]}' "$BASE/crm/contacts/")
C3=$(check "Create contact" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Weekend Special Menu","subject":"This Weekend Special Menu!","from_name":"Bella Cucina","from_email":"hello@bellacucina.com","html_content":"<h1>Weekend Specials</h1><p>Reserve your table now!</p>","campaign_type":"email"}' "$BASE/crm/campaigns/")
check "Create campaign" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Catering Contract - Chen Wedding","contact":"'"$C3"'","value":"8500.00","stage":"proposal"}' "$BASE/crm/deals/")
check "Create deal" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Italian Cooking Masterclass","slug":"italian-cooking","description":"Learn authentic Italian cooking","status":"draft","price":"149.00"}' "$BASE/courses/courses/")
check "Create course" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Private Dining Event","duration_minutes":180,"price":"500.00","description":"Private dining room booking"}' "$BASE/calendar/services/")
check "Create service" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Gift Card","description":"Restaurant gift card","price":"100.00","product_type":"digital"}' "$BASE/payments/products/")
check "Create product" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Menu & Allergen Info","content":"## Our Menu\n\nGluten-free options available. Nut-free kitchen area.\n\n## Hours\nMon-Sat 11am-10pm\nSun 10am-9pm","doc_type":"faq","source_type":"text","status":"published"}' "$BASE/kb/documents/")
check "Create KB doc" "$R"

echo ""

###############################################################################
# NICHE 4: Dental Clinic
###############################################################################
echo "=== NICHE 4: Dental Clinic ==="

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"BrightSmile Dental","slug":"brightsmile-dental"}' "$BASE/sites/sites/")
check "Create site" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"email":"lisa@patient.com","first_name":"Lisa","last_name":"Park","phone":"+1555400001","tags":["patient","insurance-verified"]}' "$BASE/crm/contacts/")
C4=$(check "Create contact" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Dental Checkup Reminder","subject":"Time for Your 6-Month Checkup!","from_name":"BrightSmile","from_email":"care@brightsmile.com","html_content":"<h1>Checkup Reminder</h1><p>Schedule your visit today</p>","campaign_type":"email"}' "$BASE/crm/campaigns/")
check "Create campaign" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Invisalign Treatment - Park","contact":"'"$C4"'","value":"5500.00","stage":"qualified"}' "$BASE/crm/deals/")
check "Create deal" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Dental Hygiene 101","slug":"dental-hygiene","description":"Oral care best practices","status":"draft","price":"0.00"}' "$BASE/courses/courses/")
check "Create course" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Dental Cleaning","duration_minutes":30,"price":"150.00","description":"Professional dental cleaning"}' "$BASE/calendar/services/")
check "Create service" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Teeth Whitening Kit","description":"At-home whitening kit","price":"89.00","product_type":"physical"}' "$BASE/payments/products/")
check "Create product" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Insurance & Payment FAQ","content":"## Accepted Insurance\n\nWe accept most major dental plans.\n\n## Payment Plans\n\nFlexible financing available for treatments over $500.","doc_type":"faq","source_type":"text","status":"published"}' "$BASE/kb/documents/")
check "Create KB doc" "$R"

echo ""

###############################################################################
# NICHE 5: Marketing Agency
###############################################################################
echo "=== NICHE 5: Marketing Agency ==="

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"GrowthPulse Agency","slug":"growthpulse-agency"}' "$BASE/sites/sites/")
check "Create site" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"email":"david@techstartup.io","first_name":"David","last_name":"Williams","phone":"+1555500001","tags":["prospect","enterprise"]}' "$BASE/crm/contacts/")
C5=$(check "Create contact" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Q1 Marketing Insights","subject":"Your Q1 Marketing Report","from_name":"GrowthPulse","from_email":"insights@growthpulse.com","html_content":"<h1>Q1 Insights</h1><p>See how your campaigns performed</p>","campaign_type":"email"}' "$BASE/crm/campaigns/")
check "Create campaign" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"SEO Retainer - TechStartup","contact":"'"$C5"'","value":"36000.00","stage":"negotiation"}' "$BASE/crm/deals/")
check "Create deal" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Digital Marketing Fundamentals","slug":"digital-marketing","description":"Master digital marketing","status":"draft","price":"499.00"}' "$BASE/courses/courses/")
check "Create course" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Strategy Consultation","duration_minutes":90,"price":"350.00","description":"Marketing strategy session"}' "$BASE/calendar/services/")
check "Create service" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Social Media Audit","description":"Complete social media audit","price":"999.00","product_type":"service"}' "$BASE/payments/products/")
check "Create product" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"SEO Best Practices","content":"## SEO Guide\n\n1. Keyword research\n2. On-page optimization\n3. Technical SEO\n4. Link building\n5. Content strategy","doc_type":"guide","source_type":"text","status":"published"}' "$BASE/kb/documents/")
check "Create KB doc" "$R"

echo ""

###############################################################################
# NICHE 6: Online Course Creator
###############################################################################
echo "=== NICHE 6: Online Course Creator ==="

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"LearnFlow Academy","slug":"learnflow-academy"}' "$BASE/sites/sites/")
check "Create site" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"email":"emma@student.edu","first_name":"Emma","last_name":"Davis","phone":"+1555600001","tags":["student","enrolled"]}' "$BASE/crm/contacts/")
C6=$(check "Create contact" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"New Course Launch","subject":"Exciting New Course Available!","from_name":"LearnFlow","from_email":"courses@learnflow.com","html_content":"<h1>New Course!</h1><p>Check out our latest course</p>","campaign_type":"email"}' "$BASE/crm/campaigns/")
check "Create campaign" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Course Bundle Upsell","contact":"'"$C6"'","value":"997.00","stage":"proposal"}' "$BASE/crm/deals/")
check "Create deal" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Python for Beginners","slug":"python-beginners","description":"Learn Python from scratch","status":"draft","price":"79.00"}' "$BASE/courses/courses/")
check "Create course" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"1-on-1 Mentoring","duration_minutes":60,"price":"150.00","description":"Personal mentoring session"}' "$BASE/calendar/services/")
check "Create service" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"All-Access Pass","description":"Lifetime access to all courses","price":"999.00","product_type":"digital"}' "$BASE/payments/products/")
check "Create product" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Student Onboarding Guide","content":"## Getting Started\n\n1. Create your account\n2. Browse courses\n3. Enroll in a course\n4. Start learning!\n\n## Support\nEmail: support@learnflow.com","doc_type":"guide","source_type":"text","status":"published"}' "$BASE/kb/documents/")
check "Create KB doc" "$R"

echo ""

###############################################################################
# NICHE 7: Wedding Photographer
###############################################################################
echo "=== NICHE 7: Wedding Photographer ==="

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Eternal Moments Photo","slug":"eternal-moments"}' "$BASE/sites/sites/")
check "Create site" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"email":"rachel@bride.com","first_name":"Rachel","last_name":"Anderson","phone":"+1555700001","tags":["bride","2025-wedding"]}' "$BASE/crm/contacts/")
C7=$(check "Create contact" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Wedding Season Promo","subject":"Book Your Wedding Photography!","from_name":"Eternal Moments","from_email":"hello@eternalmoments.com","html_content":"<h1>Wedding Season</h1><p>Book early for 2025!</p>","campaign_type":"email"}' "$BASE/crm/campaigns/")
check "Create campaign" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Anderson Wedding Package","contact":"'"$C7"'","value":"4500.00","stage":"proposal"}' "$BASE/crm/deals/")
check "Create deal" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Wedding Photography Tips","slug":"wedding-photo-tips","description":"Tips for perfect wedding photos","status":"draft","price":"0.00"}' "$BASE/courses/courses/")
check "Create course" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Engagement Shoot","duration_minutes":120,"price":"350.00","description":"Engagement photo session"}' "$BASE/calendar/services/")
check "Create service" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Photo Album Add-on","description":"Premium photo album","price":"250.00","product_type":"physical"}' "$BASE/payments/products/")
check "Create product" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Photography Packages","content":"## Wedding Packages\n\n- Essential: 4 hours, $2000\n- Classic: 8 hours, $3500\n- Premium: Full day, $5000\n\nAll include digital gallery","doc_type":"guide","source_type":"text","status":"published"}' "$BASE/kb/documents/")
check "Create KB doc" "$R"

echo ""

###############################################################################
# NICHE 8: Law Firm
###############################################################################
echo "=== NICHE 8: Law Firm ==="

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Sterling Legal Group","slug":"sterling-legal"}' "$BASE/sites/sites/")
check "Create site" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"email":"james@client.com","first_name":"James","last_name":"Wilson","phone":"+1555800001","tags":["client","family-law"]}' "$BASE/crm/contacts/")
C8=$(check "Create contact" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Legal Newsletter Q1","subject":"Legal Updates You Should Know","from_name":"Sterling Legal","from_email":"newsletter@sterlinglegal.com","html_content":"<h1>Legal Updates</h1><p>Important legal news</p>","campaign_type":"email"}' "$BASE/crm/campaigns/")
check "Create campaign" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Wilson Estate Planning","contact":"'"$C8"'","value":"15000.00","stage":"qualified"}' "$BASE/crm/deals/")
check "Create deal" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Understanding Your Legal Rights","slug":"legal-rights","description":"Know your legal rights","status":"draft","price":"0.00"}' "$BASE/courses/courses/")
check "Create course" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Legal Consultation","duration_minutes":60,"price":"300.00","description":"Initial legal consultation"}' "$BASE/calendar/services/")
check "Create service" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Legal Document Package","description":"Standard legal document package","price":"1500.00","product_type":"service"}' "$BASE/payments/products/")
check "Create product" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Legal Services FAQ","content":"## Practice Areas\n\n- Family Law\n- Estate Planning\n- Business Law\n- Real Estate\n\n## Free Consultation\nFirst 30 minutes free","doc_type":"faq","source_type":"text","status":"published"}' "$BASE/kb/documents/")
check "Create KB doc" "$R"

echo ""

###############################################################################
# NICHE 9: SaaS Startup
###############################################################################
echo "=== NICHE 9: SaaS Startup ==="

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"CloudSync Platform","slug":"cloudsync-platform"}' "$BASE/sites/sites/")
check "Create site" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"email":"alex@enterprise.co","first_name":"Alex","last_name":"Thompson","phone":"+1555900001","tags":["enterprise","trial"]}' "$BASE/crm/contacts/")
C9=$(check "Create contact" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Product Update v2.0","subject":"Exciting New Features in v2.0!","from_name":"CloudSync","from_email":"updates@cloudsync.io","html_content":"<h1>v2.0 Release</h1><p>Check out new features!</p>","campaign_type":"email"}' "$BASE/crm/campaigns/")
check "Create campaign" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Enterprise License - Thompson","contact":"'"$C9"'","value":"120000.00","stage":"negotiation"}' "$BASE/crm/deals/")
check "Create deal" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"CloudSync API Masterclass","slug":"cloudsync-api","description":"Master the CloudSync API","status":"draft","price":"199.00"}' "$BASE/courses/courses/")
check "Create course" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Product Demo","duration_minutes":30,"price":"0.00","description":"Product demonstration call"}' "$BASE/calendar/services/")
check "Create service" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Enterprise Plan Annual","description":"Enterprise annual subscription","price":"12000.00","product_type":"subscription"}' "$BASE/payments/products/")
check "Create product" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"API Documentation","content":"## CloudSync API\n\n### Authentication\nUse Bearer token\n\n### Endpoints\n- GET /api/v1/sync\n- POST /api/v1/data\n- DELETE /api/v1/data/:id","doc_type":"guide","source_type":"text","status":"published"}' "$BASE/kb/documents/")
check "Create KB doc" "$R"

echo ""

###############################################################################
# NICHE 10: E-Commerce Store
###############################################################################
echo "=== NICHE 10: E-Commerce Store ==="

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"UrbanStyle Boutique","slug":"urbanstyle-boutique"}' "$BASE/sites/sites/")
check "Create site" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"email":"nina@shopper.com","first_name":"Nina","last_name":"Garcia","phone":"+1555000001","tags":["customer","loyalty-gold"]}' "$BASE/crm/contacts/")
C10=$(check "Create contact" "$R")

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Summer Sale Blast","subject":"50% Off Everything - Summer Sale!","from_name":"UrbanStyle","from_email":"sale@urbanstyle.com","html_content":"<h1>Summer Sale</h1><p>Up to 50% off all items!</p>","campaign_type":"email"}' "$BASE/crm/campaigns/")
check "Create campaign" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Wholesale Order - Garcia","contact":"'"$C10"'","value":"2500.00","stage":"proposal"}' "$BASE/crm/deals/")
check "Create deal" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Fashion Styling 101","slug":"fashion-styling","description":"Personal styling course","status":"draft","price":"49.00"}' "$BASE/courses/courses/")
check "Create course" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Personal Styling Session","duration_minutes":60,"price":"120.00","description":"1-on-1 styling consultation"}' "$BASE/calendar/services/")
check "Create service" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"name":"Premium T-Shirt Collection","description":"Limited edition t-shirt set","price":"59.00","product_type":"physical"}' "$BASE/payments/products/")
check "Create product" "$R"

R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Shipping & Returns","content":"## Shipping Policy\n\nFree shipping on orders over $50.\nStandard: 5-7 days\nExpress: 2-3 days\n\n## Returns\n30-day return policy","doc_type":"faq","source_type":"text","status":"published"}' "$BASE/kb/documents/")
check "Create KB doc" "$R"

echo ""

###############################################################################
# CROSS-FEATURE: Site Pages (for Niche 1)
###############################################################################
echo "=== CROSS-FEATURE: Site Pages ==="

if [ -n "$SITE1" ]; then
    R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Home","slug":"home","page_type":"landing","content":{"blocks":[{"type":"hero","data":{"heading":"Transform Your Body","subheading":"Expert Personal Training"}},{"type":"cta","data":{"text":"Book a Free Session","url":"/book"}}]}}' "$BASE/sites/sites/$SITE1/pages/")
    check "Create landing page" "$R"

    R=$(curl -s -X POST -H "$AUTH" -H "$CT" -H "$ORG" -d '{"title":"Programs","slug":"programs","page_type":"landing","content":{"blocks":[{"type":"features","data":{"items":["Weight Loss","Muscle Building","Flexibility"]}}]}}' "$BASE/sites/sites/$SITE1/pages/")
    check "Create programs page" "$R"
else
    echo "  ⚠ Skipped - no site created"
fi

echo ""

###############################################################################
# CROSS-FEATURE: Receptionist Config
###############################################################################
echo "=== CROSS-FEATURE: Receptionist ==="

R=$(curl -s -X PUT -H "$AUTH" -H "$CT" -H "$ORG" -d '{"persona_name":"Alex","persona_role":"Fitness Concierge","greeting":"Hi there! Welcome to FitPro Studio. How can I help you get started on your fitness journey?","personality_traits":["friendly","motivating","knowledgeable"],"primary_color":"#FF6B35","position":"bottom-right","auto_open_delay":5}' "$BASE/receptionist/config/")
check_ok "Configure receptionist" "$R"

echo ""

###############################################################################
# CROSS-FEATURE: Notifications
###############################################################################
echo "=== CROSS-FEATURE: Notifications ==="

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/notifications/")
check_ok "List notifications" "$R"

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/notifications/unread-count/")
check_ok "Unread count" "$R"

echo ""

###############################################################################
# LIST ENDPOINTS VERIFICATION
###############################################################################
echo "=== VERIFICATION: List All Resources ==="

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/sites/sites/")
check_list "Sites" "$R"

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/crm/contacts/")
check_list "Contacts" "$R"

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/crm/campaigns/")
check_list "Campaigns" "$R"

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/crm/deals/")
check_list "Deals" "$R"

R=$(curl -s -X GET -H "$AUTH" -H "$ORG" "$BASE/courses/courses/")
check_list "Courses" "$R"

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/calendar/services/")
check_list "Services" "$R"

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/calendar/bookings/")
check_ok "Bookings list" "$R"

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/payments/products/")
check_list "Products" "$R"

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/kb/documents/")
check_list "KB Documents" "$R"

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/webhooks/endpoints/")
check_list "Webhooks" "$R"

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/receptionist/config/")
check_ok "Receptionist config" "$R"

R=$(curl -s -H "$AUTH" -H "$ORG" "$BASE/auth/orgs/")
check_ok "Organizations" "$R"

echo ""

###############################################################################
# SUMMARY
###############################################################################
echo "============================================"
echo "  SIMULATION RESULTS"
echo "============================================"
echo "  Total tests: $TOTAL"
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
echo ""
if [ $FAIL -gt 0 ]; then
    echo "  FAILURES:"
    echo -e "$FAILURES"
fi
echo "============================================"
