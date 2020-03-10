# Secret Roles

Each secret is assigned a functional role which indicates what it is used for. Secret roles are customizable. Typical roles might include:

* Login credentials
* SNMP community strings
* RADIUS/TACACS+ keys
* IKE key strings
* Routing protocol shared secrets

Roles are also used to control access to secrets. Each role is assigned an arbitrary number of groups and/or users. Only the users associated with a role have permission to decrypt the secrets assigned to that role. (A superuser has permission to decrypt all secrets, provided they have an active user key.)
