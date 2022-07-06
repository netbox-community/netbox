# L2VPN

A L2VPN object is NetBox is a representation of a layer 2 bridge technology such as VXLAN, VPLS or EPL.  Each L2VPN can be identified by name as well as an optional unique identifier (VNI would be an example).

Each L2VPN instance must have one of the following type associated with it:

* VPLS
* VPWS
* EPL
* EVPL
* EP-LAN
* EVP-LAN
* EP-TREE
* EVP-TREE
* VXLAN
* VXLAN EVPN
* MPLS-EVPN
* PBB-EVPN

!!!note
    Choosing VPWS, EPL, EP-LAN, EP-TREE will result in only being able to add 2 terminations to a given L2VPN.
