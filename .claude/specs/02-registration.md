# Spec: Registration

## Overview
Wire up the existing `/register` page so a visitor can create a Spendly account. The form currently renders but posts nowhere useful (`/register` only accepts GET). This step adds the POST handler: validate input, reject duplicate emails, store the user with a werkzeug-hashed password, and send the user to the login page. It is the first feature that writes user data through the `users` table created in Step 1, and it must exist before login (Step 3) has anyone to authenticate.

## Depends on
- Step 1 — Database setup (`users` table, `get_db()`, `init_db()`).

## Routes
- `GET /register` — render the registration form (already exists, unchanged) — public
- `POST /register` — validate the submitted form, create the user, redirect to `/login` on success, re-render the form with an error message on failure — public

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email UNIQUE`, `password_hash`, `created_at`) in `database/db.py` is sufficient.

## Templates
- **Create:** none
- **Modify:**
  - `templates/register.html` — change `action="/register"` to `action="{{ url_for('register') }}"`; re-populate the `name` and `email` inputs from the submitted values when re-rendering after an error (never re-populate the password).
  - `templates/login.html` — show an optional success notice (e.g. "Account created, please sign in") when redirected from registration, using a query parameter such as `?registered=1`.

## Files to change
- `app.py` — change `register()` to accept `GET` and `POST`, add the validation and insert logic, import `request`, `redirect`, `url_for` from Flask, `generate_password_hash` from `werkzeug.security`, and `sqlite3` for `IntegrityError`.
- `templates/register.html`
- `templates/login.html`
- `static/css/style.css` — only if a success-notice style is needed (reuse the `.auth-error` pattern, using existing CSS variables such as `--accent-light` and `--accent`).

## Files to create
- `tests/test_registration.py` — pytest tests for the registration flow (pytest and pytest-flask are already installed).

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`); never store or log the plain password
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `get_db()` from `database/db.py` and close the connection in a `finally` block
- Trim whitespace on `name` and `email`; store the email lower-cased so uniqueness is case-insensitive
- Server-side validation (do not rely on the HTML `required` attributes):
  - name, email and password are all non-empty
  - email has a basic valid shape (contains `@` and a domain part)
  - password is at least 8 characters, matching the form's "Min. 8 characters" hint
- Duplicate email: check by catching `sqlite3.IntegrityError` from the insert (or a prior `SELECT`), and show a generic message such as "An account with this email already exists"
- On error, return the form with status 200 and an `error` string; the template already renders `{{ error }}`
- Do not start a session or auto-login; session handling belongs to Step 3
- Replace the existing `register` route in place; do not add new route files
- Run the app on port 5001 as per CLAUDE.md

## Definition of done
- [ ] `GET /register` still renders the form
- [ ] Submitting a valid name, new email and password of 8+ characters redirects to `/login`, and the login page shows the "account created" notice
- [ ] The new row exists in the `users` table with `password_hash` set to a werkzeug hash (not the plain password)
- [ ] Registering again with the same email shows an error and creates no second row
- [ ] Registering with the same email in different letter case is also rejected
- [ ] Submitting with an empty field, an invalid email, or a password shorter than 8 characters shows an error and creates no row
- [ ] After a failed submit, the name and email fields keep their values and the password field is empty
- [ ] The form posts via `url_for('register')`, not a hardcoded path
- [ ] `venv/Scripts/pytest tests/test_registration.py` passes
