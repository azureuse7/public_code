### Context Overview

In both AKS and EKS, a managed Kubernetes control plane typically leverages cloud load balancers to route external and internal traffic to worker nodes. On AKS, NSGs (Network Security Groups) govern inbound and outbound traffic flows at the subnet or NIC level. On EKS, you have Security Groups that serve a similar function. Issues arise if the NSG/Security Group rules do not align with the ports, protocols, or IP ranges required by the Kubernetes Service of type LoadBalancer. This can result in broken connectivity, failed health checks, or dropped traffic.

### Prevention Strategies

1.  **Use Managed Ingress/Load Balancer Annotations**:
    
    *   **AKS**: Leverage Azure-specific Service annotations (e.g., service.beta.kubernetes.io/azure-load-balancer-resource-group, service.beta.kubernetes.io/azure-load-balancer-internal, etc.) to instruct Azure on how to configure the load balancer.
        
    *   **EKS**: Use annotations to specify internal vs. external load balancers or target group attributes (e.g., service.beta.kubernetes.io/aws-load-balancer-internal: "true").By using these native annotations, the cluster’s cloud provider integration will create load balancer rules that are aligned with the correct ports and subnets by default.
        
2.  **Standardize Port Ranges and Protocols**:
    
    *   Before deploying applications, define a fixed set of allowed ports (e.g., NodePort range) and protocols and ensure NSGs or Security Groups are set to allow the known required inbound ports and outbound access.
        
    *   Use Infrastructure as Code (IaC) frameworks (e.g., Terraform, ARM templates for Azure, or AWS CloudFormation) to define consistent firewall and NSG rules that match your application’s Kubernetes Service specifications.
        
3.  **Implement CI/CD Policy Checks**:
    
    *   Integrate linting and compliance checks in your CI/CD pipeline to verify that any changes to cluster services or NSGs are compliant with established security and connectivity rules.
        
    *   Use tools like kube-linter, polaris, or OPA/Gatekeeper to enforce that only Services that conform to approved patterns are deployed.
        
4.  **Limit Manual Changes to NSGs**:
    
    *   Avoid ad-hoc manual modifications to NSGs or Security Groups once the cluster and its services are defined.
        
    *   Changes should be performed through controlled IaC processes to prevent misconfigurations and drifts from expected state.
        
5.  **Use Separate Subnets/Node Pools for Different Traffic Types**:
    
    *   Segment workloads into different node pools or subnets with their own NSGs to reduce complexity. For example, external-facing services can run on a dedicated node pool with a security policy that is less restrictive for inbound traffic from the load balancer, while internal services have more stringent rules.
        

### Recovery Actions

If an existing LoadBalancer-type Service is failing and you suspect an NSG or Security Group issue:

1.  **Immediate Diagnostic Steps**:
    
    *   **Check Service and Endpoint Status**: Run kubectl describe service to review load balancer events and ensure the LB IP was provisioned correctly.
        
    *   **Examine NSGs or Security Groups**: Compare the required inbound ports (e.g., 80/443 for HTTP/HTTPS) with currently allowed rules. Check if the NSG/SG denies required inbound/outbound traffic.
        
    *   **Health Check the Load Balancer**: Use the cloud provider’s console (Azure Portal or AWS Console) to confirm that the LB’s health probes are passing. If health checks fail, the LB might mark backends as unhealthy due to blocked ports.
        
2.  **Short-Term Remediation**:
    
    *   **Temporarily Relax NSG/SG Rules**: If you identify a blocked port, add a temporary inbound rule allowing traffic on the required port from the load balancer’s frontend IP range.
        
    *   **Rollback to a Known Good Configuration**: If you track NSG/SG changes via version control, roll back to the last known working configuration.
        
3.  **Use Emergency Diagnostic Tools**:
    
    *   **Trace Network Paths**: On AKS, you can use nmap or curl from within pods to confirm connectivity issues. On EKS, test connections using tools within nodes or debug pods.
        
    *   **Azure Network Watcher or AWS VPC Flow Logs**: Enable or review these to identify if traffic is being dropped at the NSG/SG level.
        

### Resolution Strategies

Once the immediate issue is mitigated, implement longer-term resolutions:

1.  **Update NSG/SG Rules to Align with Kubernetes Requirements**:
    
    *   For AKS:
        
        *   Identify the service’s clusterIP, nodePort, and loadBalancerIP.
            
        *   Ensure the NSG rules allow inbound from the LB’s frontend IP or subnet range on the specified ports.
            
        *   Confirm outbound rules permit return traffic.
            
    *   For EKS:
        
        *   Update the worker node group’s Security Groups to allow inbound traffic on the nodePort and health check ports.
            
        *   Validate that the cluster’s control plane security groups or NLB/ALB target group rules are correct.
            
2.  **Refactor Infrastructure as Code**:
    
    *   Rework Terraform or ARM templates (for AKS) or CloudFormation/Terraform (for EKS) to systematically define and maintain NSGs/SG rules in sync with cluster services.
        
    *   Parameterize ports and addresses so that any change to a Kubernetes Service reflects automatically in the corresponding NSG/SG configuration.
        
3.  **Implement Observability and Alerting**:
    
    *   Add proactive monitoring on NSG rules. For instance, in Azure, you can have alerts for unexpected NSG rule changes. In AWS, CloudWatch alarms or Config Rules can detect drift or unauthorized changes.
        
    *   Set up log alerts to catch repeated connection timeouts or LB health-check failures early.
        
4.  **Document and Educate Teams**:
    
    *   Maintain a knowledge base detailing how Services map to NSG rules and the recommended approach for adding new external-facing services.
        
    *   Train DevOps and platform engineering teams to properly request and provision load-balanced services according to best practices.
        

### Example Scenario

**Issue**: An AKS Service of type LoadBalancer is failing to receive inbound traffic on port 443 because the NSG associated with the node subnet denies inbound traffic on that port.

**Prevention**:

*   Ensure NSG inbound rules are predefined for the known secure port (443).
    
*   Use annotations for internal load balancing and ensure that these subnets and ports are defined in code.
    

**Recovery**:

*   Run kubectl describe service myapp to find the LB IP.
    
*   Validate in Azure Portal that the NSG does not have an inbound allow rule for port 443.
    
*   Add a temporary rule az network nsg rule create --name allow-443 --nsg-name myNsg --priority 100 --protocol Tcp --source-address-prefixes Internet --destination-port-ranges 443 --access Allow.
    
*   Confirm traffic flow resumes.
    

**Resolution**:

*   Update Terraform templates so that for any new Services requiring port 443, an NSG rule is automatically applied. Commit this fix into the repository so that the environment remains consistent after future deployments.
    

By following these comprehensive guidelines for prevention, immediate recovery, and long-term resolution, you can ensure that load balancer and NSG-related issues in AKS and EKS are minimized and swiftly resolved.