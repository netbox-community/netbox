import { getElements, isElement } from './util';

// Keep in sync with Bootstrap's `lg` breakpoint and `navbar-expand-lg` in base/layout.html.
const SIDENAV_DESKTOP_MEDIA = '(min-width: 992px)';

// Session-scoped, unlike the localStorage fold state.
const SCROLL_STATE_KEY = 'netbox-sidenav-scroll';

// Read before the first paint by initSidebar() in js/setmode.js.
const FOLD_STATE_KEY = 'netbox-sidebar';

class SideNav {
  /**
   * Sidenav container element.
   */
  private base: HTMLElement;

  /**
   * The menu below the logo, which scrolls in the desktop layout.
   */
  private menu: HTMLElement;

  /**
   * The desktop layout, the only one where the sidebar folds.
   */
  private desktopMedia: MediaQueryList;

  /**
   * First nav item matching the current page, cached at construction.
   */
  private activePageLink: Nullable<HTMLDivElement> = null;

  /**
   * Menu offset of the unfolded layout, the expanded sidebar or the hover overlay. The compact
   * rail hides the open groups, so it cannot hold this offset.
   */
  private unfoldedScrollTop = 0;

  /**
   * A folded rail reveals the active item on its first hover, unless the unfolded menu was
   * scrolled before.
   */
  private revealPending = false;

  constructor(base: HTMLElement) {
    this.base = base;
    this.menu = base.querySelector<HTMLElement>('.navbar-collapse') ?? base;
    this.desktopMedia = window.matchMedia(SIDENAV_DESKTOP_MEDIA);

    this.init();
    this.initLinks();
    this.initScrollPosition();
    this.initMenuScroll();
  }

  /**
   * Whether the sidebar is set to fold on desktop.
   */
  private isFolded(): boolean {
    return document.documentElement.getAttribute('data-bs-sidebar') === 'folded-hover';
  }

  /**
   * Whether the menu shows its unfolded layout, expanded or opened by hover or keyboard focus.
   */
  private isUnfolded(): boolean {
    return !this.isFolded() || this.base.matches(':hover, :has(:focus-visible)');
  }

  /**
   * Set initial values & add event listeners.
   */
  private init(): void {
    for (const toggle of getElements<HTMLButtonElement>('.sidebar-toggle')) {
      toggle.addEventListener('click', () => this.setFolded(!this.isFolded()));
    }
    this.syncToggles();

    // Below lg the menu does not scroll and loses its offset.
    this.desktopMedia.addEventListener('change', () => {
      this.initLinks();
      if (!this.desktopMedia.matches) return;
      if (this.isUnfolded()) this.menu.scrollTop = this.unfoldedScrollTop;
      this.shade();
    });

    // The hover overlay returns to where the unfolded menu was, unless keyboard focus opened it.
    this.base.addEventListener('mouseenter', () => {
      if (this.isFolded() && !this.base.matches(':has(:focus-visible)')) {
        this.menu.scrollTop = this.unfoldedScrollTop;
        if (this.revealPending && this.desktopMedia.matches) {
          this.revealPending = false;
          this.revealActiveLink();
        }
      }
    });

    // A mouse unpin would leave focus on the pin that the folded rail clips away.
    this.base.addEventListener('mouseleave', () => {
      if (!this.isFolded()) return;
      for (const toggle of getElements<HTMLButtonElement>('.sidebar-toggle')) {
        if (toggle === document.activeElement && !toggle.matches(':focus-visible')) {
          toggle.blur();
        }
      }
    });
  }

  /**
   * Expand the active menu group on desktop, folded or not, and collapse it on mobile.
   */
  private initLinks(): void {
    for (const link of this.getActiveLinks()) {
      this.activePageLink ??= link;
      this.activateLink(link, this.desktopMedia.matches ? 'expand' : 'collapse');
    }
  }

  /**
   * Fold or unfold the desktop sidebar and remember the choice. Open menu groups stay open.
   */
  private setFolded(folded: boolean): void {
    if (folded) {
      document.documentElement.setAttribute('data-bs-sidebar', 'folded-hover');
    } else {
      document.documentElement.removeAttribute('data-bs-sidebar');
      this.menu.scrollTop = this.unfoldedScrollTop;
    }
    try {
      localStorage.setItem(FOLD_STATE_KEY, folded ? 'folded' : 'expanded');
    } catch {
      // A failed write still applies to the current page.
    }
    this.syncToggles();
  }

  /**
   * Mark the pin buttons pressed while the sidebar is pinned.
   */
  private syncToggles(): void {
    for (const toggle of getElements<HTMLButtonElement>('.sidebar-toggle')) {
      toggle.setAttribute('aria-pressed', String(!this.isFolded()));
    }
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
   * Restore the offset saved for this browser tab, reveal the active item when it falls outside
   * the menu viewport, and save the offset again on the way out. One offset per tab, so a shorter
   * menu can clamp a deeper value. A folded sidebar applies both when the overlay opens on hover,
   * the reveal only the first time.
   */
  private initScrollPosition(): void {
    const storedScrollTop = sessionStorage.getItem(SCROLL_STATE_KEY);

    // Leave a missing offset alone so the browser's own restoration survives.
    if (storedScrollTop !== null) {
      this.unfoldedScrollTop = Number(storedScrollTop);
      // The pointer can already rest on a folded rail.
      if (this.isUnfolded()) {
        this.menu.scrollTop = this.unfoldedScrollTop;
      }
    }

    // Reveal only in the fixed desktop layout. In the mobile flow layout, scrollIntoView would scroll the page.
    if (this.desktopMedia.matches) {
      if (this.isUnfolded()) {
        this.revealActiveLink();
      } else {
        this.revealPending = true;
      }
    }

    // Only scrolling changes the offset, so a menu that cannot scroll keeps the stored one.
    window.addEventListener('pagehide', () => {
      sessionStorage.setItem(SCROLL_STATE_KEY, String(this.unfoldedScrollTop));
    });
  }

  /**
   * Scroll the active item into the menu viewport when it falls outside.
   */
  private revealActiveLink(): void {
    const menu = this.activePageLink?.closest<HTMLElement>('.nav-item.dropdown');
    // A closed dropdown has no box to measure, so reveal its heading instead.
    const target = menu && !menu.querySelector('.dropdown-menu.show') ? menu : this.activePageLink;

    target?.scrollIntoView({ block: 'nearest' });
  }

  /**
   * Track the unfolded menu's offset and shade the logo row while the menu is scrolled.
   */
  private initMenuScroll(): void {
    this.menu.addEventListener(
      'scroll',
      () => {
        // Neither the compact rail nor the mobile menu holds the unfolded desktop offset.
        if (this.desktopMedia.matches && this.isUnfolded()) {
          this.unfoldedScrollTop = this.menu.scrollTop;
          this.revealPending = false;
        }
        this.shade();
      },
      { passive: true },
    );
    this.shade();
  }

  /**
   * Mark the sidebar while its menu is scrolled, so the logo row casts a shadow.
   */
  private shade(): void {
    this.base.classList.toggle('menu-scrolled', this.menu.scrollTop > 0);
  }
}

export function initSideNav(): void {
  for (const sidenav of getElements<HTMLElement>('.navbar-vertical')) {
    new SideNav(sidenav);
  }
}
