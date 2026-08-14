# Login App (Node.js + Express + SQLite)

A working login system: signup, login, sessions, and a protected dashboard page.

## Structure
```
login-app/
├── app.js              # Main server entry point
├── db.js                # SQLite database setup
├── routes/
│   └── auth.js           # /signup, /login, /logout, /me routes
├── public/
│   ├── login.html
│   ├── signup.html
│   └── dashboard.html    # protected — redirects to login if not authenticated
├── .env                  # secrets (SESSION_SECRET, PORT) — DO NOT commit
├── .gitignore
└── package.json
```

## Setup

```bash
cd login-app
npm install
```

Edit `.env` and set a strong random `SESSION_SECRET` before deploying anywhere
(you can leave the placeholder for local testing).

## Run

```bash
npm start
```

Then open:
- http://localhost:3000/signup.html — create an account
- http://localhost:3000/login.html — log in
- http://localhost:3000/dashboard.html — protected page, redirects to login if not authenticated

The SQLite database file `users.db` is created automatically on first run.

## What's already handled
- Passwords are hashed with bcrypt before storage — never stored in plain text.
- Login attempts are rate-limited (10 per 15 min per IP) to slow brute-force attacks.
- Sessions use `httpOnly` cookies.
- SQL queries use parameterized statements (prevents SQL injection).
- Generic "Invalid email or password" error on login — doesn't reveal whether an email is registered.

## Before deploying to production
1. Set a strong, random `SESSION_SECRET` in your production environment (not in git).
2. Serve everything over **HTTPS**, and uncomment `cookie: { secure: true }` in `app.js`.
3. Swap SQLite for **PostgreSQL** for a production-grade database (Render, Railway, Supabase all support it) — the query logic stays almost identical if you move to an ORM like Prisma later.
4. Consider adding email verification and a password-reset flow.
5. Never commit `.env` or `users.db` — both are already in `.gitignore`.

## Testing it
Try signing up with a real-looking test email (e.g. `test@example.com`) and a
password of 8+ characters, then log in and confirm the dashboard loads and
shows your email. Try wrong passwords to confirm the error handling works,
and try the rate limiter by failing login 11 times quickly.
## 🛡️ PhishShield – Scanner Module

### 🚀 Current Progress
- **Scanner UI Design:** Initiated dark-mode cyber aesthetic layout.
- **Homepage Structure:** Planning component flow and responsive layout.
- **UI/UX Research:** Analyzing modern cybersecurity scanner interfaces.
- **Core Module:** Scanner logic and input validation under development.

### 👩‍💻 Developer
**Astha Mishra**
