import { getElements } from '../util';

type ShowHideMap = {
  default: { hide: string[]; show: string[] };
  [k: string]: { hide: string[]; show: string[] };
};

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
export function initScopeSelector(): void {
  for (const element of getElements<HTMLSelectElement>('#id_scope_type')) {
    element.addEventListener('change', handleScopeChange);
  }
}
