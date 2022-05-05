import { initConnectionToggle } from './connectionToggle';
import { initDepthToggle } from './depthToggle';
import { initMoveButtons } from './moveOptions';
import { initReslug } from './reslug';
import { initSelectAll } from './selectAll';
import { initSelectMultiple } from './selectMultiple';

export function initButtons(): void {
  for (const func of [
    initDepthToggle,
    initConnectionToggle,
    initReslug,
    initSelectAll,
    initSelectMultiple,
    initMoveButtons,
  ]) {
    func();
  }
}
