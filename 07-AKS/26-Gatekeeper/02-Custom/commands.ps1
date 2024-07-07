# When you do a k apply –f deployment.yaml 
# 1)	It authenticates  and authorization and admission controller checks weather the reqies is secure and compliant then its deploys 
# Process involved in Gatekeeper implementation 
# 1)	Intsall gatekeeper
# 2)	Create a constraint thenplete (rego)
# 3)	Create constraint CRD
# 4)	Create deploy and test 




# Deploy OPA Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml

# Scenario: Enforce Having A Specific Label In Any New Namespace
# Deploy the Contraint Template
kubectl apply -f k8srequiredlabels_template.yaml

# Deploy the Constraints
kubectl apply -f all_ns_must_have_gatekeeper.yaml

# Deploy a namespace denied by Policy
kubectl apply -f bad-namespace.yaml

# Deploy a namespace allowed by Policy
kubectl apply -f good-namespace.yaml

# https://www.youtube.com/watch?v=urvSPmlU69k&ab_channel=HoussemDellai

# https://www.youtube.com/watch?v=OJGmwCMsUNE&list=WL&index=6

# https://www.youtube.com/watch?v=_pBYrm_CNrQ&list=WL&index=3