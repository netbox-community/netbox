import { getElements } from '../util';
import { StateManager } from 'src/state';
import { previousPkCheckState } from '../stores';

type PreviousPkCheckState = { element: Nullable<HTMLInputElement> };

/**
 * If there is a text selection, removes it.
 */
function removeTextSelection(): void {
  window.getSelection()?.removeAllRanges();
}

/**
 * Sets the state object passed in to the eventTargetElement object passed in.
 *
 * @param eventTargetElement HTML Input Element, retrieved from getting the target of the
 * event passed in from handlePkCheck()
 * @param state PreviousPkCheckState object.
 */
function updatePreviousPkCheckState(
  eventTargetElement: HTMLInputElement,
  state: StateManager<PreviousPkCheckState>,
): void {
  state.set('element', eventTargetElement);
}

/**
 * For all checkboxes between eventTargetElement and previousStateElement in elementList, toggle
 * "checked" value to eventTargetElement.checked
 *
 * @param eventTargetElement HTML Input Element, retrieved from getting the target of the
 * event passed in from handlePkCheck()
 * @param state PreviousPkCheckState object.
 */
function toggleCheckboxRange(
  eventTargetElement: HTMLInputElement,
  previousStateElement: HTMLInputElement,
  elementList: Generator,
): void {
  let changePkCheckboxState = false;
  for (const element of elementList) {
    const typedElement = element as HTMLInputElement;
    //Change loop's current checkbox state to eventTargetElement checkbox state
    if (changePkCheckboxState === true) {
      if (!typedElement.closest('tr')?.classList.contains('d-none')) {
        typedElement.checked = eventTargetElement.checked;
      }
    }
    //The previously clicked checkbox was above the shift clicked checkbox
    if (element === previousStateElement) {
      if (changePkCheckboxState === true) {
        changePkCheckboxState = false;
        return;
      }
      changePkCheckboxState = true;
      if (!typedElement.closest('tr')?.classList.contains('d-none')) {
        typedElement.checked = eventTargetElement.checked;
      }
    }
    //The previously clicked checkbox was below the shift clicked checkbox
    if (element === eventTargetElement) {
      if (changePkCheckboxState === true) {
        changePkCheckboxState = false;
        return;
      }
      changePkCheckboxState = true;
    }
  }
}

/**
 * IF the shift key is pressed and there is state is not null, toggleCheckboxRange between the
 * event target element and the state element.
 *
 * @param event Mouse event.
 * @param state PreviousPkCheckState object.
 */
function handlePkCheck(event: MouseEvent, state: StateManager<PreviousPkCheckState>): void {
  const eventTargetElement = event.target as HTMLInputElement;
  const previousStateElement = state.get('element');
  updatePreviousPkCheckState(eventTargetElement, state);
  //Stop if user is not holding shift key
  if (!event.shiftKey) {
    return;
  }
  removeTextSelection();
  //If no previous state, store event target element as previous state and return
  if (previousStateElement === null) {
    return updatePreviousPkCheckState(eventTargetElement, state);
  }
  const checkboxList = getElements<HTMLInputElement>('input[type="checkbox"][name="pk"]');
  toggleCheckboxRange(eventTargetElement, previousStateElement, checkboxList);
}

/**
 * Initialize table select all elements.
 */
export function initSelectMultiple(): void {
  const checkboxElements = getElements<HTMLInputElement>('input[type="checkbox"][name="pk"]');
  for (const element of checkboxElements) {
    element.addEventListener('click', event => {
      removeTextSelection();
      //Stop propogation to avoid event firing multiple times
      event.stopPropagation();
      handlePkCheck(event, previousPkCheckState);
    });
  }
}
