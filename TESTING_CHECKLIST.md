# Authentication Testing Checklist

## Pre-Testing Setup
- [ ] Database is accessible
- [ ] All migrations have run successfully
- [ ] `email_verification_tokens` table exists
- [ ] Environment variables are set

---

## Test Case 1: Successful Registration Flow

### Steps:
1. [ ] Navigate to `/register`
2. [ ] Enter valid email (e.g., `test@example.com`)
3. [ ] Enter name (e.g., `Test User`)
4. [ ] Enter password (min 8 characters)
5. [ ] Confirm password matches
6. [ ] Click "Create Account"

### Expected Results:
- [ ] Success message appears
- [ ] Verification URL is displayed
- [ ] User is NOT logged in
- [ ] Can see "Check Your Email" card
- [ ] Database: User created with `is_verified = false`

---

## Test Case 2: Duplicate Registration

### Steps:
1. [ ] Try to register again with same email from Test Case 1
2. [ ] Fill form with same email

### Expected Results:
- [ ] Error message: "User already exists, please login"
- [ ] Status code: 409
- [ ] User is NOT created again

---

## Test Case 3: Login Before Email Verification

### Steps:
1. [ ] Navigate to `/login`
2. [ ] Enter email from Test Case 1
3. [ ] Enter correct password
4. [ ] Click "Sign In"

### Expected Results:
- [ ] Error message: "Please verify your email before logging in"
- [ ] Status code: 403
- [ ] User is NOT logged in
- [ ] Reminder to check email is shown

---

## Test Case 4: Email Verification

### Steps:
1. [ ] Copy verification URL from registration success page
2. [ ] Navigate to the verification URL
3. [ ] Wait for verification to complete

### Expected Results:
- [ ] Success message: "Email verified successfully!"
- [ ] Green checkmark icon appears
- [ ] "Go to Login" button is shown
- [ ] Database: `is_verified = true`
- [ ] Database: Token marked as `used_at`

---

## Test Case 5: Successful Login After Verification

### Steps:
1. [ ] Navigate to `/login`
2. [ ] Enter verified email
3. [ ] Enter correct password
4. [ ] Click "Sign In"

### Expected Results:
- [ ] Login successful
- [ ] Redirected to `/dashboard`
- [ ] User session created
- [ ] Can access protected routes

---

## Test Case 6: Login with Wrong Password

### Steps:
1. [ ] Navigate to `/login`
2. [ ] Enter verified email
3. [ ] Enter WRONG password
4. [ ] Click "Sign In"

### Expected Results:
- [ ] Error message: "Invalid credentials"
- [ ] Status code: 401
- [ ] User is NOT logged in

---

## Test Case 7: Login with Non-Existent Email

### Steps:
1. [ ] Navigate to `/login`
2. [ ] Enter email that was never registered
3. [ ] Enter any password
4. [ ] Click "Sign In"

### Expected Results:
- [ ] Error message: "User not found"
- [ ] Status code: 404
- [ ] User is NOT logged in

---

## Test Case 8: Expired Verification Token

### Steps:
1. [ ] Register new user
2. [ ] Wait 24+ hours (or manually update `expires_at` in DB)
3. [ ] Try to verify with expired token

### Expected Results:
- [ ] Error message: "Token expired"
- [ ] User remains unverified
- [ ] Need to request new verification email (future feature)

---

## Test Case 9: Reuse Verification Token

### Steps:
1. [ ] Use verification token that was already used
2. [ ] Try to verify again

### Expected Results:
- [ ] Error message: "Token already used"
- [ ] No changes to user verification status

---

## Test Case 10: Invalid Verification Token

### Steps:
1. [ ] Navigate to `/verify-email?token=invalid_token_xxxxx`
2. [ ] Try to verify with fake/random token

### Expected Results:
- [ ] Error message: "Invalid token"
- [ ] Red X icon appears
- [ ] "Back to Register" button shown

---

## Database Verification

After each test, verify in database:

### Check Users Table:
\`\`\`sql
SELECT id, email, name, 
       raw_json->>'is_verified' as is_verified,
       created_at
FROM neon_auth.users_sync
WHERE email = 'test@example.com';
\`\`\`

### Check Verification Tokens:
\`\`\`sql
SELECT user_id, token, expires_at, created_at, used_at
FROM email_verification_tokens
ORDER BY created_at DESC
LIMIT 5;
\`\`\`

---

## Console Logs to Check

Look for these logs during testing:

### Registration:
\`\`\`
[v0] Verification email would be sent to: test@example.com
[v0] Verification URL: http://localhost:3000/verify-email?token=verify_xxxxx
\`\`\`

### Email Verification:
\`\`\`
[v0] Email verification attempt with token: verify_xxxxx
[v0] Token verification result: { valid: true, userId: 'user_xxxxx' }
[v0] User marked as verified: user_xxxxx
[v0] Token marked as used
\`\`\`

### Login:
\`\`\`
[v0] Login attempt for email: test@example.com
[v0] User verification status: { email: 'test@example.com', isVerified: true, rawValue: true }
[v0] Login successful for user: test@example.com
\`\`\`

---

## Summary

Total Tests: 10
- [ ] All registration tests passing
- [ ] All login tests passing
- [ ] All verification tests passing
- [ ] Error handling working correctly
- [ ] Database state is correct after each operation

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ All Passing
