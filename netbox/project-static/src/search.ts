import { isTruthy } from './util';

/**
 * Show/hide quicksearch clear button.
 *
 * @param event "keyup" or "search" event for the quicksearch input
 */
function quickSearchEventHandler(event: Event): void {
  const quicksearch = event.currentTarget as HTMLInputElement;
  const clearbtn = document.getElementById('quicksearch_clear') as HTMLAnchorElement;
  if (isTruthy(clearbtn)) {
    if (quicksearch.value === '') {
      clearbtn.classList.add('invisible');
    } else {
      clearbtn.classList.remove('invisible');
    }
  }
}

/**
 * Update the links to export the current view with the quick search query.
 *
 * @param query Quick search query
 */
function updateExportLinks(query: string): void {
  for (const link of document.querySelectorAll<HTMLAnchorElement>('a.export-current-view')) {
    const url = new URL(link.href);
    if (query) {
      url.searchParams.set('q', query);
    } else {
      url.searchParams.delete('q');
    }
    link.href = url.toString();
  }
}

/**
 * Update the export links to include the quick search query.
 *
 * @param event "change" event for the quicksearch input
 */
function handleQuickSearchParams(event: Event): void {
  const quicksearch = event.currentTarget as HTMLInputElement;
  updateExportLinks(quicksearch.value);
}

/**
 * Initialize Quicksearch Event listener/handlers.
 */
export function initQuickSearch(): void {
  const quicksearch = document.getElementById('quicksearch') as HTMLInputElement;
  const clearbtn = document.getElementById('quicksearch_clear') as HTMLAnchorElement;
  if (isTruthy(quicksearch)) {
    quicksearch.addEventListener('keyup', quickSearchEventHandler, {
      passive: true,
    });
    quicksearch.addEventListener('search', quickSearchEventHandler, {
      passive: true,
    });
    quicksearch.addEventListener('change', handleQuickSearchParams, {
      passive: true,
    });

    if (isTruthy(clearbtn)) {
      clearbtn.addEventListener(
        'click',
        async () => {
          const search = new Event('search');
          quicksearch.value = '';
          await new Promise(f => setTimeout(f, 100));
          quicksearch.dispatchEvent(search);
          updateExportLinks('');
        },
        {
          passive: true,
        },
      );
    }
  }
}
