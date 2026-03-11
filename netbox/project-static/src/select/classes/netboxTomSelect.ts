import TomSelect from 'tom-select';

/**
 * Extends TomSelect to work around a browser autofill bug where Edge's "last used" autofill
 * simultaneously focuses multiple inputs, triggering a cascading focus/open/blur loop between
 * TomSelect instances.
 *
 * Root cause: TomSelect's open() method calls focus(), which synchronously moves browser focus
 * to this instance's control input, then schedules setTimeout(onFocus, 0). When Edge autofill
 * has moved focus to a *different* select before the timeout fires, the delayed onFocus() call
 * re-steals browser focus back, causing the other instance to blur and close. Each instance's
 * deferred callback then repeats this, creating an infinite ping-pong loop.
 *
 * Fix: in the setTimeout callback, only proceed with onFocus() if this instance's element is
 * still the active element. If focus has already moved elsewhere, skip the call.
 *
 * Upstream bug: https://github.com/orchidjs/tom-select/issues/806
 * NetBox issue:  https://github.com/netbox-community/netbox/issues/20077
 */
export class NetBoxTomSelect extends TomSelect {
  focus(): void {
    if (this.isDisabled || this.isReadOnly) return;

    this.ignoreFocus = true;

    const focusTarget = this.control_input.offsetWidth ? this.control_input : this.focus_node;
    focusTarget.focus();

    setTimeout(() => {
      this.ignoreFocus = false;
      // Only proceed if this instance's element is still the active element. If Edge autofill
      // (or anything else) has moved focus to a different element in the interim, calling
      // onFocus() here would steal focus back and restart the cascade loop.
      if (document.activeElement === focusTarget || this.control.contains(document.activeElement)) {
        this.onFocus();
      }
    }, 0);
  }
}
