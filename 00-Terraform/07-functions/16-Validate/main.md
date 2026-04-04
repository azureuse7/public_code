# Terraform Variable Validation - Ensuring Unique Priority Values

This note covers how to validate that a field is unique across all objects in a `list(object)` variable.

## Problem

Given a variable of type `list(object)` that looks like this:

```hcl
variable "rules" {
  type = list(object({
    action      = string
    priority    = number
    source_ips  = list(string)
    description = string
  }))
}
```

The goal is to validate that the value for `priority` is unique across each object in the list.

## Solution 1: Using `distinct` with a `for` expression

The straightforward approach uses `distinct` to compare the count of all priorities against the count of unique priorities:

```hcl
validation {
  condition     = length([for rule in var.rules : rule["priority"]]) == length(distinct([for rule in var.rules : rule["priority"]]))
  error_message = "Each rule must have a unique priority."
}
```

This works correctly. The `distinct` function uses the same equality rules as `==`, so it correctly compares numbers.

## Solution 2: Simplified with splat operator (recommended)

Because the `for` expression without an `if` clause always produces the same number of elements as `var.rules`, you can replace the left-hand side with `length(var.rules)`. The right-hand side can use the splat operator `[*]` for conciseness:

```hcl
validation {
  condition     = length(var.rules) == length(distinct(var.rules[*].priority))
  error_message = "Each rule must have a unique priority."
}
```

## Solution 3: Using `toset`

An alternative is to convert the list of priorities to a set, which inherently removes duplicates. This is functionally equivalent to using `distinct` in this context:

```hcl
validation {
  condition     = length(var.rules) == length(toset(var.rules[*].priority))
  error_message = "Each rule must have a unique priority."
}
```

## Notes

- All three solutions are functionally equivalent.
- Solution 2 with `distinct` is preferred because it more directly communicates the intent of the validation.
- `toset` could be marginally faster for very large lists, but performance is rarely a concern in Terraform since collections are typically small.
