## 1\. What problem does a CA solve?

Without a CA, if you connect to https://example.com, your browser has no built-in way to know:

*   Is this really example.com, or some attacker’s server?
    
*   Has the server’s public key been tampered with?
    

A CA solves this by:

1.  Verifying the identity of an entity (person, server, org).
    
2.  Issuing a certificate that binds:
    
    *   a **public key**
        
    *   to an **identity** (e.g., DNS name example.com)
        
3.  Digitally **signing** that certificate with the CA’s private key.
    

Any client that **trusts the CA** and can verify its signature can trust the binding between identity and public key.

* * *

## 2\. Basic PKI pieces (where CA fits in)

In a typical X.509 Public Key Infrastructure (PKI), you have:

*   **Public / Private Keys**
    
    *   Private key: kept secret by the owner (server, user, app).
        
    *   Public key: can be distributed.
        
*   **Certificate (X.509)**
    
    *   Contains: public key, Subject (identity), validity period, extensions, etc.
        
    *   Signed by a CA (or self-signed in special cases).
        
*   **Certificate Authority (CA)**
    
    *   Has its own keypair.
        
    *   Uses its **private key** to sign other certificates.
        
    *   Its **public key** (root) is distributed as a **trust anchor** (in OS/browser trust store or internal trust store).
        

* * *

## 3\. Types of CAs

### 3.1 Root CA

*   A **root CA** certificate is:
    
    *   Self-signed.
        
    *   Embedded in trust stores (OS, browser, JVM, corporate).
        
*   It is the **trust anchor**. If a root CA’s key is compromised, everything below it is broken.
    
*   Typically:
    
    *   Very long-lived (10–20 years).
        
    *   Kept offline (in an HSM, with strict physical and procedural controls).
        

### 3.2 Intermediate / Subordinate CAs

*   Root CA usually signs one or more **intermediate CA** certificates.
    
*   Intermediate CAs then sign **leaf certificates** (server, client, code signing, etc.).
    
*   Benefits:
    
    *   Root CA stays offline and protected.
        
    *   Different intermediates for different purposes:
        
        *   Server TLS
            
        *   Client auth
            
        *   Code signing
            
        *   Internal-only services
            

Visually:

`[Root CA]  (self-signed)    ↓ signs [Intermediate CA]    ↓ signs [Leaf certificate: e.g. www.example.com]`

* * *

## 4\. How a CA issues a certificate (high level)

1.  **Key generation**
    
    *   The entity (e.g., web server) generates its own keypair (private + public).
        
    *   Or, sometimes the CA generates it for them (less common now for security reasons).
        
2.  **Certificate Signing Request (CSR)**
    
    *   Entity creates a CSR with:
        
        *   Public key
            
        *   Subject name (CN), Subject Alternative Names (DNS names)
            
        *   Other requested attributes
            
    *   CSR is signed with the entity’s private key (proves possession of private key).
        
3.  **Validation**
    
    *   CA verifies identity according to a policy:
        
        *   For public web TLS: DNS verification (HTTP-01, DNS-01, email, etc.).
            
        *   For enterprise: HR / directory / domain membership, etc.
            
    *   This is where **Domain Validation (DV)**, **Organization Validation (OV)**, **Extended Validation (EV)** differ (public CAs).
        
4.  **Signing**
    
    *   CA issues an X.509 certificate:
        
        *   Embeds public key, subject, validity, extensions.
            
        *   Signs the certificate using CA’s private key.
            
5.  **Delivery & installation**
    
    *   Entity gets the signed certificate, installs it on server/device along with:
        
        *   The intermediate CA chain (so clients can build chain to a root).
            

* * *

## 5\. How clients actually use a CA (TLS example)

When you open https://example.com:

1.  The server sends:
    
    *   Its leaf certificate (example.com).
        
    *   One or more intermediate CA certificates (certificate chain).
        
