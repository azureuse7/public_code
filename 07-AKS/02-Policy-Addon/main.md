(https://www.youtube.com/watch?v=_pBYrm_CNrQ)

- Create a clsuter with policy add on enabled 
<img src="images/a.png">
- Log in cluster and run 
- You can se pod with policy are running 
<img src="images/2.png">
- You can also see gatekeeper
<img src="images/3.png">

### Now lets Test This

- Lets create a pod with privilege 
<img src="images/4.png">
- Lets aapply this and run 
<img src="images/5.png">
- lets check,
<img src="images/6.png">
- we were able to create the pod becuase the constrait policy allowed us 
<img src="images/7.png">
- Now we can't change this from kubectl but we need to do it from azure policy 
- Notice we have two assigmnets now
<img src="images/20.png">


- Lets create a defination
<img src="images/8.png">
- Select Kubernetes 
<img src="images/9.png">
- Select Pod security baseline
<img src="images/10.png">
- Let assign it 
<img src="images/11.png">
- Select Scope and lets aadd the scop
<img src="images/12.png">
- From audit apply to deny
<img src="images/13.png">
- Notice we have two assigmnets now
<img src="images/15.png">
- we can see we have two co
<img src="images/16.png">

- let check the enforments. notice is deny now
<img src="images/17.png">


- Let try to apply now the pod
- Notice it fails 
<img src="images/18.png">