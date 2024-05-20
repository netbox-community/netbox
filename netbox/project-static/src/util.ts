type Method = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
type ReqData = URLSearchParams | Dict | undefined | unknown;
type SelectedOption = { name: string; options: string[] };

declare global {
    interface Window { CSRF_TOKEN: any; }
}

/**
 * Infer valid HTMLElement props based on element name.
 */
type InferredProps<
  // Element name.
  T extends keyof HTMLElementTagNameMap,
  // Element type.
  E extends HTMLElementTagNameMap[T] = HTMLElementTagNameMap[T],
> = Partial<Record<keyof E, E[keyof E]>>;

export function isApiError(data: Record<string, unknown>): data is APIError {
  return 'error' in data && 'exception' in data;
}

export function hasError<E extends ErrorBase = ErrorBase>(
  data: Record<string, unknown>,
): data is E {
  return 'error' in data;
}

export function hasMore(data: APIAnswer<APIObjectBase>): data is APIAnswerWithNext<APIObjectBase> {
  return typeof data.next === 'string';
}

/**
 * Type guard to determine if a value is not null, undefined, or empty.
 */
export function isTruthy<V extends unknown>(value: V): value is NonNullable<V> {
  const badStrings = ['', 'null', 'undefined'];
  if (Array.isArray(value)) {
    return value.length > 0;
  } else if (typeof value === 'string' && !badStrings.includes(value)) {
    return true;
  } else if (typeof value === 'number') {
    return true;
  } else if (typeof value === 'boolean') {
    return true;
  } else if (typeof value === 'object' && value !== null) {
    return true;
  }
  return false;
}

/**
 * Type guard to determine if all elements of an array are not null or undefined.
 *
 * @example
 * ```js
 * const elements = [document.getElementById("element1"), document.getElementById("element2")];
 * if (all(elements)) {
 *   const [element1, element2] = elements;
 *   // element1 and element2 are now of type HTMLElement, not Nullable<HTMLElement>.
 * }
 * ```
 */
export function all<T extends unknown>(values: T[]): values is NonNullable<T>[] {
  return values.every(value => typeof value !== 'undefined' && value !== null);
}

/**
 * Deselect all selected options and reset the field value of a select element.
 *
 * @example
 * ```js
 * const select = document.querySelectorAll<HTMLSelectElement>("select.example");
 * select.value = "test";
 * console.log(select.value);
 * // test
 * resetSelect(select);
 * console.log(select.value);
 * // ''
 * ```
 */
export function resetSelect<S extends HTMLSelectElement>(select: S): void {
  for (const option of select.options) {
    if (option.selected) {
      option.selected = false;
    }
  }
  select.value = '';
}

/**
 * Type guard to determine if a value is an `Element`.
 */
export function isElement(obj: Element | null | undefined): obj is Element {
  return typeof obj !== null && typeof obj !== 'undefined';
}

export async function apiRequest<R extends Dict, D extends ReqData = undefined>(
  url: string,
  method: Method,
  data?: D,
): Promise<APIResponse<R>> {
  const token = window.CSRF_TOKEN;
  const headers = new Headers({ 'X-CSRFToken': token });

  let body;
  if (typeof data !== 'undefined') {
    body = JSON.stringify(data);
    headers.set('content-type', 'application/json');
  }

  const res = await fetch(url, { method, body, headers, credentials: 'same-origin' });
  const contentType = res.headers.get('Content-Type');
  if (typeof contentType === 'string' && contentType.includes('text')) {
    const error = await res.text();
    return { error } as ErrorBase;
  }
  const json = (await res.json()) as R | APIError;
  if (!res.ok && Array.isArray(json)) {
    const error = json.join('\n');
    return { error } as ErrorBase;
  } else if (!res.ok && 'detail' in json) {
    return { error: json.detail } as ErrorBase;
  }
  return json;
}

export async function apiPatch<R extends Dict, D extends ReqData = Dict>(
  url: string,
  data: D,
): Promise<APIResponse<R>> {
  return await apiRequest(url, 'PATCH', data);
}

export async function apiGetBase<R extends Dict>(url: string): Promise<APIResponse<R>> {
  return await apiRequest<R>(url, 'GET');
}

export async function apiPostForm<R extends Dict, D extends Dict>(
  url: string,
  data: D,
): Promise<APIResponse<R>> {
  const body = new URLSearchParams();
  for (const [k, v] of Object.entries(data)) {
    body.append(k, String(v));
  }
  return await apiRequest<R, URLSearchParams>(url, 'POST', body);
}

