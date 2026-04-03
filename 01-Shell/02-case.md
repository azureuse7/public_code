# Bash Case Statements
> Case statements provide a multi-branch conditional structure in Bash — similar to `switch` in other languages. They match a variable against a series of patterns and execute the matching block, making scripts easier to read than long `if/elif` chains.

```bash
#!/bin/bash

echo -n "Enter the name of a country: "
read -r COUNTRY

echo -n "The official language of $COUNTRY is "

case $COUNTRY in

  Lithuania)
    echo -n "Lithuanian"
    ;;

  Romania | Moldova)
    echo -n "Romanian"
    ;;

  Italy | "San Marino" | Switzerland | "Vatican City")
    echo -n "Italian"
    ;;

  *)
    echo -n "unknown"
    ;;
esac