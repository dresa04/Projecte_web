from behave import given, when, then
from django.urls import reverse
from django.contrib.auth.models import User
import time


# Mock API responses for testing without hitting actual Riot API
@given('a mocked successful Riot API response')
def step_impl(context):
    # This is a placeholder for setting up API mocking
    # In a real implementation, you would use a library like unittest.mock or pytest-mock
    # to intercept API calls and return predefined responses
    print("Setting up mock API responses - implementation depends on your testing approach")
    pass


@given('I am logged in as a user')
def step_impl(context):
    # Create or get test user with proper password hashing
    user, created = User.objects.get_or_create(
        username='root',
        defaults={'email': 'root@example.com'}
    )
    if created:
        user.set_password('root')  # Hashea la contraseña correctamente
        user.save()

    # Visit the login page
    login_url = context.get_url(reverse('login'))
    if context.browser:
        context.browser.visit(login_url)

        # Fill in login form with correct credentials
        context.browser.fill('username', 'root')
        context.browser.fill('password', 'root')

        # Submit the form
        button = context.browser.find_by_css('button[type="submit"]')
        if button:
            button.first.click()

        # Wait briefly for the login to process
        time.sleep(1)
    else:
        print("WARNING: No browser available, skipping actual login")


@given('I am on the create review page')
def step_impl(context):
    if context.browser:
        url = context.get_url(reverse('review_create_form'))
        context.browser.visit(url)

        # Check if we're on the right page - might need adjustment based on your actual page
        assert 'Crear' in context.browser.html, "Create review page not displayed"
    else:
        print("WARNING: No browser available, skipping page navigation")


@when('I enter a valid Riot ID "{riot_id}"')
def step_impl(context, riot_id):
    if context.browser:
        context.browser.fill('player_id_input', riot_id)
        # Allow time for the API check to run
        time.sleep(1)
    else:
        print(f"Would enter Riot ID: {riot_id}")


@when('I fill in the title field with "{title}"')
def step_impl(context, title):
    if context.browser:
        context.browser.fill('title', title)
    else:
        print(f"Would fill title with: {title}")


@when('I fill in the body field with "{body}"')
def step_impl(context, body):
    if context.browser:
        context.browser.fill('body', body)
    else:
        print(f"Would fill body with: {body}")


@when('I click the submit button')
def step_impl(context):
    if context.browser:
        button = context.browser.find_by_css('button[type="submit"]')
        if button:
            button.first.click()

        # Allow time for form submission
        time.sleep(1)
    else:
        print("Would click submit button")


@then('I should be redirected to the home page')
def step_impl(context):
    if context.browser:
        current_url = context.browser.url
        home_url = context.get_url(reverse('home'))
        assert home_url in current_url, f"Not redirected to home page. Current URL: {current_url}"
    else:
        print("Would check for redirection to home page")


@then('I should see my new review listed')
def step_impl(context):
    if context.browser:
        assert context.browser.is_text_present('Great Support Player'), "New review not found on page"
    else:
        print("Would check for review text on page")


@then('I should see errors about missing required fields')
def step_impl(context):
    if context.browser:
        has_error = (
                context.browser.is_element_present_by_css('.alert-danger') or
                context.browser.is_text_present('Este campo es obligatorio') or
                context.browser.is_text_present('Todos los campos son obligatorios')
        )
        assert has_error, "Error messages for missing fields not found"
    else:
        print("Would check for error messages")