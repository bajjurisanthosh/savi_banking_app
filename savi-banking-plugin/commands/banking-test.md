Run the SaVi banking app tests and summarize results.

Steps:
1. Check if `pytest` is installed: `python -m pytest --version`
   - If missing, install it: `pip install pytest`
2. Check if a `tests/` directory exists
   - If no tests exist yet, scaffold a basic test file `tests/test_app.py` covering:
     * Login with valid credentials (demo@savi.com / password123)
     * Login with invalid credentials returns error flash
     * Dashboard redirects to login when unauthenticated
     * Transfer route deducts from account balance
3. Run tests: `python -m pytest tests/ -v`
4. Report results:
   - How many passed / failed / errored
   - For failures: show the test name, error message, and suggested fix
   - If all pass: suggest the next test to add based on untested routes

$ARGUMENTS
