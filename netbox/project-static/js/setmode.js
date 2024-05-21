/**
 * Set the color mode on the `<html/>` element and in local storage.
 *
 * @param mode {"dark" | "light"} UI color mode.
 */
function setMode(mode) {
    document.documentElement.setAttribute("data-bs-theme", mode);
    localStorage.setItem("netbox-color-mode", mode);
}

/**
 * Determine the best initial color mode to use prior to rendering.
 */
function initMode() {
    try {
        // Determine the configured color mode, if any
        var clientMode = localStorage.getItem("netbox-color-mode");
        // Detect browser preference, if set
        var preferDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        var preferLight = window.matchMedia("(prefers-color-scheme: light)").matches;

        // Use the selected color mode, if any
        if (clientMode !== null) {
            return setMode(clientMode, false);
        }

        // Fall back to the mode preferred by the browser, if specified
        if (preferDark) {
            return setMode("dark", true);
        }
        else if (preferLight) {
            return setMode("light", true);
        }
    } catch (error) {
        // In the event of an error, log it to the console and set the mode to light mode.
        console.error(error);
    }

    // Default to light mode
    return setMode("light", true);
}
