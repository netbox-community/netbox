import { initFormElements } from './elements';
import { initSpeedSelector } from './speedSelector';
import { initScopeSelector } from './scopeSelector';

export function initForms(): void {
  for (const func of [initFormElements, initSpeedSelector, initScopeSelector]) {
    func();
  }
}
