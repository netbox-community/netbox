import { all, getElement, resetSelect, toggleVisibility as _toggleVisibility } from '../util';

/**
 * Get a select element's containing `.row` element.
 *
 * @param element Select element.
 * @returns Containing row element.
 */
function fieldContainer(element: Nullable<HTMLSelectElement>): Nullable<HTMLElement> {
  const container = element?.parentElement?.parentElement ?? null;
  if (container !== null && container.classList.contains('row')) {
    return container;
  }
  return null;
}

/**
 * Toggle visibility of the select element's container and disable the select element itself.
 *
 * @param element Select element.
 * @param action 'show' or 'hide'
 */
function toggleVisibility<E extends Nullable<HTMLSelectElement>>(
  element: E,
  action: 'show' | 'hide',
): void {
  // Find the select element's containing element.
  const parent = fieldContainer(element);
  if (element !== null && parent !== null) {
    // Toggle container visibility to visually remove it from the form.
    _toggleVisibility(parent, action);
    // Create a new event so that the APISelect instance properly handles the enable/disable
    // action.
    const event = new Event(`netbox.select.disabled.${element.name}`);
    switch (action) {
      case 'hide':
        // Disable the native select element and dispatch the event APISelect is listening for.
        element.disabled = true;
        element.dispatchEvent(event);
        break;
      case 'show':
        // Enable the native select element and dispatch the event APISelect is listening for.
        element.disabled = false;
        element.dispatchEvent(event);
    }
  }
}

/**
 * Toggle element visibility when the mode field does not have a value.
 */
function handleModeNone(): void {
  const elements = [
    getElement<HTMLSelectElement>('id_tagged_vlans'),
    getElement<HTMLSelectElement>('id_untagged_vlan'),
    getElement<HTMLSelectElement>('id_vlan_group'),
  ];

  if (all(elements)) {
    const [taggedVlans, untaggedVlan] = elements;
    resetSelect(untaggedVlan);
    resetSelect(taggedVlans);
    for (const element of elements) {
      toggleVisibility(element, 'hide');
    }
  }
}

/**
 * Toggle element visibility when the mode field's value is Access.
 */
function handleModeAccess(): void {
  const elements = [
    getElement<HTMLSelectElement>('id_tagged_vlans'),
    getElement<HTMLSelectElement>('id_untagged_vlan'),
    getElement<HTMLSelectElement>('id_vlan_group'),
  ];
  if (all(elements)) {
    const [taggedVlans, untaggedVlan, vlanGroup] = elements;
    resetSelect(taggedVlans);
    toggleVisibility(vlanGroup, 'show');
    toggleVisibility(untaggedVlan, 'show');
    toggleVisibility(taggedVlans, 'hide');
  }
}

/**
 * Toggle element visibility when the mode field's value is Tagged.
 */
function handleModeTagged(): void {
  const elements = [
    getElement<HTMLSelectElement>('id_tagged_vlans'),
    getElement<HTMLSelectElement>('id_untagged_vlan'),
    getElement<HTMLSelectElement>('id_vlan_group'),
  ];
  if (all(elements)) {
    const [taggedVlans, untaggedVlan, vlanGroup] = elements;
    toggleVisibility(taggedVlans, 'show');
    toggleVisibility(vlanGroup, 'show');
    toggleVisibility(untaggedVlan, 'show');
  }
}

/**
 * Toggle element visibility when the mode field's value is Tagged (All).
 */
function handleModeTaggedAll(): void {
  const elements = [
    getElement<HTMLSelectElement>('id_tagged_vlans'),
    getElement<HTMLSelectElement>('id_untagged_vlan'),
    getElement<HTMLSelectElement>('id_vlan_group'),
  ];
  if (all(elements)) {
    const [taggedVlans, untaggedVlan, vlanGroup] = elements;
    resetSelect(taggedVlans);
    toggleVisibility(vlanGroup, 'show');
    toggleVisibility(untaggedVlan, 'show');
    toggleVisibility(taggedVlans, 'hide');
  }
}

/**
 * Reset field visibility when the mode field's value changes.
 */
function handleModeChange(element: HTMLSelectElement): void {
  switch (element.value) {
    case 'access':
      handleModeAccess();
      break;
    case 'tagged':
      handleModeTagged();
      break;
    case 'tagged-all':
      handleModeTaggedAll();
      break;
    case '':
      handleModeNone();
      break;
  }
}

export function initVlanTags(): void {
  const element = getElement<HTMLSelectElement>('id_mode');
  if (element !== null) {
    element.addEventListener('change', () => handleModeChange(element));
    handleModeChange(element);
  }
}
