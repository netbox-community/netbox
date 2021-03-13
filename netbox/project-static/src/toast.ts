import { Toast } from 'bootstrap';

type ToastLevel = 'danger' | 'warning' | 'success' | 'info';

export function createToast(
  level: ToastLevel,
  title: string,
  message: string,
  extra?: string,
): Toast {
  let iconName = 'bi-exclamation-triangle-fill';
  switch (level) {
    case 'warning':
      iconName = 'bi-exclamation-triangle-fill';
    case 'success':
      iconName = 'bi-check-circle-fill';
    case 'info':
      iconName = 'bi-info-circle-fill';
    case 'danger':
      iconName = 'bi-exclamation-triangle-fill';
  }

  const container = document.createElement('div');
  container.setAttribute('class', 'toast-container position-fixed bottom-0 end-0 m-3');

  const main = document.createElement('div');
  main.setAttribute('class', `toast bg-${level}`);
  main.setAttribute('role', 'alert');
  main.setAttribute('aria-live', 'assertive');
  main.setAttribute('aria-atomic', 'true');

  const header = document.createElement('div');
  header.setAttribute('class', `toast-header bg-${level} text-body`);

  const icon = document.createElement('i');
  icon.setAttribute('class', `bi ${iconName}`);

  const titleElement = document.createElement('strong');
  titleElement.setAttribute('class', 'me-auto ms-1');
  titleElement.innerText = title;

  const button = document.createElement('button');
  button.setAttribute('type', 'button');
  button.setAttribute('class', 'btn-close');
  button.setAttribute('data-bs-dismiss', 'toast');
  button.setAttribute('aria-label', 'Close');

  const body = document.createElement('div');
  body.setAttribute('class', 'toast-body');

  header.appendChild(icon);
  header.appendChild(titleElement);

  if (typeof extra !== 'undefined') {
    const extraElement = document.createElement('small');
    extraElement.setAttribute('class', 'text-muted');
    header.appendChild(extraElement);
  }

  header.appendChild(button);

  body.innerText = message.trim();

  main.appendChild(header);
  main.appendChild(body);
  container.appendChild(main);
  document.body.appendChild(container);

  const toast = new Toast(main);
  return toast;
}

/**
 * Find any active messages from django.contrib.messages and show them in a toast.
 */
export function initMessageToasts(): void {
  const elements = document.querySelectorAll<HTMLDivElement>(
    'body > div#django-messages > div.django-message.toast',
  );
  for (const element of elements) {
    if (element !== null) {
      const toast = new Toast(element);
      toast.show();
    }
  }
}
