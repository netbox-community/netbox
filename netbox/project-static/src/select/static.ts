import SlimSelect from 'slim-select';

export function initStaticSelect() {
  const elements = document.querySelectorAll(
    '.netbox-select2-static',
  ) as NodeListOf<HTMLSelectElement>;

  for (const select of elements) {
    if (select !== null) {
      const label = document.querySelector(`label[for=${select.id}]`) as HTMLLabelElement;
      let placeholder;
      if (label !== null) {
        placeholder = `Select ${label.innerText.trim()}`;
      }
      new SlimSelect({
        select,
        allowDeselect: true,
        deselectLabel: `<i class="bi bi-x-circle"></i>`,
        placeholder,
      });
    }
  }
}
