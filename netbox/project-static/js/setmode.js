/**
 * Set the color mode on the `<html/>` element and in local storage.
 *
 * @param mode {"dark" | "light"} NetBox Color Mode.
 * @param inferred {boolean} Value is inferred from browser/system preference.
 */
function setMode(mode, inferred) {
    document.documentElement.setAttribute("data-bs-theme", mode);
    localStorage.setItem("netbox-color-mode", mode);
    localStorage.setItem("netbox-color-mode-inferred", inferred);
}

/**
 * Determine the best initial color mode to use prior to rendering.
 */
function initMode() {
    try {
        // Browser prefers dark color scheme.
        var preferDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        // Browser prefers light color scheme.
        var preferLight = window.matchMedia("(prefers-color-scheme: light)").matches;
        // Client NetBox color-mode override.
        var clientMode = localStorage.getItem("netbox-color-mode");
        // NetBox server-rendered value.
        var serverMode = document.documentElement.getAttribute("data-netbox-color-mode");
        // Color mode is inferred from browser/system preference and not deterministically set by
        // the client or server.
        var inferred = JSON.parse(localStorage.getItem("netbox-color-mode-inferred"));

        if (inferred === true && (serverMode === "light" || serverMode === "dark")) {
            // The color mode was previously inferred from browser/system preference, but
            // the server now has a value, so we should use the server's value.
            return setMode(serverMode, false);
        }
        if (clientMode === null && (serverMode === "light" || serverMode === "dark")) {
            // If the client mode is not set but the server mode is, use the server mode.
            return setMode(serverMode, false);
        }
        if (clientMode !== null && serverMode === "unset") {
            // The color mode has been set, deterministically or otherwise, and the server
            // has no preference or has not been set. Use the client mode, but allow it to
            /// be overridden by the server if/when a server value exists.
            return setMode(clientMode, true);
        }
        if (
            clientMode !== null &&
            (serverMode === "light" || serverMode === "dark") &&
            clientMode !== serverMode
        ) {
            // If the client mode is set and is different than the server mode (which is also set),
            // use the client mode over the server mode, as it should be more recent.
            return setMode(clientMode, false);
        }
        if (clientMode === serverMode) {
            // If the client and server modes match, use that value.
            return setMode(clientMode, false);
        }
        if (preferDark && serverMode === "unset") {
            // If the server mode is not set but the browser prefers dark mode, use dark mode, but
            // allow it to be overridden by an explicit preference.
            return setMode("dark", true);
        }
        if (preferLight && serverMode === "unset") {
            // If the server mode is not set but the browser prefers light mode, use light mode,
            // but allow it to be overridden by an explicit preference.
            return setMode("light", true);
        }
    } catch (error) {
        // In the event of an error, log it to the console and set the mode to light mode.
        console.error(error);
    }
    return setMode("light", true);
}
