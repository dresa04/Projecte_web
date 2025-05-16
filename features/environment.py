from behave import *
from splinter.browser import Browser
from django.test.runner import DiscoverRunner


# Use Firefox if available, otherwise try Chrome, then fallback to a warning
def before_all(context):
    # Function to build complete URLs
    context.get_url = lambda path: f"http://localhost:8000{path}"

    # With behave-django, the test environment is already set up for us
    # We just need to set up the browser

    # Try to set up browser with multiple driver fallbacks
    try:
        context.browser = Browser('firefox', headless=False)
        print("Using Firefox browser")
    except Exception as firefox_error:
        print(f"Firefox driver error: {firefox_error}")
        try:
            context.browser = Browser('chrome', headless=True)
            print("Using Chrome browser")
        except Exception as chrome_error:
            print(f"Chrome driver error: {chrome_error}")
            print("WARNING: No suitable browser driver found. Tests requiring a browser will fail.")
            context.browser = None


def after_scenario(context, scenario):
    # Clean up after each scenario if needed
    pass


def after_all(context):
    # Proper cleanup of resources
    if hasattr(context, 'browser') and context.browser:
        context.browser.quit()
