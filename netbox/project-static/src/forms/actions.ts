import { getElements, findFirstAdjacent, isTruthy } from '../util';

/**
 * Handle bulk add/edit/rename form actions.
 *
 * @param event Click Event
 */
function handleFormActionClick(event: Event): void {
  event.preventDefault();
  const element = event.currentTarget as HTMLElement;
  if (element !== null) {
    const form = findFirstAdjacent<HTMLFormElement>(element, 'form');
    const href = element.getAttribute('href');
    if (form !== null && isTruthy(href)) {
      form.setAttribute('action', href);
      form.submit();
    }
  }
}

/**
 * Initialize bulk form action links.
 */
export function initFormActions(): void {
  for (const element of getElements<HTMLAnchorElement>('a.formaction')) {
    element.addEventListener('click', handleFormActionClick);
  }
}
