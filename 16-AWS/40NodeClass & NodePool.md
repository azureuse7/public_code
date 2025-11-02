### NodeClass & NodePool
#### NodeClass (infra template): 
 
- Where/how to launch EC2 – subnets, SGs, instanceProfile (node role), tags, storage & KMS, optional advanced networking defaults, proxy/cert bundles, etc.

- In EKS Auto Mode, the CRD is apiVersion: eks.amazonaws.com/v1, kind: NodeClass.

#### NodePool (scheduling policy): 
-  What capacity to provision – instance families/sizes, zones, arch, Spot/On-Demand, taints/labels, disruption & consolidation, limits.

- CRD is apiVersion: karpenter.sh/v1, kind: NodePool. Each NodePool references a NodeClass.