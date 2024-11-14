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
    const slugField = form.querySelector('#id_slug') as HTMLInputElement;
    if (slugField == null) continue;
    const sourceId = slugField.getAttribute('slug-source');
    const sourceField = form.querySelector(`#id_${sourceId}`) as HTMLInputElement;

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
