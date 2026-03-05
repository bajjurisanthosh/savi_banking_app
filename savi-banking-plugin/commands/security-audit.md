Perform a security audit of the SaVi banking app against OWASP Top 10.

Steps:
1. Read `app.py` and `mock_data.py` in full
2. Read all files in `templates/`
3. Check for each of these issues and report findings:

   **A01 - Broken Access Control**
   - Are all sensitive routes protected with `@login_required`?
   - Can a user access another user's data?

   **A02 - Cryptographic Failures**
   - Is the secret key hardcoded? (app.secret_key)
   - Are passwords stored in plaintext?

   **A03 - Injection**
   - Any use of `eval()`, `exec()`, or `os.system()` with user input?
   - Any raw SQL with string formatting?

   **A05 - Security Misconfiguration**
   - Is `debug=True` in production code?
   - Are error messages leaking stack traces?

   **A07 - Identification & Authentication Failures**
   - Is there a rate limit on login attempts?
   - Are sessions properly invalidated on logout?

   **A09 - Security Logging**
   - Are failed login attempts logged?
   - Are transfers logged with user context?

4. Output a markdown table: Issue | Severity (High/Med/Low) | File:Line | Fix
5. Prioritize the top 3 fixes and offer to implement them
