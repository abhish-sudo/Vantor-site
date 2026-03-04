# eSewa Integration Analysis & Fixes

## Issues Found and Fixed

### 1. **CRITICAL: Missing Payment Flow**
**Problem:** After order creation, users were redirected to the confirmation page with no way to initiate eSewa payment.

**Fix:** Added "Pay with eSewa" button to [templates/orders/confirmation.html](templates/orders/confirmation.html) that links to the `esewa_checkout` view.

---

### 2. **Template Mismatch**
**Problem:** The `esewa_checkout` view was rendering the initial checkout form template (`checkout.html`) instead of a dedicated eSewa payment template.

**Fix:** Created new template [templates/orders/esewa_payment.html](templates/orders/esewa_payment.html) that:
- Shows order summary with actual order items
- Displays the payment amount clearly
- Includes debug information for testing (remove in production)
- Better user experience with clear eSewa form

---

### 3. **Decimal/Type Conversion Issues**
**Problem:** `total_amount` formatting inconsistencies could cause signature mismatches:
```python
# OLD (problematic)
total_amount = int(float(order.total) * 100) / 100  # Can result in "1000" or "1000.0"
total_amount = round(float(order.total), 2)  # Still inconsistent formatting
```

**Fix:** Proper Decimal handling:
```python
# NEW (correct)
total_amount = str(Decimal(str(order.total)).quantize(Decimal('0.01')))
# Always results in exactly "1000.00" format
```

---

### 4. **Incorrect Template Path**
**Problem:** `esewa_checkout` was rendering `checkout.html` instead of `orders/checkout.html` (or better, ` orders/esewa_payment.html`)

**Fix:** Updated to render `orders/esewa_payment.html`

---

### 5. **Success/Failure Template Paths**
**Problem:** Success and failure views were rendering incomplete paths
```python
# OLD
return render(request, 'success.html')  # Wrong path
return render(request, 'failure.html')  # Wrong path
```

**Fix:**
```python
# NEW
return render(request, 'orders/success.html')  # Correct path
return render(request, 'orders/failure.html')  # Correct path
```

---

### 6. **Code Organization**
**Problem:** Imports scattered throughout the file, duplicate imports, inconsistent structure

**Fix:**
- Moved all imports to the top of[orders/views.py](orders/views.py)
- Consolidated `generate_signature()` function
- Clean code organization

---

### 7. **Missing Dependencies**
**Problem:** Project configuration referenced `django-allauth` and other packages not in requirements.txt

**Fix:** Installed missing packages:
- `django-allauth`
- `requests`
- `PyJWT`
- `cryptography`

---

## How eSewa Integration Works

### Order Flow:
1. User browses products
2. User adds items to cart
3. User clicks checkout
4. User fills order form and submits
5. **NEW:** Order created, user redirected to confirmation page
6. **NEW:** User clicks "Pay with eSewa" button
7. `esewa_checkout` view generates signature and renders payment form
8. User sees payment details with clear amount
9. Payment form submits to eSewa gateway
10. eSewa processes payment and redirects to success/failure URL

### Signature Generation:
```python
# Key steps:
1. Format total_amount as string with 2 decimal places: "1000.00"
2. Create data string to sign (order MUST match signed_field_names):
   data = "total_amount=1000.00,transaction_uuid=<uuid>,product_code=EPAYTEST"
3. Generate HMAC-SHA256 signature with secret key
4. Base64 encode the signature
5. Send signature with exact form fields to eSewa
```

### Key Requirements:
- `total_amount` format must be EXACTLY as string with 2 decimal places
- `signed_field_names` value MUST match the order and fields used in signature generation
- Secret key MUST match your eSewa merchant account
- `transaction_uuid` MUST be unique per transaction

---

## Testing the Integration

### 1. Create Test Order
1. Add products to cart
2. Go to checkout page
3. Fill order form completely
4. Submit (creates order with actual total)

### 2. Initiate Payment
1. On confirmation page, click "Pay with eSewa"
2. Check browser console/terminal for debug output showing:
   - Order number
   - Total amount (formatted correctly)
   - Transaction UUID
   - Data to sign
   - Generated signature

### 3. Check Debug Output
Look for console output like:
```
DEBUG - eSewa Checkout:
  Order: <uuid>
  Total Amount: 1000.00 (type: <class 'str'>)
  Transaction UUID: <uuid>
  Data to Sign: total_amount=1000.00,transaction_uuid=<uuid>,product_code=EPAYTEST
  Signature: <base64_string>
```

### 4. Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| ES104 (Invalid payload signature) | Signature doesn't match form data | Ensure total_amount formatting is "####.##" |
| | Secret key incorrect | Verify secret key with eSewa merchant account |
| | Signed field order wrong | Ensure matches "total_amount,transaction_uuid,product_code" |
| Order not found | Invalid UUID in URL | Verify order was created successfully |
| Form not rendering | Wrong template path | Check template location: `templates/orders/esewa_payment.html` |

---

## eSewa API Details

### Test Endpoint:
```
https://rc-epay.esewa.com.np/api/epay/main/v2/form
```

### Required Fields:
- `amount` - Redundant field (kept for compatibility)
- `tax_amount` - Tax on transaction
- `total_amount` - Total amount to charge (MUST be signed)
- `transaction_uuid` - Unique transaction ID (MUST be signed)
- `product_code` - Merchant product code (MUST be signed)
- `product_service_charge` - Service charge
- `product_delivery_charge` - Delivery charge
- `success_url` - Redirect after success
- `failure_url` - Redirect after failure
- `signed_field_names` - Fields included in signature (comma-separated)
- `signature` - HMAC-SHA256 Base64 encoded

### Callbacks:
After payment, eSewa will POST to your success/failure URLs with transaction details.

---

## Production Checklist

- [ ] Change test endpoint to production: `https://epay.esewa.com.np/api/epay/main/v2/form`
- [ ] Update secret key to production key
- [ ] Update product code from "EPAYTEST"
- [ ] Update success_url to production URL (not localhost)
- [ ] Update failure_url to production URL (not localhost)
- [ ] Remove debug print statements from views
- [ ] Remove debug info from esewa_payment.html template
- [ ] Implement order status updates when payment completes
- [ ] Update `is_paid` and `payment_method` fields in Order model on success
- [ ] Add payment_id tracking from eSewa response
- [ ] Implement proper error handling and logging

---

## Files Modified

1. [orders/views.py](orders/views.py)
   - Fixed esewa_checkout function
   - Proper Decimal handling
   - Added debug logging
   - Organized imports

2. [templates/orders/esewa_payment.html](templates/orders/esewa_payment.html) *(NEW)*
   - Dedicated eSewa payment form template
   - Shows order details
   - Debug information for testing

3. [templates/orders/confirmation.html](templates/orders/confirmation.html)
   - Added "Pay with eSewa" button
   - Redirects to payment flow

---

## Next Steps

1. **Test thoroughly** with valid test credentials
2. **Monitor debug output** to ensure signature generation is correct
3. **Verify eSewa response handling** in success/failure endpoints
4. **Update order status** after successful payments
5. **Implement webhook/callback** verification from eSewa
6. **Move to production** using production endpoints and credentials
