

**What Cilium Is**

Cilium is a Kubernetes CNI and service dataplane built on eBPF. It replaces/augments iptables- and IPVS-based networking with eBPF programs attached to kernel hooks, giving you high-performance networking, identity-aware policy, deep observability (Hubble), kube-proxy replacement, and lots of L7 goodies.

-----
**Core Building Blocks**

**eBPF datapath**

- **Attach points:** TC ingress/egress, XDP, socket hooks, and various tracepoints.
- **Generated programs:** Cilium compiles eBPF for packet filtering, load-balancing, NAT, policy enforcement, and visibility (flows, verdicts).
- **Per-endpoint maps:** Cilium stores pod identities, policy, service backends, etc. in eBPF maps instead of static iptables rules—fast updates, no rule explosions.

**Components**

- **cilium-agent (DaemonSet):** Programs eBPF, manages per-endpoint state, implements policy and service LB.
- **cilium-operator (Deployment):** Garbage collection, IPAM, CRD reconciliation, some multi-cluster features.
- **Hubble:** eBPF-powered flow observability (CLI + UI).
- **Optional:** **Cilium Envoy** (side-carless L7 proxy), **Cilium Ingress/Gateway**, **Clustermesh** for multi-cluster, **Egress Gateway**, **BGP Control Plane**.
-----
**Networking Modes**

**Routing & Encapsulation**

- **Direct routing (best when L2/L3 is routable):** No tunnel overhead; relies on underlay routing between nodes.
- **Tunnels (VXLAN/Geneve):** Useful when L2/L3 isn’t flat; simplifies underlay but adds overhead.

**Encryption**

- **IPsec** or **WireGuard** between nodes. WireGuard tends to be simpler/faster in most environments.

**IPAM**

- **Cluster-scope** (allocate from a pool per node).
- **Cloud-native** (ENI for AWS, Azure IPAM, etc.) to align with cloud limits/quotas.
-----
**Service Implementation (kube-proxy replacement)**

Cilium can fully replace **kube-proxy** using eBPF:

- **ClusterIP/NodePort/LoadBalancer** implemented in kernel with efficient NAT and consistent hashing (Maglev-style).
- **Reduced conntrack pressure** compared to iptables.
- **Preserves semantics** like session affinity and externalTrafficPolicy: Local.
- **Host-reachable services**: NodePort/LoadBalancer work for host-networked clients without hair-pinning pain.

You can also run Cilium with kube-proxy (gradual adoption), but the sweet spot is **kube-proxy replacement** once you’re comfortable.

-----
**Network Policy (L3/L4/L7, identity-based)**

Kubernetes NetworkPolicy is L3/L4 only. Cilium adds:

- **Identity-based policy** (labels, not just CIDRs).
- **DNS-aware egress** via toFQDNs.
- **L7 policies** (HTTP, Kafka, gRPC, DNS) enforced by embedded Envoy—sidecar not required.
- **Host policies** for traffic entering/leaving the node network namespace.



**Examples**

**1) Basic allow from frontend to backend on TCP 8080:**
```yaml
apiVersion: cilium.io/v2

kind: CiliumNetworkPolicy

metadata:

`  `name: allow-frontend-to-backend

spec:

`  `endpointSelector:

`    `matchLabels:

`      `app: backend

`  `ingress:

`  `- fromEndpoints:

`    `- matchLabels:

`        `app: frontend

`    `toPorts:

`    `- ports:

`      `- port: "8080"

`        `protocol: TCP

```

**2) L7 HTTP policy (allow only GET /health and POST /orders):**
```yaml
apiVersion: cilium.io/v2

kind: CiliumNetworkPolicy

metadata:

`  `name: backend-l7-http

spec:

`  `endpointSelector:

`    `matchLabels:

`      `app: backend

`  `ingress:

`  `- toPorts:

`    `- ports:

`      `- port: "8080"

`        `protocol: TCP

`      `rules:

`        `http:

`        `- method: GET

`          `path: ^/health$

`        `- method: POST

`          `path: ^/orders$
```
**3) Egress DNS + FQDN policy (only talk to api.example.com on 443):**
```yaml
apiVersion: cilium.io/v2

kind: CiliumNetworkPolicy

metadata:

`  `name: restrict-egress-fqdn

spec:

`  `endpointSelector:

`    `matchLabels:

`      `app: backend

`  `egress:

`  `- toFQDNs:

`    `- matchName: api.example.com

`  `- toPorts:

`    `- ports:

`      `- port: "53"

`        `protocol: UDP

`      `rules:

`        `dns:

`        `- matchPattern: "\*"

`  `- toPorts:

`    `- ports:

`      `- port: "443"

`        `protocol: TCP
```
-----
**Observability (Hubble)**

- **Flow logs:** L3/L4/L7 with verdicts (ALLOW/DENY), identities, policy names, latency.
- **Troubleshooting:** hubble observe for real-time flows; filter by namespace, pod, policy, HTTP method, etc.
- **Hubble UI:** Nice graph of service dependencies; drill into failed/denied requests.
- **Export:** To Prometheus, Loki, or SIEM.
-----
**Ingress, Gateway API, and L7**

