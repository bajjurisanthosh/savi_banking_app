Add a new Flask route to the SaVi banking app.

The user will provide: route name, URL path, HTTP methods, and whether it requires login.

Steps:
1. Read `app.py` to understand existing route patterns and imports
2. Add the new route following these conventions:
   - Protected routes use `@login_required` decorator (defined at app.py:15)
   - Flash messages use categories: `success`, `error`, `warning`, `info`
   - Pass `user_name=session["user_name"]` to templates for protected routes
3. Create the Jinja2 template in `templates/` extending `base.html`
4. If the route handles POST, validate inputs and flash an error on bad data
5. Show the user the added route and template, explain what each part does

User's request: $ARGUMENTS
