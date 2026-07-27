// Tests the real DynamicTomSelect.load() method directly (via its
// prototype), covering the sequence-guard and loading-state invariants
// added to fix netbox-community/netbox#22694. A minimal fake `self` object
// stands in for a real Tom Select instance, and global fetch() is mocked
// with controllable resolution timing -- this avoids needing jsdom (not a
// dependency of this repo) while still exercising the actual production
// code, not a reimplementation of it.
import test from 'node:test';
import assert from 'node:assert/strict';
import { DynamicTomSelect } from '../src/select/classes/dynamicTomSelect';

function createFakeSelf(): any {
  return {
    loading: 0,
    loadSequence: 0,
    wrapper: { classList: { add() {}, remove() {} } },
    settings: { loadingClass: 'loading' },
    options: {},
    nullOption: null,
    input: { getAttribute: () => null },
    clearOptions() {},
    addOption() {},
    loadCallback(options: unknown[]) {
      // Mirrors real Tom Select behavior (verified against
      // node_modules/tom-select/src/tom-select.ts): the success path
      // decrements loading and clears the loading class itself, the same
      // way our stale-discard path now does.
      this.lastLoadedOptions = options;
      this.loading = Math.max(this.loading - 1, 0);
    },
    setValue() {},
  };
}

function mockFetchQueue() {
  const pending: { resolve: (data: unknown) => void }[] = [];
  (globalThis as any).fetch = () => {
    return new Promise(resolve => {
      pending.push({
        resolve: (data: unknown) => resolve({ json: async () => data }),
      });
    });
  };
  return pending;
}

async function flush() {
  for (let i = 0; i < 5; i++) {
    await new Promise(resolve => setImmediate(resolve));
  }
}

test('a stale response that resolves after a newer request has started is discarded', async () => {
  const pending = mockFetchQueue();
  const self = createFakeSelf();
  self.getRequestUrl = () => 'http://example.test/api/1/';

  DynamicTomSelect.prototype.load.call(self, '', undefined); // sequence 1
  DynamicTomSelect.prototype.load.call(self, '', undefined); // sequence 2, supersedes it

  // Resolve the newer request first, then the older (now-stale) one --
  // simulating an out-of-order network response.
  pending[1].resolve({ results: [] });
  pending[0].resolve({ results: [] });

  await flush();

  assert.equal(self.loadSequence, 2, 'sequence counter should reflect two load() calls');
  assert.equal(self.loading, 0, 'loading must return to zero once both requests have settled');
});

test('a call that aborts early (e.g. a cleared path dependency) still invalidates an older in-flight request', async () => {
  const pending = mockFetchQueue();
  const self = createFakeSelf();
  let callCount = 0;
  self.getRequestUrl = () => {
    callCount += 1;
    // First call returns a real URL (request goes in flight); second call
    // simulates a cleared path dependency, aborting before fetch() is ever
    // reached.
    return callCount === 1 ? 'http://example.test/api/1/' : '';
  };

  DynamicTomSelect.prototype.load.call(self, '', undefined); // sequence 1, in flight
  const loadingAfterFirstCall = self.loading;

  DynamicTomSelect.prototype.load.call(self, '', undefined); // sequence 2, aborts early (no URL)

  assert.equal(
    self.loadSequence,
    2,
    'loadSequence must be bumped even by a call that aborts early, so the earlier in-flight request is correctly treated as stale'
  );

  pending[0].resolve({ results: [] });
  await flush();

  assert.equal(loadingAfterFirstCall, 1, 'loading should have been incremented for the first, real request');
  assert.equal(self.loading, 0, 'loading must not be left stuck above zero after the stale request settles');
});
