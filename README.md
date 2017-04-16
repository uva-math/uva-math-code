# Mathematics at the University of Virginia

Official website of Department of Mathematics at the University of Virginia (under construction: see the current website [here](http://www.math.virginia.edu/))

## Notes on progress and ToDos

- Two main sources of updates - google calendars of seminars, plus in-site posts for news and other things
- For now I have coded the most difficult part - retrieving data from google calendars
- The posts feature is straightforward. I will use "categories" everywhere
- The sources of other less frequently updated information will be "seminars" and "people" in \_data and maybe other database-like structures (but not for courses I hope!.. but one can mine courses from Lou's list eventually :))
- Pages which are the most static will be just coded as html's with layouts. Hopefully there will not be many of them, and we'll need to assign some responsibility for updating those..
- There will be several layouts: main page (with special navbar?), posts page, and other pages with usual navbar; and the layouts will differ by the presence of the right-pane links!
- Need to figure out navbar conventions, too
- RSS feed for department news? (it should be easy)
- Maybe think about optimizing for small screens (so that on very small screen you first get 5 talks and then the rest?

## UVA web guidelines ToDo

- fonts - when the website goes live at virginia.edu domain we can put
  ```
  <script src="//use.typekit.net/tgy5tlj.js"></script>
  <script>try{Typekit.load();}catch(e){}</script>
  ```
  into the header to use branded fonts
- "Font Styles and Hierarchy: There are no rigid rules around combining typefaces to establish a page hierarchy. The composition of fonts should be varied in scale, style and vertical spacing. This will make the page feel bold and energetic yet readable"; but there is no CSS for this, just the descriptions. Maybe this can be done, too
- "Brand Bar: The Brand Bar is a common element across all University sites. Details about the Brand Bar are
listed below." - this suggests the design of the navbar. But it also seems that they would like to have 3 elements: top brand, name of the department, and then, only then, the navbar. Ok.
- There is also information on how to make footer and which contact info must go there, ok.

## Conventions and adding content
