**Kyvernoe**

Kyverno is a **Kubernetes-native policy engine** designed specifically for Kubernetes — policies are written as Kubernetes resources (no Rego/OPA required). It integrates as an admission controller and can also mutate, generate, and verify resources.

-----
**1. Architecture**

Kyverno runs as a **Deployment** in your cluster and registers itself as:

- **ValidatingWebhookConfiguration** — for validate/audit policies
- **MutatingWebhookConfiguration** — for mutate policies

It watches the Kubernetes API server and intercepts requests before they're persisted to etcd.

kubectl request → API Server → Kyverno Webhook → Admit / Deny / Mutate → etcd

Kyverno has 4 controllers:

- **Admission Controller** — enforces policies on resource create/update/delete
- **Background Controller** — applies policies to existing resources
- **Cleanup Controller** — handles TTL-based resource cleanup
- **Reports Controller** — aggregates policy reports
-----
**2. Policy Types**

**ClusterPolicy**

Cluster-scoped — applies across all namespaces.

```yaml

apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
name: require-labels
```
**Policy**

Namespace-scoped — only applies within a specific namespace.

```yaml

apiVersion: kyverno.io/v1
kind: Policy
metadata:
  name: require-labels
  namespace: team-a

```
-----
**3. Rules**

Each policy contains one or more **rules**. Every rule has:

- A **match** block (what to target)
- An optional **exclude** block (what to skip)
- Exactly **one action**: validate, mutate, generate, or verifyImages

```yaml

spec:
  rules:
    - name: my-rule
      match:
        any:
        - resources:
            kinds:
              - Pod
      validate:
        message: "..."
        pattern:
          spec:
            containers:
             - name: "\*"
```

-----
**4. Match & Exclude**

Controls which resources a rule applies to. You can match on:

```yaml
match:
  any:                          # OR logic
  - resources:
      kinds: [Pod]
      namespaces: [production]
      names: ["app-\*"]
      selector:
        matchLabels:
         env: prod
    subjects:                   # who is making the request
    - kind: User
      name: "system:serviceaccount:default:deployer"
    roles: [cluster-admin]
    clusterRoles: [edit]
```



any = OR between blocks, all = AND between blocks.

-----
**5. Validate Rules**

The most common rule type — **enforce or audit** resource configurations.

**enforcementMode**

```yaml

spec:
  validationFailureAction: Enforce   # blocks the request
  # OR
  validationFailureAction: Audit     # allows but logs violation
```
You can also set per-rule enforcement:

```yaml
validate:
  failureAction: Enforce
```
**Pattern Matching**

```yaml
validate:
  pattern:
    spec:
      containers:
        - resources:
            limits:
              memory: "?\*"     # must exist and be non-empty
              cpu: "?\*"
```
Pattern operators:

|**Operator**|**Meaning**|
| :-: | :-: |
|?\*|Must exist, non-empty|
|\*|Wildcard match|
|!value|Not equal|
|>100|Greater than|
|1-5|Range|
|`value1|value2`|

**Deny Rules**

Explicit deny with conditions:

```yaml
validate:
  deny:
    conditions:
      any:
      - key: "{{ request.object.spec.hostNetwork }}"
        operator: Equals
        value: **true**
```
**CEL (Common Expression Language) — Kyverno 1.11+**

```yaml
validate:
  cel:
    expressions:
      - expression: "object.spec.replicas <= 10"
        message: "Replicas must be <= 10"
```
**Assert (Kyverno 1.12+)**

More expressive structured assertions using assert.v1 patterns.

-----
**6. Mutate Rules**

Automatically **modify resources** before they're persisted. Runs at admission time.

**Strategic Merge Patch**

```yaml

mutate:
  patchStrategicMerge:
    metadata:
      labels:
        managed-by: kyverno
    spec:
      containers:
        - (name): "\*"            # anchor: apply to all containers
          securityContext:
            readOnlyRootFilesystem: **true**
```
**JSON 6902 Patch**

```yaml
mutate:
  patchesJson6902:
    - path: "/metadata/labels/team"
      op: add
      value: "platform"
```
**Mutate Existing (Background)**

Mutate resources that **already exist** (not just at admission):

