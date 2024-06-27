I have a variable of type list(object) that looks like this:
```t
variable "rules" {
  type = list(object({
    action      = string
    priority    = number
    source_ips  = list(string)
    description = string
  }))
}
```
I want to validate that the value for “priority” is unique across each object in the list.

So far, the only way I’ve been able to get this to work is:
```t
validation {
  condition     = length([for rule in var.rules : rule["priority"]]) == length(distinct([for rule in var.rules : rule["priority"]]))
  error_message = "Each rule must have a unique priority."
  }
```
This seems to be working fine so far, but I was curious if this would be considered a “correct” way to do this or if this could result in any unexpected validation errors. Is there a better way to accomplish this?

The way you’ve defined this validation rule seems reasonable to me. The distinct function works using the same rules as the equality operator == and so given a list of numbers it will use numeric equality to compare them, which I think matches your stated goal.

One possible simplification is to notice that there will always be the same number of elements in [for rule in var.rules : rule["priority"]] as there are in var.rules (because this for expression has no if clause) and so it’s equivalent to write length(var.rules) here.

The distinct function in the right hand side of the == does depend on the specific priority value, and so you do still need some way to separate that out from the others and for expressions are a fine way to do that, but because this is a list value it would be equivalent to use the splat operator [*] which may make the expression more concise: var.rules[*].priority.

Putting that all together, I think the following would be functionally equivalent to what you wrote but subjectively perhaps a little less visually complicated for a future human to read. (Though of course that really depends on the knowledge and tastes of that future human!)
```t
  validation {
    condition     = length(var.rules) == length(distinct(var.rules[*].priority))
    error_message = "Each rule must have a unique priority."
  }
  ```
Another variant to think about is to convert the list of priorities into a set of priorities, and rely on the fact that set data types inherently coalese equal values into a single element. This is also functionally equivalent to using distinct in your case, because the main significant difference between the two is that distinct preserves the ordering of its input and returns a new list but the length function doesn’t care about the ordering:
```t
  validation {
    condition     = length(var.rules) == length(toset(var.rules[*].priority))
    error_message = "Each rule must have a unique priority."
  }
  ```
Subjectively I prefer to use distinct here because it seems to more directly communicate what you were intending to test. toset could be marginally faster for larger lists of rules due to its implementation, but the Terraform language is not one where we often concern ourselves with performance, because we’re most often working with small collections.

I want to be clear that there’s nothing wrong with what you tried first; these are all equivalent expressions and so I’m sharing this just in the interests of showing some different ways to express the same condition.