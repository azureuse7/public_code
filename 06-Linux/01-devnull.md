### What Is /Dev/Null
https://linuxhint.com/what_is_dev_null/



- Linux treats everything as a file. 
- The /dev directory is used to store all the physical and virtual devices. 
- If you worked with disk partitioning, you may have seen the /dev directory in use. For example: /dev/sda, /dev/sdb1, etc.

 Some of the popular virtual devices include:
``` 
/dev/null
/dev/zero
/dev/random
/dev/urandom
``` 
- The /dev/null is a null device that discards any data that is written to it. 
- However, it reports back that the write operation is successful. 
- In UNIX terminology, this null device is also referred to as the bit bucket or black hole.



Despite its unique features, /dev/null is a valid file. We can verify it using the following command:
``` 
$ stat /dev/null
``` 
- Basic Usage
Anything that is written to /dev/null vanishes for good. The following example demonstrates this property:
``` 
$ echo "hello world" > /dev/null
$ cat /dev/null
``` 
- Here, we redirect the STDOUT of the echo command to the /dev/null. Using the cat command, we read the content of the /dev/null.

- Since /dev/null doesn’t store any data, there’s nothing in the output of the cat command.


- To implement this technique, it requires prior knowledge of file descriptors: STDIN, STDOUT, and STDERR.

Example 1:
Check out the first example:
``` 
$ echo "hello world" > /dev/null
``` 
- Here, we redirect the STDOUT of the echo command to /dev/null. That’s why it won’t produce any output in the console screen.

Example 2:
Check out the next example:
``` 
$ asdfghjkl > /dev/null
``` 
- Here, the asdfghjkl command doesn’t exist. So, Bash produces an error. However, the error message didn’t get flushed to /dev/null. It’s because the error message is stored in STDERR. 
- So, we need to specify the STDERR (2) redirection as well. Here’s the updated command:
``` 
$ asdfghjkl 2> /dev/null
``` 
Example 3:
What if we want to redirect both STDOUT and STDERR to /dev/null? The command structure would look like this:
``` 
$ <command> > /dev/null 2> /dev/null
``` 
While this structure is completely valid, it’s verbose and redundant. There’s a way to shorten the structure dramatically: redirecting STDERR to STDOUT first, then redirecting STDOUT to /dev/null.

Check out the updated command:
``` 
$ <command> > /dev/null 2>&1
``` 
Here, STDOUT is redirected to /dev/null. Then, we redirect the STDERR (2) to STDOUT (1). The “&1” describes to the shell that the destination is a file descriptor, not a file name.



