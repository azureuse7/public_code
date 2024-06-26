Let's talk about these firewalls

They will control how the traffic is allowed into
and out of your EC2 instances.

Security groups are going to be very easy.

They only contain allow rules.

So we can say what is allowed to go in and to go out.

And security groups can have rules that reference
either by IP addresses, so where your computer is from,
or by other security groups.

So as we'll see, security groups can reference each other.
So here, let's take an example.

We are on our computer, so we are on the public internet,
and we're trying to access our EC2 instance
from our computer.

We are going to create a security group
around our EC2 instance,

that is the firewall that is around it.
And then this security group is going to have rules.
And these rules are going to say
whether or not some inbound traffic,
so from the outside into the EC2 instance is allowed.

And also if the EC2 instance
can perform some outbound traffic,
so to talk from where it is into the internet.
Now let's do a deeper dive, right?
Security groups are a firewall on our EC2 instances,
and they're going to really get
and regulate access to ports.
They're going to see the authorized IP ranges.

Would it be on IPv4 or IPv6?
These are the two kinds of IP on the internet.
This is going to control the inbound network,
so from the outside to the instance,
and the outbound network from the instance to the outside.
And when we look at security group rules,
they will look just like this.
So there will be the type, the protocol,
so TCP, the port allowing it,
so where the traffic can go through on the instance,
and the source, which represents an IP address range.
And 0.0.0.0/0 means everything.
And this here means just one IP.
Now let's look at a diagram, right?
So we have our EC2 instance,
and it has one security group attached to it
that has inbound rules and outbound rules,
so I've separated them onto this diagram.
So our computer is going to be authorized on, say, port 22,
so the traffic can go through from our computer
to the EC2 instance.
But someone else's computer that's not using my IP address
because they don't live where I live,
then if they try to access our EC2 instance,
they will not get through it
because the firewall is going to block it,
and it will be a timeout.
Then for the outbound rules, by default,
our EC2 instance for any security group
is going to be by default allowing any traffic out of it.
So our EC2 instance,
if it tries to access a website and initiate a connection,
it is going to be allowed by the security group.
So this is the basics of how the firewall works.
Now, good to know,
what do you need to know with security groups?
Well, they can be attached to multiple instances, OK?
There's not a one-to-one relationship
between security group and instances,
and actually an instance
can have multiple security groups too.
Security groups are locked down
to your region/VPC combination, OK?
So if you switch to another region,
you have to create a new security group,
or if you create another VPC,
and we'll see what VPCs are in the later lecture,
well, you have to recreate the security groups.
The security groups live outside the EC2.
So as I said, if the traffic is blocked,
the EC2 instance won't even see it, OK?
It's not like an application running on EC2.
It's really a firewall outside your EC2 instance.
To be honest, and that's just an advice to you
from developer to developer,
but it's good to maintain one separate security group
just for SSH access.
Usually SSH access is the most complicated thing,
and you really want to make sure that one is done correctly.
So I usually separate my security group
for SSH access separately.
If your application is not accessible, so timeout,
so we saw this in the last lecture,
then it is a security group issue, OK?
So if you try to connect to any port
and your computer just hangs and waits and waits,
that's probably a security group issue.
But if you receive a connection refused error,
you actually get a response saying connection refused,
then the security group actually worked,
the traffic went through, and the application was errored
or it wasn't launched or something like this.
So this is what you would get
if you get a connection refused.
By default, all inbound traffic is blocked
and all outbound traffic is authorized, OK?
Now there is a small advanced feature
that I really, really like,
and I think it's perfect if you start using load balancers,
and we'll see this in the next lecture as well,
which is how to reference security groups
from other security groups.
So let me explain things.
So we have an EC2 instance, and it has a security group,
what I call group number one.
And the inbound rules is basically saying,
I'm authorizing security group number one inbound
and security group number two.
So why would we even do this?
Well, if we launch another EC2 instance
and it has security group two attached to it,
well, by using the security group run rule
that we just set up, we basically allow our EC2 instance
to go connect straight through on the port we decided
onto our first EC2 instance.
Similarly, if we have another EC2 instance
with a security group one attached,
well, we've also authorized this one to communicate
straight back to our instances.
And so regardless of the IP of our EC2 instances,
because they have the right security group attached to them,
they're able to communicate straight through
to other instances.
And that's awesome because it doesn't make you think
about IPs all the time.
And if you have another EC2 instance,
maybe with security group number three attached to it,
well, because group number three wasn't authorized
in the inbound rules of security group number one,
then it's being denied and things don't work.
So that's a bit of an advanced feature,
but we'll see it when we'll deal with load balancers
'cause it's quite a common pattern.
I just want you to know about it.
Again, just remember this diagram.
And by now you should be really, really good
at security groups and understand them correctly.
Now, going into the exam, what ports do you need to know?
Well, we need to know something called SSH or secure shell.
And we're going to see this in the very next lectures.
This is the port 22.
And this allows you to log into
an EC2 instance on Linux.
You have port 21 for FTP or file transfer protocol,
which is used to upload files into a file share.
And you have SFTP, which is also using port 22.
Why?
Well, because we're going to upload files,
but this time using SSH,
because it's going to be a secure file transfer protocol.
Then we have port 80 for HTTP.
And we've been using it in the previous lecture.
This is to access unsecured websites.
And you've seen this whenever you go on the internet
and you enter HTTP colon slash slash,
and then the address of the website.
And you've seen most likely a lot more like this.
You've seen HTTPS, which is to access secured websites,
which are the standard nowadays.
And for HTTPS, it is port 443.
Finally, the last port you need to remember is 3389
for RDP or the remote desktop protocol,
which is the port that's used
to log into a Windows instance.
OK, so 22 is SSH for Linux instance,
but 3389 is RDP for a Windows instance.
Now, this is all the theory about security groups.
I will see you in the next lecture for some practice.




