import { getElements, isTruthy } from './util';

const COLOR_MODE_PREFERENCE_KEY = 'netbox-color-mode-preference';

/**
 * Determine if a value is a supported color mode string value.
 */
function isColorMode(value: unknown): value is ColorMode {
  return value === 'dark' || value === 'light';
}

function isDefinedColorModePreference(value: unknown): value is ColorModePreference {
  return value === 'auto' || isColorMode(value);
}


/**
 * Set the color mode to light or dark.
 *
 * @param mode `'light'`, `'dark'` or `'auto'`
 * @returns `true` if the color mode was successfully set, `false` if not.
 */
function storeColorMode(modePreference: ColorModePreference): void {
  return localStorage.setItem(COLOR_MODE_PREFERENCE_KEY, mode);
}

function updateElements(targetMode: ColorModePreference): void {
  const body = document.querySelector('body');
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const theme = (targetMode === 'auto')
      ? (mediaQuery.matches ? 'dark' : 'light'
      : (targetMode === 'none' ? targetMode : 'light');

  if (body) {
    body.setAttribute('data-bs-theme', theme);
  }
  if (body && targetMode === 'auto') {
    mediaQuery.onchange = event => {
      body.setAttribute('data-bs-theme', event.matches ? 'dark' : 'light');
    }
  }

  for (const elevation of getElements<HTMLObjectElement>('.rack_elevation')) {
    const svg = elevation.contentDocument?.querySelector('svg') ?? null;
    if (svg !== null) {
      svg.setAttribute(`data-bs-theme`, theme);
    }
  }
}

/**
 * Call all functions necessary to update the color mode across the UI.
 *
 * @param mode Target color mode.
 */
export function setColorMode(mode: ColorModePreference): void {
  storeColorMode(mode);
  updateElements(mode);
}

/**
 * Toggle the color mode when a color mode toggle is clicked.
 */
function handleColorModeToggle(): void {
  const prevValue = localStorage.getItem(COLOR_MODE_PREFERENCE_KEY);
  if (isColorMode(prevValue)) {
    setColorMode(prevValue === 'light' ? 'dark' : 'light');
  } else if (prevValue === 'auto') {
    console.log('Ignoring color mode toggle in auto mode');
  } else {
    console.warn('Unable to determine the current color mode');
  }
}

/**
 * Determine the user's preference and set it as the color mode.
 */
function defaultColorMode(): void {
  // Get the current color mode value from local storage.
  const currentValue = localStorage.getItem(COLOR_MODE_PREFERENCE_KEY) as Nullable<ColorModePreference>;

  if (isTruthy(currentValue) && isColorMode(currentValue)) {
    return setColorMode(currentValue);
  }

  let preference: ColorModePreference = 'none';

  // Determine if the user prefers dark, light or auto mode.
  if (preference !== 'auto') {
    for (const mode of ['dark', 'light']) {
      if (window.matchMedia(`(prefers-color-scheme: ${mode})`).matches) {
        preference = mode as ColorModePreference;
        break;
      }
    }
  }
  switch (preference) {
    case 'auto':
    case 'dark':
    case 'light':
      return setColorMode(preference);
    case 'none':
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
  for (const func of [initColorModeToggle]) {
    func();
  }
}
