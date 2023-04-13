import { createState } from '../state';

export const secretState = createState<{ hidden: boolean }>(
  { hidden: true },
  { persist: true, key: 'netbox-secret' },
);
