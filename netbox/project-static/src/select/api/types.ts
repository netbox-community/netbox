import type { Stringifiable } from 'query-string';
import type { Option, Optgroup } from 'slim-select/dist/data';

/**
 * Map of string keys to primitive array values accepted by `query-string`. Keys are used as
 * URL query parameter keys. Values correspond to query param values, enforced as an array
 * for easier handling. For example, a mapping of `{ site_id: [1, 2] }` is serialized by
 * `query-string` as `?site_id=1&site_id=2`. Likewise, `{ site_id: [1] }` is serialized as
 * `?site_id=1`.
 */
export type QueryFilter = Map<string, Stringifiable[]>;

/**
 * Tracked data for a related field. This is the value of `APISelect.filterFields`.
 */
export type FilterFieldValue = {
  /**
   * Key to use in the query parameter itself.
   */
  queryParam: string;
  /**
   * Value to use in the query parameter for the related field.
   */
  queryValue: Stringifiable[];
  /**
   * @see `DataFilterFields.includeNull`
   */
  includeNull: boolean;
};

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
  queryValue: Stringifiable[];
};

/**
 * JSON data structure from `data-static-params` attribute.
 */
export type DataStaticParam = {
  queryParam: string;
  queryValue: Stringifiable | Stringifiable[];
};

/**
 * JSON data passed from Django on the `data-filter-fields` attribute.
 */
export type DataFilterFields = {
  /**
   * Related field form name (`[name="<fieldName>"]`)
   *
   * @example tenant_group
   */
  fieldName: string;
  /**
   * Key to use in the query parameter itself.
   *
   * @example group_id
   */
  queryParam: string;
  /**
   * Optional default value. If set, value will be added to the query parameters prior to the
   * initial API call and will be maintained until the field `fieldName` references (if one exists)
   * is updated with a new value.
   *
   * @example 1
   */
  defaultValue: Nullable<Stringifiable | Stringifiable[]>;
  /**
   * Include `null` on queries for the related field. For example, if `true`, `?<fieldName>=null`
   * will be added to all API queries for this field.
   */
  includeNull: boolean;
};

/**
 * Map of string keys to primitive values. Used to track variables within URLs from the server. For
 * example, `/api/$key/thing`. `PathFilter` tracks `$key` as `{ key: '' }` in the map, and when the
 * value is later known, the value is set — `{ key: 'value' }`, and the URL is transformed to
 * `/api/value/thing`.
 */
export type PathFilter = Map<string, Stringifiable>;

/**
 * Merge or replace incoming options with current options.
 */
export type ApplyMethod = 'merge' | 'replace';

/**
 * Trigger for which the select instance should fetch its data from the NetBox API.
 */
export type Trigger =
  /**
   * Load data when the select element is opened.
   */
  | 'open'
  /**
   * Load data when the element is loaded.
   */
  | 'load'
  /**
   * Load data when a parent element is uncollapsed.
   */
  | 'collapse';

/**
 * Strict Type Guard to determine if a deserialized value from the `data-filter-fields` attribute
 * is of type `DataFilterFields`.
 *
 * @param value Deserialized value from `data-filter-fields` attribute.
 */
export function isDataFilterFields(value: unknown): value is DataFilterFields[] {
  if (Array.isArray(value)) {
    for (const item of value) {
      if (typeof item === 'object' && item !== null) {
        if ('fieldName' in item && 'queryParam' in item) {
          return (
            typeof (item as DataFilterFields).fieldName === 'string' &&
            typeof (item as DataFilterFields).queryParam === 'string'
          );
        }
      }
    }
  }
  return false;
}

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

/**
 * Strict Type Guard to determine if a deserialized value from the `data-static-params` attribute
 * is of type `DataStaticParam[]`.
 *
 * @param value Deserialized value from `data-static-params` attribute.
 */
export function isStaticParams(value: unknown): value is DataStaticParam[] {
  if (Array.isArray(value)) {
    for (const item of value) {
      if (typeof item === 'object' && item !== null) {
        if ('queryParam' in item && 'queryValue' in item) {
          return (
            typeof (item as DataStaticParam).queryParam === 'string' &&
            typeof (item as DataStaticParam).queryValue !== 'undefined'
          );
        }
      }
    }
  }
  return false;
}

/**
 * Type guard to determine if a SlimSelect `dataObject` is an `Option`.
 *
 * @param data Option or Option Group
 */
export function isOption(data: Option | Optgroup): data is Option {
  return !('options' in data);
}
