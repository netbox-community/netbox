import { createState } from '../state';

export type RackViewSelection = 'images-and-labels' | 'images-only' | 'labels-only';

export const rackImagesState = createState<{ view: RackViewSelection }>(
  { view: 'images-and-labels' },
  { persist: true },
);
