import { getElements } from '../util';

/**
 * Show/hide registered action checkboxes based on selected object_types.
 */
export function initRegisteredActions(): void {
  const actionsContainer = document.getElementById('id_registered_actions_container');
  const selectedList = document.getElementById('id_object_types_1') as HTMLSelectElement;

  if (!actionsContainer || !selectedList) {
    return;
  }

  function updateVisibility(): void {
    const selectedModels = new Set<string>();

    // Get model keys from selected options
    for (const option of Array.from(selectedList.options)) {
      const modelKey = option.dataset.modelKey;
      if (modelKey) {
        selectedModels.add(modelKey);
      }
    }

    // Show/hide action groups
    const groups = actionsContainer!.querySelectorAll('.model-actions');
    let anyVisible = false;

    groups.forEach(group => {
      const modelKey = group.getAttribute('data-model');
      const visible = modelKey !== null && selectedModels.has(modelKey);
      (group as HTMLElement).style.display = visible ? 'block' : 'none';
      if (visible) {
        anyVisible = true;
      }
    });

    // Show/hide "no actions" message
    const noActionsMsg = document.getElementById('no-custom-actions-message');
    if (noActionsMsg) {
      noActionsMsg.style.display = anyVisible ? 'none' : 'block';
    }
  }

  // Initial update
  updateVisibility();

  // Listen to move button clicks
  for (const btn of getElements<HTMLButtonElement>('.move-option')) {
    btn.addEventListener('click', () => {
      // Wait for DOM update
      setTimeout(updateVisibility, 50);
    });
  }
}
