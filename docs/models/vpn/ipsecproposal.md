# IPSec Proposal

An [IPSec](https://en.wikipedia.org/wiki/IPsec) proposal defines a set of parameters used in negotiating security associations for IPSec tunnels. IPSec proposals defined in NetBox can be referenced by [IPSec policies](./ipsecpolicy.md), which are in turn employed by [IPSec profiles](./ipsecprofile.md).

## Fields

### Name

The unique user-assigned name for the proposal.

### Encryption Algorithm

The protocol employed for data encryption. Options include DES, 3DES, and various flavors of AES.

!!! note
    If an encryption algorithm is not specified, an authentication algorithm must be specified.

### Authentication Algorithm

The mechanism employed to ensure data integrity. Options include MD5 and SHA HMAC implementations.

!!! note
    If an authentication algorithm is not specified, an encryption algorithm must be specified.

### SA Lifetime (Seconds)

The maximum amount of time for which the security association (SA) may be active, in seconds.

### SA Lifetime (Data)

The maximum amount of data which can be transferred within the security association (SA) before it must be rebuilt, in kilobytes.
