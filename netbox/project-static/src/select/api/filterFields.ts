import { isTruthy } from '../../util';
import { isDataFilterFields } from './types';

import type { Stringifiable } from 'query-string';
import type { FilterFieldValue } from './types';

/**
 * Extension of built-in `Map` to add convenience functions.
 */
export class FilterFieldMap extends Map<string, FilterFieldValue> {
  /**
   * Get the query parameter key based on field name.
   *
   * @param fieldName Related field name.
   * @returns `queryParam` key.
   */
  public queryParam(fieldName: string): Nullable<FilterFieldValue['queryParam']> {
    const value = this.get(fieldName);
    if (typeof value !== 'undefined') {
      return value.queryParam;
    }
    return null;
  }

  /**
   * Get the query parameter value based on field name.
   *
   * @param fieldName Related field name.
   * @returns `queryValue` value, or an empty array if there is no corresponding Map entry.
   */
  public queryValue(fieldName: string): FilterFieldValue['queryValue'] {
    const value = this.get(fieldName);
    if (typeof value !== 'undefined') {
      return value.queryValue;
    }
    return [];
  }

  /**
   * Update the value of a field when the value changes.
   *
   * @param fieldName Related field name.
   * @param queryValue New value.
   * @returns `true` if the update was successful, `false` if there was no corresponding Map entry.
   */
  public updateValue(fieldName: string, queryValue: FilterFieldValue['queryValue']): boolean {
    const current = this.get(fieldName);
    if (isTruthy(current)) {
      const { queryParam, includeNull } = current;
      this.set(fieldName, { queryParam, queryValue, includeNull });
      return true;
    }
    return false;
  }

  /**
   * Populate the underlying map based on the JSON passed in the `data-filter-fields` attribute.
   *
   * @param json Raw JSON string from `data-filter-fields` attribute.
   */
  public addFromJson(json: string | null | undefined): void {
    if (isTruthy(json)) {
      const deserialized = JSON.parse(json);
      // Ensure the value is the data structure we expect.
      if (isDataFilterFields(deserialized)) {
        for (const { queryParam, fieldName, defaultValue, includeNull } of deserialized) {
          let queryValue = [] as Stringifiable[];
          if (isTruthy(defaultValue)) {
            // Add the default value, if it exists.
            if (Array.isArray(defaultValue)) {
              // If the default value is an array, add all elements to the value.
              queryValue = [...queryValue, ...defaultValue];
            } else {
              queryValue = [defaultValue];
            }
          }
          // Populate the underlying map with the initial data.
          this.set(fieldName, { queryParam, queryValue, includeNull });
        }
      } else {
        throw new Error(
          `Data from 'data-filter-fields' attribute is improperly formatted: '${json}'`,
        );
      }
    }
  }
}
