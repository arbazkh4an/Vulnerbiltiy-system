# Authentication System Guide

## Complete Authentication Flow

### 1. User Registration (Signup)

**Endpoint:** `POST /api/auth/register`

**Process:**
1. User submits email, password, and name
2. System checks if user already exists
   - If exists → Returns 409 error: "User already exists, please login"
3. Creates new user with:
   - Hashed password (bcrypt)
   - `isVerified = false`
4. Generates verification token (valid for 24 hours)
5. Returns success with verification URL
6. **User is NOT logged in automatically**

**Response:**
\`\`\`json
{
  "success": true,
  "message": "Registration successful! Please check your email to verify your account.",
  "verificationUrl": "http://localhost:3000/verify-email?token=verify_xxxxx",
  "user": {
    "id": "user_xxxxx",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
\`\`\`

---

### 2. Email Verification

**Endpoint:** `GET /api/auth/verify-email?token=verify_xxxxx`

**Process:**
1. User clicks verification link from email (or demo URL)
2. System validates token:
   - Token exists
   - Token not expired (24 hours)
   - Token not already used
3. Updates user record: `isVerified = true`
4. Marks token as used
5. User can now log in

**Response:**
\`\`\`json
{
  "success": true,
  "message": "Email verified successfully! You can now log in."
}
\`\`\`

**Error Cases:**
- Invalid token → "Invalid token"
- Token already used → "Token already used"
- Token expired → "Token expired"

---

### 3. User Login

**Endpoint:** `POST /api/auth/login`

**Process:**
1. User submits email and password
2. System validates credentials in sequence:

   **Step 1: Check if user exists**
   - If not found → 404: "User not found"

   **Step 2: Verify password**
   - If incorrect → 401: "Invalid credentials"

   **Step 3: Check email verification**
   - If `isVerified = false` → 403: "Please verify your email before logging in"

   **Step 4: All checks pass**
   - Creates session/JWT
   - Returns user data
   - Redirects to dashboard

**Response:**
\`\`\`json
{
  "success": true,
  "user": {
    "id": "user_xxxxx",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
\`\`\`

**Error Cases:**
- User not found (404)
- Invalid password (401)
- Email not verified (403)

---

## Key Features

### Separation of Concerns
- **Registration:** Only creates user, does NOT log in
- **Login:** Separate endpoint with strict validation
- **Verification:** Independent process between signup and login

### Error Messages
| Scenario | Status | Message |
|----------|--------|---------|
| User already exists (signup) | 409 | "User already exists, please login" |
| User not found (login) | 404 | "User not found" |
| Wrong password (login) | 401 | "Invalid credentials" |
| Email not verified (login) | 403 | "Please verify your email before logging in" |

### Security Features
- Passwords hashed with bcrypt
- JWT-based session management
- HTTP-only cookies for session storage
- Verification tokens expire after 24 hours
- Tokens can only be used once
- No password exposure in responses

---

## Testing the Flow

### Complete Test Sequence

1. **Register a new user:**
   \`\`\`bash
   POST /api/auth/register
   {
     "email": "test@example.com",
     "password": "password123",
     "name": "Test User"
   }
   \`\`\`
   Expected: Success with verification URL

2. **Try to login immediately (should fail):**
   \`\`\`bash
   POST /api/auth/login
   {
     "email": "test@example.com",
     "password": "password123"
   }
   \`\`\`
   Expected: 403 "Please verify your email before logging in"

3. **Verify email:**
   \`\`\`bash
   GET /api/auth/verify-email?token=verify_xxxxx
   \`\`\`
   Expected: "Email verified successfully!"

4. **Login after verification:**
   \`\`\`bash
   POST /api/auth/login
   {
     "email": "test@example.com",
     "password": "password123"
   }
   \`\`\`
   Expected: Success, redirected to dashboard

5. **Try to register again with same email:**
   \`\`\`bash
   POST /api/auth/register
   {
     "email": "test@example.com",
     "password": "newpassword",
     "name": "Test User 2"
   }
   \`\`\`
   Expected: 409 "User already exists, please login"

---

## Database Schema

### neon_auth.users_sync
\`\`\`sql
CREATE TABLE neon_auth.users_sync (
  id TEXT GENERATED ALWAYS AS (raw_json->>'id') STORED PRIMARY KEY,
  email TEXT GENERATED ALWAYS AS (raw_json->>'primary_email') STORED,
  name TEXT GENERATED ALWAYS AS (raw_json->>'display_name') STORED,
  raw_json JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);
\`\`\`

**raw_json structure:**
\`\`\`json
{
  "id": "user_xxxxx",
  "primary_email": "user@example.com",
  "display_name": "John Doe",
  "password_hash": "$2b$10$xxxxx...",
  "signed_up_at_millis": 1234567890,
  "is_verified": false
}
\`\`\`

### email_verification_tokens
\`\`\`sql
CREATE TABLE email_verification_tokens (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  token TEXT UNIQUE NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  used_at TIMESTAMPTZ
);
\`\`\`

---

## Implementation Notes

1. **No Auto-Login After Registration:**
   - Registration returns success but does NOT create a session
   - User must verify email first

2. **Login Never Returns "User Already Exists":**
   - That error only appears during registration
   - Login checks: exists → password → verification

3. **Verification Token Security:**
   - Single use only
   - 24-hour expiration
   - Cryptographically secure generation

4. **Production Email (TODO):**
   - Currently logs verification URL to console
   - Integrate with email service (SendGrid, Resend, etc.)
   - Send HTML email with verification button

---

## UI/UX Flow

1. **Registration Page:**
   - User fills form
   - Submits → Shows success message with verification instructions
   - Displays demo verification link (for testing)
   - Prompts to check email

2. **Verification Page:**
   - Automatically verifies on load
   - Shows success/error state
   - Redirects to login on success

3. **Login Page:**
   - User enters credentials
   - Shows specific error messages
   - If email not verified → Shows reminder to check email
   - On success → Redirects to dashboard

---

## Troubleshooting

### Issue: Can't verify email
**Check:**
- Token is valid and not expired
- Token hasn't been used already
- Database connection is working
- Check browser console for errors

### Issue: Login says "User not found"
**Check:**
- Registration completed successfully
- Email spelling is correct
- User exists in database

### Issue: Login says "Please verify your email"
**Check:**
- Verification link was clicked
- Verification completed successfully
- Check `is_verified` field in database

### Issue: "User already exists" error
**Check:**
- This is expected if trying to register with existing email
- Use login instead, or use different email
