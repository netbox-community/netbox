import { getElements, toggleVisibility } from '../util';

type ShowHideMap = {
  /**
   * Name of view to which this map should apply.
   *
   * @example vlangroup_edit
   */
  [view: string]: string;
};

type ShowHideLayout = {
  /**
   * Name of layout config
   *
   * @example vlangroup
   */
  [config: string]: {
    /**
     * Default layout.
     */
    default: { hide: string[]; show: string[] };
    /**
     * Field name to layout mapping.
     */
    [fieldName: string]: { hide: string[]; show: string[] };
  };
};

/**
 * Mapping of layout names to arrays of object types whose fields should be hidden or shown when
 * the scope type (key) is selected.
 *
 * For example, if `region` is the scope type, the fields with IDs listed in
 * showHideMap.region.hide should be hidden, and the fields with IDs listed in
 * showHideMap.region.show should be shown.
 */
const showHideLayout: ShowHideLayout = {
  vlangroup: {
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
  },
};

/**
 * Mapping of view names to layout configurations
 *
 * For example, if `vlangroup_add` is the view, use the layout configuration `vlangroup`.
 */
const showHideMap: ShowHideMap = {
  vlangroup_add: 'vlangroup',
  vlangroup_edit: 'vlangroup',
};

/**
 * Toggle visibility of a given element's parent.
 * @param query CSS Query.
 * @param action Show or Hide the Parent.
 */
function toggleParentVisibility(query: string, action: 'show' | 'hide') {
  for (const element of getElements(query)) {
    const parent = element.parentElement?.parentElement as Nullable<HTMLDivElement>;
    if (parent !== null) {
      if (action === 'show') {
        toggleVisibility(parent, 'show');
      } else {
        toggleVisibility(parent, 'hide');
      }
    }
  }
}

/**
 * Handle changes to the Scope Type field.
 */
function handleScopeChange<P extends keyof ShowHideMap>(view: P, element: HTMLSelectElement) {
  // Scope type's innerText looks something like `DCIM > region`.
  const scopeType = element.options[element.selectedIndex].innerText.toLowerCase();
  const layoutConfig = showHideMap[view];

  for (const [scope, fields] of Object.entries(showHideLayout[layoutConfig])) {
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
      for (const field of showHideLayout[layoutConfig].default.hide) {
        toggleParentVisibility(`#${field}`, 'hide');
      }
    }
  }
}

/**
 * Initialize scope type select event listeners.
 */
export function initScopeSelector(): void {
  for (const view of Object.keys(showHideMap)) {
    for (const element of getElements<HTMLSelectElement>(
      `html[data-netbox-url-name="${view}"] #id_scope_type`,
    )) {
      handleScopeChange(view, element);
      element.addEventListener('change', () => handleScopeChange(view, element));
    }
  }
}
