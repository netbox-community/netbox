import { getElements } from '../util';
import { StateManager } from 'src/state';
import { previousPkCheckState } from '../stores';

type PreviousPkCheckState = { element: Nullable<HTMLInputElement> };

function removeTextSelection(): void {
  window.getSelection()?.removeAllRanges();
}

function updatePreviousPkCheckState(
  eventTargetElement: HTMLInputElement,
  state: StateManager<PreviousPkCheckState>,
): void {
  state.set('element', eventTargetElement);
}

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
      typedElement.checked = eventTargetElement.checked;
    }
    //The previously clicked checkbox was above the shift clicked checkbox
    if (element === previousStateElement) {
      if (changePkCheckboxState === true) {
        changePkCheckboxState = false;
        return;
      }
      changePkCheckboxState = true;
      typedElement.checked = eventTargetElement.checked;
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
