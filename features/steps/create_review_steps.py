from behave import given, when, then
from django.urls import reverse

@given('I am on the create review page')
def step_impl(context):
    url = context.get_url(reverse('create_review'))
    print(f"Visiting URL: {url}")  # Debug
    context.browser.visit(url)

@when('I fill in the title field with "{title}"')
def step_impl(context, title):
    context.browser.fill('title', title)

@when('I select {stars:d} stars rating')
def step_impl(context, stars):
    context.browser.choose(f'rating_{stars}')

@when('I fill in the comment field with "{comment}"')
def step_impl(context, comment):
    context.browser.fill('comment', comment)

@when('I click the submit button')
def step_impl(context):
    button = context.browser.find_by_css('button[type="submit"]').first
    button.click()
    print("hola")

@then('I should see a message "{message}"')
def step_impl(context, message):
    assert context.browser.is_text_present(message), f"Message '{message}' not found in page"