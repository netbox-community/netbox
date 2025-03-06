import { initFormElements } from './elements';
import { initSpeedSelector } from './speedSelector';

export function initForms(): void {
  for (const func of [initFormElements, initSpeedSelector]) {
    func();
  }
}
