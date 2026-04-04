# Terraform `join` Function

The `join` function concatenates the elements of a list into a single string, placing a separator between each element.

## Syntax

```hcl
join(separator, list)
```

## Examples

```hcl
join(", ", ["foo", "bar", "baz"])
# Result: "foo, bar, baz"

join("sana ", ["foo", "bar", "baz"])
# Result: "foosana barsana baz"
```
