import { Collapse } from 'bootstrap';
import { StateManager } from './state';
import { getElements, isElement } from './util';

type NavState = { pinned: boolean };
type BodyAttr = 'show' | 'hide' | 'hidden' | 'pinned';
type Section = [HTMLAnchorElement, InstanceType<typeof Collapse>];

class SideNav {
  /**
   * Sidenav container element.
   */
  private base: HTMLDivElement;

  /**
   * SideNav internal state manager.
   */
  private state: StateManager<NavState>;

  /**
   * The currently active parent nav-link controlling a section.
   */
  private activeLink: Nullable<HTMLAnchorElement> = null;

  /**
   * All collapsible sections and their controlling nav-links.
   */
  private sections: Section[] = [];

  constructor(base: HTMLDivElement) {
    this.base = base;
    this.state = new StateManager<NavState>(
      { pinned: true },
      { persist: true, key: 'netbox-sidenav' },
    );

    this.init();
    this.initSectionLinks();
    this.initLinks();
  }

  /**
   * Determine if `document.body` has a sidenav attribute.
   */
  private bodyHas(attr: BodyAttr): boolean {
    return document.body.hasAttribute(`data-sidenav-${attr}`);
  }

  /**
   * Remove sidenav attributes from `document.body`.
   */
  private bodyRemove(...attrs: BodyAttr[]): void {
    for (const attr of attrs) {
      document.body.removeAttribute(`data-sidenav-${attr}`);
    }
  }

  /**
   * Add sidenav attributes to `document.body`.
   */
  private bodyAdd(...attrs: BodyAttr[]): void {
    for (const attr of attrs) {
      document.body.setAttribute(`data-sidenav-${attr}`, '');
    }
  }

  /**
   * Set initial values & add event listeners.
   */
  private init() {
    for (const toggler of this.base.querySelectorAll('.sidenav-toggle')) {
      toggler.addEventListener('click', event => this.onToggle(event));
    }

    for (const toggler of getElements<HTMLButtonElement>('.sidenav-toggle-mobile')) {
      toggler.addEventListener('click', event => this.onMobileToggle(event));
    }

    if (window.innerWidth > 1200) {
      if (this.state.get('pinned')) {
        this.pin();
      }

      if (!this.state.get('pinned')) {
        this.unpin();
      }
      window.addEventListener('resize', () => this.onResize());
    }

    if (window.innerWidth < 1200) {
      this.bodyRemove('hide');
      this.bodyAdd('hidden');
      window.addEventListener('resize', () => this.onResize());
    }

    this.base.addEventListener('mouseenter', () => this.onEnter());
    this.base.addEventListener('mouseleave', () => this.onLeave());
  }

  /**
   * If the sidenav is shown, expand active nav links. Otherwise, collapse them.
   */
  private initLinks(): void {
    for (const link of this.getActiveLinks()) {
      if (this.bodyHas('show')) {
        this.activateLink(link, 'expand');
      } else if (this.bodyHas('hidden')) {
        this.activateLink(link, 'collapse');
      }
    }
  }

  /**
   * Show the sidenav.
   */
  private show(): void {
    this.bodyAdd('show');
    this.bodyRemove('hidden', 'hide');
  }

  /**
   * Hide the sidenav and collapse all active nav sections.
   */
  private hide(): void {
    this.bodyAdd('hidden');
    this.bodyRemove('pinned', 'show');
    for (const collapse of this.base.querySelectorAll('.collapse')) {
      collapse.classList.remove('show');
    }
  }

  /**
   * Pin the sidenav.
   */
  private pin(): void {
    this.bodyAdd('show', 'pinned');
    this.bodyRemove('hidden');
    this.state.set('pinned', true);
  }

  /**
   * Unpin the sidenav.
   */
  private unpin(): void {
    this.bodyRemove('pinned', 'show');
    this.bodyAdd('hidden');
    for (const collapse of this.base.querySelectorAll('.collapse')) {
      collapse.classList.remove('show');
    }
    this.state.set('pinned', false);
  }

  /**
   * When a section's controlling nav-link is clicked, update this instance's `activeLink`
   * attribute and close all other sections.
   */
  private handleSectionClick(event: Event): void {
    event.preventDefault();
    const element = event.target as HTMLAnchorElement;
    this.activeLink = element;
    this.closeInactiveSections();
  }

