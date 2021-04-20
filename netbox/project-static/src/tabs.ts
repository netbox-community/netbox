import { Tab } from 'bootstrap';
import { getElements } from './util';

/**
 * Open the tab specified in the URL. For example, /dcim/device-types/1/#tab_frontports will
 * change the open tab to the Front Ports tab.
 */
export function initTabs() {
  const { hash } = location;
  if (hash && hash.match(/^\#tab_.+$/)) {
    // The tab element will have a data-bs-target attribute with a value of the object type for
    // the corresponding tab. Once we drop the `tab_` prefix, the hash will match the target
    // element's data-bs-target value. For example, `#tab_frontports` becomes `#frontports`.
    const target = hash.replace('tab_', '');
    for (const element of getElements(`ul.nav.nav-tabs .nav-link[data-bs-target="${target}"]`)) {
      // Instantiate a Bootstrap tab instance.
      // See https://getbootstrap.com/docs/5.0/components/navs-tabs/#javascript-behavior
      const tab = new Tab(element);
      // Show the tab.
      tab.show();
    }
  }
}
