const menuButton = document.querySelector('.nav-toggle');
const menu = document.querySelector('#site-nav');
if (menuButton && menu) {
  menuButton.closest('.site-header').classList.add('has-menu');

  function setOpen(open) {
    menuButton.setAttribute('aria-expanded', String(open));
    menu.classList.toggle('is-open', open);
  }

  menuButton.addEventListener('click', () => setOpen(menuButton.getAttribute('aria-expanded') === 'false'));
  menu.addEventListener('click', () => setOpen(false));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
      setOpen(false);
      menuButton.focus();
    }
  });
}
