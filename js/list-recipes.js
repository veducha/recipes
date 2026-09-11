
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
        filename: f
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

    listOfRecipes += '<a href="recipe.html#' + anchor + '">' + title + '</a></li>';
    prevLetter = firstLetter;
  }

  // add recipes to page...
  $('#toc ul').html(listOfRecipes);

  // ...and the list of first-letters for quick nav
  $('#navigation').html(listOfLetters);
});
