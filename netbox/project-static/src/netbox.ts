import { initForms } from './forms';
import { initBootstrap } from './bs';
import { initSearch } from './search';
import { initSelect } from './select';
import { initButtons } from './buttons';
import { initColorMode } from './colorMode';
import { initMessages } from './messages';
import { initClipboard } from './clipboard';
import { initDateSelector } from './dateSelector';
import { initTableConfig } from './tableConfig';
import { initInterfaceTable } from './tables';
import { initSideNav } from './sidenav';
import { initRackElevation } from './racks';
import { initLinks } from './links';
import { initHtmx } from './htmx';

function initDocument(): void {
  for (const init of [
    initBootstrap,
    initColorMode,
    initMessages,
    initForms,
    initSearch,
    initSelect,
    initDateSelector,
    initButtons,
    initClipboard,
    initTableConfig,
    initInterfaceTable,
    initSideNav,
    initRackElevation,
    initLinks,
    initHtmx,
  ]) {
    init();
  }
}

function initWindow(): void {

  const documentForms = document.forms
  for (var documentForm of documentForms) {
    if (documentForm.method.toUpperCase() == 'GET') {
      // @ts-ignore: Our version of typescript seems to be too old for FormDataEvent
      documentForm.addEventListener('formdata', function(event: FormDataEvent) {
      let formData: FormData = event.formData;
      for (let [name, value] of Array.from(formData.entries())) {
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
