import { Toast } from 'bootstrap';

/**
 * Find any active messages from django.contrib.messages and show them in a toast.
 */
export function initMessages(): void {
  const elements = document.querySelectorAll<HTMLDivElement>(
    'body > div#django-messages > div.toast',
  );
  for (const element of elements) {
    // Skip toasts already showing, and closed toasts restored from an htmx history snapshot
    const closed = element.classList.contains('fade') && !element.classList.contains('show');
    if (Toast.getInstance(element) || closed) continue;
    const toast = new Toast(element);
    toast.show();
    // Retry on the next swap if a show.bs.toast listener cancelled the show
    if (!toast.isShown()) toast.dispose();
  }
}
