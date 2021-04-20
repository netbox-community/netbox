import { initApiSelect } from './api';
import { initColorSelect } from './color';
import { initStaticSelect } from './static';

export function initSelect() {
  for (const func of [initApiSelect, initColorSelect, initStaticSelect]) {
    func();
  }
}
