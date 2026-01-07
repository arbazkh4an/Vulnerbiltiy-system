# Authentication System Guide

## Overview
This application implements a secure authentication system with email verification. The signup and login flows are completely separated with proper validation at each step.

## Authentication Flow

### 1. Signup (Registration)

**Endpoint:** `POST /api/auth/register`

**Process:**
1. User submits email, password, and name
2. System checks if user already exists
3. If user exists → Returns "User already exists, please login" (409 status)
4. If user is new:
   - Password is hashed using bcrypt
   - User is created with `isVerified = false`
   - Verification token is generated (valid for 24 hours)
   - Verification URL is returned (in production, this would be sent via email)
   - User is **NOT** automatically logged in

**Response:**
\`\`\`json
{
  "success": true,
  "message": "Registration successful! Please check your email to verify your account.",
  "verificationUrl": "http://localhost:3000/verify-email?token=...",
  "user": {
    "id": "user_...",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
\`\`\`

**Error Cases:**
- Missing fields → 400: "Email, password, and name are required"
- Password too short → 400: "Password must be at least 8 characters long"
- User exists → 409: "User already exists, please login"

---

### 2. Email Verification

**Endpoint:** `GET /api/auth/verify-email?token=...` or `POST /api/auth/verify-email`

**Process:**
1. User clicks verification link with token
2. System validates token:
   - Token exists
   - Token not already used
   - Token not expired (24 hours)
3. If valid:
   - Sets `isVerified = true` in database
   - Marks token as used
   - User can now login

**Response:**
\`\`\`json
{
  "success": true,
  "message": "Email verified successfully! You can now log in."
}
\`\`\`

**Error Cases:**
- Missing token → 400: "Token is required"
- Invalid token → 400: "Invalid token"
- Token already used → 400: "Token already used"
- Token expired → 400: "Token expired"

---

### 3. Login

**Endpoint:** `POST /api/auth/login`

**Process:**
1. User submits email and password
2. System checks if user exists
3. If user doesn't exist → Returns "User not found" (404 status)
4. System verifies password
5. If password incorrect → Returns "Invalid credentials" (401 status)
6. System checks if email is verified
7. If not verified → Returns "Please verify your email before logging in" (403 status)
8. If all checks pass:
   - Session/JWT is created
   - User is authenticated
   - User data is returned

**Response:**
\`\`\`json
{
  "success": true,
  "user": {
    "id": "user_...",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
\`\`\`

**Error Cases:**
- Missing fields → 400: "Email and password are required"
- User not found → 404: "User not found"
- Wrong password → 401: "Invalid credentials"
- Email not verified → 403: "Please verify your email before logging in"

---

## Database Schema

### users_sync table (neon_auth schema)
- `id` (TEXT, generated from raw_json)
- `email` (TEXT, generated from raw_json)
- `name` (TEXT, generated from raw_json)
- `created_at` (TIMESTAMP, generated from raw_json)
- `raw_json` (JSONB) - Contains:
  - `id`
  - `display_name`
  - `primary_email`
  - `password_hash` (bcrypt hashed)
  - `is_verified` (boolean)
  - `signed_up_at_millis`

### email_verification_tokens table
- `id` (SERIAL PRIMARY KEY)
- `user_id` (TEXT) - References users_sync.id
- `token` (TEXT UNIQUE) - Verification token
- `expires_at` (TIMESTAMP) - Token expiration (24 hours)
- `created_at` (TIMESTAMP) - Token creation time
- `used_at` (TIMESTAMP) - When token was used (NULL if unused)

---

## Security Features

1. **Password Hashing:** All passwords are hashed using bcrypt with salt
2. **Email Verification:** Users must verify email before login
3. **Token Expiration:** Verification tokens expire after 24 hours
4. **Single Use Tokens:** Tokens can only be used once
5. **No Auto-Login:** Registration doesn't automatically log users in
6. **Proper Error Messages:** Clear, security-conscious error messages
7. **Session Management:** JWT-based sessions with HTTP-only cookies

---

## Testing the Flow

### Step 1: Register a new user
\`\`\`bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'
\`\`\`

### Step 2: Verify email (use the verificationUrl from step 1)
\`\`\`bash
curl http://localhost:3000/api/auth/verify-email?token=verify_...
\`\`\`

### Step 3: Login
\`\`\`bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
\`\`\`

---

## Frontend Integration

The frontend components are already set up to handle all error cases:

- **Registration Page** (`/register`): Shows success message with verification link
- **Login Page** (`/login`): Displays appropriate errors for each case
- **Verify Email Page** (`/verify-email`): Handles token verification
- **Auth Provider**: Manages authentication state without auto-login after registration

---

## Notes for Production

1. **Email Service:** Replace console.log with actual email sending (SendGrid, Resend, etc.)
2. **Environment Variables:** Set `NEXT_PUBLIC_APP_URL` to your production domain
3. **Rate Limiting:** Add rate limiting to prevent abuse
4. **HTTPS:** Ensure all authentication endpoints use HTTPS
5. **Token Security:** Consider adding IP address or user agent validation
6. **Password Reset:** Add forgot password flow with similar token system

---

## Common Issues & Solutions

**Issue:** "User already exists" on registration
- **Solution:** User should use the login page instead

**Issue:** "User not found" on login
- **Solution:** User needs to register first

**Issue:** "Invalid credentials" on login
- **Solution:** Check password is correct

**Issue:** "Please verify your email"
- **Solution:** User must click verification link from email

**Issue:** "Token expired"
- **Solution:** Request new verification email (feature to be added)

---

This authentication system provides a secure, production-ready foundation for your vulnerability scanning application with proper separation of concerns and comprehensive error handling.
