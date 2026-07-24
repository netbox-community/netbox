import type TomSelect from 'tom-select';
import { NetBoxTomSelect } from '../select/classes/netboxTomSelect';
import { getPlugins } from '../select/config';
import { getElements } from '../util';

/**
 * Return the TomSelect instance attached to a protocol <select>, if it has been initialized.
 */
function getProtocolSelect(select: HTMLSelectElement): TomSelect | undefined {
  return (select as HTMLSelectElement & { tomselect?: TomSelect }).tomselect;
}

/**
 * Apply NetBox's standard TomSelect styling to a protocol <select>. The widget manages these instances
 * itself (rather than leaving them to the global static-select initializer) so it can keep TomSelect in
 * sync as rows are added, removed, and their available protocols change.
 */
function initProtocolSelect(select: HTMLSelectElement, widget: HTMLElement): void {
  if (getProtocolSelect(select)) return;
  new NetBoxTomSelect(select, {
    ...getPlugins(select),
    maxOptions: undefined,
    // TomSelect emits its own (non-DOM) change event rather than a bubbling native one, so the widget's
    // delegated 'change' listener never sees protocol selections. Refresh/serialize from here instead.
    onChange: () => {
      refreshProtocolOptions(widget);
      serialize(widget);
    },
  });
}

/**
 * Serialize the visible protocol/port rows of a widget into its hidden input as a JSON array of
 * `{ protocol, ports }` objects. `ports` is kept as the raw comma/range string; the server expands it.
 */
function serialize(widget: HTMLElement): void {
  const hidden = widget.querySelector<HTMLInputElement>('input[type="hidden"]');
  if (hidden === null) return;

  const rows: Array<{ protocol: string; ports: string }> = [];
  for (const row of widget.querySelectorAll<HTMLElement>('[data-port-mapping-row]')) {
    const protocol =
      row.querySelector<HTMLSelectElement>('select.port-mapping-protocol')?.value ?? '';
    const ports = row.querySelector<HTMLInputElement>('.port-mapping-ports')?.value.trim() ?? '';
    if (protocol === '' && ports === '') continue;
    rows.push({ protocol, ports });
  }
  hidden.value = JSON.stringify(rows);
}

/**
 * The set of protocol values currently selected across the widget's rows.
 */
function usedProtocols(widget: HTMLElement): Set<string> {
  const selects = widget.querySelectorAll<HTMLSelectElement>('select.port-mapping-protocol');
  return new Set(
    Array.from(selects)
      .map(select => select.value)
      .filter(value => value !== ''),
  );
}

/**
 * The full list of protocol (value, label) choices, read from the widget's pristine `<template>` so it
 * remains available even after options have been removed from the live selects.
 */
function protocolChoices(widget: HTMLElement): Array<{ value: string; text: string }> {
  const template = widget.querySelector<HTMLTemplateElement>(
    'template[data-port-mapping-template]',
  );
  const source = template?.content.querySelector<HTMLSelectElement>('select.port-mapping-protocol');
  return Array.from(source?.options ?? [])
    .filter(option => option.value !== '')
    .map(option => ({ value: option.value, text: option.textContent?.trim() ?? option.value }));
}

/**
 * Ensure each row offers only protocols not already chosen in another row (so each protocol can be
 * selected at most once), and disable the "Add mapping" button when every protocol is in use.
 */
