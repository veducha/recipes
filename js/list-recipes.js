
// once document is loaded, load list of recipes
// and generate table of contents, plus a quick-nav list at the top
$(document).ready(function() {
  let listOfRecipes = '';
  let listOfLetters = '';
  let prevLetter = '';

  // Use recipe objects if available, otherwise construct from files
  let recipeList = [];
  if (typeof recipes !== 'undefined') {
    recipeList = recipes;
  } else if (typeof files !== 'undefined') {
    recipeList = files.map(function(f) {
      let slug = f.replace('.md', '');
      return {
        slug: slug,
        title: slug.split('-').join(' '),
        filename: f,
        has_image: false
      };
    });
  }

  for (let i = 0; i < recipeList.length; i++) {
    let item = recipeList[i];

    // skip files that start with underscore (such as template files)
    if (item.filename && item.filename.charAt(0) === '_') {
      continue;
    }

    let title = item.title;
    let anchor = item.slug;

    // if the first letter of the recipe hasn't been
    // seen yet, add to list of letters and put an anchor in
    let firstLetter = title.charAt(0).toUpperCase();
    if (firstLetter !== prevLetter) {
      listOfRecipes += '<li id="' + firstLetter + '">';
      listOfLetters += '<a href="#' + firstLetter + '">' + firstLetter + ' </a>';
    } else {
      listOfRecipes += '<li>';
    }

    // Add data-image attribute if recipe has an image
    let imageAttr = item.has_image ? ' data-image="images/' + anchor + '.jpg"' : '';
    listOfRecipes += '<a href="recipe.html#' + anchor + '"' + imageAttr + '>' + title + '</a></li>';
    prevLetter = firstLetter;
  }

  // add recipes to page...
  $('#toc ul').html(listOfRecipes);

  // ...and the list of first-letters for quick nav
  $('#navigation').html(listOfLetters);

  // Hover image preview setup
  const $preview = $('<div id="recipe-preview"><img src="" alt="Recipe preview"></div>').appendTo('body');
  const $previewImg = $preview.find('img');
  let currentSrc = '';

  $previewImg.on('error', function() {
    $preview.removeClass('active');
  });

  function positionPreview(e) {
    const previewWidth = 220;
    const previewHeight = 140;
    const padding = 15;

    let x = e.clientX + padding;
    let y = e.clientY + padding;

    // Flip to left if too close to right edge of viewport
    if (x + previewWidth > window.innerWidth - 10) {
      x = e.clientX - previewWidth - padding;
    }

    // Flip above if too close to bottom edge of viewport
    if (y + previewHeight > window.innerHeight - 10) {
      y = e.clientY - previewHeight - padding;
    }

    $preview.css({
      top: y + 'px',
      left: x + 'px'
    });
  }

  $('#toc').on('mouseenter', 'a[data-image]', function(e) {
    const src = $(this).attr('data-image');
    if (!src) return;

    if (currentSrc !== src) {
      $previewImg.attr('src', src);
      currentSrc = src;
    }
    positionPreview(e);
    $preview.addClass('active');
  });

  $('#toc').on('mousemove', 'a[data-image]', function(e) {
    positionPreview(e);
  });

  $('#toc').on('mouseleave', 'a[data-image]', function() {
    $preview.removeClass('active');
  });
});
