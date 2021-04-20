import Cookie from 'cookie';

type APIRes<T> = T | ErrorBase | APIError;
type Method = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
type ReqData = URLSearchParams | Dict | undefined | unknown;
type SelectedOption = { name: string; options: string[] };

export function isApiError(data: Record<string, unknown>): data is APIError {
  return 'error' in data && 'exception' in data;
}

export function hasError(data: Record<string, unknown>): data is ErrorBase {
  return 'error' in data;
}

/**
 * Create a slug from any input string.
 *
 * @param slug Original string.
 * @param chars Maximum number of characters.
 * @returns Slugified string.
 */
export function slugify(slug: string, chars: number): string {
  return slug
    .replace(/[^\-\.\w\s]/g, '') // Remove unneeded chars
    .replace(/^[\s\.]+|[\s\.]+$/g, '') // Trim leading/trailing spaces
    .replace(/[\-\.\s]+/g, '-') // Convert spaces and decimals to hyphens
    .toLowerCase() // Convert to lowercase
    .substring(0, chars); // Trim to first chars chars
}

/**
 * Type guard to determine if a value is not null, undefined, or empty.
 */
export function isTruthy<V extends string | number | boolean | null | undefined>(
  value: V,
): value is NonNullable<V> {
  const badStrings = ['', 'null', 'undefined'];
  if (typeof value === 'string' && !badStrings.includes(value)) {
    return true;
  } else if (typeof value === 'number') {
    return true;
  } else if (typeof value === 'boolean') {
    return true;
  }
  return false;
}

/**
 * Retrieve the CSRF token from cookie storage.
 */
export function getCsrfToken(): string {
  const { csrftoken: csrfToken } = Cookie.parse(document.cookie);
  if (typeof csrfToken === 'undefined') {
    throw new Error('Invalid or missing CSRF token');
  }
  return csrfToken;
}

export async function apiRequest<R extends Dict, D extends ReqData = undefined>(
  url: string,
  method: Method,
  data?: D,
): Promise<APIRes<R>> {
  const token = getCsrfToken();
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
): Promise<APIRes<R>> {
  return await apiRequest(url, 'PATCH', data);
}

export async function apiGetBase<R extends Dict>(url: string): Promise<APIRes<R>> {
  return await apiRequest<R>(url, 'GET');
}

export async function apiPostForm<R extends Dict, D extends Dict>(
  url: string,
  data: D,
): Promise<APIRes<R>> {
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
) {
  for (const query of key) {
    for (const element of document.querySelectorAll(query)) {
      if (element !== null) {
        yield element;
      }
    }
  }
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

export function getSelectedOptions<E extends HTMLElement>(base: E): SelectedOption[] {
  let selected = [] as SelectedOption[];
  for (const element of base.querySelectorAll<HTMLSelectElement>('select')) {
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

export function getNetboxData(key: string): string | null {
  if (!key.startsWith('data-')) {
    key = `data-${key}`;
  }
  for (const element of getElements('body > div#netbox-data > *')) {
    const value = element.getAttribute(key);
    if (isTruthy(value)) {
      return value;
    }
  }
  return null;
}

/**
 * Toggle visibility of card loader.
 */
export function toggleLoader(action: 'show' | 'hide') {
  const spinnerContainer = document.querySelector('div.card-overlay');
  if (spinnerContainer !== null) {
    if (action === 'show') {
      spinnerContainer.classList.remove('d-none');
    } else {
      spinnerContainer.classList.add('d-none');
    }
  }
}
