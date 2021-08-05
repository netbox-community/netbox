type Primitives = string | number | boolean | undefined | null;

type JSONAble = Primitives | Primitives[] | { [k: string]: JSONAble } | JSONAble[];

type Dict<T extends unknown = unknown> = Record<string, T>;

type Nullable<T> = T | null;

interface Window {
  /**
   * Bootstrap Modal Instance.
   */
  Modal: typeof import('bootstrap').Modal;

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
  display: string;
  name?: Nullable<string>;
  url: string;
  _depth?: number;
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

type LLDPInterface = {
  parent_interface: string | null;
  remote_chassis_id: string | null;
  remote_port: string | null;
  remote_port_description: string | null;
  remote_system_capab: string[];
  remote_system_description: string | null;
  remote_system_enable_capab: string[];
  remote_system_name: string | null;
};

type LLDPNeighborDetail = {
  get_lldp_neighbors_detail: { [interface: string]: LLDPInterface[] };
};

type DeviceConfig = {
  get_config: {
    candidate: string;
    running: string;
    startup: string;
  };
};

type DeviceEnvironment = {
  cpu?: {
    [core: string]: { '%usage': number };
  };
  memory?: {
    available_ram: number;
    used_ram: number;
  };
  power?: {
    [psu: string]: { capacity: number; output: number; status: boolean };
  };
  temperature?: {
    [sensor: string]: {
      is_alert: boolean;
      is_critical: boolean;
      temperature: number;
    };
  };
  fans?: {
    [fan: string]: {
      status: boolean;
    };
  };
};

type DeviceFacts = {
  fqdn: string;
  hostname: string;
  interface_list: string[];
  model: string;
  os_version: string;
  serial_number: string;
  uptime: number;
  vendor: string;
};

type DeviceStatus = {
  get_environment: DeviceEnvironment | ErrorBase;
  get_facts: DeviceFacts | ErrorBase;
};

interface ObjectWithGroup extends APIObjectBase {
  group: Nullable<APIReference>;
}

declare const messages: string[];

type FormControls = HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;

type ColorMode = 'light' | 'dark';
type ColorModePreference = ColorMode | 'none';
type ConfigContextFormat = 'json' | 'yaml';

type UserPreferences = {
  ui: {
    colorMode: ColorMode;
    showRackImages: boolean;
  };
};
