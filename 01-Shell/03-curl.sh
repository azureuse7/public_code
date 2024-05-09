# response=$( curl -s -k -H "Content-Type: application/json" -X POST -d '{"username":"'$username'", "password":"'$password'"}' ${api_addr}/api/v1/authenticate )

# -k, --insecure --> skip certificate validation
# -X, --request --> used to send custom request to the server.
# -h --> extra header to include in the request.
# Content-Type: application/json -->  Indicates that the request body format is JSON
# -d -->  This causes curl to send the data using the application/x-www-form-urlencoded

# token=$( jq -r '.token' <<< "${response}" )

# jq transform JSON data into a more readable format

# response=$( curl -s -k -H "authorization: Bearer ${token}" -X POST ${api_addr}/api/v1/scripts/defender.sh?project=${twistlock_console_name} -o /root/defender.sh && chmod a+x /root/defender.sh )

# -o, --output -->Write output to <file> instead of stdout

# Bearer ${token} -->HTTP provides a user authentication framework to control access to protected resources. Bearer authentication (also called token authentication) is done by sending security tokens in the authorization header.

# /root/defender.sh -c "$console_cn" -d 'tcp' --install-host