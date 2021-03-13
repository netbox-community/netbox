import Cookie from 'cookie';

export function isApiError(data: Record<string, unknown>): data is APIError {
  return 'error' in data;
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

/**
 * Fetch data from the NetBox API (authenticated).
 * @param url API endpoint
 */
export async function getApiData<T extends APIObjectBase>(
  url: string,
): Promise<APIAnswer<T> | APIError> {
  const token = getCsrfToken();
  const res = await fetch(url, {
    method: 'GET',
    headers: { 'X-CSRFToken': token },
  });
  const json = (await res.json()) as APIAnswer<T> | APIError;
  return json;
}

export function getElements<K extends keyof SVGElementTagNameMap>(
  key: K,
): Generator<SVGElementTagNameMap[K]>;
export function getElements<K extends keyof HTMLElementTagNameMap>(
  key: K,
): Generator<HTMLElementTagNameMap[K]>;
export function getElements<E extends Element>(key: string): Generator<E>;
export function* getElements(
  key: string | keyof HTMLElementTagNameMap | keyof SVGElementTagNameMap,
) {
  for (const element of document.querySelectorAll(key)) {
    if (element !== null) {
      yield element;
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
