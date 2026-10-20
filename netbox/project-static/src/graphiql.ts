// The GraphiQL interface served at /graphql/ (see templates/graphql/graphiql.html). build.mjs
// bundles it separately from netbox.js, along with the web workers that GraphiQL's editor needs.
import { explorerPlugin } from '@graphiql/plugin-explorer';
import { createGraphiQLFetcher } from '@graphiql/toolkit';
import { GraphiQL, HISTORY_PLUGIN } from 'graphiql';
import { createElement } from 'react';
import { createRoot } from 'react-dom/client';
// GraphiQL's stylesheet includes Monaco's. Import it after the scripts, so that it follows the
// copy of Monaco's styles that Monaco's own modules import.
import 'graphiql/style.css';
import '@graphiql/plugin-explorer/style.css';

const DEFAULT_QUERY = `# Welcome to GraphiQL 🍓
#
# GraphiQL is an in-browser tool for writing, validating, and
# testing GraphQL queries.
#
# Type queries into this side of the screen, and you will see intelligent
# typeaheads aware of the current GraphQL type schema and live syntax and
# validation errors highlighted within the text.
#
# GraphQL queries typically start with a "{" character. Lines that starts
# with a # are ignored.
#
# An example GraphQL query might look like:
#
#     {
#       field(arg: "value") {
#         subField
#       }
#     }
#
# Keyboard shortcuts:
#
#       Run Query:  Ctrl-Enter (or press the play button above)
#
#   Auto Complete:  Ctrl-Space (or just start typing)
#
`;

/**
 * Return the query shared by a `#query=` link, if any. Remove it from the URL, so that copying the
 * URL doesn't share a stale query.
 */
function takeSharedQuery(): string | undefined {
  const hashArgs = new URLSearchParams(window.location.hash.substring(1));
  const query = hashArgs.get('query');
  if (query === null) {
    return undefined;
  }
  hashArgs.delete('query');
  const remainingHash = hashArgs.size ? `#${hashArgs.toString()}` : '';
  history.pushState(
    '',
    document.title,
    window.location.pathname + window.location.search + remainingHash,
  );
  return query;
}

// Monaco (GraphiQL's editor) runs its language services in web workers. build.mjs writes them
// beside this bundle, so they are served from the page's own origin, as browsers require.
self.MonacoEnvironment = {
  getWorker(_workerId, label) {
    const name = label === 'json' || label === 'graphql' ? label : 'editor';
    return new Worker(new URL(`${name}.worker.js`, import.meta.url));
  },
};

const sharedQuery = takeSharedQuery();
const fetcher = createGraphiQLFetcher({ url: window.location.href });

createRoot(document.getElementById('graphiql')!).render(
  createElement(GraphiQL, {
    fetcher,
    // Passing any plugins replaces the default History plugin, so include it explicitly
    plugins: [HISTORY_PLUGIN, explorerPlugin()],
    defaultEditorToolsVisibility: true,
    inputValueDeprecation: true,
    defaultQuery: DEFAULT_QUERY,
    initialQuery: sharedQuery,
  }),
);
