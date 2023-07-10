import Clipboard from 'clipboard';
import { getElements } from './util';

export function initClipboard(): void {
  for (const element of getElements('a.copy-content')) {
    new Clipboard(element);
  }
}
