// The GraphiQL interface served at /graphql/ (see templates/graphql/graphiql.html). build.mjs
// bundles it separately from netbox.js, along with the web workers that GraphiQL's editor needs.
import { explorerPlugin } from '@graphiql/plugin-explorer';
import { createGraphiQLFetcher } from '@graphiql/toolkit';
import { GraphiQL, HISTORY_PLUGIN } from 'graphiql';
import { createElement } from 'react';
import { createRoot } from 'react-dom/client';
// Includes Monaco's styles (see build.mjs)
import 'graphiql/style.css';
import '@graphiql/plugin-explorer/style.css';

const DEFAULT_QUERY = `# Welcome to GraphiQL, a web-based client for NetBox's
# GraphQL API.
#
# Write a query in this editor, which suggests fields
# and highlights errors as you type, and run it to see
# the result. The sidebar on the left offers:
#
#   Docs      Browse the types and fields in the schema
#   History   Revisit queries you've run before
#   Explorer  Build a query by selecting fields
#
# Run query:     Ctrl-Enter (Cmd-Enter on macOS)
# Autocomplete:  Ctrl-Space, or just start typing
#
# For example, this query returns the name, status and
# tenant of the first five sites:

{
  site_list(pagination: {limit: 5}) {
    name
    status
    tenant {
      name
    }
  }
}
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
  history.replaceState(
    '',
    document.title,
    window.location.pathname + window.location.search + remainingHash,
  );
  return query;
}

const container = document.getElementById('graphiql')!;

// Monaco (GraphiQL's editor) runs its language services in web workers. Browsers won't start a
// worker from another origin, which static files may be served from, so the page provides a URL
// for each worker on NetBox's own origin (see GraphiQLWorkerView).
self.MonacoEnvironment = {
  getWorker(_workerId, label) {
    const name = label === 'json' || label === 'graphql' ? label : 'editor';
    return new Worker(container.dataset[`${name}Worker`]!);
  },
};

const sharedQuery = takeSharedQuery();
const fetcher = createGraphiQLFetcher({ url: window.location.href });

createRoot(container).render(
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
