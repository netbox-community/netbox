import { getElements } from '../util';

/**
 * Enable/disable registered action checkboxes based on selected object_types.
 */
export function initRegisteredActions(): void {
  const selectedList = document.querySelector<HTMLSelectElement>(
    'select[data-object-types-selected]',
  );

  if (!selectedList) {
    return;
  }

  const actionCheckboxes = Array.from(
    document.querySelectorAll<HTMLInputElement>('input[type="checkbox"][data-models]'),
  );

  if (actionCheckboxes.length === 0) {
    return;
  }

  function updateState(): void {
    const selectedModels = new Set<string>();

    // Get model keys from selected options
    for (const option of Array.from(selectedList!.options)) {
      const modelKey = option.dataset.modelKey;
      if (modelKey) {
        selectedModels.add(modelKey);
      }
    }

    // Enable a checkbox if any of its supported models is selected
    for (const checkbox of actionCheckboxes) {
      const modelKeys = (checkbox.dataset.models ?? '').split(',').filter(Boolean);
      const enabled = modelKeys.some(m => selectedModels.has(m));
      checkbox.disabled = !enabled;
      if (!enabled) {
        checkbox.checked = false;
      }
      checkbox.style.opacity = enabled ? '' : '0.75';

      // Fade the label text when disabled
      const label = checkbox.nextElementSibling as HTMLElement | null;
      if (label) {
        label.style.opacity = enabled ? '' : '0.5';
      }
    }
  }

  // Initial update
  updateState();

  // Listen to move button clicks
  for (const btn of getElements<HTMLButtonElement>('.move-option')) {
    btn.addEventListener('click', () => {
      // Wait for DOM update
      setTimeout(updateState, 0);
    });
  }
}
