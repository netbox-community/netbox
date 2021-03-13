type Nullable<T> = T | null;

type APIAnswer<T> = {
  count: number;
  next: Nullable<string>;
  previous: Nullable<string>;
  results: T[];
};

type APIError = {
  error: string;
  exception: string;
  netbox_version: string;
  python_version: string;
};

type APIObjectBase = {
  id: number;
  name: string;
  url: string;
  [k: string]: unknown;
};

interface APIReference {
  id: number;
  name: string;
  slug: string;
  url: string;
  _depth: number;
}

interface ObjectWithGroup extends APIObjectBase {
  group: Nullable<APIReference>;
}

declare const messages: string[];

type FormControls = HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
