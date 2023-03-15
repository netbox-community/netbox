import { getElements, replaceAll, findFirstAdjacent } from '../util';

type ShowHide = 'show' | 'hide';

function isShowHide(value: unknown): value is ShowHide {
  return typeof value === 'string' && ['show', 'hide'].includes(value);
}

/**
 * When this error is thrown, it's an indication that we don't need to manage this table, because
 * it doesn't contain the required elements.
 */
class TableStateError extends Error {
  table: HTMLTableElement;
  constructor(message: string, table: HTMLTableElement) {
    super(message);
    this.table = table;
  }
}

/**
 * Manage the display text of a button element as well as the visibility of its corresponding rows.
 */
class ButtonState {
  /**
   * Underlying Button DOM Element
   */
  public button: HTMLButtonElement;

  /**
   * Table rows provided in constructor
   */
  private rows: NodeListOf<HTMLTableRowElement>;

  constructor(button: HTMLButtonElement, rows: NodeListOf<HTMLTableRowElement>) {
    this.button = button;
    this.rows = rows;
  }

  /**
   * Remove visibility of button state rows.
   */
  private hideRows(): void {
    for (const row of this.rows) {
      row.classList.add('d-none');
    }
  }

  /**
   * Update the DOM element's `data-state` attribute.
   */
  public set buttonState(state: Nullable<ShowHide>) {
    if (isShowHide(state)) {
      this.button.setAttribute('data-state', state);
    }
  }

  /**
   * Get the DOM element's `data-state` attribute.
   */
  public get buttonState(): Nullable<ShowHide> {
    const state = this.button.getAttribute('data-state');
    if (isShowHide(state)) {
      return state;
    }
    return null;
  }

  /**
   * Update the DOM element's display text to reflect the action opposite the current state. For
   * example, if the current state is to hide enabled interfaces, the DOM text should say
   * "Show Enabled Interfaces".
   */
  private toggleButton(): void {
    if (this.buttonState === 'show') {
      this.button.innerText = replaceAll(this.button.innerText, 'Show', 'Hide');
    } else if (this.buttonState === 'hide') {
      this.button.innerText = replaceAll(this.button.innerHTML, 'Hide', 'Show');
    }
  }

  /**
   * Toggle the DOM element's `data-state` attribute.
   */
  private toggleState(): void {
    if (this.buttonState === 'show') {
      this.buttonState = 'hide';
    } else if (this.buttonState === 'hide') {
      this.buttonState = 'show';
    }
  }

  /**
   * Toggle all controlled elements.
   */
  private toggle(): void {
    this.toggleState();
    this.toggleButton();
  }

  /**
   * When the button is clicked, toggle all controlled elements and hide rows based on
   * buttonstate.
   */
  public handleClick(event: Event): void {
    const button = event.currentTarget as HTMLButtonElement;
    if (button.isEqualNode(this.button)) {
      this.toggle();
    }
    if (this.buttonState === 'hide') {
      this.hideRows();
    }
  }
}

/**
 * Manage the state of a table and its elements.
 */
class TableState {
  /**
   * Underlying DOM Table Element.
   */

  private table: HTMLTableElement;
  /**
   * Instance of ButtonState for the 'show/hide enabled rows' button.
   */
  // @ts-expect-error null handling is performed in the constructor
  private enabledButton: ButtonState;

  /**
   * Instance of ButtonState for the 'show/hide disabled rows' button.
   */
  // @ts-expect-error null handling is performed in the constructor
  private disabledButton: ButtonState;

  /**
   * Instance of ButtonState for the 'show/hide virtual rows' button.
   */
  // @ts-expect-error null handling is performed in the constructor
  private virtualButton: ButtonState;

  /**
   * Underlying DOM Table Caption Element.
   */
  private caption: Nullable<HTMLTableCaptionElement> = null;

  /**
   * All table rows in table
   */
  private rows: NodeListOf<HTMLTableRowElement>;

