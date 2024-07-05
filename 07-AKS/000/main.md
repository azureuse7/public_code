(https://www.youtube.com/watch?v=_pBYrm_CNrQ)

- Create a Cluster with policy add-on enabled.
<img src="images/a.png">

- Log in to the to the cluster.
- You can see that the policy is running.
<img src="images/2.png">
You can also see gatekeeper namespace has been created and pods
<img src="images/3.png">

Check what constraints are running.
``` 
 k get constraint template
``` 
- https://open-policy-agent.github.io/gatekeeper/website/docs/constrainttemplates/
``` 
 k get constraint
``` 
- These constraints can't be changed, using Kubectl; you have to edit the Azure policy.
-These are dry runs.

Now let's check a constrainttemplate
 and view the definition.
```  
kubcetl get constrainttemplate <>
``` 
### Now let's test this

Let's create a pod with privileges.
<img src="images/4.png">
Let's apply this and run.
<img src="images/5.png">
Lets check,
<img src="images/6.png">
We were able to create the pod because the Constrait policy allowed us
<img src="images/7.png">
Now we can't change this from Kubectl, but we need to do it from Azure Policy.
- Notice we have two agreements now.
<img src="images/20.png">


Let's create a definition.
<img src="images/8.png">
Select Kubernetes.
<img src="images/9.png">
Select the pod security baseline.
<img src="images/10.png">
Let's assign it
<img src="images/11.png">
Select Scope, and let's add the scope.
<img src="images/12.png">
From audit, apply to deny
<img src="images/13.png">
- Notice we have two agreements now.
<img src="images/15.png">
We can see we have two
<img src="images/16.png">

- Let's check the enforcings. notice is denied now.
<img src="images/17.png">


Let's try to apply the pod now.
Notice it fails.
<img src="images/18.png">






<!-- 
(https://www.youtube.com/watch?v=_pBYrm_CNrQ)

- Create a clsuter with policy add on enabled 
<img src="images/a.png">

- Log in cluster and run 
- You can se pod with policy are running 
<img src="images/2.png">
- You can also see gatekeeper namespace is created and pods 
<img src="images/3.png">

- check what constrainys are running 
- k get constrainttemplate
- https://open-policy-agent.github.io/gatekeeper/website/docs/constrainttemplates/
- 
- k get constraint
These constrain can 't be changed husng kubectl, you have to edit from azure policy 
These are dry run 

Now lets check a constrait and view the deintaion 
- kubcetl get constrainttemplate <>
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
<img src="images/18.png"> -->