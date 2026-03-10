/**
 * newsletter.js — Kit subscription handler for GoodFuture.ai
 *
 * Included on every page that has a newsletter form.
 * Form must call: onsubmit="handleSubscribe(event)"
 */

function handleSubscribe(e) {
  e.preventDefault();
  const input = e.target.querySelector('input');
  const btn   = e.target.querySelector('button');
  const email = input.value.trim();
  if (!email) return;
  const orig = btn.textContent;
  btn.textContent = 'Sending\u2026';
  btn.disabled = true;
  fetch('https://api.convertkit.com/v3/forms/9188945/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key: 'TkhCZ9YQzyGHWRGH6Wwz0A', email: email })
  })
  .then(res => {
    if (res.ok) {
      btn.textContent = "You're in!";
      btn.style.background = 'var(--morning-teal)';
      input.value = '';
      setTimeout(() => { btn.textContent = orig; btn.style.background = ''; btn.disabled = false; }, 3500);
    } else { throw new Error(); }
  })
  .catch(() => {
    btn.textContent = 'Try again';
    btn.style.background = 'var(--living-coral)';
    setTimeout(() => { btn.textContent = orig; btn.style.background = ''; btn.disabled = false; }, 3000);
  });
}
