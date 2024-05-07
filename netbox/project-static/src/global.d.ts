type Primitives = string | number | boolean | undefined | null;

type JSONAble = Primitives | Primitives[] | { [k: string]: JSONAble } | JSONAble[];

type Dict<T extends unknown = unknown> = Record<string, T>;

type Nullable<T> = T | null;

interface Window {
  /**
   * Bootstrap Collapse Instance.
   */
  Collapse: typeof import('bootstrap').Collapse;

  /**
   * Bootstrap Modal Instance.
   */
  Modal: typeof import('bootstrap').Modal;

  /**
   * Bootstrap Popover Instance.
   */
  Popover: typeof import('bootstrap').Popover;

  /**
   * Bootstrap Toast Instance.
   */
  Toast: typeof import('bootstrap').Toast;

  /**
   * Bootstrap Tooltip Instance.
   */
  Tooltip: typeof import('bootstrap').Tooltip;
}

/**
 * Enforce string index type (not `number` or `symbol`).
 */
type Index<O extends Dict, K extends keyof O> = K extends string ? K : never;

type APIResponse<T> = T | ErrorBase | APIError;

type APIAnswer<T> = {
  count: number;
  next: Nullable<string>;
  previous: Nullable<string>;
  results: T[];
};

type APIAnswerWithNext<T> = Exclude<APIAnswer<T>, 'next'> & { next: string };

type ErrorBase = {
  error: string;
};

type APIError = {
  exception: string;
  netbox_version: string;
  python_version: string;
} & ErrorBase;

type APIObjectBase = {
  id: number;
  display: string;
  name?: Nullable<string>;
  url: string;
  _depth?: number;
  [k: string]: JSONAble;
};

type APIUserConfig = {
  tables: { [k: string]: { columns: string[]; available_columns: string[] } };
  [k: string]: unknown;
};

declare const messages: string[];

type FormControls = HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;

type ColorMode = 'light' | 'dark';
type ColorModePreference = ColorMode | 'none';
