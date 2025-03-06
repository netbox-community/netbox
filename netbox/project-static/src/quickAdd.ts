import { Modal } from 'bootstrap';

function handleQuickAddObject(): void {
  const quick_add = document.getElementById('quick-add-object');
  if (quick_add == null) return;

  const object_id = quick_add.getAttribute('data-object-id');
  if (object_id == null) return;
  const object_repr = quick_add.getAttribute('data-object-repr');
  if (object_repr == null) return;

  const target_id = quick_add.getAttribute('data-target-id');
  if (target_id == null) return;
  const target = document.getElementById(target_id);
  if (target == null) return;

  //@ts-expect-error tomselect added on init
  target.tomselect.addOption({
    id: object_id,
    display: object_repr,
  });
  //@ts-expect-error tomselect added on init
  target.tomselect.addItem(object_id);

  const modal_element = document.getElementById('htmx-modal');
  if (modal_element) {
    const modal = Modal.getInstance(modal_element);
    if (modal) {
      modal.hide();
    }
  }
}

export function initQuickAdd(): void {
  const quick_add_modal = document.getElementById('htmx-modal-content');
  if (quick_add_modal) {
    quick_add_modal.addEventListener('htmx:afterSwap', () => handleQuickAddObject());
  }
}