2.  The client (browser, OS, app):
    
    *   Validates:
        
        *   Cert is within **validity period** (not expired, not before start).
            
        *   Cert is not revoked (using CRL or OCSP, if enforced).
            
        *   Signature of leaf cert using intermediate CA public key.
            
        *   Signature of intermediate CA using root CA public key.
            
    *   Checks chain ends at a **trusted root CA** in its trust store.
        
    *   Ensures hostname (example.com) matches CN/SAN in certificate.
        
3.  If all checks pass:
    
    *   Client trusts server’s public key.
        
    *   Proceeds with TLS handshake and negotiates symmetric keys.
        

If any step fails (e.g., unknown CA, name mismatch, expired cert), the client shows a warning or refuses connection.

* * *

## 6\. Public vs Private (Enterprise) CAs

### Public CA

*   Examples: Let’s Encrypt, DigiCert, GlobalSign, etc.
    
*   Used for certificates that must be trusted globally on the public internet.
    
*   Their root certs are in browser/OS trust stores.
    
*   Follow CA/Browser Forum rules, audits, etc.
    

### Private / Enterprise CA

*   Used inside an organisation:
    
    *   For internal services, VPN, Wi-Fi, service-to-service TLS, mTLS, code signing, etc.
        
*   Implementations:
    
    *   Microsoft AD CS
        
    *   HashiCorp Vault PKI
        
    *   AWS Private CA
        
    *   etc.
        
*   The organisation distributes its internal **root CA** (or an intermediate) to:
    
    *   Servers
        
    *   Clients
        
    *   Devices
        
*   Not trusted by public internet, only within the org’s environment.
    

* * *

## 7\. CA responsibilities (beyond just signing)

A serious CA does much more than just “sign certs”:

1.  **Key management**
    
    *   Protect the CA private keys (often in HSM).
        
    *   Key rotation and rollover strategies.
        
    *   Backup and recovery procedures.
        
2.  **Policies & practices**
    
    *   **Certificate Policy (CP)**: high-level rules on what certificates mean.
        
    *   **Certification Practice Statement (CPS)**: how the CA implements those rules.
        
3.  **Revocation**
    
    *   If a certificate is compromised, mis-issued, or owner is no longer valid:
        
        *   Mark as revoked.
            
        *   Publish **CRL (Certificate Revocation List)** or support **OCSP**.
            
    *   Clients can check revocation status during validation (though enforcement varies).
        
4.  **Auditing & logging**
    
    *   Track all issuance, revocation, administrative actions.
        
    *   For public CAs, compliance audits and Certificate Transparency logs.
        

* * *

## 8\. Self-signed certificates vs CA-signed

*   **Self-signed cert**:
    
    *   Signed by its own private key.
        
    *   Useful for dev/test or completely isolated systems.
        
    *   Not trusted by default by others; you must manually add it to trust store.
        
*   **CA-signed cert**:
    
    *   Signed by a trusted CA.
        
    *   Automatically trusted by clients that include that CA in their trust store.
        

* * *

## 9\. How this maps to real engineering work

As a computer engineer you typically interact with CAs in scenarios like:

*   **Web / API platforms**
    
    *   Getting TLS certs for your domains via Let’s Encrypt, ACME, or corporate PKI.
        
    *   Configuring Nginx/Envoy/Ingress controllers with the cert + key + chain.
        
*   **Kubernetes / service mesh**
    
    *   Using internal CA for:
        
        *   mTLS between pods (e.g., Istio, Linkerd, cert-manager + Vault).
            
        *   Rotating short-lived certs automatically.
            
*   **Infrastructure & cloud**
    
    *   Using AWS/Azure/GCP PKI services or Vault PKI to issue certs for:
        
        *   Internal endpoints
            
        *   Databases
            
        *   Mutual TLS between microservices.
            
*   **Enterprise security**
    
    *   AD CS issuing client auth certs for users, devices, VPNs, Wi-Fi (802.1X).
        
    *   Smart cards, device certificates for Zero Trust access.
        

* * *

If you want, next I can:

*   Compare a **traditional CA** (AD CS) vs **Vault PKI** vs **AWS/Azure managed CA**, or
    
*   Walk through the lifecycle: “design an internal PKI with root + intermediate CAs and integrate it with Kubernetes (cert-manager).”