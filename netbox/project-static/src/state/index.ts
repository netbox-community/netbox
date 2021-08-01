/**
 * `StateManger` configuration options.
 */
interface StateOptions {
  /**
   * If true, all values will be written to localStorage when calling `set()`. Additionally, when
   * a new state instance is initialized, if the same localStorage state key (see `key` property)
   * exists in localStorage, the value will be read and used as the initial value.
   */
  persist?: boolean;

  /**
   * Use a static localStorage key instead of automatically generating one.
   */
  key?: string;
}

/**
 * Typed implementation of native `ProxyHandler`.
 */
class ProxyStateHandler<T extends Dict, K extends keyof T = keyof T> implements ProxyHandler<T> {
  public set<S extends Index<T, K>>(target: T, key: S, value: T[S]): boolean {
    target[key] = value;
    return true;
  }

  public get<G extends Index<T, K>>(target: T, key: G): T[G] {
    return target[key];
  }
  public has(target: T, key: string): boolean {
    return key in target;
  }
}

/**
 * Manage runtime and/or locally stored (via localStorage) state.
 */
export class StateManager<T extends Dict, K extends keyof T = keyof T> {
  /**
   * implemented `ProxyHandler` for the underlying `Proxy` object.
   */
  private handlers: ProxyStateHandler<T>;
  /**
   * Underlying `Proxy` object for this instance.
   */
  private proxy: T;
  /**
   * Options for this instance.
   */
  private options: StateOptions;
  /**
   * localStorage key for this instance.
   */
  private key: string = '';

  constructor(raw: T, options: StateOptions) {
    this.options = options;

    // Use static key if defined.
    if (typeof this.options.key === 'string') {
      this.key = this.options.key;
    } else {
      this.key = this.generateStateKey(raw);
    }

    if (this.options.persist) {
      const saved = this.retrieve();
      if (saved !== null) {
        raw = { ...raw, ...saved };
      }
    }

    this.handlers = new ProxyStateHandler<T>();
    this.proxy = new Proxy(raw, this.handlers);

    if (this.options.persist) {
      this.save();
    }
  }

  /**
   * Generate a semi-unique localStorage key for this instance.
   */
  private generateStateKey(obj: T): string {
    const encoded = window.btoa(Object.keys(obj).join('---'));
    return `netbox-${encoded}`;
  }

  /**
   * Get the current value of `key`.
   *
   * @param key Object key name.
   * @returns Object value.
   */
  public get<G extends Index<T, K>>(key: G): T[G] {
    return this.handlers.get(this.proxy, key);
  }

  /**
   * Set a new value for `key`.
   *
   * @param key Object key name.
   * @param value New value.
   */
  public set<G extends Index<T, K>>(key: G, value: T[G]): void {
    this.handlers.set(this.proxy, key, value);
    if (this.options.persist) {
      this.save();
    }
  }

  /**
   * Access the full instance.
   *
   * @returns StateManager instance.
   */
  public all(): T {
    return this.proxy;
  }

  /**
   * Access all state keys.
   */
  public keys(): K[] {
    return Object.keys(this.proxy) as K[];
  }

  /**
   * Access all state values.
   */
  public values(): T[K][] {
    return Object.values(this.proxy) as T[K][];
  }

  /**
   * Serialize and save the current state to localStorage.
   */
  private save(): void {
    const value = JSON.stringify(this.proxy);
    localStorage.setItem(this.key, value);
  }

  /**
   * Retrieve the serialized state object from localStorage.
   *
   * @returns Parsed state object.
   */
  private retrieve(): T | null {
    const raw = localStorage.getItem(this.key);
    if (raw !== null) {
      const data = JSON.parse(raw) as T;
      return data;
    }
    return null;
  }
}

/**
 * Create a new state object. Only one instance should exist at runtime for a given state.
 *
 * @param initial State's initial value.
 * @param options State management instance options.
 * @returns State management instance.
 */
export function createState<T extends Dict>(
  initial: T,
  options: StateOptions = {},
): StateManager<T> {
  return new StateManager<T>(initial, options);
}
