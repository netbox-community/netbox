import { getElements, scrollTo, findFirstAdjacent, isTruthy } from './util';

type ShowHideMap = {
  default: { hide: string[]; show: string[] };
  [k: string]: { hide: string[]; show: string[] };
};

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
function initFormActions() {
  for (const element of getElements<HTMLAnchorElement>('a.formaction')) {
    element.addEventListener('click', handleFormActionClick);
  }
}

/**
 * Get form data from a form element and transform it into a body usable by fetch.
 *
 * @param element Form element
 * @returns Fetch body
 */
export function getFormData(element: HTMLFormElement): URLSearchParams {
  const formData = new FormData(element);
  const body = new URLSearchParams();
  for (const [k, v] of formData) {
    body.append(k, v as string);
  }
  return body;
}

/**
 * Set the value of the number input field based on the selection of the dropdown.
 */
function initSpeedSelector(): void {
  for (const element of getElements<HTMLAnchorElement>('a.set_speed')) {
    if (element !== null) {
      function handleClick(event: Event) {
        // Don't reload the page (due to href="#").
        event.preventDefault();
        // Get the value of the `data` attribute on the dropdown option.
        const value = element.getAttribute('data');
        // Find the input element referenced by the dropdown element.
        const input = document.getElementById(element.target) as Nullable<HTMLInputElement>;
        if (input !== null && value !== null) {
          // Set the value of the input field to the `data` attribute's value.
          input.value = value;
        }
      }
      element.addEventListener('click', handleClick);
    }
  }
}

function handleFormSubmit(event: Event, form: HTMLFormElement): void {
  // Track the names of each invalid field.
  const invalids = new Set<string>();

  for (const element of form.querySelectorAll<FormControls>('*[name]')) {
    if (!element.validity.valid) {
      invalids.add(element.name);

      // If the field is invalid, but contains the .is-valid class, remove it.
      if (element.classList.contains('is-valid')) {
        element.classList.remove('is-valid');
      }
      // If the field is invalid, but doesn't contain the .is-invalid class, add it.
      if (!element.classList.contains('is-invalid')) {
        element.classList.add('is-invalid');
      }
    } else {
      // If the field is valid, but contains the .is-invalid class, remove it.
      if (element.classList.contains('is-invalid')) {
        element.classList.remove('is-invalid');
      }
      // If the field is valid, but doesn't contain the .is-valid class, add it.
      if (!element.classList.contains('is-valid')) {
        element.classList.add('is-valid');
      }
    }
  }

  if (invalids.size !== 0) {
    // If there are invalid fields, pick the first field and scroll to it.
    const firstInvalid = form.elements.namedItem(Array.from(invalids)[0]) as Element;
    scrollTo(firstInvalid);

    // If the form has invalid fields, don't submit it.
    event.preventDefault();
  }
}

/**
 * Attach an event listener to each form's submitter (button[type=submit]). When called, the
 * callback checks the validity of each form field and adds the appropriate Bootstrap CSS class
 * based on the field's validity.
 */
function initFormElements() {
  for (const form of getElements('form')) {
    // Find each of the form's submitters. Most object edit forms have a "Create" and
    // a "Create & Add", so we need to add a listener to both.
    const submitters = form.querySelectorAll<HTMLButtonElement>('button[type=submit]');

    for (const submitter of submitters) {
      // Add the event listener to each submitter.
      submitter.addEventListener('click', event => handleFormSubmit(event, form));
    }
  }
}

/**
 * Move selected options of a select element up in order.
 *
 * Adapted from:
 * @see https://www.tomred.net/css-html-js/reorder-option-elements-of-an-html-select.html
 * @param element Select Element
 */
function moveOptionUp(element: HTMLSelectElement): void {
  const options = Array.from(element.options);
  for (let i = 1; i < options.length; i++) {
    const option = options[i];
    if (option.selected) {
      element.removeChild(option);
      element.insertBefore(option, element.options[i - 1]);
    }
  }
}

/**
 * Move selected options of a select element down in order.
 *
 * Adapted from:
 * @see https://www.tomred.net/css-html-js/reorder-option-elements-of-an-html-select.html
 * @param element Select Element
 */
function moveOptionDown(element: HTMLSelectElement): void {
  const options = Array.from(element.options);
  for (let i = options.length - 2; i >= 0; i--) {
    let option = options[i];
    if (option.selected) {
      let next = element.options[i + 1];
      option = element.removeChild(option);
      next = element.replaceChild(option, next);
      element.insertBefore(next, option);
    }
  }
}