```yaml
mutate:
  targets:
    - apiVersion: v1
      kind: ConfigMap
      name: app-config
      namespace: "{{ request.object.metadata.namespace }}"
  patchStrategicMerge:
    data:
      updated: "true"
```
**Anchors in Mutate**

```yaml
patchStrategicMerge:
  spec:
    containers:
      - (name): "nginx"          # conditional anchor — only if name=nginx
        `image: nginx:1.25
      - <(name): "sidecar-\*"    # global anchor — skip rule if no match
```
Anchor types:

|**Syntax**|**Type**|**Meaning**|
| :-: | :-: | :-: |
|(key)|Conditional|Apply patch only if this matches|
|<(key)|Global|Skip entire rule if this doesn't match|
|=(key)|Default|Add if not present|
|+(key)|Add if not exists|Only add, never replace|
|X(key)|Deny|Deny if this matches|

-----
**7. Generate Rules**

**Automatically create** Kubernetes resources when other resources are created/updated.

```yaml
generate:
  apiVersion: v1
  kind: ConfigMap
  name: default-config
  namespace: "{{ request.object.metadata.name }}"
  synchronize: **true**             # keep generated resource in sync
  data:
    kind: ConfigMap
    metadata:
      labels:
        generated-by: kyverno
    data:
      ENV: production
```
**synchronize: true** — Kyverno will recreate the resource if deleted and update it if the policy changes. Without it, it's a one-time creation.

Use cases:

- Auto-create NetworkPolicies for every new namespace
- Auto-create default LimitRanges
- Clone secrets into new namespaces
- Create RBAC roles per namespace

**Clone existing resource:**

```yaml
generate:
  kind: Secret
  name: registry-credentials
  namespace: "{{ request.object.metadata.name }}"
  clone:
    namespace: kyverno
    name: registry-credentials-template
```
-----
**8. Verify Images**

Validates **container image signatures and attestations** (integrates with Cosign/Notary).

```yaml
verifyImages:
  - imageReferences:
      - "myregistry.azurecr.io/\*"
    attestors:
      - count: 1
        entries:
          - keys:
              publicKeys: |-
            -----BEGIN PUBLIC KEY-----
...

            -----END PUBLIC KEY-----
    `attestations:
      `- type: https://slsa.dev/provenance/v0.2
        `conditions:
          `- all:
            `- key: "{{ builder.id }}"
              `operator: Equals
              `value: "https://github.com/actions/runner"
```
-----
**9. Variables & JMESPath**

Kyverno uses **JMESPath** for dynamic value extraction from resources and context.

```yaml

# Access request fields

{{ request.object.metadata.name }}
{{ request.object.metadata.namespace }}
{{ request.userInfo.username }}
{{ request.operation }}           # CREATE, UPDATE, DELETE

# Access old object (on UPDATE)

{{ request.oldObject.spec.replicas }}

# String operations
{{ to\_upper(request.object.metadata.name) }}
{{ split(request.object.metadata.name, '-')[0] }}
{{ regex\_match('^app-.**\*'**, request.object.metadata.name) }}

# Arithmetic

{{ request.object.spec.replicas \* `2` }}
```
Common JMESPath filters:

```yaml

{{ request.object.spec.containers[].image | [?contains(@, 'latest')] | length(@) }}
```
-----
**10. Context & External Data Lookups**

Rules can pull in **external data** at evaluation time.

**ConfigMap Lookup**

```yaml

context:

`  `- name: allowedRegistries

`    `configMap:

`      `name: registry-allowlist

`      `namespace: kyverno
```
**API Call**

```yaml

context:

`  `- name: existingPods

`    `apiCall:

`      `urlPath: "/api/v1/namespaces/{{ request.object.metadata.namespace }}/pods"

`      `jmesPath: "items[].metadata.name"
```
**Image Registry Lookup**

```yaml

context:

`  `- name: imageData

`    `imageRegistry:

`      `reference: "{{ request.object.spec.containers[0].image }}"

`      `jmesPath: "configData.Labels"
```
**Variables (Kyverno 1.12+)**

```yaml

context:

`  `- name: myVar

`    `variable:

`      `value: "{{ request.object.metadata.namespace }}-suffix"
```
-----
**11. Policy Exceptions**

Allow specific resources to **bypass** a policy without modifying the policy itself.

