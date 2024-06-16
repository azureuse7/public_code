# Azure Routing explained

<img src="images/a.png">

- How do two VMs communicate within a subnet? :  
- They have a default route (VM--> NIC--> Effective Routes) they are called system routes.


<img src="images/b.png">


- Next Hop-> Virtual network (route within the Vnet) 

- Source--> Default → who created: default (Azure created it) 

#### How are they communicating to On-premise 



Now 

<img src="images/c.png">

<img src="images/d.png">



- There would be route on both as above 


<img src="images/e.png">


- Now we have a ZOOKeeper 


<img src="images/f.png">


- Address with the longest subnet mask wins 

<img src="images/g.png">

- If all the same but different source 

<img src="images/h.png">

- User DEfined route 

- Create a routeing table 

<img src="images/i.png">


- None → Blackhole (Rule 3)

- Virtual appliance → Route to IP or subnet (Rule 1 and 2)

- Internet -->

- Virtual network ->default azure route

<img src="images/j.png">