# Content Security Policy

!!! info "This feature was introduced in NetBox v4.8."

A [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP) (CSP) tells the browser from which sources a page may load scripts, images, fonts, and other resources. NetBox does not send one by default. To send one, define it with the [`SECURE_CSP`](../configuration/security.md#secure_csp) or [`SECURE_CSP_REPORT_ONLY`](../configuration/security.md#secure_csp_report_only) configuration parameter.

NetBox's own pages are written to work under a strict script policy. Every `<script>` element NetBox renders carries the per-request nonce, and NetBox does not use inline event handler attributes or evaluate strings as code. This applies to scripts only. NetBox makes no equivalent promise for styles: it renders inline `<style>` elements and `style=` attributes, and none of them carry a nonce.

!!! warning "Debug mode"
    With `DEBUG` enabled, Django's debug error pages, GraphiQL's debug integration and django-htmx's error handler run scripts that a strict policy blocks or reports. Test policies with `DEBUG` disabled, and don't loosen a policy to accommodate them.

## Example policy

```python
from django.utils.csp import CSP

SECURE_CSP = {
    'default-src': [CSP.SELF],
    'script-src': [
        CSP.SELF,
        CSP.NONCE,
        'https://static.copilot.netboxlabs.ai',
    ],
    'style-src': [CSP.SELF, CSP.UNSAFE_INLINE, 'https://fonts.googleapis.com'],
    'font-src': [CSP.SELF, 'data:', 'https://fonts.gstatic.com'],
    'img-src': [CSP.SELF, 'data:', 'https:'],
    'connect-src': [CSP.SELF],
    'worker-src': [CSP.SELF, 'blob:'],
    'base-uri': [CSP.SELF],
}
```

Try a policy first by assigning it to `SECURE_CSP_REPORT_ONLY`, which reports violations in the browser console without blocking anything.

If your users enable NetBox Copilot, also allow `https://unpkg.com` and `https://js.stripe.com` in `script-src`, `'self'` and `https://js.stripe.com` in `frame-src`, and `https://api.copilot.netboxlabs.ai` and `wss://api.copilot.netboxlabs.ai` in `connect-src`.
