import { getElements, isTruthy } from './util';

type ColorMode = 'light' | 'dark';
type ColorModePreference = ColorMode | 'none';

const COLOR_MODE_KEY = 'netbox-color-mode';
const TEXT_WHEN_DARK = 'Light Mode';
const TEXT_WHEN_LIGHT = 'Dark Mode';
const ICON_WHEN_DARK = 'mdi-lightbulb-on';
const ICON_WHEN_LIGHT = 'mdi-lightbulb';

function isColorMode(value: string): value is ColorMode {
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
  document.body.setAttribute(`data-${COLOR_MODE_KEY}`, targetMode);

  for (const text of getElements<HTMLSpanElement>('span.color-mode-text')) {
    if (targetMode === 'light') {
      text.innerText = TEXT_WHEN_LIGHT;
    } else if (targetMode === 'dark') {
      text.innerText = TEXT_WHEN_DARK;
    }
  }
  for (const icon of getElements<HTMLSpanElement>('i.color-mode-icon', 'span.color-mode-icon')) {
    if (targetMode === 'light') {
      icon.classList.remove(ICON_WHEN_DARK);
      icon.classList.add(ICON_WHEN_LIGHT);
    } else if (targetMode === 'dark') {
      icon.classList.remove(ICON_WHEN_LIGHT);
      icon.classList.add(ICON_WHEN_DARK);
    }
  }

  for (const elevation of getElements<HTMLObjectElement>('.rack_elevation')) {
    const svg = elevation.contentDocument?.querySelector('svg') ?? null;
    if (svg !== null) {
      svg.setAttribute(`data-${COLOR_MODE_KEY}`, targetMode);
    }
  }
}

/**
 * Call all functions necessary to update the color mode across the UI.
 *
 * @param mode Target color mode.
 */
function setColorMode(mode: ColorMode): void {
  for (const func of [storeColorMode, updateElements]) {
    func(mode);
  }
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
  const bodyValue = document.body.getAttribute(`data-${COLOR_MODE_KEY}`);

  if (isTruthy(bodyValue) && isTruthy(currentValue)) {
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

  if (isTruthy(currentValue) && !isTruthy(bodyValue) && isColorMode(currentValue)) {
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
  for (const func of [initColorModeToggle]) {
    func();
  }
}
