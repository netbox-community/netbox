const HOTKEYS: Record<string, () => void> = {
  '/': focusGlobalSearch,
};

function focusGlobalSearch(): void {
  const searchInput = document.querySelector<HTMLInputElement>('header input[name="q"]')!;
  if (searchInput) {
    searchInput.focus();
  }
}

function handleKeydown(event: KeyboardEvent): void {
  // Ignore hotkeys when focused on form elements or when modal is open
  if ((event.target as Element).matches('input, textarea, select') || document.body.classList.contains('modal-open')) {
    return;
  }

  const handler = HOTKEYS[event.key];
  if (!handler) {
    return;
  }

  event.preventDefault();
  handler();
}

export function initHotkeys(): void {
  document.addEventListener('keydown', handleKeydown);
}
