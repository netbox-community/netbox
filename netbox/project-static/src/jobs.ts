import { createToast } from './toast';
import { apiGetBase, hasError } from './util';

let timeout: number = 1000;

interface JobInfo {
  id: Nullable<string>;
  complete: boolean;
}

/**
 * Mimic the behavior of setTimeout() in an async function.
 */
function asyncTimeout(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Job ID & Completion state are only from Django context, which can only be used from the HTML
 * template. Hidden elements are present in the template to provide access to these values from
 * JavaScript.
 */
function getJobInfo(): JobInfo {
  let id: Nullable<string> = null;
  let complete = false;

  // Determine the Job ID, if present.
  const jobIdElement = document.getElementById('jobId');
  if (jobIdElement !== null && jobIdElement.getAttribute('data-value')) {
    id = jobIdElement.getAttribute('data-value');
  }

  // Determine the job completion status, if present. If the job is not complete, the value will be
  // "None". Otherwise, it will be a stringified date.
  const jobCompleteElement = document.getElementById('jobComplete');
  if (jobCompleteElement !== null && jobCompleteElement.getAttribute('data-value') !== 'None') {
    complete = true;
  }
  return { id, complete };
}

/**
 * Update the job status label element based on the API response.
 */
function updateLabel(status: JobStatus) {
  const element = document.querySelector<HTMLSpanElement>('#pending-result-label > span.badge');
  if (element !== null) {
    let labelClass = 'secondary';
    switch (status.value) {
      case 'failed' || 'errored':
        labelClass = 'danger';
      case 'running':
        labelClass = 'warning';
      case 'completed':
        labelClass = 'success';
    }
    element.setAttribute('class', `badge bg-${labelClass}`);
    element.innerText = status.label;
  }
}

/**
 * Recursively check the job's status.
 * @param id Job ID
 */
async function checkJobStatus(id: string) {
  const res = await apiGetBase<APIJobResult>(`/api/extras/job-results/${id}/`);
  if (hasError(res)) {
    // If the response is an API error, display an error message and stop checking for job status.
    const toast = createToast('danger', 'Error', res.error);
    toast.show();
    return;
  } else {
    // Update the job status label.
    updateLabel(res.status);

    // If the job is complete, reload the page.
    if (['completed', 'failed', 'errored'].includes(res.status.value)) {
      location.reload();
      return;
    } else {
      // Otherwise, keep checking the job's status, backing off 1 second each time, until a 10
      // second interval is reached.
      if (timeout < 10000) {
        timeout += 1000;
      }
      await Promise.all([checkJobStatus(id), asyncTimeout(timeout)]);
    }
  }
}

function initJobs() {
  const { id, complete } = getJobInfo();
  if (id !== null && !complete) {
    // If there is a job ID and it is not completed, check for the job's status.
    Promise.resolve(checkJobStatus(id));
  }
}

if (document.readyState !== 'loading') {
  initJobs();
} else {
  document.addEventListener('DOMContentLoaded', initJobs);
}
