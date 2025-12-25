import { getElements, isTruthy } from './util';

const COLOR_MODE_KEY = 'netbox-color-mode';

/**
 * Determine if a value is a supported color mode string value.
 */
function isColorMode(value: unknown): value is ColorMode {
  return value === 'dark' || value === 'light';
}

/**
 * Set the color mode to light or dark.
 *
 * @param mode `'light'` or `'dark'`
 * @returns `true` if the color mode was successfully set, `false` if not.
 */
function storeColorMode(mode: ColorMode): void {
  return localStorage.setItem(COLOR_MODE_KEY, mode);
}

function updateElements(targetMode: ColorMode): void {
  const body = document.querySelector('body');
  if (body && targetMode == 'dark') {
    body.setAttribute('data-bs-theme', 'dark');
  } else if (body) {
    body.setAttribute('data-bs-theme', 'light');
  }

  for (const elevation of getElements<HTMLObjectElement>('.rack_elevation')) {
    const svg = elevation.firstElementChild ?? null;
    if (svg !== null && svg.nodeName == 'svg') {
      svg.setAttribute(`data-bs-theme`, targetMode);
    }
  }
}

/**
 * Set the color mode to light of elevations after an htmx call.
 * Pulls current color mode from document
 *
 * @param event htmx listener event details. See: https://htmx.org/events/#htmx:afterSwap
 */
function updateElevations(evt: CustomEvent, ): void {
  const swappedElement = evt.detail.elt
  if (swappedElement.nodeName == 'svg') {
    const currentMode = localStorage.getItem(COLOR_MODE_KEY);
    swappedElement.setAttribute('data-bs-theme', currentMode)
  }
}

/**
 * Call all functions necessary to update the color mode across the UI.
 *
 * @param mode Target color mode.
 */
export function setColorMode(mode: ColorMode): void {
  storeColorMode(mode);
  updateElements(mode);
  window.dispatchEvent(
    new CustomEvent<ColorModeData>('netbox.colorModeChanged', {
      detail: { netboxColorMode: mode },
    }),
  );
}

/**
 * Toggle the color mode when a color mode toggle is clicked.
 */
function handleColorModeToggle(): void {
  const currentValue = localStorage.getItem(COLOR_MODE_KEY);
  if (currentValue === 'light') {
    setColorMode('dark');
  } else if (currentValue === 'dark') {
    setColorMode('light');
  } else {
    console.warn('Unable to determine the current color mode');
  }
}

/**
 * Determine the user's preference and set it as the color mode.
 */
function defaultColorMode(): void {
  // Get the current color mode value from local storage.
  const currentValue = localStorage.getItem(COLOR_MODE_KEY) as Nullable<ColorMode>;

  if (isTruthy(currentValue)) {
    return setColorMode(currentValue);
  }

  let preference: ColorModePreference = 'none';

  // Determine if the user prefers dark or light mode.
  for (const mode of ['dark', 'light']) {
    if (window.matchMedia(`(prefers-color-scheme: ${mode})`).matches) {
      preference = mode as ColorModePreference;
      break;
    }
  }

  if (isTruthy(currentValue) && isColorMode(currentValue)) {
    return setColorMode(currentValue);
  }

  switch (preference) {
    case 'dark':
      return setColorMode('dark');
    case 'light':
      return setColorMode('light');
    case 'none':
      return setColorMode('light');
    default:
      return setColorMode('light');
  }
}

/**
 * Initialize color mode toggle buttons and set the default color mode.
 */
function initColorModeToggle(): void {
  for (const element of getElements<HTMLButtonElement>('button.color-mode-toggle')) {
    element.addEventListener('click', handleColorModeToggle);
  }
}

/**
 * Initialize all color mode elements.
 */
export function initColorMode(): void {
  window.addEventListener('load', defaultColorMode);
  window.addEventListener('htmx:afterSwap', updateElevations as EventListener); // Uses a custom event from HTMX
  for (const func of [initColorModeToggle]) {
    func();
  }
}
