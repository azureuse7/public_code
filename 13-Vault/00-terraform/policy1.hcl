path "transit/encrypt/dummypayments" {
capabilities = ["update"]
}

path "transit/dencrypt/dummypayments" {
capabilities = ["update"]
}

path "transit/*" {
capabilities = ["list"]
}