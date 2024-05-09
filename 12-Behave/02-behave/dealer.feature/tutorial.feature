Feature: Testing the incrementor

Scenario: Test the incrementing a number
  Given a new incrementor of size 5
  When we increment 10
  Then we should see 15