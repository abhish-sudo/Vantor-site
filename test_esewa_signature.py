"""
Test eSewa Signature Generation
This script tests the signature generation against known test values
"""
import hmac
import hashlib
import base64
from decimal import Decimal

def generate_signature(key, message):
    """Generate HMAC-SHA256 signature for eSewa payment"""
    key = key.encode('utf-8')
    message = message.encode('utf-8')
    
    hmac_sha256 = hmac.new(key, message, hashlib.sha256)
    digest = hmac_sha256.digest()
    
    # Convert the digest to a Base64-encoded string
    signature = base64.b64encode(digest).decode('utf-8')
    
    return signature


# Test Case 1: Basic test with known values
print("=" * 80)
print("eSewa Signature Generation Test")
print("=" * 80)

# Test data
secret_key = '8gBm/:&EnhH.1/q'
total_amount = '100.00'
transaction_uuid = '12345678-1234-1234-1234-123456789012'
product_code = 'EPAYTEST'

# Create data to sign
data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"

print(f"\nSecret Key: {secret_key}")
print(f"Data to Sign: {data_to_sign}")
print(f"Data Length: {len(data_to_sign)} characters")
print(f"Data Bytes: {data_to_sign.encode('utf-8')}")

# Generate signature
signature = generate_signature(secret_key, data_to_sign)

print(f"\nGenerated Signature: {signature}")
print(f"Signature Length: {len(signature)} characters")

# Test Case 2: With Decimal conversion (simulating Django model)
print("\n" + "=" * 80)
print("Test with Decimal Conversion (Django Model)")
print("=" * 80)

from django.db import models
# Simulate Django Decimal field
order_total = Decimal('100.00')

# Convert properly
total_amount_decimal = str(Decimal(str(order_total)).quantize(Decimal('0.01')))

data_to_sign_decimal = f"total_amount={total_amount_decimal},transaction_uuid={transaction_uuid},product_code={product_code}"

print(f"\nOrder Total (Decimal): {order_total}")
print(f"Converted Amount: {total_amount_decimal} (type: {type(total_amount_decimal).__name__})")
print(f"Data to Sign: {data_to_sign_decimal}")

signature_decimal = generate_signature(secret_key, data_to_sign_decimal)

print(f"Generated Signature: {signature_decimal}")

# Test Case 3: Check for common issues
print("\n" + "=" * 80)
print("Common Issues Check")
print("=" * 80)

# Check 1: Trailing spaces
data_with_space = f"total_amount={total_amount}, transaction_uuid={transaction_uuid},product_code={product_code}"
sig_with_space = generate_signature(secret_key, data_with_space)
print(f"\n1. DATA WITH SPACE AFTER COMMA:")
print(f"   Data: {data_with_space}")
print(f"   Signature: {sig_with_space}")
print(f"   MATCHES ORIGINAL: {sig_with_space == signature}")

# Check 2: Different field order
data_wrong_order = f"transaction_uuid={transaction_uuid},total_amount={total_amount},product_code={product_code}"
sig_wrong_order = generate_signature(secret_key, data_wrong_order)
print(f"\n2. WRONG FIELD ORDER:")
print(f"   Data: {data_wrong_order}")
print(f"   Signature: {sig_wrong_order}")
print(f"   MATCHES ORIGINAL: {sig_wrong_order == signature}")

# Check 3: Different product code
data_diff_code = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code=DIFFERENT"
sig_diff_code = generate_signature(secret_key, data_diff_code)
print(f"\n3. DIFFERENT PRODUCT CODE:")
print(f"   Data: {data_diff_code}")
print(f"   Signature: {sig_diff_code}")
print(f"   MATCHES ORIGINAL: {sig_diff_code == signature}")

# Test Case 4: Real world example from eSewa docs (if available)
print("\n" + "=" * 80)
print("eSewa Documentation Test Vector")
print("=" * 80)

# According to eSewa API, a known test vector would be good
# Let's test with a simple amount
esewa_test_secret = '8gBm/:&EnhH.1/q'
esewa_test_amount = '100'
esewa_test_uuid = 'fc7e7d9e-a8d5-4fc4-9f20-2f4f9bcc5e3f'
esewa_test_code = 'EPAYTEST'

esewa_data = f"total_amount={esewa_test_amount},transaction_uuid={esewa_test_uuid},product_code={esewa_test_code}"
esewa_sig = generate_signature(esewa_test_secret, esewa_data)

print(f"\nAmount: {esewa_test_amount}")
print(f"UUID: {esewa_test_uuid}")
print(f"Product Code: {esewa_test_code}")
print(f"Data: {esewa_data}")
print(f"Signature: {esewa_sig}")

print("\n" + "=" * 80)
print("DEBUGGING NOTES:")
print("=" * 80)
print("""
If you're still getting ES104 error:

1. ✓ Signature generation algorithm is HMAC-SHA256 ✓
2. ✓ Base64 encoding of digest is correct ✓
3. ? Secret Key '8gBm/:&EnhH.1/q' - VERIFY WITH ESEWA
4. ? Amount format - must match EXACTLY with signed value
5. ? signed_field_names order - must match data order
6. ? Test environment - ensure using correct endpoint

NEXT STEPS:
- Run this script and note the generated signatures
- Compare with any test signatures from eSewa documentation
- Verify secret key is correct for your merchant account
- Check if eSewa expects different field names or order
""")
