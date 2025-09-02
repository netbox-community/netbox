# User Interface

## Light & Dark Mode

The NetBox user interface supports toggling between light and dark versions of the theme. If needed, a plugin can determine the currently active color theme by inspecting `window.localStorage['netbox-color-mode']`, which will indicate either `light` or `dark`.

Additionally, when the color scheme is toggled by the user, a custom event `netbox.colorModeChanged` indicating the new scheme is dispatched. A plugin can listen for this event if needed to react to the change:

```typescript
window.addEventListener('netbox.colorModeChanged', e => {
  const customEvent = e as CustomEvent<ColorModeData>;
  console.log('New color mode:', customEvent.detail.netboxColorMode);
});
```
