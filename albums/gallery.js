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
    image.src = source.currentSrc || source.src;
    image.alt = source.alt;
    caption.textContent = source.closest('figure').querySelector('figcaption')?.textContent || '';
    count.textContent = `${current + 1} / ${photos.length}`;
  }
  photos.forEach((photo, index) => {
    const link = document.createElement('a');
    link.href = photo.src;
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
  viewer.addEventListener('close', () => {
    document.body.style.overflow = previousOverflow;
    image.removeAttribute('src');
  });
})();
