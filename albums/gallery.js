(() => {
  const photos = [...document.querySelectorAll('.panel > figure img')];
  if (!photos.length || typeof HTMLDialogElement === 'undefined') return;
  const viewer = document.createElement('dialog');
  viewer.className = 'photo-viewer';
  viewer.setAttribute('aria-label', 'Photo viewer');
  viewer.innerHTML = '<div class="viewer-toolbar"><span class="viewer-count" aria-live="polite"></span><div class="viewer-controls"><button type="button" data-action="prev" aria-label="Previous photo">←</button><button type="button" data-action="next" aria-label="Next photo">→</button><button type="button" data-action="close" aria-label="Close photo viewer">Close ×</button></div></div><img class="viewer-image" alt=""><p class="viewer-caption"></p>';
  document.body.append(viewer);
  const image = viewer.querySelector('.viewer-image');
  const caption = viewer.querySelector('.viewer-caption');
  const count = viewer.querySelector('.viewer-count');
  let current = 0;
  let previousOverflow = '';
  function show(index) {
    current = (index + photos.length) % photos.length;
    const source = photos[current];
    image.src = source.dataset.full || source.currentSrc || source.src;
    image.alt = source.alt;
    caption.textContent = source.closest('figure').querySelector('figcaption')?.textContent || '';
    count.textContent = `${current + 1} / ${photos.length}`;
  }
  photos.forEach((photo, index) => {
    const link = document.createElement('a');
    link.href = photo.dataset.full || photo.src;
    link.setAttribute('aria-label', `Enlarge photo ${index + 1}: ${photo.alt}`);
    photo.replaceWith(link);
    link.append(photo);
    link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      show(index);
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      viewer.showModal();
    });
  });
  viewer.querySelector('[data-action="close"]').addEventListener('click', () => viewer.close());
  viewer.querySelector('[data-action="prev"]').addEventListener('click', () => show(current - 1));
  viewer.querySelector('[data-action="next"]').addEventListener('click', () => show(current + 1));
  viewer.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      show(current + (event.key === 'ArrowLeft' ? -1 : 1));
    }
  });
  viewer.addEventListener('click', event => {
    if (event.target !== viewer) return;
    const rect = viewer.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) viewer.close();
  });
  let gesture = null;
  image.addEventListener('touchstart', event => {
    gesture = event.touches.length === 1 ? {x: event.touches[0].clientX, y: event.touches[0].clientY, time: Date.now()} : null;
  }, {passive: true});
  image.addEventListener('touchmove', event => {
    if (event.touches.length !== 1) gesture = null;
  }, {passive: true});
  image.addEventListener('touchcancel', () => { gesture = null; }, {passive: true});
  image.addEventListener('touchend', event => {
    if (!gesture || event.touches.length || !event.changedTouches.length) return;
    const dx = event.changedTouches[0].clientX - gesture.x;
    const dy = event.changedTouches[0].clientY - gesture.y;
    if (Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy) * 1.5 && Date.now() - gesture.time < 1000) {
      show(current + (dx < 0 ? 1 : -1));
    }
    gesture = null;
  }, {passive: true});
  viewer.addEventListener('close', () => {
    document.body.style.overflow = previousOverflow;
    image.removeAttribute('src');
  });
})();
