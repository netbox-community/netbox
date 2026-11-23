import { Toast } from 'bootstrap';

/**
 * Find any active messages from django.contrib.messages and show them in a toast.
 */
export function initMessages(): void {
  const elements = document.querySelectorAll<HTMLDivElement>(
    'body > div#django-messages > div.toast',
  );
  for (const element of elements) {
    // Show each toast only once; this runs after every htmx swap, and a closed toast stays in the DOM
    if (element.dataset.toastShown === 'true') continue;
    element.dataset.toastShown = 'true';
    new Toast(element).show();
  }
}
