# Delegate Domain to Azure DNS

## Step-01: Introduction

This guide covers how to delegate a domain from AWS Route53 to Azure DNS by creating DNS Zones in Azure Cloud. Topics covered:

- Domain Registrar
- DNS Zones

[![Image](https://www.stacksimplify.com/course-images/azure-aks-delegate-domain-to-azure-dns.png "Azure AKS Kubernetes - Masterclass")](https://www.udemy.com/course/aws-eks-kubernetes-masterclass-devops-microservices/?referralCode=257C9AD5B5AF8D12D1E1)

## Step-02: Create a DNS Zone in Azure

Navigate to **Services -> DNS Zones** in the Azure Portal and create a new zone with the following settings:

- **Subscription:** StackSimplify-Paid-Subscription (a paid subscription is required)
- **Resource Group:** dns-zones
- **Name:** kubeoncloud.com
- **Resource Group Location:** East US

Click **Review + Create**.

## Step-03: Make a Note of Azure Nameservers

Go to **Services -> DNS Zones -> kubeoncloud.com** and record the nameservers:

```
ns1-04.azure-dns.com.
ns2-04.azure-dns.net.
ns3-04.azure-dns.org.
ns4-04.azure-dns.info.
```

## Step-04: Update Nameservers at Your Domain Registrar (AWS Route53)

Verify the current nameservers before making changes:

```bash
nslookup -type=SOA kubeoncloud.com
nslookup -type=NS kubeoncloud.com
```

Update the nameservers in AWS Route53:

1. Go to **Services -> Route53 -> Registered Domains -> kubeoncloud.com**
2. Click **Add or edit name servers**
3. Replace the existing nameservers with the Azure nameservers noted in Step-03
4. Click **Update**
5. Go to **Hosted Zones** and delete the hosted zone named `kubeoncloud.com`

Verify the updated nameservers have propagated:

```bash
nslookup -type=SOA kubeoncloud.com 8.8.8.8
nslookup -type=NS kubeoncloud.com 8.8.8.8
```
