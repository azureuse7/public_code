# Behave: Behaviour-Driven Development (BDD) Testing

> Behave is a Python BDD testing framework that lets you write tests in plain English using the Gherkin syntax (`Given / When / Then`). Tests are readable by both developers and non-technical stakeholders.

---

## Contents

| Directory | Topic |
|-----------|-------|
| [01-Text/](01-Text/) | Introduction to BDD concepts and Behave setup |
| [02-behave/](02-behave/) | Feature files and step definitions |

---

## How Behave Works

1. Write a **feature file** (`.feature`) describing behaviour in plain English
2. Write **step definitions** (Python functions) that map to each `Given/When/Then` line
3. Run `behave` — it matches each step to a function and reports pass/fail

---

## Folder Structure

```
project/
├── features/
│   ├── my_feature.feature    # Gherkin scenarios
│   └── steps/
│       └── my_steps.py       # Python step definitions
└── behave.ini                # Optional configuration
```

---

## Example Feature File

```gherkin
Feature: User login

  Scenario: Successful login with valid credentials
    Given the user is on the login page
    When they enter valid username and password
    Then they should be redirected to the dashboard
```

## Example Step Definitions

```python
from behave import given, when, then

@given("the user is on the login page")
def step_on_login(context):
    context.browser.get("/login")

@when("they enter valid username and password")
def step_enter_credentials(context):
    context.browser.fill("username", "admin")
    context.browser.fill("password", "secret")
    context.browser.submit()

@then("they should be redirected to the dashboard")
def step_check_dashboard(context):
    assert "/dashboard" in context.browser.url
```

## Running Tests

```bash
# Install behave
pip install behave

# Run all tests
behave

# Run a specific feature
behave features/my_feature.feature

# Run with verbose output
behave --no-capture
```
