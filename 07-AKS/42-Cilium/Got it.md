s

**What kube-proxy does (quick refresher)**

- Watches Service + EndpointSlice objects.
- Programs **node-local dataplane** rules so packets arriving at a node for a Service VIP (ClusterIP/NodePort/LB) get load-balanced to one of the Service’s pod IPs.
- kube-proxy itself doesn’t proxy packets in userspace (that old “userspace mode” is legacy). It **programs the kernel**, then the kernel fast-paths the packets.
-----
**kube-proxy (iptables mode)**

**How it works**

- kube-proxy writes a bunch of **netfilter/iptables** rules in the nat and filter tables.
- For each Service it creates chains like:
  - KUBE-SERVICES → main dispatch chain
  - KUBE-SVC-<hash> → one per Service/port
  - KUBE-SEP-<hash> → one per backend (pod IP/port)
  - Helpers: KUBE-MARK-MASQ, KUBE-NODEPORTS, etc.
- **Load-balancing** is done by **DNAT** rules that pick a backend using “statistic”/“random” matches. Once conntrack sees the first packet’s DNAT decision, the rest of the flow sticks to that backend.

**Traffic paths (typical)**

- **ClusterIP**: packet to VIP:port → PREROUTING (nat) → KUBE-SERVICES → DNAT to podIP:podPort → conntrack remembers it.
- **NodePort**: packet to nodeIP:nodePort → KUBE-NODEPORTS → DNAT to podIP.
- **LoadBalancer**: cloud LB forwards to nodeIP:nodePort → same as NodePort on arrival.

**Affinity, hairpin, SNAT**

- sessionAffinity: ClientIP is implemented by matching source IP and steering to a consistent endpoint chain.
- **Hairpin** (pod accessing Service that resolves back to itself/same node): handled via NAT with appropriate hairpinMode + iptables rules.
- **SNAT** (masquerade): kube-proxy decides when to SNAT via KUBE-MARK-MASQ rules. It generally **does not** SNAT pod→pod traffic inside the cluster CIDR, but will SNAT for external backends/egress per config (--cluster-cidr, --masquerade-all).

**externalTrafficPolicy**

- externalTrafficPolicy: Cluster: node receiving NodePort/LB can forward to **any** node’s pod; client IP may be lost due to SNAT.
- externalTrafficPolicy: Local: only forwards to **local** pods, preserving client IP; if no local pods, node drops (or LB health-probes mark node as unhealthy). Often paired with strictARP: true (in kube-proxy config) when using ARP/BGP LBs (e.g., MetalLB).

**Pros / cons**

**Pros**

- Works everywhere; no kernel modules beyond standard netfilter.
- Simple mental model; easy to grep rules.

**Cons**

- **Rule explosion**: O(number of services × endpoints). Large clusters → thousands of rules → slow syncs and CPU spikes when endpoints churn.
- Linear rule evaluation until a match; not optimal at very large scale.

**Ops: inspect & debug**

\# See KUBE-\* chains

iptables-save -t nat | sed -n '/\\*nat/,/COMMIT/p' | grep KUBE-

\# Conntrack entry for a Service VIP

conntrack -L | grep <ClusterIP>

\# NodePorts

iptables -t nat -S KUBE-NODEPORTS

-----
**kube-proxy (IPVS mode)**

**How it works**

- Uses the Linux **IPVS** (“IP Virtual Server”) subsystem (kernel L4 load balancer).
- kube-proxy:
  - Ensures IPVS + ipset modules are present (ip\_vs, ip\_vs\_rr/wrr/sh, nf\_conntrack, ip\_set\*).
  - Creates an **IPVS virtual server** per Service/port (VIP:port).
  - Registers each pod endpoint as an IPVS **real server** with a chosen scheduler.
- kube-proxy still installs a **thin** set of iptables rules to get traffic into IPVS fast, but the heavy lifting is in IPVS’s **hash tables**.

**Schedulers (choose one)**

- rr (round-robin, default), wrr (weighted RR), lc (least-connection), wlc (weighted LC), sh (source-hash—good for sticky flows).

**Traffic path**

- Packet hits node → minimal iptables jump → IPVS virtual server → pick real server → DNAT to podIP:port. Conntrack tracks it; subsequent packets bypass most iptables evaluation and are handled by IPVS’s fast path.

**Affinity, externalTrafficPolicy**

