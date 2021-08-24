import { getElements, findFirstAdjacent } from '../util';

type InterfaceState = 'enabled' | 'disabled';
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
   * Table rows with `data-enabled` set to `"enabled"`
   */
  private enabledRows: NodeListOf<HTMLTableRowElement>;
  /**
   * Table rows with `data-enabled` set to `"disabled"`
   */
  private disabledRows: NodeListOf<HTMLTableRowElement>;

  constructor(button: HTMLButtonElement, table: HTMLTableElement) {
    this.button = button;
    this.enabledRows = table.querySelectorAll<HTMLTableRowElement>('tr[data-enabled="enabled"]');
    this.disabledRows = table.querySelectorAll<HTMLTableRowElement>('tr[data-enabled="disabled"]');
  }

  /**
   * This button's controlled type. For example, a button with the class `toggle-disabled` has
   * directive 'disabled' because it controls the visibility of rows with
   * `data-enabled="disabled"`. Likewise, `toggle-enabled` controls rows with
   * `data-enabled="enabled"`.
   */
  private get directive(): InterfaceState {
    if (this.button.classList.contains('toggle-disabled')) {
      return 'disabled';
    } else if (this.button.classList.contains('toggle-enabled')) {
      return 'enabled';
    }
    // If this class has been instantiated but doesn't contain these classes, it's probably because
    // the classes are missing in the HTML template.
    console.warn(this.button);
    throw new Error('Toggle button does not contain expected class');
  }

  /**
   * Toggle visibility of rows with `data-enabled="enabled"`.
   */
  private toggleEnabledRows(): void {
    for (const row of this.enabledRows) {
      row.classList.toggle('d-none');
    }
  }

  /**
   * Toggle visibility of rows with `data-enabled="disabled"`.
   */
  private toggleDisabledRows(): void {
    for (const row of this.disabledRows) {
      row.classList.toggle('d-none');
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
      this.button.innerText = this.button.innerText.replaceAll('Show', 'Hide');
    } else if (this.buttonState === 'hide') {
      this.button.innerText = this.button.innerText.replaceAll('Hide', 'Show');
    }
  }

  /**
   * Toggle visibility for the rows this element controls.
   */
  private toggleRows(): void {
    if (this.directive === 'enabled') {
      this.toggleEnabledRows();
    } else if (this.directive === 'disabled') {
      this.toggleDisabledRows();
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
    this.toggleRows();
  }

  /**
   * When the button is clicked, toggle all controlled elements.
   */
  public handleClick(event: Event): void {
    const button = event.currentTarget as HTMLButtonElement;
    if (button.isEqualNode(this.button)) {
      this.toggle();
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
   * Underlying DOM Table Caption Element.
   */
  private caption: Nullable<HTMLTableCaptionElement> = null;

  constructor(table: HTMLTableElement) {
    this.table = table;

    try {
      const toggleEnabledButton = findFirstAdjacent<HTMLButtonElement>(
        this.table,
        'button.toggle-enabled',
      );
      const toggleDisabledButton = findFirstAdjacent<HTMLButtonElement>(
        this.table,
        'button.toggle-disabled',
      );

      const caption = this.table.querySelector('caption');
      this.caption = caption;

      if (toggleEnabledButton === null) {
        throw new TableStateError("Table is missing a 'toggle-enabled' button.", table);
      }

      if (toggleDisabledButton === null) {
        throw new TableStateError("Table is missing a 'toggle-disabled' button.", table);
      }

      // Attach event listeners to the buttons elements.
      toggleEnabledButton.addEventListener('click', event => this.handleClick(event, this));
      toggleDisabledButton.addEventListener('click', event => this.handleClick(event, this));

      // Instantiate ButtonState for each button for state management.
      this.enabledButton = new ButtonState(toggleEnabledButton, this.table);
      this.disabledButton = new ButtonState(toggleDisabledButton, this.table);
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

    if (showEnabled && !showDisabled) {
      this.captionText = 'Showing Enabled Interfaces';
    } else if (showEnabled && showDisabled) {
      this.captionText = 'Showing Enabled & Disabled Interfaces';
    } else if (!showEnabled && showDisabled) {
      this.captionText = 'Showing Disabled Interfaces';
    } else if (!showEnabled && !showDisabled) {
      this.captionText = 'Hiding Enabled & Disabled Interfaces';
    } else {
      this.captionText = '';
    }
  }

  /**
   * When toggle buttons are clicked, pass the event to the relevant button's handler and update
   * this instance's state.
   *
   * @param event onClick event for toggle buttons.
   * @param instance Instance of TableState (`this` cannot be used since that's context-specific).
   */
  public handleClick(event: Event, instance: TableState): void {
    const button = event.currentTarget as HTMLButtonElement;
    const enabled = button.isEqualNode(instance.enabledButton.button);
    const disabled = button.isEqualNode(instance.disabledButton.button);

    if (enabled) {
      instance.enabledButton.handleClick(event);
    } else if (disabled) {
      instance.disabledButton.handleClick(event);
    }
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
