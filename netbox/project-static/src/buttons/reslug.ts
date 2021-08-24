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
 * If a slug field exists, add event listeners to handle automatically generating its value.
 */
export function initReslug(): void {
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
