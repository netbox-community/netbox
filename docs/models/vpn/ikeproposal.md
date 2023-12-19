# IKE Proposals

An [Internet Key Exhcnage (IKE)](https://en.wikipedia.org/wiki/Internet_Key_Exchange) proposal defines a set of parameters used to establish a secure bidirectional connection across an untrusted medium, such as the Internet. IKE proposals defined in NetBox can be referenced by [IKE policies](./ikepolicy.md), which are in turn employed by [IPSec profiles](./ipsecprofile.md).

!!! note
    Some platforms refer to IKE proposals as [ISAKMP](https://en.wikipedia.org/wiki/Internet_Security_Association_and_Key_Management_Protocol), which is a framework for authentication and key exchange which employs IKE.

## Fields

### Name

The unique user-assigned name for the proposal.

### Authentication Method

The strategy employed for authenticating the IKE peer. Available options are listed below.

| Name           |
|----------------|
| Pre-shared key |
| Certificate    |
| RSA signature  |
| DSA signature  |

### Encryption Algorithm

The protocol employed for data encryption. Options include DES, 3DES, and various flavors of AES.

### Authentication Algorithm

The mechanism employed to ensure data integrity. Options include MD5 and SHA HMAC implementations. Specifying an authentication algorithm is optional, as some encryption algorithms (e.g. AES-GCM) provide authentication natively.

### Group

The [Diffie-Hellman group](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange) supported by the proposal. Group IDs are [managed by IANA](https://www.iana.org/assignments/ikev2-parameters/ikev2-parameters.xhtml#ikev2-parameters-8).

### SA Lifetime

The maximum lifetime for the IKE security association (SA), in seconds.
