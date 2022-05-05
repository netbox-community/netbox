import { getElements } from '../util';
import { StateManager } from 'src/state';
import { previousPkCheckState } from '../stores';

type PreviousPkCheckState = { element: Nullable<HTMLInputElement> };

function updatePreviousPkCheckState(eventTargetElement: HTMLInputElement, state: StateManager<PreviousPkCheckState>): void {
  console.log(state)
  state.set('element', eventTargetElement);
}


export function initSelectMultiple(): void {
  const checkboxElements = getElements<HTMLInputElement>('input[type="checkbox"][name="pk"]');
  for (const element of checkboxElements) {
    element.addEventListener('click', (event) => {
      event.stopPropagation();
      updatePreviousPkCheckState(event.target as HTMLInputElement, previousPkCheckState);
    });
  }
}
