type Primitives = string | number | boolean | undefined | null;

type JSONAble = Primitives | Primitives[] | { [k: string]: JSONAble } | JSONAble[];

type Dict<T extends unknown = unknown> = Record<string, T>;

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

type JobResultLog = {
  message: string;
  status: 'success' | 'warning' | 'danger' | 'info';
};

type JobStatus = {
  label: string;
  value: 'completed' | 'failed' | 'errored' | 'running';
};

type APIJobResult = {
  completed: string;
  created: string;
  data: {
    log: JobResultLog[];
    output: string;
  };
  display: string;
  id: number;
  job_id: string;
  name: string;
  obj_type: string;
  status: JobStatus;
  url: string;
  user: {
    display: string;
    username: string;
    id: number;
    url: string;
  };
};

type APIUserConfig = {
  tables: { [k: string]: { columns: string[]; available_columns: string[] } };
  [k: string]: unknown;
};

interface ObjectWithGroup extends APIObjectBase {
  group: Nullable<APIReference>;
}

declare const messages: string[];

type FormControls = HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
