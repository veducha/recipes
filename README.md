# RECIPE BOOK

A minimal static recipe website, forked from [Jeff Thompson's own](https://github.com/jeffThompson/Recipes) – great for keeping track of family recipesor have created yourself!

**Live site: [veducha.github.io/recipe-website](https://veducha.github.io/recipes/)**

## FEATURES
* Recipes in a simple [Markdown format](https://daringfireball.net/projects/markdown), just dump them in `recipes/` and push  
* List of recipes will auto-populate with quick alpha links at the top  
* Each recipe is displayed in a nice, clean format designed for use while cooking or at the grocery store – no extra 💩 or ads  
* Auto-generated links to Google image search for that dish and additional recipe ideas  
* To save your place while scrolling around on the page, click the step you're on to highlight it; click it again to remove the highlight, or use the left/right arrow keys to advance  
* 100% static: automatically builds and deploys via GitHub Pages on every push  


## PROJECT STRUCTURE
```text
├── .github/workflows/deploy.yml   # GitHub Pages automated deployment workflow
├── css/stylesheet.css             # Stylesheet
├── js/
│   ├── create-recipe.js           # Client-side Markdown parser & recipe viewer
│   ├── list-recipes.js            # Table of contents generator
│   ├── recipes.js                 # Auto-generated catalog of recipes
│   └── utils.js                   # URL linkify & domain utilities
├── scripts/build.py               # Generates js/recipes.js from recipes/*.md
├── templates/
│   └── recipe-template.md         # Starter template for new recipes
├── recipes/                       # Recipe Markdown files
│   └── *.md                       # Individual recipe files
├── images/                        # Recipe hero images (*.jpg)
├── index.html                     # Homepage / Table of Contents
└── recipe.html                    # Single recipe view template
```


## HOW TO ADD A RECIPE
1. Copy `templates/recipe-template.md` to a new `.md` file in `recipes/` named with dashes in place of spaces:
   ```bash
   cp templates/recipe-template.md recipes/my-new-dish.md
   ```
2. Fill in your recipe details following the format below.
3. *(Optional)* Add a matching `.jpg` image in `images/my-new-dish.jpg`.
4. Commit and push:
   ```bash
   git add recipes/ images/
   git commit -m "Add my new dish"
   git push origin master
   ```
   GitHub Actions will automatically run `scripts/build.py` to index the new recipe and publish the site to GitHub Pages!


## RECIPE FORMAT
In order to show up properly, your recipe's Markdown file should be named with dashes in place of spaces (ex: `rice-pilaf.md` or `saag-paneer.md`). This will be used to populate your list of recipes on the main page.

Use `templates/recipe-template.md` and/or follow this format:

```markdown
# TITLE
Optional subheader

## info  
* About XXX minutes  
* XXX servings  

## ingredients
* 

## steps  
1. 

## notes  
* 

## based on  
* url to where the recipe came from
```

For example:

```markdown
# Raspberry and Elderflower Gin and Tonic
A delicious light-red drink perfect for winter gatherings!

## ingredients
* 8 raspberries (frozen ok but should be thawed)  
* Fresh thyme (optional)  
* Gin  
* 1/2 lime  
* 1-2 tbsp St Germaine (or 1-2 tsp simple syrup)  

## steps
1. Muddle raspberries with 1.5 oz gin (and fresh thyme, if using)  
2. Add juice of half a lime  
3. Add 1-2 tbsp St Germaine (or 1-2 tsp simple syrup)  
4. Strain into glass, add ice cubes and top with tonic 

## notes
* Replace tonic with champagne for a *French 75* mashup   

## based on
* https://www.instagram.com/p/Bq3ckR8HIDE/
```

You can optionally include info about how long the recipe takes and how many servings it makes. Put this before the `Ingredients` list:  

```markdown
## info  
* Takes about 90 minutes  
* Enough for a large biryani or a full-sized curry
```

The `Ingredients` and `Steps` sections can be split with subheaders too:

```markdown
## steps
1. Soak urad dal for 4 hours to overnight, drain  
2. Grind in blender until a smooth and thick paste (add a little water if necessary)  
3. Put in mixing bowl and whip with hands for 2-3 minutes until fluffy  
4. Add spices, herbs, and salt and whip again to combine  

To fry:
1. Heat oil over medium/medium-high heat  
2. Take a bowl of water, wet hands, and form small balls  
3. Slide into oil and cook, flipping often, until golden  
4. Drain on paper towels  
```

## ADDING IMAGES  
Thanks to a suggestion from @mpember, if you have a `jpg` image with the same filename as your recipe, it will automatically be added! 
Using images of dimensions 1200x400 for consistency.

For example: `aloo-matar.md` will automatically display `images/aloo-matar.jpg`.

You can also include other images inside the recipe using Markdown's image syntax: `![alt text](url)`.


## OTHER OPTIONS  
The `recipe.html` file includes some options you can customize:

* `helpUrls`: dictionary with the `label` (text displayed) and `url` in template form. The string `<name>` will be replaced with your recipe's name  
* `lookForHeroImage`: on by default, but you can turn it off if you never intend to include hero images  
* `autoUrlSections`: list of sections in the recipe template where you want raw URLs to be turned into real links  
* `shortenUrls`: turns a super-long url into just the main domain name (off by default)


## LOCAL TESTING
To test the website locally, run a simple HTTP server from the root directory:
```bash
python3 scripts/build.py
python3 -m http.server 8000
```
Then visit `http://localhost:8000` in your browser.
