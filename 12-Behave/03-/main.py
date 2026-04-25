# Initialize connection to Kubernetes cluster and create CoreV1Api client for K8s operations
context = cluster_connect().CoreV1Api() # type: ignore

# Retrieve the name of the current EKS cluster
cluster_name = get_cluster_name()  # type: ignore

# Get the Kubernetes version running on the cluster
EKS_VERSION = get_cluster_version(cluster_name)      # type: ignore

# BDD test step: Setup initial context with cluster details
@given('an EKS cluster named') # type: ignore
def step_given_cluster_name(context): 
    # Store cluster name in test context for use across test steps
    context.cluster_name = cluster_name 
    # Create AWS EKS client for eu-west-2 region to interact with EKS API
    context.eks_client = boto3.client('eks', region_name='eu-west-2')   # type: ignore

# BDD test step: Execute action to retrieve cluster configuration
@when('I check the cluster configuration') # type: ignore
def step_check_cluster_config(context): 
    try: 
        #  Call EKS DescribeCluster for the chosen cluster.
        response = context.eks_client.describe_cluster(name=context.cluster_name) 
        # Extract cluster details from response and store in context
        context.cluster_info = response['cluster'] 
        # Clear any previous errors
        context.error = None 
    except ClientError as e: # type: ignore
        # Capture any AWS API errors for later assertion
        context.error = e 
        # Set cluster_info to None if API call failed
        context.cluster_info = None 

# BDD test step: Verify EKS Auto Mode is enabled (primary method)
@then('EKS Auto Mode should be enabled') # type: ignore
def step_verify_auto_mode_enabled(context): 
    # Ensure no errors occurred during cluster information retrieval
    assert context.error is None, f"Failed to describe cluster: {context.error}" 
    # Verify cluster information was successfully retrieved
    assert context.cluster_info is not None, "Cluster information not found" 

    # Extract access configuration settings from cluster info (default to empty dict)
    access_config = context.cluster_info.get('accessConfig', {}) 
    # Get the authentication mode setting (how users/services authenticate to cluster)
    authentication_mode = access_config.get('authenticationMode', '')     

    # Check if Auto Mode is enabled by verifying authentication mode
    # API_AND_CONFIG_MAP mode indicates the cluster uses both API and ConfigMap for auth
    is_auto_mode = ( 
        authentication_mode == 'API_AND_CONFIG_MAP' 
    ) 

    # Retrieve current cluster status (e.g., ACTIVE, CREATING, FAILED)
    status = context.cluster_info.get('status', '') 

    # Assert that Auto Mode is enabled, provide diagnostic info if it fails
    assert is_auto_mode, ( 
        f"EKS Auto Mode is not enabled {context.cluster_name}. " 
        f"AccessConfig: {access_config}, Status: {status}" 
    ) 

# BDD test step: Alternative verification method for EKS Auto Mode
@then('EKS Auto Mode should be enabled using alternative method') # type: ignore
def step_verify_auto_mode_alternative(context): 
    # Ensure no errors occurred during cluster information retrieval
    assert context.error is None, f"Failed to describe cluster: {context.error}" 
    # Verify cluster information was successfully retrieved
    assert context.cluster_info is not None, "Cluster information not found" 

    try: 
        # Retrieve list of all node groups in the cluster
        nodegroups_response = context.eks_client.list_nodegroups( 
            clusterName=context.cluster_name 
        ) 
        # Extract node group names from response
        nodegroups = nodegroups_response.get('nodegroups', []) 

        # Check if any node group name contains 'auto' (case-insensitive)
        # This indicates auto-managed node groups, a sign of Auto Mode
        has_auto_managed_nodes = any('auto' in ng.lower() for ng in nodegroups) 

    except ClientError: # type: ignore
        # If API call fails, assume no auto-managed nodes exist
        has_auto_managed_nodes = False 

    try: 
        # Retrieve list of all add-ons installed on the cluster
        addons_response = context.eks_client.list_addons( 
            clusterName=context.cluster_name 
        ) 
        # Extract add-on names from response
        addons = addons_response.get('addons', []) 

        # Define set of add-ons that indicate Auto Mode is enabled
        auto_mode_addons = {'kube-proxy'} 
        # Check if all required Auto Mode add-ons are present in cluster
        has_required_addons = auto_mode_addons.issubset(set(addons)) 

    except ClientError: # type: ignore
        # If API call fails, assume required add-ons are not present
        has_required_addons = False 

    # Determine if any Auto Mode indicators were found
    # Auto Mode is considered enabled if EITHER condition is true
    auto_mode_indicators = has_auto_managed_nodes or has_required_addons 

    # Assert that at least one Auto Mode indicator was found
    # Provide diagnostic information about node groups and add-ons if assertion fails
    assert auto_mode_indicators, ( 
        f"EKS Auto Mode indicators not found on cluster {context.cluster_name}. " 
        f"Node groups: {nodegroups if 'nodegroups' in locals() else []}, " 
        f"Addons: {addons if 'addons' in locals() else []}" 
    )