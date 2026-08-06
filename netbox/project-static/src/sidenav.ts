import { Collapse } from 'bootstrap';
import { StateManager } from './state';
import { getElements, isElement } from './util';

type NavState = { pinned: boolean };
type BodyAttr = 'show' | 'hide' | 'hidden' | 'pinned';
type Section = [HTMLAnchorElement, InstanceType<typeof Collapse>];

const SCROLL_PADDING = 8;
const SCROLL_STATE_KEY = 'netbox-sidenav-scroll';
// Keep in sync with media-breakpoint-up(lg) in styles/transitional/_navigation.scss.
// The separate 1200px threshold in init() controls whether active dropdowns start expanded.
const SIDENAV_SCROLL_MEDIA = '(min-width: 992px)';

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
   * First nav item matching the current page, cached at construction.
   */
  private activePageLink: Nullable<HTMLDivElement> = null;

  /**
   * All collapsible sections and their controlling nav-links.
   */
  private sections: Section[] = [];

  /**
   * Last sidebar offset recorded while the sidebar was visible, scoped to this browser tab.
   */
  private savedScrollTop: Nullable<number> = null;

  /**
   * Whether the saved offset has been applied since the sidebar last became usable.
   */
  private scrollPositionRestored = false;

  /**
   * Whether restoration of the saved scroll position is currently scheduled.
   */
  private scrollRestorePending = false;

  /**
   * Suppresses recording while a programmatic restore is in flight.
   */
  private restoringScrollPosition = false;

  /**
   * Matches while the vertical sidebar owns its own scroll position.
   */
  private readonly scrollMedia = window.matchMedia(SIDENAV_SCROLL_MEDIA);

  constructor(base: HTMLDivElement) {
    this.base = base;
    this.state = new StateManager<NavState>(
      { pinned: true },
      { persist: true, key: 'netbox-sidenav' },
    );

    this.init();
    this.initSectionLinks();
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

    if (window.innerWidth >= 1200) {
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
    for (const section of this.base.querySelectorAll<HTMLAnchorElement>(
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
            groupItem.classList.add('active');
            dropdownMenu.classList.add('show');
            link.classList.add('active');
            break;
          case 'collapse':
            groupLink.setAttribute('aria-expanded', 'false');
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
      const link = menuitem.querySelector<HTMLAnchorElement>('a')
      if (link) {
        const href = new RegExp(link.href, 'gi');
        if (window.location.href.match(href)) {
          yield menuitem;
        }
      }
    }
  }

  /*
   * Sidebar scroll position
   *
   * Restore the offset saved for this browser tab and keep it while the active item stays
   * visible. If navigation activates an item outside that viewport, adjust only enough to reveal
   * it, or its top-level menu when that menu is closed. A change of top-level menu alone must not
   * trigger repositioning.
   */

  /**
   * Determine whether the vertical sidebar owns its own scroll position at this breakpoint.
   */
  private isScrollEnabled(): boolean {
    return this.scrollMedia.matches;
  }

  /**
   * Read the saved sidebar offset for this browser tab.
   */
  private getStoredScrollTop(): Nullable<number> {
    try {
      const value = sessionStorage.getItem(SCROLL_STATE_KEY);

      if (value === null || value === '') {
        return null;
      }

      const scrollTop = Number(value);

      if (Number.isFinite(scrollTop)) {
        return this.normalizeScrollTop(scrollTop);
      }
    } catch {
      // Ignore unavailable or invalid session storage.
    }

    return null;
  }

  /**
   * Persist the saved sidebar offset for this browser tab.
   */
  private setStoredScrollTop(scrollTop: number): void {
    try {
      sessionStorage.setItem(SCROLL_STATE_KEY, String(scrollTop));
    } catch {
      // Ignore unavailable session storage.
    }
  }

  /**
   * Clamp a raw scroll offset to a non-negative integer.
   */
  private normalizeScrollTop(value: number): number {
    return Math.max(0, Math.round(value));
  }

  /**
   * Arm restoration and persistence of the sidebar scroll position.
   */
  private initScrollPosition(): void {
    this.savedScrollTop = this.getStoredScrollTop();

    const onScrollMediaChange = () => this.syncScrollRestore();

    this.base.addEventListener('scroll', () => this.onScroll(), { passive: true });
    this.base.addEventListener('click', event => this.onClick(event), { capture: true });
    window.addEventListener('pagehide', () => this.persistScrollPosition());

    if (typeof this.scrollMedia.addEventListener === 'function') {
      this.scrollMedia.addEventListener('change', onScrollMediaChange);
    } else {
      // Safari below 14 implements only the legacy MediaQueryList listener API.
      this.scrollMedia.addListener(onScrollMediaChange);
    }

    this.tryRestoreScrollPosition();
  }

  /**
   * Re-arm or retry restoration when the viewport crosses the scrollable breakpoint.
   */
  private syncScrollRestore(): void {
    if (!this.isScrollEnabled()) {
      this.scrollPositionRestored = false;
      return;
    }

    this.tryRestoreScrollPosition();
  }

  /**
   * Apply the saved offset once the sidebar is usable, reveal the active item if it was left
   * outside the viewport, then adopt whichever offset the restore actually produced.
   */
  private tryRestoreScrollPosition(): void {
    if (this.scrollPositionRestored || this.scrollRestorePending || !this.isScrollEnabled()) {
      return;
    }

    this.scrollRestorePending = true;

    requestAnimationFrame(() => {
      this.scrollRestorePending = false;

      if (this.scrollPositionRestored || !this.isScrollEnabled()) {
        return;
      }

      this.restoringScrollPosition = true;

      // Leave a missing offset alone so the browser's own restoration survives.
      if (this.savedScrollTop !== null) {
        this.base.scrollTop = this.savedScrollTop;
      }

      this.scrollPositionRestored = true;
      this.revealActivePageLink();
      // The browser clamps an offset the current content cannot reach, so keep what it landed on.
      this.recordScrollPosition();

      // Scroll events fire before the next frame's callbacks, so this clears after them.
      requestAnimationFrame(() => {
        this.restoringScrollPosition = false;
      });
    });
  }

  /**
   * Reveal the active item while its menu is open, otherwise reveal the menu holding it. A closed
   * dropdown offers no box to measure.
   */
  private revealActivePageLink(): void {
    if (this.activePageLink === null) {
      return;
    }

    const menu = this.activePageLink.closest<HTMLElement>('.nav-item.dropdown');
    const dropdown = menu?.querySelector<HTMLElement>('.dropdown-menu');

    if (dropdown?.classList.contains('show')) {
      if (!this.isElementInView(this.activePageLink)) {
        this.scrollActiveMenuIntoView(this.activePageLink);
      }
    } else if (menu !== null && !this.isElementInView(menu)) {
      this.scrollIntoViewIfNeeded(menu);
    }
  }

  /**
   * Determine whether an element is fully visible within the padded sidebar viewport.
   */
  private isElementInView(element: HTMLElement): boolean {
    if (!this.base.contains(element) || this.base.clientHeight === 0) {
      return false;
    }

    const elementRect = element.getBoundingClientRect();
    const containerRect = this.base.getBoundingClientRect();

    return (
      elementRect.top >= containerRect.top + SCROLL_PADDING &&
      elementRect.bottom <= containerRect.bottom - SCROLL_PADDING
    );
  }

  /**
   * Bring an active menu that fits within the sidebar fully into view with the smallest possible
   * adjustment. For a longer menu, retain its heading when it fits with the active child. Otherwise,
   * reveal only the active child using the nearest viewport edge.
   */
  private scrollActiveMenuIntoView(link: HTMLDivElement): void {
    const menu = link.closest<HTMLElement>('.nav-item.dropdown');

    if (menu === null) {
      this.scrollIntoViewIfNeeded(link);
      return;
    }

    const menuRect = menu.getBoundingClientRect();
    const linkRect = link.getBoundingClientRect();
    const availableHeight = Math.max(0, this.base.clientHeight - SCROLL_PADDING * 2);

    if (menuRect.height <= availableHeight) {
      this.scrollIntoViewIfNeeded(menu);
      return;
    }

    if (linkRect.bottom - menuRect.top <= availableHeight) {
      this.scrollRangeIntoViewIfNeeded(menuRect.top, linkRect.bottom);
      return;
    }

    this.scrollIntoViewIfNeeded(link);
  }

  /**
   * Reveal the supplied vertical range, preferring the top of the sidebar when the range fits
   * there so the NetBox logo stays visible.
   */
  private scrollRangeIntoViewIfNeeded(top: number, bottom: number): void {
    if (this.base.clientHeight === 0 || this.base.scrollHeight <= this.base.clientHeight) {
      return;
    }

    const containerRect = this.base.getBoundingClientRect();
    const topDelta = top - containerRect.top - SCROLL_PADDING;
    const bottomDelta = bottom - containerRect.bottom + SCROLL_PADDING;

    if (topDelta < 0) {
      const bottomAtScrollStart = this.base.scrollTop + bottom - containerRect.top;

      if (bottomAtScrollStart <= this.base.clientHeight - SCROLL_PADDING) {
        this.base.scrollTop = 0;
      } else {
        this.base.scrollTop += topDelta;
      }
    } else if (bottomDelta > 0) {
      this.base.scrollTop += bottomDelta;
    }
  }

  /**
   * Scroll the sidebar just enough to make the supplied element visible.
   */
  private scrollIntoViewIfNeeded(element: HTMLElement): void {
    if (!this.base.contains(element)) {
      return;
    }

    const elementRect = element.getBoundingClientRect();

    this.scrollRangeIntoViewIfNeeded(elementRect.top, elementRect.bottom);
  }

  /**
   * Record the current visible offset.
   */
  private recordScrollPosition(): void {
    if (!this.scrollPositionRestored || !this.isScrollEnabled()) {
      return;
    }

    this.savedScrollTop = this.normalizeScrollTop(this.base.scrollTop);
  }

  /**
   * Write the recorded offset to session storage.
   */
  private persistScrollPosition(): void {
    if (this.savedScrollTop !== null) {
      this.setStoredScrollTop(this.savedScrollTop);
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
   * Record visible sidebar scrolling. Programmatic restores are ignored.
   */
  private onScroll(): void {
    if (this.restoringScrollPosition) {
      return;
    }

    this.recordScrollPosition();
  }

  /**
   * Record and persist the position before a sidebar link navigates away.
   */
  private onClick(event: Event): void {
    if (event.target instanceof Element && event.target.closest('a[href]') !== null) {
      this.recordScrollPosition();
      this.persistScrollPosition();
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
  for (const sidenav of getElements<HTMLDivElement>('.navbar-vertical')) {
    new SideNav(sidenav);
  }
}
