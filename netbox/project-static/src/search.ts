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
 * Clear the existing search parameters in the link to export Current View.
 */
function clearLinkParams(): void {
  const link = document.getElementById('export_current_view') as HTMLLinkElement;
  const linkUpdated = link?.href.split('&')[0];
  link.setAttribute('href', linkUpdated);
}

/**
 * Update the Export View link to add the Quick Search parameters.
 * @param event
 */
function handleQuickSearchParams(event: Event): void {
  const quickSearchParameters = event.currentTarget as HTMLInputElement;

  // Clear the existing search parameters
  clearLinkParams();

  if (quickSearchParameters != null) {
    const link = document.getElementById('export_current_view') as HTMLLinkElement;
    const search_parameter = `q=${quickSearchParameters.value}`;
    const linkUpdated = link?.href + '&' + search_parameter;
    link.setAttribute('href', linkUpdated);
  }
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
          clearLinkParams();
        },
        {
          passive: true,
        },
      );
    }
  }
}
