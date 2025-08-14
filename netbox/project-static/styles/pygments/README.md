## Pygments style for NetBox

The style are based on the `Pygments` themes `solarized-light` and `solarized-dark`.
To generated the scss files in this directory execute the following code in a Python environment where `Pygments` is installed:

```python
from pygments.formatters import HtmlFormatter
h = HtmlFormatter(linenos="inline", classprefix="pygments-", style="solarized-dark")
print(h.get_style_defs())

h = HtmlFormatter(linenos="inline", classprefix="pygments-", style="solarized-light")
print(h.get_style_defs())
```

To get the correct theme for dark and light modes wrap the resulting CSS in the following selectors:

```scss
// _dark.scss
body[data-bs-theme='dark'] {
  // Insert generated CSS for dark theme here
}

// _light.scss
body[data-bs-theme='light'] {
  // Insert generated CSS for light theme here
}
```

The run the formatter:

```bash
yarn run format:styles
```