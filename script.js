(function () {
  var grid = document.getElementById('workGrid');
  var countEl = document.getElementById('workCount');
  var lightbox = document.getElementById('lightbox');
  var lightboxTitle = document.getElementById('lightboxTitle');
  var lightboxCategory = document.getElementById('lightboxCategory');
  var lightboxScroll = document.getElementById('lightboxScroll');
  var lightboxClose = document.getElementById('lightboxClose');
  var lastFocused = null;

  function openLightbox(project) {
    lastFocused = document.activeElement;
    lightboxTitle.textContent = project.title;
    lightboxCategory.textContent = project.category || '';
    lightboxScroll.innerHTML = '';
    project.images.forEach(function (name) {
      var img = document.createElement('img');
      img.src = 'assets/work/' + project.slug + '/full/' + name;
      img.alt = project.title;
      img.loading = 'lazy';
      lightboxScroll.appendChild(img);
    });
    lightbox.hidden = false;
    document.body.style.overflow = 'hidden';
    lightboxClose.focus();
  }

  function closeLightbox() {
    lightbox.hidden = true;
    document.body.style.overflow = '';
    lightboxScroll.innerHTML = '';
    if (lastFocused) lastFocused.focus();
  }

  lightboxClose.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', function (e) {
    if (e.target === lightbox) closeLightbox();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !lightbox.hidden) closeLightbox();
  });

  function renderCard(project) {
    var card = document.createElement('button');
    card.type = 'button';
    card.className = 'work-card';
    card.style.setProperty('--accent', project.accent === 'blue' ? 'var(--blue)' : 'var(--pink)');

    var thumb = document.createElement('div');
    thumb.className = 'work-thumb';

    var img = document.createElement('img');
    img.src = project.cover;
    img.alt = project.title;
    img.loading = 'lazy';
    thumb.appendChild(img);

    var border = document.createElement('div');
    border.className = 'thumb-border';
    thumb.appendChild(border);

    var hint = document.createElement('span');
    hint.className = 'expand-hint';
    hint.textContent = project.images.length + ' images ↗';
    thumb.appendChild(hint);

    var meta = document.createElement('div');
    meta.className = 'work-meta';
    meta.innerHTML =
      '<div>' +
        '<div class="display work-title"></div>' +
        '<div class="work-category"></div>' +
      '</div>' +
      (project.year ? '<span class="work-year"></span>' : '');
    meta.querySelector('.work-title').textContent = project.title;
    meta.querySelector('.work-category').textContent = project.category || '';
    if (project.year) meta.querySelector('.work-year').textContent = project.year;

    card.appendChild(thumb);
    card.appendChild(meta);
    card.addEventListener('click', function () { openLightbox(project); });

    return card;
  }

  var projects = window.WORK_PROJECTS || [];
  grid.innerHTML = '';
  if (!projects.length) {
    grid.innerHTML = '<p class="work-empty">No projects yet.</p>';
  } else {
    projects.forEach(function (p) { grid.appendChild(renderCard(p)); });
  }
  countEl.textContent = projects.length + (projects.length === 1 ? ' project' : ' projects');
})();
