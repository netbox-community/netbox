# NetBox Threat Model

## Purpose & Scope

This document describes the security threat model for **NetBox Community Edition**, installed and operated according to the [official documentation](https://netboxlabs.com/docs/netbox/). Its purpose is to state explicitly who and what NetBox trusts, what a supported deployment looks like, and — most importantly — which classes of behavior are intended, privileged operations rather than security vulnerabilities.

NetBox is a feature-rich application that deliberately grants powerful capabilities (code execution, template rendering, outbound requests) to privileged users in order to support advanced network automation workflows. Many security reports we receive describe these intended capabilities as if they were defects. This document exists so that prospective reporters — and the maintainers who triage their reports — can quickly distinguish a genuine vulnerability from an authorized, privileged operation working as designed.

This document **complements** our [Security Policy](SECURITY.md); it does not replace it. The policy governs *how* to report a suspected vulnerability and the conditions a report must meet. This document governs *what* constitutes a vulnerability in the first place.

This model anchors to [OWASP's threat modeling guidance](https://owasp.org/www-community/Threat_Modeling) and uses a lightweight [STRIDE](https://en.wikipedia.org/wiki/STRIDE_%28security%29) breakdown (see below).

## Supported Deployment Model

NetBox's threat model assumes a deployment consistent with the recommendations in our [Security Policy](SECURITY.md) and [installation documentation](https://netboxlabs.com/docs/netbox/installation/):

* **Not exposed to the public Internet.** NetBox is intended to run on an internal or otherwise access-controlled network, behind a reverse proxy (e.g. nginx). It is not designed or hardened to serve as an anonymous, public-facing web application.
* **Administered by trusted operators.** The individuals who deploy, configure, and administer NetBox — including holders of the `is_superuser` flag and anyone with shell, filesystem, or database access to the host — are assumed to be trusted system administrators.
* **The database is reachable only by the application.** PostgreSQL and Redis are assumed to be accessible only to the NetBox application itself, not to arbitrary clients.
* **An authenticated user base.** NetBox is intended for use only by authenticated users. [`LOGIN_REQUIRED`](https://netboxlabs.com/docs/netbox/configuration/security/#login_required) defaults to `True`, and support for unauthenticated access is being removed entirely in NetBox v5.0.
* **The reverse proxy owns the network edge.** TLS termination, HTTP request rate limiting, and authoritative determination of the client IP address are the responsibility of the deployment's reverse proxy and surrounding infrastructure — not the application. (See [`HTTP_CLIENT_IP_HEADERS`](https://netboxlabs.com/docs/netbox/configuration/system/#http_client_ip_headers); the headers NetBox trusts for client IP are only as trustworthy as the proxy that sets them.)

Reports that assume a deployment outside this model — for example, "an anonymous Internet user can reach the login page" or "an administrator can modify the database" — describe the intended operating environment, not a vulnerability.

## Trusted vs. Untrusted Actors

The central question when evaluating any NetBox security report is: **does the attack require a privilege that NetBox already designates as trusted?**

| Actor | Trust | Notes |
| --- | --- | --- |
| The NetBox server / process | **Trusted** | Executes application code; holds secrets. |
| PostgreSQL database, Redis | **Trusted** | Assumed reachable only by the application. |
| Infrastructure operators | **Trusted** | Shell/filesystem/DB access implies total control by design. |
| Superusers (`is_superuser`) | **Trusted** | An active superuser bypasses all object-level permission checks. This is intentional. |
| Users permitted to author code-bearing objects | **Trusted** | Holders of permissions to create/modify custom scripts, export templates, config templates, custom links, or webhooks (see below). |
| Authenticated users **without** those permissions | **Untrusted** | Subject to full object-based permission enforcement. |
| Unauthenticated / network-adjacent parties | **Untrusted** | Outside the supported deployment model entirely. |

The governing principle:

> **Granting a user permission to author a custom script, export or config template, custom link, or webhook is equivalent to granting that user a degree of code execution — by design.** Abuse of such a feature by a user who holds the corresponding permission is not a vulnerability. The mitigation is administrative: grant these permissions only to trusted users, as instructed by the documentation for each feature.

## Privileged-by-Design Features

The following features deliberately allow trusted users to supply code or logic that NetBox executes or renders. Each is gated by a specific permission and carries an explicit warning in its documentation. Using these features as designed — even in ways that read like "code execution" or "data access" to an outside observer — is **not** a vulnerability.

### Custom Scripts

Custom scripts are Python modules with **unrestricted access to the NetBox ORM, database, and Python runtime**. They are gated by the `extras.run_script` permission (and authored by users who can add/modify script modules). The documentation states plainly that they are *"inherently unsafe and should be installed and run only from trusted sources"*.

### Export Templates, Config Templates, Custom Links & Webhooks (Jinja)

These features render **user-authored [Jinja templates](https://jinja.palletsprojects.com/en/stable/)** with live application objects in scope. Templates are evaluated in a Jinja [`SandboxedEnvironment`](https://jinja.palletsprojects.com/en/stable/sandbox/) (`netbox/utilities/Jinja.py`), which restricts access to unsafe attributes and operations.

It is important to be precise about where the boundary lies:

* The sandbox **is** a boundary NetBox maintains. A genuine, reproducible *escape* from the sandbox — code or attribute access the sandbox is supposed to block — **is** a vulnerability we take seriously (see "In-Scope Vulnerabilities").
* Authoring these objects is nonetheless a **privileged action**. A template author legitimately has broad read access to NetBox objects and can produce arbitrary output within the sandbox's bounds. That a template can read data the author is otherwise permitted to see, or generate HTML/configuration, is intended behavior — not an injection vulnerability.

Each feature's documentation states that the relevant permission should be granted only to trusted users:

* [Export templates](https://netboxlabs.com/docs/netbox/customization/export-templates/)
* [Custom links](https://netboxlabs.com/docs/netbox/customization/custom-links/)
* [Webhooks](https://netboxlabs.com/docs/netbox/integrations/webhooks/)
* [Configuration rendering](https://netboxlabs.com/docs/netbox/features/configuration-rendering)

### Webhooks & Event Rules (Outbound Requests)

Webhooks issue **outbound HTTP requests to operator-defined URLs**, with the URL, headers, and body all rendered from user-authored Jinja. A trusted webhook author can therefore direct requests to arbitrary endpoints. This server-side request capability is the entire purpose of the feature; it is available only to users permitted to create webhooks, and is not a server-side request forgery (SSRF) vulnerability when exercised by such a user.

### Config Contexts & Custom Fields

Config contexts store arbitrary JSON applied to devices and virtual machines; custom fields add operator-defined attributes (with optional regex/JSON-schema validation). Neither executes code directly. Config context data may, however, be consumed by config templates during rendering, so it inherits the same "template author is trusted" posture described above.

### Object-Based Permissions

NetBox enforces a robust [object-based permission system](https://netboxlabs.com/docs/netbox/features/authentication-permissions/) layered on top of Django's model permissions. Permissions combine object types, users/groups, actions, and optional JSON **constraints** (including the special `$user` token). A failure of this system to enforce a permission or constraint that it advertises **is** a vulnerability (see below).

## In-Scope Vulnerabilities

We take the following seriously. The common thread is a breach of a boundary NetBox *claims* to enforce, or harm to a user who never consented to the risk.

* **Authorization bypass** — reading or acting on objects a user has no permission to access.
* **Privilege escalation** — bypassing a permission or constraint to gain access beyond what was granted.
* **Injection that crosses a data boundary** — e.g. filter/ORM operator injection in the REST or GraphQL API exposing data a user shouldn't reach.
* **Cross-site scripting (XSS) against a non-consenting victim** — stored or DOM-based XSS that executes in another user's session.
* **Jinja sandbox escapes** — a reproducible escape from the template sandbox's intended restrictions.
* **Authentication bypass** and **unauthenticated remote code execution or data access**.
* **Dependency vulnerabilities with a realistic exploit path** through NetBox (not merely a flagged version).

## Out-of-Scope / Non-Issues

The following are **not** treated as NetBox vulnerabilities. Most describe a privileged feature used by a user the documentation already designates as trusted, or a concern that belongs to the deployment/platform layer.

| Scenario | Status | Reason                                                                                                                                                                                                          |
| --- | --- |-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A permitted user runs code via a custom script, Jinja template, custom link, or webhook | Not a vulnerability | These features exist to execute user-authored logic; the required permission is trusted, operator-tier by design.                                                                                               |
| A superuser modifies the database, reads secrets, or creates another superuser | Not a vulnerability | Superusers and infrastructure operators are trusted by design.                                                                                                                                                  |
| A template author reads NetBox data they are otherwise permitted to view | Not a vulnerability | Template rendering with objects in scope is the purpose of the feature; the sandbox, not permission scoping, is the boundary.                                                                                   |
| Missing login/request rate limiting | Out of scope | A deployment-layer concern, handled by the reverse proxy rather than the application.                                                                                                                           |
| Client IP spoofing via `X-Forwarded-For` and similar headers | Out of scope | NetBox trusts the headers the reverse proxy sets; trustworthy client IP is a proxy responsibility ([`HTTP_CLIENT_IP_HEADERS`](https://docs.netbox.dev/en/stable/configuration/system/#http_client_ip_headers)). |
| Self-XSS (a user injecting script into their own session) | Not a vulnerability | The user is attacking only themselves; no privilege boundary is crossed.                                                                                                                                        |
| CSRF on the login form | Not a vulnerability | Login CSRF is not a meaningful attack in NetBox's deployment model.                                                                                                                                             |
| Automated-scanner reports that a file *may* be vulnerable | Rejected | Per our [Security Policy](SECURITY.md), we do not accept reports from automated tooling that merely suggest potential vulnerability without a confirmed reproducible exploit.                                   |

## Lightweight STRIDE View

| Category | NetBox posture |
| --- | --- |
| **S**poofing | Authentication via local accounts, LDAP, or SSO (python-social-auth); API tokens. Authoritative client-IP determination is delegated to the reverse proxy. |
| **T**ampering | All writes are gated by object-based permissions with optional constraints, validated within atomic transactions. Code-bearing objects are writable only by trusted users. |
| **R**epudiation | Changes are recorded via the changelog and journaling; event rules can emit notifications. |
| **I**nformation disclosure | Object-based view permissions filter every queryset. Cross-boundary disclosure (e.g. API/GraphQL filter injection) is in scope; data legitimately visible to a template author is not. |
| **D**enial of service | Request rate limiting and resource controls are a deployment/reverse-proxy responsibility, not the application's. |
| **E**levation of privilege | The superuser flag is all-or-nothing and trusted. Any *unintended* escalation across the permission system (constraint bypass, action bypass) is in scope. |

## Triage & Severity

When triaging a report we assess the **CVSS environmental score**, not solely the base score. A finding with a high CVSS base score may be downgraded substantially once NetBox's deployment assumptions and trust boundaries are applied — for example, a "remote code execution" that in fact requires a permission we already designate as trusted (script or template authoring) is mitigated by design rather than by a code change.

We use [CVSS v3.1/v4.0](https://www.first.org/cvss/) for scoring and the [STRIDE](https://en.wikipedia.org/wiki/STRIDE_%28security%29) categories above to reason about boundaries. If you believe you have a fix that closes an in-scope issue without degrading the affected feature, you are welcome to propose it alongside your report.

## Reporting

Before reporting, please confirm that the behavior you've observed is an in-scope vulnerability under this document and not an intended, privileged operation, and that it is reproducible in the current stable release of NetBox.

To report a suspected vulnerability, follow the process in our [Security Policy](SECURITY.md). In summary, a report must:

* Affect the most recent stable release of NetBox, or a current beta release;
* Affect a NetBox instance installed and configured per the official documentation; and
* Be reproducible following a prescribed set of instructions.

Confidential reports may be sent to `security@netboxlabs.com`.
