import { initClearField } from './clearField';
import { initFormElements } from './elements';
import { initFilterModifiers } from './filterModifiers';
import { initSpeedSelector } from './speedSelector';

export function initForms(): void {
  for (const func of [initFormElements, initSpeedSelector, initFilterModifiers, initClearField]) {
    func();
  }
}
