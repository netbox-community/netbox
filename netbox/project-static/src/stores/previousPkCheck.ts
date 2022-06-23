import { createState } from '../state';

export const previousPkCheckState = createState<{ element: Nullable<HTMLInputElement> }>(
  { element: null },
  { persist: false },
);
