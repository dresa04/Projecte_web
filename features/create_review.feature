Feature: Create Review
  As a registered user
  I want to create a review for a League of Legends player
  So that I can share my opinions about their gameplay

  Scenario: Successfully create a review
    Given I am logged in as a user
    And I am on the create review page
    When I enter a valid Riot ID "TestPlayer#EUW"
    And I fill in the title field with "Great Support Player"
    And I fill in the body field with "This player has excellent map awareness and good communication."
    And I click the submit button
    Then I should be redirected to the home page
    And I should see my new review listed

  Scenario: Create review with missing information
    Given I am logged in as a user
    And I am on the create review page
    When I fill in the title field with "Incomplete Review"
    And I click the submit button
    Then I should see errors about missing required fields