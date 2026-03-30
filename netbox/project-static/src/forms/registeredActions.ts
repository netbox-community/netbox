import { getElements } from '../util';

/**
 * Enable/disable registered action checkboxes based on selected object_types.
 */
export function initRegisteredActions(): void {
  const actionsContainer = document.getElementById('id_registered_actions_container');
  const selectedList = document.getElementById('id_object_types_1') as HTMLSelectElement;

  if (!actionsContainer || !selectedList) {
    return;
  }

  function updateState(): void {
    const selectedModels = new Set<string>();

    // Get model keys from selected options
    for (const option of Array.from(selectedList.options)) {
      const modelKey = option.dataset.modelKey;
      if (modelKey) {
        selectedModels.add(modelKey);
      }
    }

    // Enable/disable action groups based on selected models
    const groups = actionsContainer!.querySelectorAll('.model-actions');

    groups.forEach(group => {
      const modelKey = group.getAttribute('data-model');
      const enabled = modelKey !== null && selectedModels.has(modelKey);
      const el = group as HTMLElement;

      // Toggle disabled on checkboxes, overriding Bootstrap's disabled opacity
      // to keep them visible in dark mode
      for (const checkbox of Array.from(
        el.querySelectorAll<HTMLInputElement>('input[type="checkbox"]'),
      )) {
        checkbox.disabled = !enabled;
        checkbox.style.opacity = enabled ? '' : '0.75';
      }

      // Fade text for disabled groups
      for (const label of Array.from(
        el.querySelectorAll<HTMLElement>('small, .form-check-label'),
      )) {
        label.style.opacity = enabled ? '' : '0.5';
      }
    });
  }

  // Initial update
  updateState();

  // Listen to move button clicks
  for (const btn of getElements<HTMLButtonElement>('.move-option')) {
    btn.addEventListener('click', () => {
      // Wait for DOM update
      setTimeout(updateState, 50);
    });
  }
}
