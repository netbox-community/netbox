import { createState } from '../state';

export const previousPKCheckState = createState<{ hidden: boolean }>(
  { hidden: false },
  { persist: false },
);

