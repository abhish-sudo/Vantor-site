"""
eSewa Integration Debugging Guide
This document helps diagnose the ES104 "Invalid payload signature" error
"""

# According to eSewa API Documentation for Test Environment:
# https://esewa.com.np/developers

ESEWA_TEST_INFO = {
    "endpoint": "https://rc-epay.esewa.com.np/api/epay/main/v2/form",
    "test_merchant_code": "EPAYTEST",
    "test_secret_key": "8gBm/:&EnhH.1/q",  # This is the OFFICIAL test secret from eSewa docs
    "test_product_code": "EPAYTEST",
}

CRITICAL_ISSUES_CHECKLIST = """
ES104 ERROR DIAGNOSIS - Invalid Payload Signature

The signature mismatch usually happens due to:

✓ VERIFIED:
  1. HMAC-SHA256 algorithm is CORRECT
  2. Base64 encoding is CORRECT
  3. Field order is CORRECT: total_amount, transaction_uuid, product_code
  4. Data format is CORRECT: field1=value1,field2=value2,field3=value3
  5. No extra spaces in data string

? NEEDS VERIFICATION:
  1. SECRET KEY - Is '8gBm/:&EnhH.1/q' correct?
     - Contact eSewa support to confirm
     - This key should be in your merchant account settings
  
  2. AMOUNT FORMAT - eSewa might expect:
     - Option A: "100.00" (with 2 decimals) ✓ Currently using this
     - Option B: "100" (without decimals)
     - Option C: "10000" (in paisa, smallest unit)
  
  3. PRODUCT CODE - Must match signed value exactly:
     - Current: "EPAYTEST" ✓
     - Check if your test account uses different code
  
  4. FORM FIELDS - All fields must be in form:
     - All signed fields MUST be in the form
     - signed_field_names tells eSewa which fields are signed
     - Order matters: must match signature generation order
  
  5. TEST vs PRODUCTION:
     - Test endpoint: https://rc-epay.esewa.com.np/...
     - Prod endpoint: https://epay.esewa.com.np/...
     - Currently using: TEST ✓
     - Different endpoints may have different credentials

SOLUTION STEPS:
=================

1. VERIFY YOUR MERCHANT ACCOUNT:
   - Login to https://merchant.esewa.com.np
   - Check your merchant code
   - Check your secret key (should be in settings)
   - Write them down and replace in code

2. TEST THE SIGNATURE MANUALLY:
   - Use Python to generate signature
   - Submit test transaction manually to eSewa
   - Note what error eSewa returns

3. CHECK ESEWA LOGS:
   - If you have merchant dashboard access
   - Check transaction history for errors
   - eSewa might provide error details

4. CONTACT ESEWA SUPPORT:
   - Email: support@esewa.com.np
   - Phone: +977-1-4484485
   - Ask them to verify your test credentials
   - Ask for sample test transaction signature

ALTERNATIVE APPROACH - REQUEST VALIDATION:
============================================
Instead of trying to debug blindly, you could:

1. Send eSewa a test request with debug=true
2. Ask them to validate your merchant setup
3. Get confirmation of correct secret key
4. Get a sample signature or test transaction ID

This would save time instead of guessing.
"""

# Test Different Amount Formats
print(ESEWA_TEST_INFO)
print("\n" + "=" * 80)
print(CRITICAL_ISSUES_CHECKLIST)
print("=" * 80)

print("\nRECOMMENDED NEXT STEP:")
print("""
1. Login to your eSewa Merchant account at https://merchant.esewa.com.np
2. Verify your merchant code and secret key
3. Compare with what's in the code:
   - Merchant Code: EPAYTEST
   - Secret Key: 8gBm/:&EnhH.1/q
   
4. If they don't match, update the code with correct credentials

5. If they do match, contact eSewa support with:
   - Your merchant code
   - Test transaction UUID
   - Amount being tested
   - Error message from eSewa (should be more specific than ES104)
""")
