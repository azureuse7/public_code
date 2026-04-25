# Azure Load Balancer

Azure Load Balancer distributes inbound traffic across backend VM instances according to rules and health probes. This guide walks through the key configuration steps.

## Architecture Diagram

<img src="images/1.png">

## Setup Steps

### Step 1: Add Backend Pools

Add the VMs or VM scale set instances that will receive the distributed traffic.

<img src="images/2.png">

### Step 2: Create a Load Balancing Rule

Define a rule that maps a frontend IP and port to a backend pool and port.

<img src="images/3.png">

### Step 3: Access the Application via the Frontend IP

Once the rule is configured, access the application using the load balancer's frontend IP address.

<img src="images/4.png">

## Reference

- [YouTube: Azure Load Balancer Tutorial](https://www.youtube.com/watch?v=hR84YJpffIs)
