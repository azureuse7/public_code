Load Balancer Health Probes

### Background

In a Kubernetes cluster deployed on AKS or EKS, services of type LoadBalancer are commonly used to expose workloads externally. The associated cloud load balancer (Azure Load Balancer, Application Gateway, or AWS Application/Network Load Balancer) routinely sends health probes to the nodes and then to the pods to verify service availability. When these probes fail, traffic may be dropped, resulting in intermittent or total service outages.


    

### Prevention Measures

1.  **Accurate Kubernetes Health Probe Settings**:
    
    *   **Readiness Probes**: Ensure that your pods have accurate readiness probes configured. A readiness probe should check an endpoint that verifies the application’s ability to serve incoming requests. For HTTP-based services, use a dedicated health check endpoint (e.g., /healthz) that returns a 200 HTTP status code if the application is ready.
        
    *   **Liveness Probes**: Set a liveness probe that restarts the container if it becomes unresponsive. This ensures that if the service becomes non-functional internally, Kubernetes recycles it, potentially restoring the health for the load balancer.
        
2.  **Proper Load Balancer Service Specification**:
    
    *   **Matching Ports and Protocols**: Confirm that the Kubernetes Service spec.ports\[\*\].port and spec.ports\[\*\].targetPort align with the container ports. The load balancer health probes should match these ports.
        
    *   **Stable Endpoints**: Use stable and lightweight endpoints (like a simple /health handler) that respond quickly and do not depend on complex application logic. This reduces the risk of transient failures.
        
3.  **Security and Network Configuration**:
    
    *   **Network Policies (Kubernetes)**: If using NetworkPolicies, ensure that the ingress rules allow traffic from the load balancer’s source IP range to the pods on the health check ports.
        
    *   **Security Groups (AWS EKS) or NSGs (AKS)**: Make sure the worker node security groups (EKS) or node resource group Network Security Groups (AKS) allow inbound traffic from the load balancer’s source IP and configured probe ports.
        
    *   **Managed Identity and RBAC (AKS)**: If using advanced features such as managed identities or custom RBAC rules for network objects, verify that the cluster’s control plane has the appropriate permissions to set up and update load balancer rules and health probes.
        
4.  **Resource and Performance Considerations**:
    
    *   **Sufficient Compute Resources**: Ensure the application has adequate CPU and memory resources to respond quickly and consistently. Overloaded containers that exceed resource limits may fail health checks.
        
    *   **Pre-warming the Load Balancer (Azure/AWS)**: For heavy traffic scenarios, consider pre-provisioning or scaling the load balancer to avoid slow-start conditions that could cause initial health check failures.
        
5.  **Annotation Usage**:
    
    *   **Azure-specific Annotations (AKS)**: You can use specific annotations on Service objects (e.g., service.beta.kubernetes.io/azure-load-balancer-health-probe-request-path) to control the health probe path.
        
    *   **AWS-specific Annotations (EKS)**: Similar annotations exist for AWS load balancers (e.g., service.beta.kubernetes.io/aws-load-balancer-healthcheck-path, service.beta.kubernetes.io/aws-load-balancer-healthcheck-interval, etc.). Use these to fine-tune the health checking parameters.
        

### Recovery Actions During an Incident

1.  **Immediate Diagnostics**:
    
    *   Run kubectl describe service and kubectl describe endpoints to verify endpoints and ports.
        
    *   Check the pods associated with the service using kubectl describe pod and confirm that readiness and liveness probes are passing.
        
2.  **Logs and Metrics Examination**:
    
    *   Examine the pod logs (kubectl logs ) and application logs for errors during health check requests.
        
    *   Check cluster events (kubectl get events) for warnings or errors relating to the load balancer configuration or pod health probes.
        
    *   Use external monitoring (Prometheus, CloudWatch, Azure Monitor) to see if requests to health endpoints are timing out or failing intermittently.
        
3.  **Network and Security Verification**:
    
    *   Validate that the load balancer’s front-end IP is allowed in security groups/network policies.
        
    *   Temporarily relax network policies or firewall settings to confirm if they are the cause, then tighten them again once verified.
        
4.  **Rolling Restarts or Pod Scale-up**:
    
    *   If pods are unhealthy, initiate a rolling restart via a kubectl rollout restart deployment/.
        
    *   If insufficient capacity or performance issues are suspected, scale up the Deployment/StatefulSet to distribute load and improve response times.
        
5.  **Check Cloud Load Balancer Configuration in the Console**:
    
    *   For AKS: Check the Azure Portal for the corresponding load balancer configuration. Confirm the health probe path, port, and interval match your Kubernetes Service annotations and pod configuration.
        
    *   For EKS: Check the AWS Console or CLI (describe-load-balancers) to ensure the health check settings match the service annotations and are functional.
        

### Long-term Resolution Steps

1.  **Refine Health Check Endpoints**:
    
    *   Implement a dedicated lightweight health endpoint that responds quickly and without dependencies on external systems (like databases), to reduce chances of transient failures.
        
    *   Ensure readiness endpoints return non-200 responses quickly when the application cannot serve traffic (e.g., if a dependent service is down), preventing load balancer from directing traffic to non-ready instances.
        
2.  **Adjust Probe Configuration Parameters**:
    
    *   Increase or decrease the initialDelaySeconds, periodSeconds, timeoutSeconds, and failureThreshold of Kubernetes readiness/liveness probes to ensure that short-lived spikes in latency don’t falsely mark pods as unhealthy.
        
    *   For the cloud load balancer, adjust the health check interval, timeout, and healthy/unhealthy thresholds (using service.beta.kubernetes.io annotations) so that minor network blips do not cause failovers or route interruptions.
        
3.  **Load Balancer-Level Logging and Monitoring**:
    
    *   Enable load balancer logs and access logs at the cloud level.
        
        *   On AWS: Enable ALB/NLB access logs.
            
        *   On Azure: Enable Azure Load Balancer diagnostic logs and metrics.
            
    *   Use these logs to track patterns and correlate probe failures with application metrics or external events.
        
4.  **Infrastructure as Code (IaC) and Version Control**:
    
    *   Ensure all annotations, probe configurations, and security rules are captured in version-controlled IaC templates (e.g., Terraform, Pulumi, Helm charts).
        
    *   By maintaining configuration as code, it’s easier to audit changes, roll back to known-good configurations, and ensure consistent health check settings across environments.
        
5.  **Regular Audits and Tests**:
    
    *   Periodically review and test your health check endpoints and ensure they still reflect the readiness of your services.
        
    *   Integrate synthetic tests that periodically query the load balancer’s external endpoint and verify that they receive the correct responses.
        
    *   Include load balancer and health check parameters in your periodic cluster configuration reviews and performance tuning cycles.
        

### Summary

**Prevention** focuses on correct probe configurations, aligning service and port definitions, ensuring open network paths, and monitoring resource usage. **Recovery actions** involve quick diagnostics, verifying configuration in both Kubernetes and cloud load balancer consoles, adjusting network rules, and restoring pod health. **Long-term resolutions** include refining health endpoints, tuning probe intervals and thresholds, formalizing configuration via IaC, monitoring LB logs, and regularly auditing probe and network configurations.

By consistently applying these measures, you can maintain stable external connectivity to workloads on AKS and EKS clusters and avoid health probe-related disruptions.