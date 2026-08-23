"""Quick paraphrase test — prints matched FAQ answer for each query."""

import sys
sys.path.insert(0, ".")

from faq_matcher import match

TESTS = [
    ("I need to book an appointment", "hospital"),
    ("what time do you close", "hospital"),
    ("can someone come pick me up in an ambulance", "hospital"),
    ("I want to talk to a different specialist", "hospital"),
    ("where do I go to get my medicines", "hospital"),
    ("I am locked out of my account", "enterprise"),
    ("can we set up a walkthrough of the product", "enterprise"),
    ("I need someone to look into a bug", "enterprise"),
    ("do you work with retail companies", "enterprise"),
    ("we need a trainer for our team", "enterprise"),
    ("this thing arrived broken", "store"),
    ("can I try this on before buying", "store"),
    ("I ordered something where is it", "store"),
    ("is this the real deal or a knockoff", "store"),
    ("I want to buy a bunch of these for my business", "store"),
]

passed = 0
failed = 0

for query, industry in TESTS:
    result = match(query, industry)
    tag = "PASS" if result else "FAIL"
    print(f"\n[{tag}] ({industry}) \"{query}\"")
    if result:
        print(f"  Q: {result['questions'][0]}")
        print(f"  A: {result['answer']}")
        passed += 1
    else:
        print("  -> No match")
        failed += 1

print(f"\n{'='*60}")
print(f"Results: {passed} passed, {failed} failed, {len(TESTS)} total")
