import { getElements } from '../util';
import { DynamicTomSelect } from './classes/dynamicTomSelect'

const VALUE_FIELD = 'id';
const LABEL_FIELD = 'display';
const MAX_OPTIONS = 100;


// Render the HTML for a dropdown option
function renderOption(data: any, escape: Function) {

  // If the option has a `_depth` property, indent its label
  if (typeof data._depth === 'number' && data._depth > 0) {
    return `<div>${'─'.repeat(data._depth)} ${escape(data[LABEL_FIELD])}</div>`;
  }

  return `<div>${escape(data[LABEL_FIELD])}</div>`;
}


// Initialize <select> elements which are populated via a REST API call
export function initDynamicSelects(): void {

  for (const select of getElements<HTMLSelectElement>('select.api-select')) {
    new DynamicTomSelect(select, {
      valueField: VALUE_FIELD,
      labelField: LABEL_FIELD,
      maxOptions: MAX_OPTIONS,

      // Provides the "clear" button on the widget
      plugins: ['clear_button'],

      // Disable local search (search is performed on the backend)
      searchField: [],

      // Reference the disabled-indicator attr on the <select> element to determine
      // the name of the attribute which indicates whether an option should be disabled
      disabledField: select.getAttribute('disabled-indicator') || undefined,

      // Load options from API immediately on focus
      preload: 'focus',

      // Define custom rendering functions
      render: {
        option: renderOption
      },

      // By default, load() will be called only if query.length > 0
      shouldLoad: function(): boolean { return true; }
	});
  }

}
