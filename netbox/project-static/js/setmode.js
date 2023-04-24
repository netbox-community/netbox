/**
 * Set the color mode on the `<html/>` element.
 *
 * @param mode {"dark" | "light" | "system"} NetBox Color Mode.
 */
function setMode(mode) {
  if (mode === 'system') {
    mode = getSystemColorMode();
  }
  document.documentElement.setAttribute('data-netbox-color-mode', mode);
}

/**
 * Determine the system color mode (light or dark).
 *
 * @return {string} "dark" or "light" based on system preference.
 */
function getSystemColorMode() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/**
 * Determine the best initial color mode to use prior to rendering.
 */
function initMode() {
  try {
    // NetBox server-rendered value.
    const serverMode = document.documentElement.getAttribute('data-netbox-color-mode');

    if (serverMode === 'light' || serverMode === 'dark' || serverMode === 'system') {
      // If the server mode is set (light, dark, or system), use the server mode.
      return setMode(serverMode);
    }

    // If server mode is not set, use the system color mode.
    return setMode('system');
  } catch (error) {
    // In the event of an error, log it to the console and set the mode to system mode.
    console.error(error);
    return setMode('system');
  }
}
