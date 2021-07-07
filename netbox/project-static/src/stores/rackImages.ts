import { createState } from '../state';

export const rackImagesState = createState<{ hidden: boolean }>(
  { hidden: false },
  { persist: true },
);