  constructor(table: HTMLTableElement) {
    this.table = table;
    this.rows = this.table.querySelectorAll('tr');
    try {
      const toggleEnabledButton = findFirstAdjacent<HTMLButtonElement>(
        this.table,
        'button.toggle-enabled',
      );
      const toggleDisabledButton = findFirstAdjacent<HTMLButtonElement>(
        this.table,
        'button.toggle-disabled',
      );
      const toggleVirtualButton = findFirstAdjacent<HTMLButtonElement>(
        this.table,
        'button.toggle-virtual',
      );

      const caption = this.table.querySelector('caption');
      this.caption = caption;

      if (toggleEnabledButton === null) {
        throw new TableStateError("Table is missing a 'toggle-enabled' button.", table);
      }

      if (toggleDisabledButton === null) {
        throw new TableStateError("Table is missing a 'toggle-disabled' button.", table);
      }

      if (toggleVirtualButton === null) {
        throw new TableStateError("Table is missing a 'toggle-virtual' button.", table);
      }

      // Attach event listeners to the buttons elements.
      toggleEnabledButton.addEventListener('click', event => this.handleClick(event, this));
      toggleDisabledButton.addEventListener('click', event => this.handleClick(event, this));
      toggleVirtualButton.addEventListener('click', event => this.handleClick(event, this));

      // Instantiate ButtonState for each button for state management.
      this.enabledButton = new ButtonState(
        toggleEnabledButton,
        table.querySelectorAll<HTMLTableRowElement>('tr[data-enabled="enabled"]'),
      );
      this.disabledButton = new ButtonState(
        toggleDisabledButton,
        table.querySelectorAll<HTMLTableRowElement>('tr[data-enabled="disabled"]'),
      );
      this.virtualButton = new ButtonState(
        toggleVirtualButton,
        table.querySelectorAll<HTMLTableRowElement>('tr[data-type="virtual"]'),
      );
    } catch (err) {
      if (err instanceof TableStateError) {
        // This class is useless for tables that don't have toggle buttons.
        console.debug('Table does not contain enable/disable toggle buttons');
        return;
      } else {
        throw err;
      }
    }
  }

  /**
   * Get the table caption's text.
   */
  private get captionText(): string {
    if (this.caption !== null) {
      return this.caption.innerText;
    }
    return '';
  }

  /**
   * Set the table caption's text.
   */
  private set captionText(value: string) {
    if (this.caption !== null) {
      this.caption.innerText = value;
    }
  }

  /**
   * Update the table caption's text based on the state of each toggle button.
   */
  private toggleCaption(): void {
    const showEnabled = this.enabledButton.buttonState === 'show';
    const showDisabled = this.disabledButton.buttonState === 'show';
    const showVirtual = this.virtualButton.buttonState === 'show';

    if (showEnabled && !showDisabled && !showVirtual) {
      this.captionText = 'Showing Enabled Interfaces';
    } else if (showEnabled && showDisabled && !showVirtual) {
      this.captionText = 'Showing Enabled & Disabled Interfaces';
    } else if (!showEnabled && showDisabled && !showVirtual) {
      this.captionText = 'Showing Disabled Interfaces';
    } else if (!showEnabled && !showDisabled && !showVirtual) {
      this.captionText = 'Hiding Enabled, Disabled & Virtual Interfaces';
    } else if (!showEnabled && !showDisabled && showVirtual) {
      this.captionText = 'Showing Virtual Interfaces';
    } else if (showEnabled && !showDisabled && showVirtual) {
      this.captionText = 'Showing Enabled & Virtual Interfaces';
    } else if (showEnabled && showDisabled && showVirtual) {
      this.captionText = 'Showing Enabled, Disabled & Virtual Interfaces';
    } else {
      this.captionText = '';
    }
  }

  /**
   * When toggle buttons are clicked, reapply visability all rows and
   * pass the event to all button handlers
   *
   * @param event onClick event for toggle buttons.
   * @param instance Instance of TableState (`this` cannot be used since that's context-specific).
   */
  public handleClick(event: Event, instance: TableState): void {
    for (const row of this.rows) {
      row.classList.remove('d-none');
    }

    instance.enabledButton.handleClick(event);
    instance.disabledButton.handleClick(event);
    instance.virtualButton.handleClick(event);
    instance.toggleCaption();
  }
}

/**
 * Initialize table states.
 */
export function initInterfaceTable(): void {
  for (const element of getElements<HTMLTableElement>('table')) {
    new TableState(element);
  }
}
