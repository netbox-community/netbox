/**
 * Get the text to be copied by a `.copy-content` element. This is either the literal value of its
 * `data-clipboard-text` attribute, or the content of the element matched by the CSS selector in its
 * `data-clipboard-target` attribute.
 */
function getCopyText(trigger: HTMLElement): Nullable<string> {
  const text = trigger.getAttribute('data-clipboard-text');
  if (text) {
    return text;
  }
  const selector = trigger.getAttribute('data-clipboard-target');
  let target: Nullable<Element> = null;
  if (selector) {
    try {
      target = document.querySelector(selector);
    } catch {
      // An invalid selector (such as an ID beginning with a digit) raises a SyntaxError
      console.warn(`Invalid data-clipboard-target selector: ${selector}`);
      return null;
    }
  }
  if (
    target instanceof HTMLInputElement ||
    target instanceof HTMLTextAreaElement ||
    target instanceof HTMLSelectElement
  ) {
    return target.value;
  }
  if (target instanceof HTMLElement) {
    return target.innerText;
  }
  console.warn('Found no content to copy for', trigger);
  return null;
}

/**
 * Copy text using a temporary <textarea> and the legacy `execCommand()` API, for contexts in which
 * the Clipboard API is unavailable (outside HTTPS or localhost) or the browser refuses the request.
 */
function copyTextLegacy(text: string, trigger: HTMLElement): void {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  // Prevent mobile browsers from opening a keyboard, or zooming in on focus
  textarea.readOnly = true;
  textarea.style.fontSize = '12pt';
  textarea.style.position = 'fixed';
  textarea.style.top = '0';
  textarea.style.left = '0';
  textarea.style.opacity = '0';

  const previousFocus = document.activeElement;
  (trigger.closest('.modal') ?? document.body).append(textarea);
  textarea.focus({ preventScroll: true });
  textarea.select();
  // iOS ignores select() on a read-only field
  textarea.setSelectionRange(0, text.length);
  if (!document.execCommand('copy')) {
    console.warn('Failed to copy text to the clipboard');
  }
  textarea.remove();
  if (previousFocus instanceof HTMLElement) {
    previousFocus.focus({ preventScroll: true });
  }
}

/**
 * Copy text to the clipboard, falling back to the legacy method if the Clipboard API fails.
 */
function copyText(text: string, trigger: HTMLElement): void {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).catch(() => copyTextLegacy(text, trigger));
  } else {
    copyTextLegacy(text, trigger);
  }
}

function handleClick(event: MouseEvent): void {
  if (!(event.target instanceof Element)) {
    return;
  }
  const trigger = event.target.closest<HTMLElement>('.copy-content');
  if (trigger === null) {
    return;
  }
  const text = getCopyText(trigger);
  if (text !== null) {
    copyText(text, trigger);
  }
}

/**
 * Enable copy-to-clipboard buttons. A single listener on the document handles every `.copy-content`
 * element, including those swapped in later by HTMX.
 */
export function initClipboard(): void {
  document.addEventListener('click', handleClick);
}
