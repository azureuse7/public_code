# Azure Web Application Firewall (WAF)

This guide walks through setting up the Azure Application Gateway Web Application Firewall (WAF) to protect a web application.

**Reference:** [YouTube: Azure WAF Tutorial](https://www.youtube.com/watch?v=CZGdfcKZ31I)

<img src="images/1.png">

<img src="images/2.png">

## WAF Modes

WAF supports two modes of operation:

<img src="images/3.png">

## Setup Steps

### Step 1: Create an App Service

Create an App Service, download a sample application, and test that it is working.

<img src="images/3.5.png">

### Step 2: Create a WAF Policy

Create a WAF policy in the Azure portal.

<img src="images/4.png">

### Step 3: Add a Network

Configure the virtual network for the WAF.

<img src="images/5.png">

### Step 4: Create a Public IP

Assign a public IP address to the WAF.

<img src="images/6.png">

### Step 5: Create a Backend Pool

Create a backend pool and add the App Service created in Step 1.

<img src="images/7.png">

### Step 6: Verify WAF is Working

Once the WAF is created, retrieve the IP address and confirm that the application is accessible.

<img src="images/8.png">

### Step 7: Test WAF Detection

Add a simulated attack (hacking code) to a request to test the WAF.

<img src="images/9.png">

### Step 8: Enable Prevention Mode

Switch the WAF to **Prevention** mode and confirm that malicious requests receive a `403 Forbidden` response.

<img src="images/4.png">