- **Cilium Ingress / Gateway API:** Runs Envoy under the hood; supports TLS, HTTP routing, can enforce L7 policy inline.
- **No sidecars:** Envoy managed by Cilium handles L7 policy and visibility without per-pod proxies.
- **mTLS & auth patterns:** Often combined with external IdP at the edge; Cilium can enforce HTTP authz at L7 if desired.
-----
**Egress Control**

- **Egress Gateway:** Route selected pod egress via dedicated NAT nodes/IPs (auditing, allow-listing, or static egress IP needs).
- **Egress NAT policy:** Control which traffic is SNAT’d and to what addresses.
- **FQDN-aware:** Combine with DNS policy for “allow only named destinations.”
-----
**Multi-cluster (Clustermesh)**

- **Shared identities and service discovery** across clusters.
- **Cross-cluster service LB** without overlay complexity.
- Works with different cluster CIDRs; supports encryption and policy consistently.
-----
**BGP Control Plane (optional)**

- Advertise **pod CIDRs** and/or **Service VIPs** (including LoadBalancer IPs) to your physical/virtual routers.
- Can reduce reliance on cloud LB or simplify on-prem routing.
-----
**Performance Traits**

- **Low latency & CPU** vs iptables rule churn (no rule explosions for large clusters).
- **Fast policy updates** (modify eBPF maps instead of flushing tables).
- **XDP** can accelerate drops and DDoS mitigation at the NIC ingress path.
-----
**Security Posture**

- **Fine-grained L7 allow-listing** with Envoy.
- **Transparent encryption** (WireGuard/IPsec).
- **Host firewall** and **Host policies** protect node processes.
- **Identity-aware policy** avoids brittle IP-based lists; plays nicely with autoscaling.
-----
**Installation & Ops (high level)**

- **Prereqs:** Modern Linux kernel with eBPF enabled (4.19+ recommended; newer is better). Disable conflicting iptables rules when using kube-proxy replacement.
- **Install:** cilium install (CLI) or Helm chart.
- **Pick modes:**
  - routing (direct vs VXLAN/Geneve),
  - encryption (none/WireGuard/IPsec),
  - kube-proxy replacement (strict or partial),
  - IPAM (cluster-scope or cloud-native).
- **Day-2 ops:**
  - cilium status (agent/health),
  - cilium endpoint list (per-pod state),
  - cilium monitor / hubble observe (flows, verdicts),
  - cilium sysdump (support bundle).
- **Upgrades:** Rolling with careful attention to datapath compatibility (keep minor/patch pairings coherent across nodes), and drain/order nodes if switching proxy mode or tunneling.
-----
**Common Design Choices & Tips**

1. **Start simple:** Keep kube-proxy initially, validate Cilium policy & observability, then enable kube-proxy replacement.
2. **Prefer direct routing** when underlay allows; use **WireGuard** for encryption unless IPsec is mandated.
3. **Identity over IP:** Write policies on labels; reserve CIDRs for third-party/legacy.
4. **Adopt Hubble early:** It pays off in incident response and audits.
5. **Egress control:** Use Egress Gateway + FQDN rules to cleanly constrain outbound traffic.
6. **Gradual L7:** Begin at L3/L4, then add L7 only where it provides security value (avoid over-specifying paths too early).
7. **Multi-cluster:** If you need east-west traffic across clusters, Clustermesh is cleaner than DIY peering.
8. **BGP:** Great for on-prem or hybrid to advertise Service or pod routes to upstream routers.
-----
**Quick Commands You’ll Actually Use**

\# Status & health
```yaml
kubectl -n kube-system exec ds/cilium -- cilium status

kubectl -n kube-system exec ds/cilium -- cilium health status
```
\# Endpoints and policy
```yaml
kubectl -n kube-system exec ds/cilium -- cilium endpoint list

kubectl -n kube-system exec ds/cilium -- cilium policy get

kubectl -n kube-system exec ds/cilium -- cilium policy trace --src-k8s-pod default/frontend --dst-k8s-pod default/backend --dport 8080/TCP
```
\# Hubble (requires hubble-relay)

kubectl -n kube-system exec deploy/hubble-relay -- hubble observe --namespace default --http-method POST --since 1m

kubectl -n kube-system exec deploy/hubble-relay -- hubble status

\# Sysdump for support

kubectl -n kube-system exec ds/cilium -- cilium sysdump --output-filename cilium-sysdump

-----
**When to Choose Cilium**

- You need **high-scale** clusters and want to avoid iptables pain.
- You want **kube-proxy replacement** and better service LB performance.
- You require **L7 policies** without sidecars.
- You care about **deep network visibility** (Hubble) and **clean egress control**.
- You’re going **multi-cluster** and want consistent identities/policies across them.
-----


