# Azure Policy and OPA Gatekeeper on AKS

Reference video: [Azure Policy with OPA Gatekeeper on AKS](https://www.youtube.com/watch?v=_pBYrm_CNrQ)

## Step-01: Create a Cluster with Policy Add-On

- Create a cluster with the policy add-on enabled.
<img src="images/a.png">

## Step-02: Log In and Verify

- Log in to the cluster.
- Confirm that the policy pods are running.
<img src="images/2.png">

You can also see that the `gatekeeper` namespace has been created and its pods are running.
<img src="images/3.png">

## Step-03: Review Existing Constraints

Check what constraint templates are currently running:

```bash
kubectl get constrainttemplate
```

Reference: [OPA Gatekeeper Constraint Templates](https://open-policy-agent.github.io/gatekeeper/website/docs/constrainttemplates/)

```bash
kubectl get constraint
```

- These constraints cannot be changed using `kubectl`; you must edit them from Azure Policy.
- These are dry-run mode by default.

View the definition of a specific constraint template:

```bash
kubectl get constrainttemplate <name>
```

### Step-04: Test the Policy

Let's create a pod with elevated privileges.
<img src="images/4.png">

Apply and run it:
<img src="images/5.png">

Check the result:
<img src="images/6.png">

We were able to create the pod because the constraint policy allowed it (dry-run mode).
<img src="images/7.png">

Note that constraints cannot be changed from `kubectl` — changes must be made through Azure Policy. Notice there are two assignments now.
<img src="images/20.png">

## Step-05: Create a Policy Definition to Enforce Denial

Let's create a new policy definition.
<img src="images/8.png">

Select Kubernetes.
<img src="images/9.png">

Select the Pod Security Baseline.
<img src="images/10.png">

Assign it to your scope.
<img src="images/11.png">

Select the scope and add it.
<img src="images/12.png">

Change the effect from **Audit** to **Deny**.
<img src="images/13.png">

Notice there are now two assignments.
<img src="images/15.png">

We can confirm both assignments are active.
<img src="images/16.png">

## Step-06: Verify Enforcement

Check the enforcements — the policy effect is now **Deny**.
<img src="images/17.png">

Try to apply the privileged pod again. Notice it now fails as expected.
<img src="images/18.png">
