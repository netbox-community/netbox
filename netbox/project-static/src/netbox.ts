import { initForms } from './forms';
import { initBootstrap } from './bs';
import { initQuickSearch } from './search';
import { initSelects } from './select';
import { initButtons } from './buttons';
import { initColorMode } from './colorMode';
import { initMessages } from './messages';
import { initClipboard } from './clipboard';
import { initDateSelector } from './dateSelector';
import { initTableConfig } from './tableConfig';
import { initInterfaceTable } from './tables';
import { initSideNav } from './sidenav';
import { initDashboard } from './dashboard';
import { initRackElevation } from './racks';
import { initHtmx } from './htmx';

function initDocument(): void {
  for (const init of [
    initBootstrap,
    initColorMode,
    initMessages,
    initForms,
    initQuickSearch,
    initSelects,
    initDateSelector,
    initButtons,
    initClipboard,
    initTableConfig,
    initInterfaceTable,
    initSideNav,
    initDashboard,
    initRackElevation,
    initHtmx,
  ]) {
    init();
  }
}

function initWindow(): void {
  const documentForms = document.forms;
  for (const documentForm of documentForms) {
    if (documentForm.method.toUpperCase() == 'GET') {
      documentForm.addEventListener('formdata', function (event: FormDataEvent) {
        const formData: FormData = event.formData;
        // formData may have multiple values associated with a given key
        // (see netbox/templates/django/forms/widgets/checkbox.html).
	for (const name of Array.from(new Set(formData.keys()))) {
	  const values = formData.getAll(name);
	  formData.delete(name);
	  values.forEach(value => {
	    if (value !== '') formData.append(name, value)
	  });
	}
      });
    }
  }

  const contentContainer = document.querySelector<HTMLElement>('.content-container');
  if (contentContainer !== null) {
    // Focus the content container for accessible navigation.
    contentContainer.focus();
  }
}

window.addEventListener('load', initWindow);

if (document.readyState !== 'loading') {
  initDocument();
} else {
  document.addEventListener('DOMContentLoaded', initDocument);
}
