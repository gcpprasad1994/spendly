# Spec: Login and Logout

## Overview
Make the existing `/login` page work and turn the `/logout` placeholder into a real route. A visitor signs in with the email and password they registered with in Step 2; the app verifies the werkzeug hash, stores the user's id and name in the Flask session, and sends them to `/profile`. Logout clears the session and returns to the landing page. This is the first step that gives the app a notion of "who is logged in", which every later step (profile, expenses) relies on. The navbar also changes to reflect the signed-in state.

## Depends on
- Step 1 — Database setup (`users` table, `get_db()`).
- Step 2 — Registration (users with hashed passwords exist; `/login?registered=1` notice already handled in `login.html`).

## Routes
- `GET /login` — render the sign-in form (already exists). If a user is already logged in, redirect to `/profile` — public
- `POST /login` — verify credentials; on success set the session and redirect to `/profile`; on failure re-render the form with an error — public
- `GET /logout` — clear the session and redirect to `/` (landing) — logged-in (a logged-out visitor is simply redirected to `/` too, no error)

`/profile` remains the Step 4 placeholder string; the redirect target only needs to resolve.

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email UNIQUE`, `password_hash`, `created_at`) in `database/db.py` is sufficient.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — change `action="/login"` to `action="{{ url_for('login') }}"`; re-populate the `email` input from the submitted value after an error (never the password).
  - `templates/base.html` — navbar shows "Sign in" / "Get started" when logged out, and the user's name plus a "Sign out" link to `url_for('logout')` when `session.user_id` is set.

## Files to change
- `app.py` — import `session` from Flask and `check_password_hash` from werkzeug; set `app.secret_key`; make `login()` handle GET and POST; replace the `logout()` placeholder.
- `templates/login.html`
- `templates/base.html`
- `static/css/style.css` — only if the signed-in navbar needs a small style (e.g. the user name); use existing CSS variables.

## Files to create
- `tests/test_login_logout.py` — pytest tests for login and logout (reuse the temporary-database fixture approach from `tests/test_registration.py`; move the shared fixture to `tests/conftest.py` if it avoids duplication).

## New dependencies
No new dependencies. Flask's built-in signed-cookie session and werkzeug's `check_password_hash` are enough.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug; verify with `check_password_hash`, never compare plain text
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `get_db()` from `database/db.py` and close the connection in a `finally` block
- Session secret: read `app.secret_key` from an environment variable (e.g. `SPENDLY_SECRET_KEY`) with a clearly-labelled development fallback; never commit a real production secret
- Look the user up by `email.strip().lower()` to match how registration stores emails
- Use one generic error for both "unknown email" and "wrong password" (e.g. "Invalid email or password.") so the form does not reveal which emails are registered
- Run `check_password_hash` against a dummy hash when the email is not found, or otherwise keep the two failure paths similar in work done
- Store only `user_id` and `name` in the session, never the password hash
- Call `session.clear()` before setting the user on login, and on logout
- Do not honour a user-supplied `next`/redirect parameter (avoids open redirects); always redirect to `/profile` after login
- Empty fields are rejected server-side with the same generic error; do not rely on the HTML `required` attribute
- Replace the existing `login` and `logout` routes in place; do not add new route files
- Run the app on port 5001 as per CLAUDE.md

## Definition of done
- [ ] `GET /login` still renders the form for a logged-out visitor
- [ ] Logging in with the email and password used at registration redirects to `/profile`
- [ ] Email matching is case-insensitive (`ASHA@Example.com` logs in the account registered as `asha@example.com`)
- [ ] A wrong password and an unregistered email both show the identical "Invalid email or password." error and set no session
- [ ] An empty email or password shows the error and sets no session
- [ ] After a failed login the email field keeps its value and the password field is empty
- [ ] After login the navbar shows the user's name and a "Sign out" link instead of "Sign in" / "Get started"
- [ ] Visiting `/login` while logged in redirects to `/profile`
- [ ] `GET /logout` clears the session, redirects to `/`, and the navbar shows "Sign in" / "Get started" again
- [ ] `GET /logout` while logged out redirects to `/` without an error
- [ ] The session cookie contains no password hash (inspect via the browser dev tools or the test client)
- [ ] The form posts via `url_for('login')`, not a hardcoded path
- [ ] `venv/Scripts/pytest` passes, including the new login/logout tests and the existing registration tests
