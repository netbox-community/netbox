import { getElements } from '../util';

/**
 * Create a slug from any input string.
 *
 * @param slug Original string.
 * @param chars Maximum number of characters.
 * @returns Slugified string.
 */
function slugify(slug: string, chars: number): string {
  return slug
    .replace(/[^\-.\w\s]/g, '') // Remove unneeded chars
    .replace(/^[\s.]+|[\s.]+$/g, '') // Trim leading/trailing spaces
    .replace(/[-.\s]+/g, '-') // Convert spaces and decimals to hyphens
    .toLowerCase() // Convert to lowercase
    .substring(0, chars); // Trim to first chars chars
}

/**
 * For any slug fields, add event listeners to handle automatically generating slug values.
 */
export function initReslug(): void {
  for (const slugButton of getElements<HTMLButtonElement>('button#reslug')) {
    const form = slugButton.form;
    if (form == null) continue;

    // Try without prefix first, fallback to quickadd prefix for quick-add modals
    const slugField = (form.querySelector('#id_slug') ??
      form.querySelector('#id_quickadd-slug')) as HTMLInputElement;
    if (slugField == null) continue;

    const sourceId = slugField.getAttribute('slug-source');

    // Try both patterns for source field as well
    const sourceField = (form.querySelector(`#id_${sourceId}`) ??
      form.querySelector(`#id_quickadd-${sourceId}`)) as HTMLInputElement;

    const slugLengthAttr = slugField.getAttribute('maxlength');
    let slugLength = 50;

    if (slugLengthAttr) {
      slugLength = Number(slugLengthAttr);
    }
    sourceField.addEventListener('blur', () => {
      if (!slugField.value) {
        slugField.value = slugify(sourceField.value, slugLength);
      }
    });
    slugButton.addEventListener('click', () => {
      slugField.value = slugify(sourceField.value, slugLength);
    });
  }
}
