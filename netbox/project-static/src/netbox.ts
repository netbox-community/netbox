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
import { initSavedFilterSelect } from './forms/savedFiltersSelect';

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
    initSavedFilterSelect,
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
        for (const [name, value] of Array.from(formData.entries())) {
          if (value === '') formData.delete(name);
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
