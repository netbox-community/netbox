import { getElement, getElements } from './util';

const breakpoints = {
  sm: 540,
  md: 720,
  lg: 960,
  xl: 1140,
};

function toggleBodyPosition(position: HTMLBodyElement['style']['position']): void {
  for (const element of getElements('body')) {
    element.style.position = position;
  }
}

export function initSideNav() {
  const element = getElement<HTMLAnchorElement>('sidebarMenu');
  if (element !== null && document.body.clientWidth < breakpoints.lg) {
    element.addEventListener('shown.bs.collapse', () => toggleBodyPosition('fixed'));
    element.addEventListener('hidden.bs.collapse', () => toggleBodyPosition('relative'));
  }
}
