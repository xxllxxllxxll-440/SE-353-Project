/* Small enhancements only: core navigation and forms work without JavaScript. */
document.addEventListener('DOMContentLoaded', () => {
  const mobileMenu = document.querySelector('#mobile-menu');
  if (mobileMenu) {
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') mobileMenu.open = false;
    });
    document.addEventListener('click', (event) => {
      if (!mobileMenu.contains(event.target)) mobileMenu.open = false;
    });
  }

  const form = document.querySelector('#purchase-form');
  if (!form) return;
  const lines = document.querySelector('#purchase-lines');
  const add = document.querySelector('#add-purchase-line');
  const total = document.querySelector('#purchase-estimate');

  const dollars = new Intl.NumberFormat('en-US', {style: 'currency', currency: 'USD'});
  function recalculate() {
    let sum = 0;
    for (const row of lines.querySelectorAll('.purchase-line')) {
      const quantity = Number(row.querySelector('[name="quantity"]').value);
      const price = Number(row.querySelector('[name="unit_cost"]').value);
      if (Number.isFinite(quantity) && Number.isFinite(price) && quantity > 0 && price >= 0) sum += quantity * price;
    }
    total.textContent = dollars.format(sum);
  }
  lines.addEventListener('input', recalculate);
  lines.addEventListener('click', event => {
    if (!event.target.closest('.remove-line')) return;
    if (lines.children.length === 1) return;
    event.target.closest('.purchase-line').remove();
    recalculate();
  });
  add.addEventListener('click', () => {
    if (lines.children.length >= 20) return;
    const copy = lines.firstElementChild.cloneNode(true);
    copy.querySelectorAll('input, select').forEach(input => input.value = '');
    lines.append(copy);
    copy.querySelector('select').focus();
    recalculate();
  });
  form.addEventListener('submit', event => {
    const selected = [...lines.querySelectorAll('[name="item_id"]')].map(input => input.value);
    if (selected.some(value => !value) || new Set(selected).size !== selected.length) {
      event.preventDefault();
      alert('Choose each inventory item once and fill in all fields.');
    }
  });
  recalculate();
});
