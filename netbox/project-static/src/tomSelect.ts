import { getElements } from './util';
import { TomOption } from 'tom-select/src/types';
import TomSelect from 'tom-select';


class DynamicTomSelect extends TomSelect {

  // Override load() to automatically clear any cached options. (Only options included
  // in the API response should be present.)
  load(value: string) {
    this.clearOptions();
    super.load(value);
  }

}

// Initialize <select> elements with statically-defined options
function initStaticSelects(): void {

  for (const select of getElements<HTMLSelectElement>('select:not(.api-select):not(.color-select)')) {
    new TomSelect(select, {
      plugins: ['clear_button']
    });
  }

}

// Initialize <select> elements which are populated via a REST API call
function initDynamicSelects(): void {

  for (const select of getElements<HTMLSelectElement>('select.api-select')) {
    const api_url = select.getAttribute('data-url') as string;
    new DynamicTomSelect(select, {
      plugins: ['clear_button'],
      valueField: 'id',
      labelField: 'display',
      searchField: [],
      copyClassesToDropdown: false,
      dropdownParent: 'body',
      controlInput: '<input>',
      preload: 'focus',
      load: function(query: string, callback: Function) {
        let url = api_url + '?brief=True&q=' + encodeURIComponent(query);
        fetch(url)
            .then(response => response.json())
            .then(json => {
                callback(json.results);
            }).catch(()=>{
                callback();
            });
		},
	});
  }

}

// Initialize color selection fields
function initColorSelects(): void {

  for (const select of getElements<HTMLSelectElement>('select.color-select')) {
    new TomSelect(select, {
      render: {
        option: function(item: TomOption, escape: Function) {
          return `<div style="background-color: #${escape(item.value)}">${escape(item.text)}</div>`;
        }
      }
    });
  }

}

export function initSelects(): void {
  initStaticSelects();
  initDynamicSelects();
  initColorSelects();
}
