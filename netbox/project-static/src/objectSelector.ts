import { getElements } from './util';

function handleSelection(link: HTMLAnchorElement): void {
  const selector_results = document.getElementById('selector_results');
  if (selector_results == null) {
    return
  }
  const target_id = selector_results.getAttribute('data-selector-target');
  if (target_id == null) {
    return
  }
  const target = document.getElementById(target_id);
  if (target == null) {
    return
  }

  const label = link.getAttribute('data-label');
  const value = link.getAttribute('data-value');

  //@ts-ignore
  target.slim.setData([
    {text: label, value: value}
  ]);
  const change = new Event('change');
  target.dispatchEvent(change);

}


export function initObjectSelector(): void {
  for (const element of getElements<HTMLAnchorElement>('#selector_results a')) {
    element.addEventListener('click', () => handleSelection(element));
  }
}
