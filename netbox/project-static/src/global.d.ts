type Primitives = string | number | boolean | undefined | null;

type JSONAble = Primitives | Primitives[] | { [k: string]: JSONAble } | JSONAble[];

type Nullable<T> = T | null;

type APIAnswer<T> = {
  count: number;
  next: Nullable<string>;
  previous: Nullable<string>;
  results: T[];
};

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

type APISecret = {
  assigned_object: APIObjectBase;
  assigned_object_id: number;
  assigned_object_type: string;
  created: string;
  custom_fields: Record<string, unknown>;
  display: string;
  hash: string;
  id: number;
  last_updated: string;
  name: string;
  plaintext: Nullable<string>;
  role: APIObjectBase;
  tags: number[];
  url: string;
};

interface ObjectWithGroup extends APIObjectBase {
  group: Nullable<APIReference>;
}

declare const messages: string[];

type FormControls = HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
