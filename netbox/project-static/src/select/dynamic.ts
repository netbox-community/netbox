import { TomOption } from 'tom-select/src/types';
import { escape_html } from 'tom-select/src/utils';
import { DynamicTomSelect } from './classes/dynamicTomSelect';
import { config } from './config';
import { getElements } from '../util';

const VALUE_FIELD = 'id';
const LABEL_FIELD = 'display';
const MAX_OPTIONS = 100;

// Render the HTML for a dropdown option
function renderOption(data: TomOption, escape: typeof escape_html) {
  let html = '<div>';

  // If the option has a `depth` property, indent its label
  if (typeof data.depth === 'number' && data.depth > 0) {
    html = `${html}${'─'.repeat(data.depth)} `;
  }

  html = `${html}${escape(data[LABEL_FIELD])}`;
  if (data['parent']) {
    html = `${html} <span class="text-secondary">${escape(data['parent'])}</span>`;
  }
  if (data['count']) {
    html = `${html} <span class="badge">${escape(data['count'])}</span>`;
  }
  if (data['description']) {
    html = `${html}<br /><small class="text-secondary">${escape(data['description'])}</small>`;
  }
  html = `${html}</div>`;

  return html;
}

// Render the HTML for a selected item
function renderItem(data: TomOption, escape: typeof escape_html) {
  if (data['parent']) {
    return `<div>${escape(data['parent'])} > ${escape(data[LABEL_FIELD])}</div>`;
  }
  return `<div>${escape(data[LABEL_FIELD])}<div>`;
}

// Initialize <select> elements which are populated via a REST API call
export function initDynamicSelects(): void {
  for (const select of getElements<HTMLSelectElement>('select.api-select:not(.tomselected)')) {
    new DynamicTomSelect(select, {
      ...config,
      valueField: VALUE_FIELD,
      labelField: LABEL_FIELD,
      maxOptions: MAX_OPTIONS,

      // Disable local search (search is performed on the backend)
      searchField: [],

      // Load options from API immediately on focus
      preload: 'focus',

      // Define custom rendering functions
      render: {
        option: renderOption,
        item: renderItem,
      },

      // By default, load() will be called only if query.length > 0
      shouldLoad: function (): boolean {
        return true;
      },
    });
  }
}
