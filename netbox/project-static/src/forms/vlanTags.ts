import { all, getElement, resetSelect, toggleVisibility } from '../util';

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
      toggleVisibility(fieldContainer(element), 'hide');
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
    toggleVisibility(fieldContainer(vlanGroup), 'show');
    toggleVisibility(fieldContainer(untaggedVlan), 'show');
    toggleVisibility(fieldContainer(taggedVlans), 'hide');
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
    toggleVisibility(fieldContainer(taggedVlans), 'show');
    toggleVisibility(fieldContainer(vlanGroup), 'show');
    toggleVisibility(fieldContainer(untaggedVlan), 'show');
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
    toggleVisibility(fieldContainer(vlanGroup), 'show');
    toggleVisibility(fieldContainer(untaggedVlan), 'show');
    toggleVisibility(fieldContainer(taggedVlans), 'hide');
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
