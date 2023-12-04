# Tunnels

NetBox can model private tunnels formed among virtual termination points across your network. Typical tunnel implementations include GRE, IP-in-IP, and IPSec. A tunnel may be terminated to two or more device or virtual machine interfaces. For convenient organization, tunnels may be assigned to user-defined groups.

```mermaid
flowchart TD
    Termination1[TunnelTermination]
    Termination2[TunnelTermination]
    Interface1[Interface]
    Interface2[Interface]
    Tunnel --> Termination1 & Termination2
    Termination1 --> Interface1
    Termination2 --> Interface2
    Interface1 --> Device
    Interface2 --> VirtualMachine

click Tunnel "../../models/vpn/tunnel/"
click TunnelTermination1 "../../models/vpn/tunneltermination/"
click TunnelTermination2 "../../models/vpn/tunneltermination/"
```

# IPSec & IKE

NetBox includes robust support for modeling IPSec & IKE policies. These are used to define encryption and authentication parameters for IPSec tunnels.

```mermaid
flowchart TD
    subgraph IKEProposals[Proposals]
    IKEProposal1[IKEProposal]
    IKEProposal2[IKEProposal]
    end
    subgraph IPSecProposals[Proposals]
    IPSecProposal1[IPSecProposal]
    IPSecProposal2[IPSecProposal]
    end
    IKEProposals --> IKEPolicy
    IPSecProposals --> IPSecPolicy
    IKEPolicy & IPSecPolicy--> IPSecProfile
    IPSecProfile --> Tunnel

click IKEProposal1 "../../models/vpn/ikeproposal/"
click IKEProposal2 "../../models/vpn/ikeproposal/"
click IKEPolicy "../../models/vpn/ikepolicy/"
click IPSecProposal1 "../../models/vpn/ipsecproposal/"
click IPSecProposal2 "../../models/vpn/ipsecproposal/"
click IPSecPolicy "../../models/vpn/ipsecpolicy/"
click IPSecProfile "../../models/vpn/ipsecprofile/"
click Tunnel "../../models/vpn/tunnel/"
```
