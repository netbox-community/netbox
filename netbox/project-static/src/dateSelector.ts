import flatpickr from 'flatpickr';

export function initDateSelector(): void {
  flatpickr('.date-picker', { allowInput: true });
  flatpickr('.datetime-picker', {
    allowInput: true,
    enableSeconds: true,
    enableTime: true,
    time_24hr: true,
  });
  flatpickr('.time-picker', {
    allowInput: true,
    enableSeconds: true,
    enableTime: true,
    noCalendar: true,
    time_24hr: true,
  });
}
