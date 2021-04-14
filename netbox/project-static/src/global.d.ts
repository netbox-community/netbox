type Primitives = string | number | boolean | undefined | null;

type JSONAble = Primitives | Primitives[] | { [k: string]: JSONAble } | JSONAble[];

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
  display?: string;
  name: string;
  url: string;
  [k: string]: JSONAble;
};

type APIKeyPair = {
  public_key: string;
  private_key: string;
};

type APIReference = {
  id: number;
  name: string;
  slug: string;
  url: string;
  _depth: number;
};

interface ObjectWithGroup extends APIObjectBase {
  group: Nullable<APIReference>;
}

declare const messages: string[];

type FormControls = HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
