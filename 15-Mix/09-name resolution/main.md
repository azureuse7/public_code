#### Name resolution is the process of associating names and IP addresses, and it's one of the most essential services on a network.



The three identities are the following:

##### Media access control (MAC) address. 
The network interface card (NIC) has a MAC address encoded on its firmware.
##### IP address. 
The NIC also has a logical IP address assigned to it.
##### Hostname. 
The system has a human-friendly hostname set during the OS installation.

- These identities provide a means of finding a given node on a network or network segment.


#### The name resolution process
When all is working correctly, a system resolves the hostname 
It checks two resources to discover the necessary IP address: a local file and a DNS database server.

The first method relies on a text file named hosts that resides on the local machine's storage disk. 


The second, more dynamic method is to store all names and IP addresses on one or more network servers and configure the hosts to query the server to retrieve the information needed. The modern implementation of this is DNS.

DNS servers maintain a database of names and IP addresses. Client systems, such as Windows, Linux and macOS, dynamically update the DNS server's database any time their hostname or IP address changes. This ensures the database is current. Hostname and IP address relationships are stored in entries called resource records.