- **Session affinity** uses scheduler/connection tracking. sessionAffinity: ClientIP works.
- externalTrafficPolicy: Local is respected; kube-proxy in IPVS mode avoids programming non-local endpoints when policy is Local. Use strictARP: true when appropriate.

**Pros / cons**

**Pros**

- **Performance & scale**: O(1) lookups via IPVS hash tables; stable with tens of thousands of endpoints.
- Faster rule updates during endpoint churn; fewer iptables rules overall.
- Rich schedulers (e.g., least-conn, source-hash).

**Cons**

- Requires kernel IPVS modules (not always available on minimal images).
- A bit more moving parts (ipvs/ipset tooling) and things to verify.
- Some corner features historically lagged iptables in very old k8s releases; in modern k8s they’re on par for typical needs.

**Ops: inspect & debug**

\# IPVS tables

ipvsadm -Ln --stats --timeout

\# Per-service/endpoint counters

ipvsadm -Ln --stats | sed -n '1,200p'

\# ipset lists kube-proxy maintains

ipset list

\# kube-proxy config

kubectl -n kube-system get cm kube-proxy -o yaml | sed -n '1,120p'

-----
**Choosing between them**

|**Dimension**|**iptables mode**|**IPVS mode**|
| :-: | :-: | :-: |
|Scale (services/endpoints)|OK for small/medium|**Best** for large|
|Update churn|Slower reprogramming|**Faster** (hash table updates)|
|CPU during resync|Higher with many rules|**Lower**|
|Scheduling options|Basic random/statistic|**rr, wrr, lc, wlc, sh**|
|Dependencies|netfilter only|+ **IPVS/ipset** kernel modules|
|Operability|Very common, simple|Slightly more to verify|

**Rule of thumb:** If you have **hundreds to thousands** of Services and/or high endpoint churn (e.g., HPA, Jobs), pick **IPVS**. For small clusters or when you can’t load kernel modules, **iptables** is fine.

-----
**How to enable/switch modes**

Support varies by distribution/managed provider—always check your platform’s docs before changing this.

1. Verify kernel support (for IPVS):

lsmod | egrep 'ip\_vs|nf\_conntrack'

sudo modprobe ip\_vs ip\_vs\_rr ip\_vs\_wrr ip\_vs\_sh nf\_conntrack

2. Update kube-proxy config (DaemonSet uses this ConfigMap):

\# kube-system/kube-proxy ConfigMap (snippet)

apiVersion: kubeproxy.config.k8s.io/v1alpha1

kind: KubeProxyConfiguration

mode: "ipvs"        # or "iptables"

clusterCIDR: "10.244.0.0/16"   # set to your pod CIDR

ipvs:

`  `scheduler: "rr"   # rr|wrr|lc|wlc|sh

\# For ARP-based LBs with externalTrafficPolicy: Local:

\# iptables:

\#   masqueradeAll: false

\# strictARP: true

3. Restart kube-proxy pods:

kubectl -n kube-system rollout restart ds/kube-proxy

\# Confirm

kubectl -n kube-system get pods -l k8s-app=kube-proxy -o wide

4. Verify dataplane:

\# IPVS mode

ipvsadm -Ln | head

\# iptables mode

iptables -t nat -S | grep KUBE-SVC

-----
**Common pitfalls & tips**

- **No endpoints**: Service has no ready pods → kube-proxy installs “reject”/blackhole rules (iptables) or an empty virtual server (IPVS). Check kubectl get endpointslices.
- **Client IP preservation**: For LB/NodePort, use externalTrafficPolicy: Local and ensure health checks target only nodes with local pods. Consider strictARP: true with ARP/BGP LBs.
- **Hairpin** issues: Ensure CNI supports hairpin and kube-proxy hairpin settings are correct (some CNIs require hairpinMode: hairpin-veth).
- **Masquerade logic**: Set clusterCIDR so kube-proxy knows what traffic is “in-cluster” (avoid unnecessary SNAT).
- **Huge churn**: Prefer IPVS; if you must stay on iptables, tune kube-proxy sync intervals and avoid flapping endpoints.
- **Observability**: Use ipvsadm --stats (IPVS) or conntrack -S and iptables-save (iptables). For per-flow debugging, tcpdump on host veth pairs plus conntrack -L.
-----
If you tell me your distro/managed service (AKS/EKS/kubeadm, etc.), I can give you provider-specific steps and any gotchas for switching modes in that environment.

