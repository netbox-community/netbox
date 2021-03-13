import { Tooltip } from 'bootstrap';
import Masonry from 'masonry-layout';
import { initApiSelect, initStaticSelect, initColorSelect } from './select';
import { initDateSelector } from './dateSelector';
import { initMessageToasts } from './toast';
import { initSpeedSelector, initForms } from './forms';
import { initSearchBar } from './search';
import { getElements } from './util';

const INITIALIZERS = [
  initSearchBar,
  initMasonry,
  bindReslug,
  initApiSelect,
  initStaticSelect,
  initDateSelector,
  initSpeedSelector,
  initColorSelect,
] as (() => void)[];

/**
 * Enable any defined Bootstrap Tooltips.
 *
 * @see https://getbootstrap.com/docs/5.0/components/tooltips
 */
function initBootstrap(): void {
  if (document !== null) {
    for (const tooltip of getElements('[data-bs-toggle="tooltip"]')) {
      new Tooltip(tooltip, { container: 'body', boundary: 'window' });
    }
    initMessageToasts();
    initForms();
  }
}

/**
 * Initialize masonry-layout for homepage (or any other masonry layout cards).
 */
function initMasonry(): void {
  if (document !== null) {
    for (const grid of getElements('.masonry')) {
      new Masonry(grid, {
        itemSelector: '.masonry-item',
        percentPosition: true,
      });
    }
  }
}

/**
 * Create a slug from any input string.
 *
 * @param slug Original string.
 * @param chars Maximum number of characters.
 * @returns Slugified string.
 */
function slugify(slug: string, chars: number): string {
  return slug
    .replace(/[^\-\.\w\s]/g, '') // Remove unneeded chars
    .replace(/^[\s\.]+|[\s\.]+$/g, '') // Trim leading/trailing spaces
    .replace(/[\-\.\s]+/g, '-') // Convert spaces and decimals to hyphens
    .toLowerCase() // Convert to lowercase
    .substring(0, chars); // Trim to first chars chars
}

/**
 * If a slug field exists, add event listeners to handle automatically generating its value.
 */
function bindReslug(): void {
  const slugField = document.getElementById('id_slug') as HTMLInputElement;
  const slugButton = document.getElementById('reslug') as HTMLButtonElement;
  if (slugField === null || slugButton === null) {
    return;
  }
  const sourceId = slugField.getAttribute('slug-source');
  const sourceField = document.getElementById(`id_${sourceId}`) as HTMLInputElement;

  if (sourceField === null) {
    console.error('Unable to find field for slug field.');
    return;
  }

  const slugLengthAttr = slugField.getAttribute('maxlength');
  let slugLength = 50;

  if (slugLengthAttr) {
    slugLength = Number(slugLengthAttr);
  }
  sourceField.addEventListener('blur', () => {
    slugField.value = slugify(sourceField.value, slugLength);
  });
  slugButton.addEventListener('click', () => {
    slugField.value = slugify(sourceField.value, slugLength);
  });
}

if (document.readyState !== 'loading') {
  initBootstrap();
} else {
  document.addEventListener('DOMContentLoaded', initBootstrap);
}

for (const init of INITIALIZERS) {
  init();
}
