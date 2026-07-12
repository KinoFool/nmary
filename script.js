document.addEventListener('DOMContentLoaded', function () {
  var contact = document.querySelector('.contact');
  if (!contact) return;
  var confirmEl = contact.querySelector('.copied-confirm');

  contact.addEventListener('click', function (e) {
    if (navigator.clipboard && window.isSecureContext) {
      e.preventDefault();
      navigator.clipboard.writeText('nicolas@nmary.net').then(function () {
        if (confirmEl) {
          confirmEl.style.opacity = '1';
          setTimeout(function () { confirmEl.style.opacity = '0'; }, 2000);
        }
      });
    }
  });
});
