import { TomOption } from 'tom-select/src/types';
import TomSelect from 'tom-select';
import { escape_html } from 'tom-select/src/utils';
import { getElements } from '../util';

// Initialize <select> elements with statically-defined options
export function initStaticSelects(): void {
  for (const select of getElements<HTMLSelectElement>(
    'select:not(.api-select):not(.color-select)',
  )) {
    new TomSelect(select, {
      plugins: ['clear_button'],
    });
  }
}

// Initialize color selection fields
export function initColorSelects(): void {
  for (const select of getElements<HTMLSelectElement>('select.color-select')) {
    new TomSelect(select, {
      render: {
        option: function (item: TomOption, escape: typeof escape_html) {
          return `<div style="background-color: #${escape(item.value)}">${escape(item.text)}</div>`;
        },
      },
    });
  }
}
