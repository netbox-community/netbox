import { createToast } from '../bs';
import { apiGetBase, getNetboxData, hasError, toggleLoader } from '../util';

/**
 * Initialize device config elements.
 */
function initConfig() {
  toggleLoader('show');
  const url = getNetboxData('data-object-url');

  if (url !== null) {
    apiGetBase<DeviceConfig>(url)
      .then(data => {
        if (hasError(data)) {
          createToast('danger', 'Error Fetching Device Config', data.error).show();
          return;
        } else {
          const configTypes = [
            'running',
            'startup',
            'candidate',
          ] as (keyof DeviceConfig['get_config'])[];

          for (const configType of configTypes) {
            const element = document.getElementById(`${configType}_config`);
            if (element !== null) {
              element.innerHTML = data.get_config[configType];
            }
          }
        }
      })
      .finally(() => {
        toggleLoader('hide');
      });
  }
}

if (document.readyState !== 'loading') {
  initConfig();
} else {
  document.addEventListener('DOMContentLoaded', initConfig);
}
