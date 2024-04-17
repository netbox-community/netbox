import Clipboard from 'clipboard';
import { getElements } from './util';

export function initClipboard(): void {
  for (const element of getElements('.copy-content')) {
    new Clipboard(element);
  }
}
