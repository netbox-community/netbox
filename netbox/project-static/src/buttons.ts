import { createToast } from './bs';
import { isTruthy, getElements, apiPatch, hasError, slugify } from './util';

/**
 * Add onClick callback for toggling rack elevation images.
 */
function initRackElevation() {
  for (const button of getElements('button.toggle-images')) {
    /**
     * Toggle the visibility of device images and update the toggle button style.
     */
    function handleClick(event: Event) {
      const target = event.target as HTMLButtonElement;
      const selected = target.getAttribute('selected');

      if (isTruthy(selected)) {
        target.innerHTML = `<i class="bi bi-file-image"></i> Show Images`;

        for (const elevation of getElements<HTMLObjectElement>('.rack_elevation')) {
          const images = elevation.contentDocument?.querySelectorAll('image.device-image') ?? [];
          for (const image of images) {
            if (!image.classList.contains('hidden')) {
              image && image.classList.add('hidden');
            }
          }
        }
        target.setAttribute('selected', '');
      } else {
        target.innerHTML = `<i class="bi bi-file-image"></i> Hide Images`;

        for (const elevation of getElements<HTMLObjectElement>('.rack_elevation')) {
          const images = elevation.contentDocument?.querySelectorAll('image.device-image') ?? [];
          for (const image of images) {
            image && image.classList.remove('hidden');
          }
        }

        target.setAttribute('selected', 'selected');
      }
    }
    button.addEventListener('click', handleClick);
  }
}

/**
 * When the toggle button is clicked, swap the connection status via the API and toggle CSS
 * classes to reflect the connection status.
 *
 * @param element Connection Toggle Button Element
 */
function toggleConnection(element: HTMLButtonElement) {
  const id = element.getAttribute('data');
  const connected = element.classList.contains('connected');
  const status = connected ? 'planned' : 'connected';

  if (isTruthy(id)) {
    apiPatch(`/api/dcim/cables/${id}/`, { status }).then(res => {
      if (hasError(res)) {
        // If the API responds with an error, show it to the user.
        createToast('danger', 'Error', res.error).show();
        return;
      } else {
        // Get the button's row to change its styles.
        const row = element.parentElement?.parentElement as HTMLTableRowElement;
        // Get the button's icon to change its CSS class.
        const icon = element.querySelector('i.mdi, span.mdi') as HTMLSpanElement;
        if (connected) {
          row.classList.remove('success');
          row.classList.add('info');
          element.classList.remove('connected', 'btn-warning');
          element.title = 'Mark Installed';
          icon.classList.remove('mdi-lan-disconnect');
          icon.classList.add('mdi-lan-connect');
        } else {
          row.classList.remove('info');
          row.classList.add('success');
          element.classList.remove('btn-success');
          element.classList.add('connected', 'btn-warning');
          element.title = 'Mark Installed';
          icon.classList.remove('mdi-lan-connect');
          icon.classList.add('mdi-lan-disconnect');
        }
      }
    });
  }
}

function initConnectionToggle() {
  for (const element of getElements<HTMLButtonElement>('button.cable-toggle')) {
    element.addEventListener('click', () => toggleConnection(element));
  }
}

/**
 * If a slug field exists, add event listeners to handle automatically generating its value.
 */
function initReslug(): void {
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

export function initButtons() {
  for (const func of [initRackElevation, initConnectionToggle, initReslug]) {
    func();
  }
}
