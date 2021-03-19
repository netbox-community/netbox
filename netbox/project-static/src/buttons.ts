import { isTruthy, getElements } from './util';

/**
 * Add onClick callback for toggling rack elevation images.
 */
export function initRackElevation() {
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
