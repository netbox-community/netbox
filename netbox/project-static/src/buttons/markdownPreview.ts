/**
 * interface for htmx configRequest event
 */
declare global {
  interface HTMLElementEventMap {
    'htmx:configRequest': CustomEvent<{
      parameters: Record<string, string>;
      headers: Record<string, string>;
    }>;
  }
}

function initMarkdownPreview(markdownWidget: HTMLDivElement) {
  const previewButton = markdownWidget.querySelector('button.preview-button') as HTMLButtonElement;
  const textarea = markdownWidget.querySelector('textarea') as HTMLTextAreaElement;
  const preview = markdownWidget.querySelector('div.preview') as HTMLDivElement;

  /**
   * Add the value of the textarea to the body of the htmx request
   * and copy the height of text are to the preview div
   */
  previewButton.addEventListener('htmx:configRequest', e => {
    e.detail.parameters = { text: textarea.value || '' };
    e.detail.headers['X-CSRFToken'] = window.CSRF_TOKEN;
    preview.style.minHeight = textarea.style.height;
    preview.innerHTML = '';
  });
}

export function initMarkdownPreviews(): void {
  for (const markdownWidget of document.querySelectorAll<HTMLDivElement>('.markdown-widget')) {
    initMarkdownPreview(markdownWidget);
  }
}
