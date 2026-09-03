import { StateManager } from './state';
import { getElements, isElement } from './util';

type NavState = { pinned: boolean };
type BodyAttr = 'show' | 'hide' | 'hidden' | 'pinned';

// Keep in sync with Bootstrap's `lg` breakpoint and `navbar-expand-lg` in base/layout.html.
const SIDENAV_DESKTOP_MEDIA = '(min-width: 992px)';

// Session-scoped, unlike the localStorage `netbox-sidenav` pin state.
const SCROLL_STATE_KEY = 'netbox-sidenav-scroll';

class SideNav {
  /**
   * Sidenav container element.
   */
  private base: HTMLElement;

  /**
   * SideNav internal state manager.
   */
  private state: StateManager<NavState>;

  /**
   * First nav item matching the current page, cached at construction.
   */
  private activePageLink: Nullable<HTMLDivElement> = null;

  constructor(base: HTMLElement) {
    this.base = base;
    this.state = new StateManager<NavState>(
      { pinned: true },
      { persist: true, key: 'netbox-sidenav' },
    );

    this.init();
    this.initLinks();
    this.initScrollPosition();
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

    const desktopMedia = window.matchMedia(SIDENAV_DESKTOP_MEDIA);
    this.setResponsiveState(desktopMedia.matches);
    desktopMedia.addEventListener('change', event => {
      this.setResponsiveState(event.matches);
      this.initLinks();
    });

    window.addEventListener('resize', () => this.onResize());

    this.base.addEventListener('mouseenter', () => this.onEnter());
    this.base.addEventListener('mouseleave', () => this.onLeave());
  }

  /**
   * Apply the appropriate sidenav state for the current responsive layout.
   */
  private setResponsiveState(isDesktop: boolean): void {
    this.bodyRemove('hide');

    if (isDesktop && this.state.get('pinned')) {
      this.bodyRemove('hidden');
      this.bodyAdd('show', 'pinned');
    } else {
      this.bodyRemove('show', 'pinned');
      this.bodyAdd('hidden');
    }
  }

  /**
   * If the sidenav is shown, expand active nav links. Otherwise, collapse them.
   */
  private initLinks(): void {
    for (const link of this.getActiveLinks()) {
      this.activePageLink ??= link;

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
   * Hide the sidenav and close any nested collapse elements.
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
   * Expand or collapse the `.dropdown-menu` containing an active link, and toggle the `active`
   * class on the link and on its containing `.nav-item`.
   *
   * @param link Active nav link
   * @param action Expand or Collapse
   */
  private activateLink(link: HTMLDivElement, action: 'expand' | 'collapse'): void {
    // Find the closest .dropdown-menu element, which should contain `link`.
    const dropdownMenu = link.closest('.dropdown-menu') as Nullable<HTMLDivElement>;
    if (isElement(dropdownMenu)) {
      // Find the closest `.nav-link`, which should be adjacent to the `.dropdown-menu` element.
      const groupItem = dropdownMenu.parentElement;
      const groupLink = dropdownMenu.parentElement?.querySelector('.nav-link');
      if (isElement(groupLink) && isElement(groupItem)) {
        switch (action) {
          case 'expand':
            groupLink.setAttribute('aria-expanded', 'true');
            groupLink.classList.add('show');
            groupItem.classList.add('active');
            dropdownMenu.classList.add('show');
            link.classList.add('active');
            break;
          case 'collapse':
            groupLink.setAttribute('aria-expanded', 'false');
            groupLink.classList.remove('show');
            groupItem.classList.remove('active');
            dropdownMenu.classList.remove('show');
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
  private *getActiveLinks(): Generator<HTMLDivElement> {
    for (const menuitem of this.base.querySelectorAll<HTMLDivElement>(
      'ul.navbar-nav .nav-item .dropdown-item',
    )) {
      const link = menuitem.querySelector<HTMLAnchorElement>('a');
      if (link) {
        const href = new RegExp(link.href, 'gi');
        if (window.location.href.match(href)) {
          yield menuitem;
        }
      }
    }
  }

  /**
   * Whether the aside currently overflows, as opposed to whether the layout lets it scroll at all.
   */
  private isScrollable(): boolean {
    return this.base.scrollHeight > this.base.clientHeight;
  }

  /**
   * Restore the offset saved for this browser tab, reveal the active item when it falls outside
   * the sidebar viewport, and save the offset again on the way out. One offset per tab, so a
   * shorter menu can clamp a deeper value.
   */
  private initScrollPosition(): void {
    const initiallyScrollable = this.isScrollable();
    const storedScrollTop = sessionStorage.getItem(SCROLL_STATE_KEY);

    // Leave a missing offset alone so the browser's own restoration survives.
    if (storedScrollTop !== null) {
      this.base.scrollTop = Number(storedScrollTop);
    }

    // Reveal only in the fixed desktop layout. In the mobile flow layout, scrollIntoView would scroll the page.
    if (window.matchMedia(SIDENAV_DESKTOP_MEDIA).matches) {
      const menu = this.activePageLink?.closest<HTMLElement>('.nav-item.dropdown');
      // A closed dropdown has no box to measure, so reveal its heading instead.
      const target =
        menu && !menu.querySelector('.dropdown-menu.show') ? menu : this.activePageLink;

      target?.scrollIntoView({ block: 'nearest' });
    }

    window.addEventListener('pagehide', () => {
      // Zero counts only from a sidebar that was already scrollable at load, not one that grew on hover.
      if (this.isScrollable() && (initiallyScrollable || this.base.scrollTop > 0)) {
        sessionStorage.setItem(SCROLL_STATE_KEY, String(this.base.scrollTop));
      }
    });
  }

  /**
   * Show the sidenav and expand any active menu groups.
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
   * Hide the sidenav and collapse any active menu groups.
   */
  private onLeave(): void {
    if (!this.bodyHas('pinned')) {
      this.bodyRemove('show');
      this.bodyAdd('hide');
      for (const link of this.getActiveLinks()) {
        this.activateLink(link, 'collapse');
      }
      this.bodyRemove('hide');
      this.bodyAdd('hidden');
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
  for (const sidenav of getElements<HTMLElement>('.navbar-vertical')) {
    new SideNav(sidenav);
  }
}