function refreshProtocolOptions(widget: HTMLElement): void {
  const choices = protocolChoices(widget);
  const selects = Array.from(
    widget.querySelectorAll<HTMLSelectElement>('select.port-mapping-protocol'),
  );
  const used = new Set(selects.map(select => select.value).filter(value => value !== ''));

  for (const select of selects) {
    const current = select.value;
    const ts = getProtocolSelect(select);
    if (ts) {
      // TomSelect renders its dropdown from its own option map, ignoring later changes to the native
      // <option> disabled attribute — so add/remove options in that map to control what's offered.
      // A protocol is offered only if it's free or already chosen in this row (never remove the row's
      // own selection).
      choices.forEach(({ value, text }, index) => {
        const allowed = value === current || !used.has(value);
        const exists = Object.prototype.hasOwnProperty.call(ts.options, value);
        if (allowed && !exists) {
          // Preserve the original ordering by mirroring the choice's index as TomSelect's $order.
          ts.addOption({ value, text, $order: index + 1 });
        } else if (!allowed && exists) {
          ts.removeOption(value, true);
        }
      });
      ts.refreshOptions(false);
    } else {
      // Fallback for a not-yet-enhanced select: toggle the native disabled attribute.
      for (const option of Array.from(select.options)) {
        if (option.value === '') continue;
        option.disabled = used.has(option.value) && option.value !== current;
      }
    }
  }

  const addButton = widget.querySelector<HTMLButtonElement>('[data-port-mapping-add]');
  if (addButton !== null) {
    addButton.disabled = choices.length > 0 && used.size >= choices.length;
  }
}

/**
 * Add a new empty row by cloning the widget's `<template>`, defaulting it to the first protocol that
 * is not already in use.
 */
function addRow(widget: HTMLElement): void {
  const template = widget.querySelector<HTMLTemplateElement>(
    'template[data-port-mapping-template]',
  );
  const body = widget.querySelector<HTMLElement>('[data-port-mapping-rows]');
  if (template === null || body === null) return;

  const used = usedProtocols(widget);
  const fragment = template.content.cloneNode(true) as DocumentFragment;
  body.appendChild(fragment);

  // Default the new row to the first protocol not already selected elsewhere
  const rows = body.querySelectorAll<HTMLElement>('[data-port-mapping-row]');
  const newSelect = rows[rows.length - 1]?.querySelector<HTMLSelectElement>(
    'select.port-mapping-protocol',
  );
  if (newSelect) {
    // Cloned rows come from an inert <template>, so their select is a plain element that hasn't been
    // enhanced yet; style it before setting a value so the change is reflected in the TomSelect control.
    initProtocolSelect(newSelect, widget);
    const available = protocolChoices(widget).find(choice => !used.has(choice.value));
    if (available) {
      const ts = getProtocolSelect(newSelect);
      if (ts) {
        ts.setValue(available.value, true);
      } else {
        newSelect.value = available.value;
      }
    }
  }

  refreshProtocolOptions(widget);
  serialize(widget);
}

/**
 * Wire up a single port-mapping widget: add/remove row controls plus re-serialization on any change
 * and on form submission.
 */
function initWidget(widget: HTMLElement): void {
  // Style the server-rendered protocol selects. TomSelect emits change events through its own callback
  // (wired in initProtocolSelect), so the widget-level 'change' listener below only handles the ports
  // inputs.
  for (const select of widget.querySelectorAll<HTMLSelectElement>('select.port-mapping-protocol')) {
    initProtocolSelect(select, widget);
  }

  const addButton = widget.querySelector<HTMLButtonElement>('[data-port-mapping-add]');
  addButton?.addEventListener('click', () => addRow(widget));

  // Remove-row buttons (event delegation, since rows are added dynamically)
  widget.addEventListener('click', event => {
    const target = event.target as HTMLElement;
    const removeButton = target.closest('[data-port-mapping-remove]');
    if (removeButton === null) return;
    removeButton.closest('[data-port-mapping-row]')?.remove();
    refreshProtocolOptions(widget);
    serialize(widget);
  });

  // Keep the hidden input in sync as the user edits the ports fields
  widget.addEventListener('input', () => serialize(widget));
  widget.addEventListener('change', () => {
    refreshProtocolOptions(widget);
    serialize(widget);
  });

  // Ensure the hidden input is current at submit time
  widget.closest('form')?.addEventListener('submit', () => serialize(widget));

  // Initialize option state and the hidden input from whatever rows are present on load
  refreshProtocolOptions(widget);
  serialize(widget);
}

export function initPortMappings(): void {
  for (const widget of getElements<HTMLElement>('.port-mapping-widget')) {
    initWidget(widget);
  }
}