/**
 * Fetch data from the NetBox API (authenticated).
 * @param url API endpoint
 */
export async function getApiData<T extends APIObjectBase>(
  url: string,
): Promise<APIAnswer<T> | ErrorBase | APIError> {
  return await apiGetBase<APIAnswer<T>>(url);
}

export function getElements<K extends keyof SVGElementTagNameMap>(
  ...key: K[]
): Generator<SVGElementTagNameMap[K]>;
export function getElements<K extends keyof HTMLElementTagNameMap>(
  ...key: K[]
): Generator<HTMLElementTagNameMap[K]>;
export function getElements<E extends Element>(...key: string[]): Generator<E>;
export function* getElements(
  ...key: (string | keyof HTMLElementTagNameMap | keyof SVGElementTagNameMap)[]
): Generator<Element> {
  for (const query of key) {
    for (const element of document.querySelectorAll(query)) {
      if (element !== null) {
        yield element;
      }
    }
  }
}

export function getElement<E extends HTMLElement>(id: string): Nullable<E> {
  return document.getElementById(id) as Nullable<E>;
}

export function removeElements(...selectors: string[]): void {
  for (const element of getElements(...selectors)) {
    element.remove();
  }
}

export function elementWidth<E extends HTMLElement>(element: Nullable<E>): number {
  let width = 0;
  if (element !== null) {
    const style = getComputedStyle(element);
    const pre = style.width.replace('px', '');
    width = parseFloat(pre);
  }
  return width;
}

/**
 * scrollTo() wrapper that calculates a Y offset relative to `element`, but also factors in an
 * offset relative to div#content-title. This ensures we scroll to the element, but leave enough
 * room to see said element.
 *
 * @param element Element to scroll to
 * @param offset Y Offset. 0 by default, to take into account the NetBox header.
 */
export function scrollTo(element: Element, offset: number = 0): void {
  let yOffset = offset;
  const title = document.getElementById('content-title') as Nullable<HTMLDivElement>;
  if (title !== null) {
    // If the #content-title element exists, add it to the offset.
    yOffset += title.getBoundingClientRect().bottom;
  }
  // Calculate the scrollTo target.
  const top = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
  // Scroll to the calculated location.
  window.scrollTo({ top, behavior: 'smooth' });
  return;
}

/**
 * Iterate through a select element's options and return an array of options that are selected.
 *
 * @param base Select element.
 * @param selector Optionally specify a selector. 'select' by default.
 * @returns Array of selected options.
 */
export function getSelectedOptions<E extends HTMLElement>(
  base: E,
  selector: string = 'select',
): SelectedOption[] {
  let selected = [] as SelectedOption[];
  for (const element of base.querySelectorAll<HTMLSelectElement>(selector)) {
    if (element !== null) {
      const select = { name: element.name, options: [] } as SelectedOption;
      for (const option of element.options) {
        if (option.selected) {
          select.options.push(option.value);
        }
      }
      selected = [...selected, select];
    }
  }
  return selected;
}

/**
 * Toggle visibility of an element.
 */
export function toggleVisibility<E extends HTMLElement | SVGElement>(
  element: E | null,
  action?: 'show' | 'hide',
): void {
  if (element !== null) {
    if (typeof action === 'undefined') {
      // No action is passed, so we should toggle the existing state.
      const current = window.getComputedStyle(element).display;
      if (current === 'none') {
        element.style.display = '';
      } else {
        element.style.display = 'none';
      }
    } else {
      if (action === 'show') {
        element.style.display = '';
      } else {
        element.style.display = 'none';
      }
    }
  }
}

/**
 * Toggle visibility of card loader.
 */
export function toggleLoader(action: 'show' | 'hide'): void {
  for (const element of getElements<HTMLDivElement>('div.card-overlay')) {
    toggleVisibility(element, action);
  }
}

/**
 * Get the value of every cell in a table.
 * @param table Table Element
 */
export function* getRowValues(table: HTMLTableRowElement): Generator<string> {
  for (const element of table.querySelectorAll<HTMLTableCellElement>('td')) {
    if (element !== null) {
      if (isTruthy(element.innerText) && element.innerText !== '—') {
        yield replaceAll(element.innerText, '[\n\r]', '').trim();
      }
    }
  }
}

/**
 * Recurse upward through an element's siblings until an element matching the query is found.
 *
 * @param base Base Element
 * @param query CSS Query
 * @param boundary Optionally specify a CSS Query which, when matched, recursion will cease.
 */
