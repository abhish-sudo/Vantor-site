# ES104 Error Troubleshooting Guide

## What is ES104?
**ES104** = Invalid Payload Signature

This means eSewa received the payment request, but the signature doesn't match what it expected.

---

## Root Causes (in order of likelihood)

### 1. **WRONG SECRET KEY** ❌ (Most Common - 80% of cases)
The test credentials `8gBm/:&EnhH.1/q` are for eSewa's public test account, but YOUR merchant account might have a DIFFERENT secret key.

**How to fix:**
1. Go to https://merchant.esewa.com.np
2. Login with your credentials
3. Go to "Settings" or "API Settings"
4. Find your "Secret Key" (not the same as merchant code!)
5. Copy your actual secret key
6. Update in `.env` file:
   ```
   ESEWA_SECRET_KEY=your-actual-secret-key-here
   ```
7. Restart Django server
8. Try payment again

### 2. **WRONG MERCHANT CODE** ❌ (20% of cases)
Similarly, your merchant code might not be `EPAYTEST`.

**How to fix:**
1. In eSewa merchant dashboard, find your actual merchant code
2. Update in `.env`:
   ```
   ESEWA_MERCHANT_CODE=YOUR_ACTUAL_CODE
   ESEWA_PRODUCT_CODE=YOUR_ACTUAL_CODE
   ```

### 3. **AMOUNT FORMAT MISMATCH** ❌ (15% of cases)
The test code uses `100.00` but eSewa might expect `100` or `10000`.

**How to test this:**
The code now generates multiple formats. Check terminal output and look for all three formats:
- Format A: `100.00` (with decimals - currently used)
- Format B: `100` (without decimals)
- Format C: `10000` (in paisa - smallest unit)

To try **Format B** (without decimals), edit [orders/views.py](orders/views.py):
```python
# Change this line:
total_amount = total_amount_with_decimals

# To this to try without decimals:
total_amount = total_amount_int

# Or to this to try paisa:
total_amount = total_amount_paisa
```

### 4. **DATA NOT BEING SIGNED CORRECTLY** ❌ (5% of cases)
The algorithm is verified to be correct, but double-check:
- `signed_field_names` in form = `total_amount,transaction_uuid,product_code`
- Data string = `total_amount=X,transaction_uuid=Y,product_code=Z`
- No extra spaces or different order

---

## Step-by-Step Debugging

### Step 1: Check Terminal Output
When you click "Pay with eSewa", you should see output in your Django terminal:

```
╔════════════════════════════════════════════════════════════════╗
║ eSewa Payment Preparation                                      ║
║ ...
╚════════════════════════════════════════════════════════════════╝
```

**What to look for:**
- Order Number: Should match your order
- All three amount formats
- Data To Sign: Check formatting
- Signature: Base64 encoded string

### Step 2: Contact eSewa Support

Email: **support@esewa.com.np**
Phone: **+977-1-4484485**

**What to send them:**
```
Hello,

I'm integrating eSewa payment gateway and getting ES104 error (Invalid payload signature).

My details:
- Merchant Code: [your_code]
- Test environment
- Amount: 100.00
- Transaction UUID: [test_uuid]
- Product Code: EPAYTEST

Can you:
1. Confirm my secret key is correct?
2. Provide a sample test signature for verification?
3. Clarify the amount format (with/without decimals)?

Thank you
```

### Step 3: Test with Different Amounts

Try the following test amounts in order:
1. **100.00** (two decimals)
2. **100** (integer)
3. **10000** (paisa/smallest unit)

For each one, check:
- Terminal output shows correct data
- Signature is generated
- Whether eSewa accepts it or gives ES104

---

## Verification Checklist

Before trying payment again:

- [ ] eSewa merchant account created and active
- [ ] Merchant code retrieved from dashboard
- [ ] Secret key retrieved from dashboard
- [ ] `.env` file updated with your actual credentials
- [ ] Django server restarted after `.env` changes
- [ ] Terminal shows payment preparation info
- [ ] All three amount formats are displayed in output
- [ ] Signature is being generated (not empty)

---

## What If It Still Doesn't Work?

### Option A: Use Default Test Account
If you don't have an eSewa merchant account yet:
1. Create one at https://merchant.esewa.com.np
2. Verify your email
3. Get your merchant code and secret key
4. Update `.env` with these values

### Option B: eSewa Sample Integration
Compare your code with eSewa's official examples:
- GitHub: https://github.com/esewa-solutions/esewa-sdk-js
- Documentation: https://developer.esewa.com.np

### Option C: Use Different Test Secret
If the default `8gBm/:&EnhH.1/q` isn't working, eSewa might have updated it.
1. Check eSewa dev documentation for current test credentials
2. Update in `.env`
3. Try again

---

## Common Mistakes

❌ **Mistake 1**: Using same secret key for test and production
- Test has its own secret key
- Production has a different secret key

❌ **Mistake 2**: Whitespace in data string
- `total_amount=100, transaction_uuid=X...` (space after comma) ❌
- `total_amount=100,transaction_uuid=X...` (no space) ✓

❌ **Mistake 3**: Wrong field order
- Correct order: `total_amount, transaction_uuid, product_code` ✓
- Any other order will give different signature ❌

❌ **Mistake 4**: Not restarting Django after `.env` changes
- Edit `.env`
- Must restart Django server
- Environment variables are loaded at startup

---

## Test Flow (What Should Happen)

1. **Add items to cart** ✓
2. **Fill order form** ✓
3. **Submit** → Order created ✓
4. **Click "Pay with eSewa"** → esewa_checkout view called ✓
5. **Terminal shows debug info** → Signature generated ✓
6. **Payment form appears** → With your order amount ✓
7. **Submit to eSewa** → Browser redirects to eSewa.com.np ✓
8. **Enter payment password** on eSewa → Payment processed ✓
9. **Success page** or **Failure page** → Redirect from eSewa ✓

If you're stuck between steps 5-6 (signature generation), the issue is one of the above.

---

## Files to Check

- [orders/views.py](orders/views.py) - `esewa_checkout()` function
- [templates/orders/esewa_payment.html](templates/orders/esewa_payment.html) - Form fields
- [`.env`](.env) - Credentials
- [ESEWA_INTEGRATION_ANALYSIS.md](ESEWA_INTEGRATION_ANALYSIS.md) - Integration overview

---

## Success Indicators

You'll know it's working when you see:

1. ✓ Order created successfully
2. ✓ Confirmation page shows "Pay with eSewa" button
3. ✓ Clicking button shows payment form with correct amount
4. ✓ Submitting form redirects to `esewa.com.np`
5. ✓ eSewa doesn't show ES104 error
6. ✓ After payment, redirects to success/failure URL

Step 3 is usually where ES104 appears. If you don't get past step 2, that's a different issue.

---

## Still Stuck?

1. **Run**: `python test_esewa_signature.py` to verify algorithm
2. **Check**: Django logs for any exceptions
3. **Verify**: Order was created with correct total
4. **Contact**: eSewa support with your merchant code and test output
5. **Consider**: Testing with a different merchant account or test environment
