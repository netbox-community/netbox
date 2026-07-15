import { getElements } from '../util';

/**
 * Serialize the visible protocol/port rows of a widget into its hidden input as a JSON array of
 * `{ protocol, ports }` objects. `ports` is kept as the raw comma/range string; the server expands it.
 */
function serialize(widget: HTMLElement): void {
  const hidden = widget.querySelector<HTMLInputElement>('input[type="hidden"]');
  if (hidden === null) return;

  const rows: Array<{ protocol: string; ports: string }> = [];
  for (const row of widget.querySelectorAll<HTMLElement>('[data-port-mapping-row]')) {
    const protocol = row.querySelector<HTMLSelectElement>('.port-mapping-protocol')?.value ?? '';
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
  const selects = widget.querySelectorAll<HTMLSelectElement>('.port-mapping-protocol');
  return new Set(
    Array.from(selects)
      .map(select => select.value)
      .filter(value => value !== ''),
  );
}

/**
 * Disable protocol options already chosen in another row so each protocol can be selected at most
 * once, and disable the "Add mapping" button when every protocol is in use.
 */
function refreshProtocolOptions(widget: HTMLElement): void {
  const selects = Array.from(widget.querySelectorAll<HTMLSelectElement>('.port-mapping-protocol'));
  const used = new Set(selects.map(select => select.value).filter(value => value !== ''));

  let protocolCount = 0;
  for (const select of selects) {
    let selectableCount = 0;
    for (const option of Array.from(select.options)) {
      if (option.value === '') continue;
      selectableCount += 1;
      // Keep the option enabled in the row that currently owns it
      option.disabled = used.has(option.value) && option.value !== select.value;
    }
    protocolCount = Math.max(protocolCount, selectableCount);
  }

  const addButton = widget.querySelector<HTMLButtonElement>('[data-port-mapping-add]');
  if (addButton !== null) {
    addButton.disabled = protocolCount > 0 && used.size >= protocolCount;
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
  const newSelect =
    rows[rows.length - 1]?.querySelector<HTMLSelectElement>('.port-mapping-protocol');
  if (newSelect) {
    const available = Array.from(newSelect.options).find(
      option => option.value !== '' && !used.has(option.value),
    );
    if (available) newSelect.value = available.value;
  }

  refreshProtocolOptions(widget);
  serialize(widget);
}

/**
 * Wire up a single port-mapping widget: add/remove row controls plus re-serialization on any change
 * and on form submission.
 */
function initWidget(widget: HTMLElement): void {
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

  // Keep the hidden input in sync as the user edits rows
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
