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

      el.style.opacity = enabled ? '1' : '0.4';

      // Toggle disabled on checkboxes within the group
      for (const checkbox of Array.from(
        el.querySelectorAll<HTMLInputElement>('input[type="checkbox"]'),
      )) {
        checkbox.disabled = !enabled;
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
