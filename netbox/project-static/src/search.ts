import { isTruthy } from './util';

/**
 * Show/hide quicksearch clear button.
 *
 * @param event "keyup" or "search" event for the quicksearch input
 */
function quickSearchEventHandler(event: Event): void {
  const quicksearch = event.currentTarget as HTMLInputElement;
  const clearbtn = document.getElementById("quicksearch_clear") as HTMLAnchorElement;
  if (isTruthy(clearbtn)) {
    if (quicksearch.value === "") {
      clearbtn.classList.add("invisible");
    } else {
      clearbtn.classList.remove("invisible");
    }
  }
}

/**
 * Initialize Quicksearch Event listener/handlers.
 */
export function initQuickSearch(): void {
  const quicksearch = document.getElementById("quicksearch") as HTMLInputElement;
  const clearbtn = document.getElementById("quicksearch_clear") as HTMLAnchorElement;
  if (isTruthy(quicksearch)) {
    quicksearch.addEventListener("keyup", quickSearchEventHandler, {
      passive: true
    })
    quicksearch.addEventListener("search", quickSearchEventHandler, {
      passive: true
    })
    if (isTruthy(clearbtn)) {
      clearbtn.addEventListener("click", async () => {
        const search = new Event('search');
        quicksearch.value = '';
        await new Promise(f => setTimeout(f, 100));
        quicksearch.dispatchEvent(search);
      }, {
        passive: true
      })
    }
  }
}
