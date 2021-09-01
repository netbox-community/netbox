import { createToast } from '../bs';
import { apiGetBase, getNetboxData, hasError, toggleLoader } from '../util';

/**
 * Initialize device config elements.
 */
function initConfig(): void {
  toggleLoader('show');
  const url = getNetboxData('data-object-url');

  if (url !== null) {
    apiGetBase<DeviceConfig>(url)
      .then(data => {
        if (hasError(data)) {
          createToast('danger', 'Error Fetching Device Config', data.error).show();
          console.error(data.error);
          return;
        } else if (hasError<Required<DeviceConfig['get_config']>>(data.get_config)) {
          createToast('danger', 'Error Fetching Device Config', data.get_config.error).show();
          console.error(data.get_config.error);
          return;
        } else {
          const configTypes = ['running', 'startup', 'candidate'] as DeviceConfigType[];

          for (const configType of configTypes) {
            const element = document.getElementById(`${configType}_config`);
            if (element !== null) {
              const config = data.get_config[configType];
              if (typeof config === 'string') {
                // If the returned config is a string, set the element innerHTML as-is.
                element.innerHTML = config;
              } else {
                // If the returned config is an object (dict), convert it to JSON.
                element.innerHTML = JSON.stringify(data.get_config[configType], null, 2);
              }
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
