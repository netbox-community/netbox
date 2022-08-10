# L2VPN & Overlay

L2VPN and overlay networks, such as VXLAN and EVPN, can be defined in NetBox and tied to interfaces and VLANs. This allows for easy tracking of overlay assets and their relationships with underlay resources.

Each L2VPN instance has a type and optional unique identifier. Like VRFs, L2VPNs can also have import and export route targets assigned to them. Terminations can then be created to assign VLANs and/or device and virtual machine interfaces to the overlay.
