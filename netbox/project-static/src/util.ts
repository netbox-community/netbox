import Cookie from 'cookie';
export function isApiError(data: Record<string, unknown>): data is APIError {
  return 'error' in data && 'exception' in data;
}

export function hasError(data: Record<string, unknown>): data is ErrorBase {
  return 'error' in data;
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

export async function apiGetBase<T extends Record<string, unknown>>(
  url: string,
): Promise<T | ErrorBase | APIError> {
  const token = getCsrfToken();
  const res = await fetch(url, {
    method: 'GET',
    headers: { 'X-CSRFToken': token },
    credentials: 'same-origin',
  });
  const contentType = res.headers.get('Content-Type');
  if (typeof contentType === 'string' && contentType.includes('text')) {
    const error = await res.text();
    return { error } as ErrorBase;
  }

  const json = (await res.json()) as T | APIError;
  if (!res.ok && Array.isArray(json)) {
    const error = json.join('\n');
    return { error } as ErrorBase;
  }
  return json;
}

export async function apiPostForm<
  T extends Record<string, unknown>,
  R extends Record<string, unknown>
>(url: string, data: T): Promise<R | ErrorBase | APIError> {
  const token = getCsrfToken();
  const body = new URLSearchParams();
  for (const [k, v] of Object.entries(data)) {
    body.append(k, String(v));
  }
  const res = await fetch(url, {
    method: 'POST',
    body,
    headers: { 'X-CSRFToken': token },
  });

  const contentType = res.headers.get('Content-Type');
  if (typeof contentType === 'string' && contentType.includes('text')) {
    let error = await res.text();
    if (contentType.includes('text/html')) {
      error = res.statusText;
    }
    return { error } as ErrorBase;
  }

  const json = (await res.json()) as R | APIError;
  if (!res.ok && 'detail' in json) {
    return { error: json.detail as string } as ErrorBase;
  }
  return json;
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
