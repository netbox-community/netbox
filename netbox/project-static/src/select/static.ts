import type { TomOption } from 'tom-select/dist/esm/types/index.js';
import { escape_html } from 'tom-select/utils';
import { NetBoxTomSelect } from './classes/netboxTomSelect';
import { getPlugins } from './config';
import { getElements } from '../util';

// Prefix an option's image (if any) to its rendered label. When `placeholder` is set, an option without an image
// gets an empty placeholder in its place, keeping its label aligned with those of options that have images.
// TomSelect copies an <option>'s data-* attributes into the option data, so `data-image` and `data-description`
// attributes surface here as `data.image` and `data.description` without any DOM lookup.
function withImage(data: TomOption, escape: typeof escape_html, html: string, placeholder = false) {
  let img: string;
  if (data.image) {
    img = `<img src="${escape(data.image)}" class="choice-image" alt="" loading="lazy" />`;
  } else if (placeholder) {
    img = '<span class="choice-image"></span>';
  } else {
    return html;
  }
  return `<div class="d-flex align-items-center gap-2">${img}${html}</div>`;
}

// Render a static option, appending a description subtitle when one is present.
function renderOption(data: TomOption, escape: typeof escape_html, hasImages: boolean) {
  let html = `<div>${escape(data.text)}`;
  if (data.description) {
    html = `${html}<br /><small class="text-secondary">${escape(data.description)}</small>`;
  }
  return withImage(data, escape, `${html}</div>`, hasImages);
}

// Render a selected item. The description is omitted so it doesn't clutter the input.
function renderItem(data: TomOption, escape: typeof escape_html) {
  if (data.image) {
    return withImage(data, escape, `<span>${escape(data.text)}</span>`);
  }
  return `<div>${escape(data.text)}</div>`;
}

// Initialize <select> elements with statically-defined options
export function initStaticSelects(): void {
  for (const select of getElements<HTMLSelectElement>(
    'select:not(.tomselected):not(.no-ts):not([size]):not(.api-select):not(.color-select)',
  )) {
    const hasImages = select.querySelector('option[data-image]') !== null;
    new NetBoxTomSelect(select, {
      ...getPlugins(select),
      maxOptions: undefined,
      render: {
        option: (data: TomOption, escape: typeof escape_html) =>
          renderOption(data, escape, hasImages),
        item: renderItem,
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
