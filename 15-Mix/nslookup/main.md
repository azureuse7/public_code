- The **nslookup** command is a network administration tool used for querying the Domain Name System (DNS) to obtain domain name or IP address mapping information.

#### Overview
- **Purpose**: To query DNS servers and retrieve domain name or IP address mappings.
- **Usage**: Commonly used to troubleshoot DNS-related problems, such as resolving domain names to IP addresses or vice versa.
#### How nslookup Works
When you run **nslookup**, it sends a DNS query to the specified DNS server (or the default one configured in your system) and retrieves the DNS records associated with a domain name or IP address. 

It operates in both interactive and non-interactive modes:

- **Interactive Mode**: Allows multiple queries in a single session.
- **Non-Interactive Mode**: Executes a single query and returns the result.
```yaml
nslookup [options] [hostname] [server]
```
- **hostname**: The domain name or IP address you want to look up.
- **server**: (Optional) The DNS server you want to query. If omitted, it uses the default DNS server configured on your system.
- **options**: Command-line options to modify the behavior of nslookup.
#### Common Command-Line Options
- ```-type=record_type```: Specifies the type of DNS record to look up (e.g., A, MX, TXT, NS).
- ```-debug```: Enables debugging mode to provide more detailed output.
- ```-timeout=N```: Sets the timeout for a response to N seconds.
- ```-retry=N```: Sets the number of retries to N.
#### Examples
##### Example 1: Basic Domain Lookup
```yaml
nslookup example.com
```
Output:
```yaml
yaml
Copy code
Server:         192.168.1.1
Address:        192.168.1.1#53

Non-authoritative answer:
Name:   example.com
Address: 93.184.216.34
```
- Explanation: Queries the default DNS server for the IP address of example.com.
#### Example 2: Specifying a DNS Server
```yaml
nslookup google.com 8.8.8.8
```
- **Explanation**: Queries the DNS server at 8.8.8.8 (Google's public DNS) for the IP address of google.com.
#### Example 3: Querying for a Specific Record Type
```yaml
nslookup -type=MX example.com
```
Output:

```yaml
Non-authoritative answer:
example.com     mail exchanger = 10 mail.example.com.
```
**Explanation**: Retrieves the Mail Exchange (MX) records for example.com.
Example 4: Reverse DNS Lookup
bash
```yaml
nslookup 93.184.216.34
```
**Explanation**: Finds the domain name associated with the IP address 93.184.216.34.
Interactive Mode
To enter interactive mode, simply run nslookup without any arguments:

```yaml
nslookup
```
Once in interactive mode, you can set options and perform multiple queries:

```yaml
> set type=NS
> example.com
```
**Explanation**: Sets the query type to Name Server (NS) records and queries for example.com.
#### Troubleshooting with nslookup
##### Checking DNS Resolution
- **Symptom**: Unable to reach a website via its domain name but can reach it via IP address.
- **Action**: Use nslookup to verify if the domain name resolves to the correct IP address.
Verifying DNS Records After Changes
Symptom: After updating DNS records, changes aren't reflected.

#### Action: Use nslookup with a specific DNS server to bypass cached records:

```yaml
nslookup example.com your_dns_server
```
### Testing Mail Server Configuration
**Symptom**: Issues with email delivery.

Action: Check MX records to ensure they point to the correct mail server:

```yaml
nslookup -type=MX example.com
```
Advanced Usage
Debugging Mode
Enable detailed output to diagnose complex issues:

```yaml
nslookup -debug example.com
```
Changing Default Port
DNS queries typically use port 53, but you can specify a different port if necessary:

```yaml
nslookup -port=5353 example.com
```
