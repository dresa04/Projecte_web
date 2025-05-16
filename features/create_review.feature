# features/create_review.feature
@wip
Feature: Create a review
  As a user
  I want to create a review
  To share my opinion about a champion

  @wip
  Scenario: Successfully create a review
    Given I am on the create review page
    When I fill in the title field with "My experience with the champion"
    And I select 4 stars rating
    And I fill in the comment field with "An excellent champion, highly recommended"
    And I click the submit button
    Then I should see a message "Review created successfully"