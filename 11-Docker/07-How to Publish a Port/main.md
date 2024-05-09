## How to Publish a Port

To allow access from outside of a container, you must publish the appropriate port inside the container to a port on your local network. The common syntax for the --publish or -p option is as follows:

--publish <host port>:<container port>

When you wrote --publish 8080:80 in the previous sub-section, it meant any request sent to port 8080 of your host system will be forwarded to port 80 inside the container‌.

Now to access the application on your browser, visit http://127.0.0.1:8080.