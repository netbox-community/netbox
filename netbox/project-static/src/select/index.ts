import { initColorSelects, initStaticSelects } from './static';
import { initDynamicSelects } from './dynamic';

export function initSelects(): void {
  initStaticSelects();
  initDynamicSelects();
  initColorSelects();
}