  /**
   * Close all sections that are not associated with the currently active link (`activeLink`).
   */
  private closeInactiveSections(): void {
    for (const [link, collapse] of this.sections) {
      if (link !== this.activeLink) {
        link.classList.add('collapsed');
        link.setAttribute('aria-expanded', 'false');
        collapse.hide();
      }
    }
  }

  /**
   * Initialize `bootstrap.Collapse` instances on all section collapse elements and add event
   * listeners to the controlling nav-links.
   */
  private initSectionLinks(): void {
    for (const section of getElements<HTMLAnchorElement>(
      '.navbar-nav .nav-item .nav-link[data-bs-toggle]',
    )) {
      if (section.parentElement !== null) {
        const collapse = section.parentElement.querySelector<HTMLDivElement>('.collapse');
        if (collapse !== null) {
          const collapseInstance = new Collapse(collapse, {
            toggle: false, // Don't automatically open the collapse element on invocation.
          });
          this.sections.push([section, collapseInstance]);
          section.addEventListener('click', event => this.handleSectionClick(event));
        }
      }
    }
  }

  /**
   * Starting from the bottom-most active link in the element tree, work backwards to determine the
   * link's containing `.collapse` element and the `.collapse` element's containing `.nav-link`
   * element. Once found, expand (or collapse) the `.collapse` element and add (or remove) the
   * `.active` class to the the parent `.nav-link` element.
   *
   * @param link Active nav link
   * @param action Expand or Collapse
   */
  private activateLink(link: HTMLAnchorElement, action: 'expand' | 'collapse'): void {
    // Find the closest .collapse element, which should contain `link`.
    const collapse = link.closest('.collapse') as Nullable<HTMLDivElement>;
    if (isElement(collapse)) {
      // Find the closest `.nav-link`, which should be adjacent to the `.collapse` element.
      const groupLink = collapse.parentElement?.querySelector('.nav-link');
      if (isElement(groupLink)) {
        groupLink.classList.add('active');
        switch (action) {
          case 'expand':
            groupLink.setAttribute('aria-expanded', 'true');
            collapse.classList.add('show');
            link.classList.add('active');
            break;
          case 'collapse':
            groupLink.setAttribute('aria-expanded', 'false');
            collapse.classList.remove('show');
            link.classList.remove('active');
            break;
        }
      }
    }
  }

  /**
   * Find any nav links with `href` attributes matching the current path, to determine which nav
   * link should be considered active.
   */
  private *getActiveLinks(): Generator<HTMLAnchorElement> {
    for (const link of this.base.querySelectorAll<HTMLAnchorElement>(
      '.navbar-nav .nav .nav-item a.nav-link',
    )) {
      const href = new RegExp(link.href, 'gi');
      if (window.location.href.match(href)) {
        yield link;
      }
    }
  }

  /**
   * Show the sidenav and expand any active sections.
   */
  private onEnter(): void {
    if (!this.bodyHas('pinned')) {
      this.bodyRemove('hide', 'hidden');
      this.bodyAdd('show');
      for (const link of this.getActiveLinks()) {
        this.activateLink(link, 'expand');
      }
    }
  }

  /**
   * Hide the sidenav and collapse any active sections.
   */
  private onLeave(): void {
    if (!this.bodyHas('pinned')) {
      this.bodyRemove('show');
      this.bodyAdd('hide');
      for (const link of this.getActiveLinks()) {
        this.activateLink(link, 'collapse');
      }
      setTimeout(() => {
        this.bodyRemove('hide');
        this.bodyAdd('hidden');
      }, 300);
    }
  }

  /**
   * Close the (unpinned) sidenav when the window is resized.
   */
  private onResize(): void {
    if (this.bodyHas('show') && !this.bodyHas('pinned')) {
      this.bodyRemove('show');
      this.bodyAdd('hidden');
    }
  }

  /**
   * Pin & unpin the sidenav when the pin button is toggled.
   */
  private onToggle(event: Event): void {
    event.preventDefault();

    if (this.state.get('pinned')) {
      this.unpin();
    } else {
      this.pin();
    }
  }

  /**
   * Handle sidenav visibility state for small screens. On small screens, there is no pinned state,
   * only open/closed.
   */
  private onMobileToggle(event: Event): void {
    event.preventDefault();
    if (this.bodyHas('hidden')) {
      this.show();
    } else {
      this.hide();
    }
  }
}

export function initSideNav(): void {
  for (const sidenav of getElements<HTMLDivElement>('.sidenav')) {
    new SideNav(sidenav);
  }
}