export function findFirstAdjacent<R extends HTMLElement, B extends Element = Element>(
  base: B,
  query: string,
  boundary?: string,
): Nullable<R> {
  function atBoundary<E extends Element | null>(element: E): boolean {
    if (typeof boundary === 'string' && element !== null) {
      if (element.matches(boundary)) {
        return true;
      }
    }
    return false;
  }
  function match<P extends Element | null>(parent: P): Nullable<R> {
    if (parent !== null && parent.parentElement !== null && !atBoundary(parent)) {
      for (const child of parent.parentElement.querySelectorAll<R>(query)) {
        if (child !== null) {
          return child;
        }
      }
      return match(parent.parentElement.parentElement);
    }
    return null;
  }
  return match(base);
}

/**
 * Helper for creating HTML elements.
 *
 * @param tag HTML element type.
 * @param properties Properties/attributes to apply to the element.
 * @param classes CSS classes to apply to the element.
 * @param children Child elements.
 */
export function createElement<
  // Element name.
  T extends keyof HTMLElementTagNameMap,
  // Element props.
  P extends InferredProps<T>,
  // Child element type.
  C extends HTMLElement = HTMLElement,
>(
  tag: T,
  properties: P | null,
  classes: Nullable<string[]> = null,
  children: C[] = [],
): HTMLElementTagNameMap[T] {
  // Create the base element.
  const element = document.createElement<T>(tag);

  if (properties !== null) {
    for (const k of Object.keys(properties)) {
      // Add each property to the element.
      const key = k as keyof InferredProps<T>;
      const value = properties[key] as NonNullable<P[keyof P]>;
      if (key in element) {
        element[key] = value;
      }
    }
  }

  // Add each CSS class to the element's class list.
  if (classes !== null && classes.length > 0) {
    element.classList.add(...classes);
  }

  for (const child of children) {
    // Add each child element to the base element.
    element.appendChild(child);
  }
  return element as HTMLElementTagNameMap[T];
}

/**
 * Deduplicate an array of objects based on the value of a property.
 *
 * @example
 * ```js
 * const withDups = [{id: 1, name: 'One'}, {id: 2, name: 'Two'}, {id: 1, name: 'Other One'}];
 * const withoutDups = uniqueByProperty(withDups, 'id');
 * console.log(withoutDups);
 * // [{id: 1, name: 'One'}, {id: 2, name: 'Two'}]
 * ```
 * @param arr Array of objects to deduplicate.
 * @param prop Object property to use as a unique key.
 * @returns Deduplicated array.
 */
export function uniqueByProperty<T extends unknown, P extends keyof T>(arr: T[], prop: P): T[] {
  const baseMap = new Map<T[P], T>();
  for (const item of arr) {
    const value = item[prop];
    if (!baseMap.has(value)) {
      baseMap.set(value, item);
    }
  }
  return Array.from(baseMap.values());
}

/**
 * Replace all occurrences of a pattern with a replacement string.
 *
 * This is a browser-compatibility-focused drop-in replacement for `String.prototype.replaceAll()`,
 * introduced in ES2021.
 *
 * @param input string to be processed.
 * @param pattern regex pattern string or RegExp object to search for.
 * @param replacement replacement substring with which `pattern` matches will be replaced.
 * @returns processed version of `input`.
 */
export function replaceAll(input: string, pattern: string | RegExp, replacement: string): string {
  // Ensure input is a string.
  if (typeof input !== 'string') {
    throw new TypeError("replaceAll 'input' argument must be a string");
  }
  // Ensure pattern is a string or RegExp.
  if (typeof pattern !== 'string' && !(pattern instanceof RegExp)) {
    throw new TypeError("replaceAll 'pattern' argument must be a string or RegExp instance");
  }
  // Ensure replacement is able to be stringified.
  switch (typeof replacement) {
    case 'boolean':
      replacement = String(replacement);
      break;
    case 'number':
      replacement = String(replacement);
      break;
    case 'string':
      break;
    default:
      throw new TypeError("replaceAll 'replacement' argument must be stringifyable");
  }

  if (pattern instanceof RegExp) {
    // Add global flag to existing RegExp object and deduplicate
    const flags = Array.from(new Set([...pattern.flags.split(''), 'g'])).join('');
    pattern = new RegExp(pattern.source, flags);
  } else {
    // Create a RegExp object with the global flag set.
    pattern = new RegExp(pattern, 'g');
  }

  return input.replace(pattern, replacement);
}
