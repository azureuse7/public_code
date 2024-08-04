```bash
response=$( curl -s -k -H "Content-Type: application/json" -X POST -d '{"username":"'$username'", "password":"'$password'"}' ${api_addr}/api/v1/authenticate )

#-k, --insecure --> skip certificate validation
-X, --request --> used to send custom request to the server.
-h --> extra header to include in the request.
Content-Type: application/json -->  Indicates that the request body format is JSON
-d -->  This causes curl to send the data using the application/x-www-form-urlencoded

token=$( jq -r '.token' <<< "${response}" )

jq transform JSON data into a more readable format

response=$( curl -s -k -H "authorization: Bearer ${token}" -X POST ${api_addr}/api/v1/scripts/defender.sh?project=${twistlock_console_name} -o /root/defender.sh && chmod a+x /root/defender.sh )

-o, --output -->Write output to <file> instead of stdout

Bearer ${token} -->HTTP provides a user authentication framework to control access to protected resources. Bearer authentication (also called token authentication) is done by sending security tokens in the authorization header.

/root/defender.sh -c "$console_cn" -d 'tcp' --install-host
```

- #### curl is a command-line tool in Bash used for transferring data with URLs. 
- It is extremely versatile and supports a wide range of protocols, including HTTP, HTTPS, FTP, and more. Here are some common use cases and examples of how to use curl in Bash:

#### Basic Syntax
```bash
curl [options] [URL]
```
#### Common Use Cases
##### 1) Downloading a File

- You can use curl to download a file from the internet.

```bash
curl -O https://example.com/file.txt
```
- -O: Saves the file with the same name as the remote file.
##### 2) Saving a File with a Specific Name

If you want to save the file with a different name, use the -o option:

```bash
curl -o myfile.txt https://example.com/file.txt
```
##### 3) Making HTTP GET Requests

You can make HTTP GET requests to retrieve data from a server:
```bash
curl https://api.example.com/data
```
#### 4) Making HTTP POST Requests

To send data to a server using HTTP POST, use the -d option:

```bash
curl -X POST -d "param1=value1&param2=value2" https://api.example.com/submit
```
- -X POST: Specifies the HTTP method to use (POST in this case).
- -d: Sends the specified data in a POST request to the server.
##### 5) Setting HTTP Headers

To send custom HTTP headers, use the -H option:

```bash
curl -H "Content-Type: application/json" -H "Authorization: Bearer token" https://api.example.com/data
```
##### 6) Downloading Files with Authentication

- If a file is behind basic authentication, use the -u option:

```bash
curl -u username:password -O https://example.com/securefile.txt
Handling HTTPS Connections
```
#### 7) If you need to ignore certificate warnings, use the -k option:

```bash
curl -k https://self-signed.example.com
```
#### 8) Following Redirects

- To follow HTTP redirects automatically, use the -L option:

```bash
curl -L https://example.com/redirect
```
#### 9) Uploading Files

To upload a file to a server, use the -F option:

```bash
curl -F "file=@/path/to/file.txt" https://api.example.com/upload
```
-F: Emulates a form submission in which files can be uploaded.
Verbose Output

To see detailed request and response information, use the -v option:

```bash
curl -v https://example.com
```
#### Examples
##### Example 1: Downloading a Web Page
```bash
curl https://www.example.com -o example.html
```
This command downloads the web page at https://www.example.com and saves it as example.html.

##### Example 2: Fetching JSON Data
```bash
curl -H "Accept: application/json" https://api.example.com/data
```
This command fetches JSON data from an API endpoint, specifying the Accept header to request JSON.

#####  Example 3: Submitting Form Data
```bash
curl -X POST -d "name=John&age=30" https://example.com/form-submit
```
This command submits form data to a server using an HTTP POST request.

Useful Options
-I: Fetches the HTTP headers only, useful for checking the response status.

```bash
curl -I https://example.com
```
--max-time <seconds>: Limits the total time allowed for the transfer.

```bash
curl --max-time 10 https://example.com
```
--limit-rate <speed>: Limits the download rate, useful for bandwidth management.

```bash
curl --limit-rate 100k https://example.com
```
##### Conclusion
- curl is an essential tool in the Bash toolkit for web scraping, API interaction, file downloading, and more. 
- By combining various options, you can handle a wide range of HTTP tasks effectively and efficiently. 
- For more advanced usage, refer to the curl man page or use man curl in the terminal to explore all available options and examples.






