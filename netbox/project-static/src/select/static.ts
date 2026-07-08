import { TomOption } from 'tom-select/src/types';
import { escape_html } from 'tom-select/src/utils';
import { NetBoxTomSelect } from './classes/netboxTomSelect';
import { getPlugins } from './config';
import { getElements } from '../util';

// Render a static option, appending a description subtitle when one is present. TomSelect copies an
// <option>'s data-* attributes into the option data, so a `data-description` attribute surfaces here as
// `data.description` without any DOM lookup.
function renderOption(data: TomOption, escape: typeof escape_html) {
  let html = `<div>${escape(data.text)}`;
  if (data.description) {
    html = `${html}<br /><small class="text-secondary">${escape(data.description)}</small>`;
  }
  return `${html}</div>`;
}

// Initialize <select> elements with statically-defined options
export function initStaticSelects(): void {
  for (const select of getElements<HTMLSelectElement>(
    'select:not(.tomselected):not(.no-ts):not([size]):not(.api-select):not(.color-select)',
  )) {
    new NetBoxTomSelect(select, {
      ...getPlugins(select),
      maxOptions: undefined,
      render: {
        // Only `option` (the dropdown list) renders the description; `item` (the compact selected-value display
        // shown inside the input) is intentionally left at the default so the subtitle doesn't clutter it.
        option: renderOption,
      },
    });
  }
}

// Initialize color selection fields
export function initColorSelects(): void {
  function renderColor(item: TomOption, escape: typeof escape_html) {
    return `<div><span class="dropdown-item-indicator color-label" style="background-color: #${escape(
      item.value,
    )}"></span> ${escape(item.text)}</div>`;
  }

  for (const select of getElements<HTMLSelectElement>('select.color-select:not(.tomselected)')) {
    new NetBoxTomSelect(select, {
      ...getPlugins(select),
      maxOptions: undefined,
      render: {
        option: renderColor,
        item: renderColor,
      },
    });
  }
}
