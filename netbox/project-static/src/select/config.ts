interface PluginConfig {
  [plugin: string]: object;
}

export function getPlugins(element: HTMLSelectElement): object {
  const plugins: PluginConfig = {};

  // Enable "clear all" button
  plugins.clear_button = {
    html: (data: Dict) =>
      `<i class="mdi mdi-close-circle ${data.className}" title="${data.title}"></i>`,
  };

  // Enable individual "remove" buttons for items on multi-select fields
  if (element.hasAttribute('multiple')) {
    plugins.remove_button = {
      title: 'Remove',
    };
  }

  return {
    plugins: plugins,
  };
}
