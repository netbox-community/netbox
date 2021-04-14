import Clipboard from 'clipboard';
import { getElements } from './util';

export function initClipboard() {
  for (const element of getElements('a.copy-token', 'button.copy-secret')) {
    new Clipboard(element);
  }
}
