import { getElements } from './util';
import TomSelect from 'tom-select';

export function initTomSelect(): void {

  // Static selects
  for (const select of getElements<HTMLSelectElement>('select:not(.api-select)')) {
    new TomSelect(select, {});
  }

  // API selects
  for (const select of getElements<HTMLSelectElement>('.api-select')) {
    const api_url = select.getAttribute('data-url') as string;
    new TomSelect(select, {
      valueField: 'id',
      labelField: 'display',
      searchField: ['name'],
      copyClassesToDropdown: false,
      dropdownParent: 'body',
      controlInput: '<input>',
      preload: 'focus',
      load: function(query, callback) {
        var url = api_url + '?brief=True&q=' + encodeURIComponent(query);
        console.log(url);
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