/**
 * Initialize move up/down buttons.
 */
function initMoveButtons() {
  for (const button of getElements<HTMLButtonElement>('#move-option-up')) {
    const target = button.getAttribute('data-target');
    if (target !== null) {
      for (const select of getElements<HTMLSelectElement>(`#${target}`)) {
        button.addEventListener('click', () => moveOptionUp(select));
      }
    }
  }
  for (const button of getElements<HTMLButtonElement>('#move-option-down')) {
    const target = button.getAttribute('data-target');
    if (target !== null) {
      for (const select of getElements<HTMLSelectElement>(`#${target}`)) {
        button.addEventListener('click', () => moveOptionDown(select));
      }
    }
  }
}

/**
 * Mapping of scope names to arrays of object types whose fields should be hidden or shown when
 * the scope type (key) is selected.
 *
 * For example, if `region` is the scope type, the fields with IDs listed in
 * showHideMap.region.hide should be hidden, and the fields with IDs listed in
 * showHideMap.region.show should be shown.
 */
const showHideMap: ShowHideMap = {
  region: {
    hide: ['id_sitegroup', 'id_site', 'id_location', 'id_rack', 'id_clustergroup', 'id_cluster'],
    show: ['id_region'],
  },
  'site group': {
    hide: ['id_region', 'id_site', 'id_location', 'id_rack', 'id_clustergroup', 'id_cluster'],
    show: ['id_sitegroup'],
  },
  site: {
    hide: ['id_location', 'id_rack', 'id_clustergroup', 'id_cluster'],
    show: ['id_region', 'id_sitegroup', 'id_site'],
  },
  location: {
    hide: ['id_rack', 'id_clustergroup', 'id_cluster'],
    show: ['id_region', 'id_sitegroup', 'id_site', 'id_location'],
  },
  rack: {
    hide: ['id_clustergroup', 'id_cluster'],
    show: ['id_region', 'id_sitegroup', 'id_site', 'id_location', 'id_rack'],
  },
  'cluster group': {
    hide: ['id_region', 'id_sitegroup', 'id_site', 'id_location', 'id_rack', 'id_cluster'],
    show: ['id_clustergroup'],
  },
  cluster: {
    hide: ['id_region', 'id_sitegroup', 'id_site', 'id_location', 'id_rack'],
    show: ['id_clustergroup', 'id_cluster'],
  },
  default: {
    hide: [
      'id_region',
      'id_sitegroup',
      'id_site',
      'id_location',
      'id_rack',
      'id_clustergroup',
      'id_cluster',
    ],
    show: [],
  },
};

/**
 * Toggle visibility of a given element's parent.
 * @param query CSS Query.
 * @param action Show or Hide the Parent.
 */
function toggleParentVisibility(query: string, action: 'show' | 'hide') {
  for (const element of getElements(query)) {
    if (action === 'show') {
      element.parentElement?.classList.remove('d-none', 'invisible');
    } else {
      element.parentElement?.classList.add('d-none', 'invisible');
    }
  }
}

/**
 * Handle changes to the Scope Type field.
 */
function handleScopeChange(event: Event) {
  const element = event.currentTarget as HTMLSelectElement;
  // Scope type's innerText looks something like `DCIM > region`.
  const scopeType = element.options[element.selectedIndex].innerText.toLowerCase();

  for (const [scope, fields] of Object.entries(showHideMap)) {
    // If the scope type ends with the specified scope, toggle its field visibility according to
    // the show/hide values.
    if (scopeType.endsWith(scope)) {
      for (const field of fields.hide) {
        toggleParentVisibility(`#${field}`, 'hide');
      }
      for (const field of fields.show) {
        toggleParentVisibility(`#${field}`, 'show');
      }
      // Stop on first match.
      break;
    } else {
      // Otherwise, hide all fields.
      for (const field of showHideMap.default.hide) {
        toggleParentVisibility(`#${field}`, 'hide');
      }
    }
  }
}

/**
 * Initialize scope type select event listeners.
 */
function initScopeSelector() {
  for (const element of getElements<HTMLSelectElement>('#id_scope_type')) {
    element.addEventListener('change', handleScopeChange);
  }
}

export function initForms(): void {
  for (const func of [
    initFormElements,
    initFormActions,
    initMoveButtons,
    initSpeedSelector,
    initScopeSelector,
  ]) {
    func();
  }
}
