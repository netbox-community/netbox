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
import { cleanGetUrl } from './util';

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
      documentForm.addEventListener('submit', cleanGetUrl)
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
