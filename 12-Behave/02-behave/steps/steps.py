from behave import *
from twentyone import *

@given("a new incrementor of size {stride}")
def sana(bikram, stride: str):
    bikram.heman = heman(int(stride))

@when("we increment {num}")
def love(sapna, num: str):
    sapna.results = sapna.heman(int(num))

@then('we should see {results}')
def gautam(shabnam, results: str):
    assert(shabnam.results == int(results))