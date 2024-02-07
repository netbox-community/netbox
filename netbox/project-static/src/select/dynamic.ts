import { getElements } from '../util';
import { DynamicTomSelect } from './classes/dynamicTomSelect'

const VALUE_FIELD = 'id';
const LABEL_FIELD = 'display';


// Render the HTML for a dropdown option
function renderOption(data: any, escape: Function) {
  // If the object has a `_depth` property, indent its display text
  if (typeof data._depth === 'number' && data._depth > 0) {
    return `<div>${'─'.repeat(data._depth)} ${escape(data[LABEL_FIELD])}</div>`;
  }
  return `<div>${escape(data[LABEL_FIELD])}</div>`;
}


// Initialize <select> elements which are populated via a REST API call
export function initDynamicSelects(): void {

  for (const select of getElements<HTMLSelectElement>('select.api-select')) {
    new DynamicTomSelect(select, {
      plugins: ['clear_button'],
      valueField: VALUE_FIELD,
      labelField: LABEL_FIELD,
      searchField: [],
      disabledField: select.getAttribute('disabled-indicator') || undefined,
      copyClassesToDropdown: false,
      dropdownParent: 'body',
      controlInput: '<input>',
      preload: 'focus',
      maxOptions: 100,
      render: {
        option: renderOption
      }
	});
  }

}
