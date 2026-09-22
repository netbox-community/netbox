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
import { initSideNav } from './sidenav';
import { initDashboard } from './dashboard';
import { initRackElevation } from './racks';
import { initHtmx } from './htmx';
import { initSavedFilterSelect } from './forms/savedFiltersSelect';
import { initHotkeys } from './hotkeys';
import { initSSOForms } from './sso';
import { focusFirstPageFormError } from './forms/errors';

// Anything but post or dialog is a GET, and a control named "method" shadows the property.
const GET_FORM_SELECTOR = 'form:not([method="post" i]):not([method="dialog" i])';

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
    initSideNav,
    initDashboard,
    initRackElevation,
    initHtmx,
    initSavedFilterSelect,
    initHotkeys,
    initSSOForms,
  ]) {
    init();
  }
}

function initWindow(): void {
  for (const documentForm of document.querySelectorAll<HTMLFormElement>(GET_FORM_SELECTOR)) {
    documentForm.addEventListener('formdata', function (event: FormDataEvent) {
      const formData: FormData = event.formData;
      for (const [name, value] of Array.from(formData.entries())) {
        if (value === '') formData.delete(name);
      }
    });
  }

  // A rejected submission takes priority over the default landing focus.
  if (!focusFirstPageFormError()) {
    const contentContainer = document.querySelector<HTMLElement>('.content-container');
    if (contentContainer !== null) {
      // Focus the content container for accessible navigation.
      contentContainer.focus();
    }
  }
}

window.addEventListener('load', initWindow);

if (document.readyState !== 'loading') {
  initDocument();
} else {
  document.addEventListener('DOMContentLoaded', initDocument);
}
