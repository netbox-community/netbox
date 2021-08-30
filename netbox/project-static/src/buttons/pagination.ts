import { getElements } from '../util';

function handlePerPageSelect(event: Event): void {
  const select = event.currentTarget as HTMLSelectElement;
  if (select.form !== null) {
    select.form.submit();
  }
}

export function initPerPage(): void {
  for (const element of getElements<HTMLSelectElement>('select.per-page')) {
    element.addEventListener('change', handlePerPageSelect);
  }
}
