import { getElements } from '../util';
import { DynamicTomSelect } from './classes/dynamicTomSelect'


// Initialize <select> elements which are populated via a REST API call
export function initDynamicSelects(): void {

  for (const select of getElements<HTMLSelectElement>('select.api-select')) {
    new DynamicTomSelect(select, {
      plugins: ['clear_button'],
      valueField: 'id',
      labelField: 'display',
      searchField: [],
      copyClassesToDropdown: false,
      dropdownParent: 'body',
      controlInput: '<input>',
      preload: 'focus',
	});
  }

}
