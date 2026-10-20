/**
 * A primitive value which can be sent as a URL query parameter value. `null` is sent as an empty
 * value (`?key=`), and `undefined` is omitted.
 */
export type QueryValue = string | number | boolean | null | undefined;

/**
 * Map of string keys to primitive array values. Keys are used as URL query parameter keys. Values
 * correspond to query param values, enforced as an array for easier handling. For example, a
 * mapping of `{ site_id: [1, 2] }` is serialized as `?site_id=1&site_id=2`. Likewise,
 * `{ site_id: [1] }` is serialized as `?site_id=1`.
 */
export type QueryFilter = Map<string, QueryValue[]>;

/**
 * JSON data structure from `data-dynamic-params` attribute.
 */
export type DataDynamicParam = {
  /**
   * Name of form field to track.
   *
   * @example [name="tenant_group"]
   */
  fieldName: string;
  /**
   * Query param key.
   *
   * @example group_id
   */
  queryParam: string;
};

/**
 * `queryParams` Map value.
 */
export type QueryParam = {
  queryParam: string;
  queryValue: QueryValue[];
};

/**
 * Map of string keys to string values. Used to track variables within URLs from the server. For
 * example, `/api/$key/thing`. `PathFilter` tracks `$key` as `{ key: '' }` in the map, and when the
 * value is later known, the value is set — `{ key: 'value' }`, and the URL is transformed to
 * `/api/value/thing`.
 */
export type PathFilter = Map<string, string>;

/**
 * Strict Type Guard to determine if a deserialized value from the `data-dynamic-params` attribute
 * is of type `DataDynamicParam[]`.
 *
 * @param value Deserialized value from `data-dynamic-params` attribute.
 */
export function isDataDynamicParams(value: unknown): value is DataDynamicParam[] {
  if (Array.isArray(value)) {
    for (const item of value) {
      if (typeof item === 'object' && item !== null) {
        if ('fieldName' in item && 'queryParam' in item) {
          return (
            typeof (item as DataDynamicParam).fieldName === 'string' &&
            typeof (item as DataDynamicParam).queryParam === 'string'
          );
        }
      }
    }
  }
  return false;
}