So we've launched our EC2 instance
<img src="images/18.png">

and now let's have a look at security groups.

So we have a short idea of security groups

by just clicking on security in here.

And we get some overview

of the security groups attached to our instance

as well as the inbound rules and the outbound rules.

But what I will do is

that I will just access the more complete page

of security groups from the left hand side menu.

So under networking and security,

you click on security group.

And we can see so far

that we have two security groups

in our console so far.

So the default security group that is created by default

as well as the launch wizard one

which is the first security group

that was created when we created our EC2 instance.

And so a security group has an ID.

So an identifier, just like an EC2 instance has an ID.

And then we can check the inbound rules.
<img src="images/19.png">
So the inbound rules are the rules that allows connectivity

from the outside into the EC2 instance.

And as we can see, we have two inbound rules in here.

And the first one is of type SSH,

which allows port 22 in our instance.

And let me just click on edit inbound rules to see better.

So set first one as SSH on port 22 from anywhere.

So 000/0 is anywhere.

And the second one is HTTP

from port 80, again, anywhere.

So this rule right here is what allowed us

to access our web servers.

So if you go back to the EC2 console,

go to our instance

and

we were doing this IPv4 address.

Okay, so we were opening it as an HTTP website.

This worked thanks to this rule, port 80.

Let's verify this.

So if we delete this rule on port 80 and save the rules,

as we can see now we only have port 22.

So if I go back to this and refresh my page,

now as we can see,

there is an infinite loading screen right here

on the top of my screen,

which shows that well,

indeed I don't have access to my EC2 instance.

So here is a very important tip for you.

Any time you see a timeout,

okay, this is a timeout

because it keeps on trying to connect

but it doesn't succeed

and then it will eventually fail, called a timeout.

So if you see a timeout when trying to establish any kind

of connection into your EC2 instances,

for example, if you try to SSH into it,

but there's a timeout,

or if you try to do an HTTP query,

but there's a timeout,

or if you try to do anything with it

and there is a timeout,

this is 100% the cause

of an EC2 security group.

Okay, so in that case,

go to your security group rules

and make sure that they are correct,

because if they're not correct,

then you will get a timeout.

So to fix this, we can add back a rule.

We will do

HTTP,

which allows to get port 80

in here automatically.

And then from anywhere IPv6, IPv4, excuse me, right here,

which allows this block right here.

We save the rule.

Now the rule is done.

If I go back to my page and refresh

as you can see, now it is fully working.

So this inbound rule really did the trick.

But we could add any sort of inbound rule.

So we could define the port or the port range

that we want to.

So we could say, for example, any port we want,

for example 443, which is HTTPS

or choose directly from a dropdown here

as a little shortcut the type of protocol you want.

For example, HTTPS is 443 automatically.

And then you can define where you want to allow from.

So you have different CIDR blocks

and we don't need them right now,

or security groups or prefix list,

but we'll get to see them later on,

okay, in this course.

For now, just know that you could have

either a custom CIDR anywhere which adds this blog

or if you want to, can select my IP

to only allow access to your IP.

But just be aware that if your IP changes,

then you will get a timeout

and will not be able to access your EC2 instance.

Finally, one last bit of information.

So we can have a look at outbound rules.

So we allow all traffic on IPv4 to anywhere.

So this allows our EC2 instance

to get full internet connectivity anywhere.

And something you should know,

so we have two security groups right here

default and launch wizard,

and an EC2 instance

can have many security groups attached to it.

So it can attach one but two or three

if you want maybe five security groups

and the rules will just add on to each other.

And also this security group we have created from default

so for example, this launch wizard one can be attached

to other EC2 instances.

Okay, so you can attach

as many security groups as you want

as well as as many EC2 instances you want

to one security group.

That's it for this lecture.

I hope you liked it.

And I will see you in the next lecture.