```yaml

apiVersion: kyverno.io/v2

kind: PolicyException

metadata:

`  `name: allow-privileged-monitoring

`  `namespace: monitoring

spec:

`  `exceptions:

`    `- policyName: disallow-privileged-containers

`      `ruleNames:

`        `- check-privileged

`  `match:

`    `any:

`    `- resources:

`        `kinds: [Pod]

`        `namespaces: [monitoring]

`        `names: ["prometheus-\*"]
```
-----
**12. Cleanup Policies**

**TTL-based automatic deletion** of resources.

```yaml
apiVersion: kyverno.io/v2alpha1
kind: ClusterCleanupPolicy
metadata:
`  `name: clean-old-jobs
spec:
`  `schedule: "0 \* \* \* \*"          # cron schedule
`  `match:
`    `any:
`    `- resources:
`        `kinds: [Job]
`        `selector:
`          `matchLabels:
`            `temp: "true"
`  `conditions:
`    `any:
`    `- key: "{{ time\_since('', request.object.metadata.creationTimestamp, '') }}"
`      `operator: GreaterThanOrEquals
`      `value: 24h
```
-----
**13. Policy Reports**

Kyverno generates **PolicyReport** (namespace-scoped) and **ClusterPolicyReport** (cluster-scoped) CRDs — compatible with the Kubernetes Policy WG standard.

```

kubectl get policyreport -A

kubectl get clusterpolicyreport
```
\# Detailed view
```
kubectl describe policyreport -n production
```
Reports contain per-resource pass/fail/warn/error/skip results — useful for compliance dashboards (integrates with **Policy Reporter UI**).

-----
**14. Background Scanning**

Even in Audit mode, Kyverno continuously scans **existing resources** against policies and populates policy reports. Configurable:

```yaml
spec:
  `background: **true**    # default true — scan existing resources
Set background: false to only evaluate at admission time.
```
-----
**15. Preconditions**

Skip a rule entirely based on conditions **before** the main logic runs:

```yaml
preconditions:
`  `any:
`  `- key: "{{ request.operation }}"
`    `operator: NotEquals
`    `value: DELETE
`  `- key: "{{ request.object.metadata.annotations.\"skip-policy\" }}"
`    `operator: NotEquals
`    `value: "true"
```
-----
**16. Installation on AKS**

```

\# Via Helm (recommended)

helm repo add kyverno https://kyverno.github.io/kyverno/

helm repo update

\# Production install (3 replicas for HA)

helm install kyverno kyverno/kyverno \

`  `--namespace kyverno \

`  `--create-namespace \

`  `--set admissionController.replicas=3 \

`  `--set backgroundController.replicas=2 \

`  `--set cleanupController.replicas=2 \

`  `--set reportsController.replicas=2

**AKS-specific considerations:**

**Azure Policy vs Kyverno** — AKS has built-in Azure Policy (OPA Gatekeeper). Kyverno runs alongside it without conflict, but be aware both can validate the same resources.

**Workload Identity** — if Kyverno needs to call Azure APIs in context lookups, configure pod identity or workload identity on the Kyverno pods.

**Node pools** — exclude system node pool namespaces from restrictive policies:
```
```yaml

exclude:

`  `any:

`  `- resources:

`      `namespaces:

`        `- kube-system

`        `- kyverno

`        `- azure-arc

`        `- gatekeeper-system
```
**ACR integration** — for verifyImages, configure imagePullSecrets or AKS's integrated ACR attachment.

-----
**17. Kyverno CLI**

For local testing and CI/CD integration:

bash

\# Install

brew install kyverno   # or download binary

\# Test policy against a resource

kyverno apply ./policy.```yaml --resource ./pod.```yaml

\# Test with test cases

kyverno test ./tests/

\# Generate resources locally

kyverno apply ./generate-policy.```yaml --resource ./namespace.```yaml

-----
**Summary of Rule Types**

|**Type**|**When to Use**|
| :-: | :-: |
|validate|Enforce/audit resource configuration standards|
|mutate|Auto-inject defaults, labels, sidecars|
|generate|Auto-create companion resources|
|verifyImages|Image signing/provenance enforcement|

The combination of these four rule types plus PolicyExceptions and CleanupPolicies makes Kyverno a very complete policy lifecycle tool for AKS. Let me know if you want deep dives into any specific area — e.g., writing policies for AKS-specific scenarios like ACR image verification, namespace isolation, or resource quota enforcement.

