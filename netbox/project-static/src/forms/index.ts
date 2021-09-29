import { initFormElements } from './elements';
import { initSpeedSelector } from './speedSelector';
import { initScopeSelector } from './scopeSelector';
import { initVlanTags } from './vlanTags';

export function initForms(): void {
  for (const func of [initFormElements, initSpeedSelector, initScopeSelector, initVlanTags]) {
    func();
  }
}
