import { isTruthy } from '../../util';
import { isDataDynamicParams } from './types';

import type { QueryParam } from './types';

/**
 * Extension of built-in `Map` to add convenience functions.
 */
export class DynamicParamsMap extends Map<string, QueryParam> {
  /**
   * Get the query parameter key based on field name.
   *
   * @param fieldName Related field name.
   * @returns `queryParam` key.
   */
  public queryParam(fieldName: string): Nullable<QueryParam['queryParam']> {
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
  public queryValue(fieldName: string): QueryParam['queryValue'] {
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
  public updateValue(fieldName: string, queryValue: QueryParam['queryValue']): boolean {
    const current = this.get(fieldName);
    if (isTruthy(current)) {
      const { queryParam } = current;
      this.set(fieldName, { queryParam, queryValue });
      return true;
    }
    return false;
  }

  /**
   * Populate the underlying map based on the JSON passed in the `data-dynamic-params` attribute.
   *
   * @param json Raw JSON string from `data-dynamic-params` attribute.
   */
  public addFromJson(json: string | null | undefined): void {
    if (isTruthy(json)) {
      const deserialized = JSON.parse(json);
      // Ensure the value is the data structure we expect.
      if (isDataDynamicParams(deserialized)) {
        for (const { queryParam, fieldName } of deserialized) {
          // Populate the underlying map with the initial data.
          this.set(fieldName, { queryParam, queryValue: [] });
        }
      } else {
        throw new Error(
          `Data from 'data-dynamic-params' attribute is improperly formatted: '${json}'`,
        );
      }
    }
  }
}
