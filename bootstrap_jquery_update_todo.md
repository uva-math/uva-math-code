# Bootstrap & jQuery Update Plan for UVA Math Website

## Executive Summary

This document provides a comprehensive plan for updating Bootstrap from 4.0.0-alpha.6 to 5.3.3 and evaluating jQuery dependencies. The update involves significant breaking changes and requires careful migration of CSS classes, JavaScript components, and custom styles.

## Current State Analysis

### Library Versions
- **Bootstrap**: 4.0.0-alpha.6 (2017 alpha release)
- **jQuery**: 3.2.1 (required by Bootstrap 4)
- **Tether**: 1.4.0 (required by Bootstrap 4 for tooltips/popovers)
- **Popper.js**: Not present (will be needed for Bootstrap 5)

### Alpha Version Risk Assessment
**CRITICAL**: The migration is from Bootstrap 4.0.0-alpha.6, which carries higher intrinsic risk than migrating from a stable Bootstrap 4 release. Alpha versions can have undocumented features, bugs, and inconsistencies that might not be covered by standard BS4-to-BS5 migration guides. Expect more "unknown unknowns" including:
- Potentially unstable API implementations
- Undocumented behavior that may have been fixed or changed in later versions
- Edge cases not covered in official migration guides
- Custom workarounds that may have been implemented for alpha bugs

### jQuery Usage
1. **Minimal Direct Usage**:
   - Tooltip initialization in `_includes/UVA_fonts.html`
   - iOS touch cursor fix
   - Legacy seminar pages with accordion functionality
   - IMS workshop schedule pages with show/hide functionality

2. **Bootstrap 4 Dependencies**:
   - Collapse (navbar mobile menu)
   - Dropdown (navigation menus)
   - Tooltip (conditional)

### Bootstrap Components Used
1. **Layout**: Grid system, containers, responsive utilities
2. **Navigation**: Navbar with collapse, dropdowns
3. **Components**: Cards, buttons, forms, list groups
4. **Utilities**: Spacing, display, text alignment, colors

## Breaking Changes Summary

### 1. Grid System Changes
- `col-xs-*` → `col-*` (xs is now default)
- New `col-xxl-*` for extra large screens
- `.row-offcanvas` is custom, needs review

### 2. Responsive Utilities
- `hidden-*-up/down` → `d-*-none` display utilities
- `hidden-xs-down` → `d-block d-sm-none`
- `hidden-md-up` → `d-md-none`
- `hidden-lg-up` → `d-lg-none`

### 3. Component Changes
- `.card-block` → `.card-body`
- `.navbar-toggleable-*` → removed (use `.navbar-expand-*`)
- `.navbar-inverse` → `.navbar-dark`
- `.bg-inverse` → `.bg-dark` (custom color override exists)
- Form control sizing classes changed

### 4. JavaScript Changes
- jQuery no longer required
- Tether.js replaced by Popper.js
- Data attributes: `data-*` → `data-bs-*`
- New initialization syntax for components

### 5. Removed Components
- `.btn-outline-*` classes restructured
- Input group addons changed
- Various utility classes renamed

## Migration Plan

### Phase 1: Preparation & Testing Infrastructure

#### 1.1 Set Up Testing Environment
```bash
# Create feature branch
git checkout -b feature/bootstrap5-update

# Create backup branch
git checkout -b backup/pre-bootstrap5

# Return to feature branch
git checkout feature/bootstrap5-update

# Set up local Jekyll build
bundle install
bundle exec jekyll serve --watch
```

#### 1.2 Pre-emptive Change Detection via Site Build Comparison

**Baseline Site Build & Backup:**
```bash
# Before ANY code changes, create baseline build
bundle exec jekyll build --destination _site_before_migration

# Create backup of this baseline
cp -r _site_before_migration _site_before_migration_backup
```

**Post-Migration Comparison Process:**
1. After completing primary migrations (Phase 2), build again:
   ```bash
   bundle exec jekyll build --destination _site_after_migration
   ```

2. Use directory comparison tools:
   ```bash
   # Linux/macOS
   diff -rq _site_before_migration _site_after_migration > migration_changes.txt
   
   # Or use visual tools:
   # - WinMerge (Windows)
   # - Kaleidoscope (macOS)
   # - Meld (Cross-platform)
   ```

3. Create a checklist from differing HTML files for focused human review:
   - Open before/after versions side-by-side
   - Check layout, components, interactivity at all breakpoints
   - Document any unexpected changes

This targeted review complements automated testing by highlighting structural changes that might not be visually obvious but could affect JavaScript behavior or SEO.

#### 1.3 Create Automated Tests

**HTML/CSS Linting Setup:**
```bash
# Install linters
npm install --save-dev htmlhint stylelint stylelint-config-standard

# Create .htmlhintrc
{
  "tagname-lowercase": true,
  "attr-lowercase": true,
  "attr-value-double-quotes": true,
  "doctype-first": true,
  "tag-pair": true,
  "spec-char-escape": true,
  "id-unique": true,
  "src-not-empty": true,
  "attr-no-duplication": true,
  "alt-require": true
}

# Create .stylelintrc.json
{
  "extends": "stylelint-config-standard",
  "rules": {
    "selector-class-pattern": null,
    "no-descending-specificity": null
  }
}
```

**Ruby Test Suite** (`test_bootstrap_migration.rb`):
```ruby
require 'minitest/autorun'
require 'nokogiri'
require 'fileutils'

class BootstrapMigrationTest < Minitest::Test
  def setup
    @site_dir = '_site'
  end
  
  def test_no_old_bootstrap_classes
    deprecated_classes = [
      'hidden-xs-down', 'hidden-sm-down', 'hidden-md-down',
      'hidden-lg-down', 'hidden-xl-down', 'hidden-xs-up',
      'hidden-sm-up', 'hidden-md-up', 'hidden-lg-up',
      'card-block', 'navbar-toggleable', 'navbar-inverse'
    ]
    
    Dir.glob("#{@site_dir}/**/*.html").each do |file|
      content = File.read(file)
      doc = Nokogiri::HTML(content)
      
      deprecated_classes.each do |old_class|
        elements = doc.css(".#{old_class}")
        assert_empty elements, "Found deprecated class '#{old_class}' in #{file}"
      end
    end
  end
  
  def test_data_attributes_updated
    old_attributes = ['data-toggle', 'data-target', 'data-dismiss']
    
    Dir.glob("#{@site_dir}/**/*.html").each do |file|
      content = File.read(file)
      
      old_attributes.each do |attr|
        refute content.include?(attr), "Found old attribute '#{attr}' in #{file}"
      end
    end
  end
  
  def test_responsive_images
    Dir.glob("#{@site_dir}/**/*.html").each do |file|
      doc = Nokogiri::HTML(File.read(file))
      images = doc.css('img')
      
      images.each do |img|
        assert img['class']&.include?('img-fluid') || 
               img['style']&.include?('max-width'), 
               "Image without responsive class in #{file}"
      end
    end
  end
  
  def test_navbar_structure
    test_files = ['index.html', 'people/index.html', 'seminars/index.html']
    
    test_files.each do |file|
      doc = Nokogiri::HTML(File.read("#{@site_dir}/#{file}"))
      navbar = doc.at_css('.navbar')
      
      assert navbar, "No navbar found in #{file}"
      assert navbar['class'].include?('navbar-expand'), 
             "Navbar missing expand class in #{file}"
    end
  end
end
```

#### 1.4 Create Visual Regression Tests

**Enhanced Visual Regression with Comparison Tools:**
```javascript
const puppeteer = require('puppeteer');
const pixelmatch = require('pixelmatch');
const fs = require('fs');
const PNG = require('pngjs').PNG;

const pages = [
  '/',
  '/people/',
  '/seminars/',
  '/undergraduate/',
  '/graduate/',
  '/research/'
];

async function captureScreenshots(baseUrl, outputDir) {
  const browser = await puppeteer.launch();
  
  for (const page of pages) {
    const pageObj = await browser.newPage();
    
    // Desktop viewport
    await pageObj.setViewport({ width: 1200, height: 800 });
    await pageObj.goto(baseUrl + page, { waitUntil: 'networkidle2' });
    await pageObj.screenshot({ 
      path: `${outputDir}/desktop${page.replace(/\//g, '-')}.png`,
      fullPage: true 
    });
    
    // Mobile viewport
    await pageObj.setViewport({ width: 375, height: 667 });
    await pageObj.screenshot({ 
      path: `${outputDir}/mobile${page.replace(/\//g, '-')}.png`,
      fullPage: true 
    });
  }
  
  await browser.close();
}

// Compare screenshots function
function compareScreenshots(img1Path, img2Path, diffPath) {
  const img1 = PNG.sync.read(fs.readFileSync(img1Path));
  const img2 = PNG.sync.read(fs.readFileSync(img2Path));
  const {width, height} = img1;
  const diff = new PNG({width, height});
  
  const numDiffPixels = pixelmatch(
    img1.data, img2.data, diff.data, width, height,
    {threshold: 0.1}
  );
  
  fs.writeFileSync(diffPath, PNG.sync.write(diff));
  
  const diffPercent = (numDiffPixels / (width * height)) * 100;
  return {numDiffPixels, diffPercent};
}

// Usage:
// 1. Capture baseline: captureScreenshots('http://localhost:4000', 'screenshots/before');
// 2. After migration: captureScreenshots('http://localhost:4000', 'screenshots/after');
// 3. Compare: compareScreenshots('before/desktop-home.png', 'after/desktop-home.png', 'diff/desktop-home.png');
```

**Alternative: Use established tools like BackstopJS, Percy, or Applitools for more sophisticated visual regression testing with better reporting and CI integration.**

### Phase 2: File-by-File Migration

#### 2.1 Update CDN Links
**File**: `_includes/bootjs`
```html
<!-- Remove jQuery and Tether -->
<!-- Remove: jquery-3.2.1.min.js -->
<!-- Remove: tether.min.js -->

<!-- Add Bootstrap 5 bundle (includes Popper.js) -->
<script 
  src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" 
  integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" 
  crossorigin="anonymous"></script>
```

**Files**: `_includes/header.html`, `_includes/main_header.html`
```html
<!-- Replace Bootstrap 4 CSS -->
<link 
  href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" 
  rel="stylesheet" 
  integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" 
  crossorigin="anonymous">
```

#### 2.2 Update HTML Templates

**Data Attribute Migration Strategy:**

Create a reference table for systematic updates:
| Old Attribute | New Attribute | Used In |
|--------------|---------------|---------|
| `data-toggle="collapse"` | `data-bs-toggle="collapse"` | Navbar, Accordions |
| `data-target="#id"` | `data-bs-target="#id"` | Collapse, Modals |
| `data-toggle="dropdown"` | `data-bs-toggle="dropdown"` | Dropdown menus |
| `data-dismiss="modal"` | `data-bs-dismiss="modal"` | Modal close buttons |
| `data-toggle="tooltip"` | `data-bs-toggle="tooltip"` | Tooltips |
| `data-placement="*"` | `data-bs-placement="*"` | Tooltips, Popovers |

**Systematic Update Process:**
```bash
# Backup all files first
cp -r _includes _includes_backup

# Use careful search and replace
# Example for data-toggle:
find _includes -name "*.html" -exec sed -i.bak 's/data-toggle="/data-bs-toggle="/g' {} \;
find _layouts -name "*.html" -exec sed -i.bak 's/data-toggle="/data-bs-toggle="/g' {} \;

# Review changes before committing
git diff
```

**Responsive Utilities Migration Map**:
```
hidden-xs-down → d-block d-sm-none
hidden-sm-down → d-block d-md-none
hidden-md-down → d-block d-lg-none
hidden-lg-down → d-block d-xl-none
hidden-xl-down → d-block d-xxl-none

hidden-xs-up → d-none
hidden-sm-up → d-none d-sm-block
hidden-md-up → d-none d-md-block
hidden-lg-up → d-none d-lg-block
hidden-xl-up → d-none d-xl-block
```

**Key Files to Update**:

1. **`_includes/navbar.html`**:
   - `navbar-toggleable-sm` → `navbar-expand-sm`
   - `navbar-inverse` → `navbar-dark bg-dark`
   - `data-toggle` → `data-bs-toggle`
   - `data-target` → `data-bs-target`
   - `navbar-toggler-right` → `ms-auto`

2. **`_includes/footer.html`**:
   - Update grid classes
   - Replace responsive utilities

3. **`_includes/people_roll.html`**:
   - `card-block` → `card-body`
   - Update button classes if needed

4. **`index.html`**:
   - Update jumbotron (removed in Bootstrap 5, use custom CSS)
   - Update grid classes
   - Fix responsive utilities

#### 2.3 Audit Third-Party JavaScript Libraries

**Create inventory of all JavaScript dependencies:**
```bash
# Search for script tags
grep -r "<script" _includes _layouts | grep -v "bootstrap\|jquery"

# Check for potential Bootstrap 4 dependencies
grep -r "tooltip\|popover\|modal\|carousel" _includes _layouts *.html
```

**Common libraries to check:**
- Date pickers (may depend on jQuery/Bootstrap 4)
- Form validation libraries
- Carousel/slider plugins (Swiper.js detected - verify BS5 compatibility)
- Chart libraries
- Any jQuery plugins

**For each third-party library:**
1. Check if Bootstrap 5 compatible version exists
2. Look for vanilla JS alternatives
3. Plan updates or replacements
4. Test thoroughly after migration

#### 2.4 Update Custom CSS
**File**: `css/main.css`

```css
/* Add Bootstrap 5 compatibility styles */

/* Jumbotron replacement */
.jumbotron {
  padding: 2rem 1rem;
  margin-bottom: 2rem;
  background-color: #F1F1EF;
  border-radius: .3rem;
}

@media (min-width: 576px) {
  .jumbotron {
    padding: 4rem 2rem;
  }
}

/* Card compatibility */
.card-block {
  padding: 1.25rem;
}

/* Navbar compatibility */
.navbar-toggleable-sm {
  /* Map to navbar-expand-sm behavior */
}

/* Custom .bg-inverse to .bg-uva-blue */
/* NOTE: Using !important as last resort due to specificity conflicts with Bootstrap utilities */
/* TODO: Investigate increasing selector specificity to remove !important in future refactor */
.bg-uva-blue {
  background-color: #002F6C !important;
  color: white;
}

/* Better approach without !important (if possible): */
.navbar.bg-uva-blue,
.bg-uva-blue.card,
.bg-uva-blue.list-group-item {
  background-color: #002F6C;
  color: white;
}

/* Update selectors */
.navbar-dark .navbar-nav .nav-link {
  color: rgba(255,255,255,.75);
}

.navbar-dark .navbar-nav .nav-link:hover,
.navbar-dark .navbar-nav .nav-link:focus {
  color: #EB5F0C;
}

/* Temporary offcanvas compatibility layer */
/* TODO: Refactor to use Bootstrap 5's native offcanvas component */
@media (max-width: 767.98px) {
  .row-offcanvas {
    position: relative;
    transition: all .25s ease-out;
  }
  
  .row-offcanvas-right {
    right: 0;
  }
  
  .row-offcanvas-right .sidebar-offcanvas {
    right: -100%;
  }
  
  .row-offcanvas-right.active .sidebar-offcanvas {
    right: -75%;
  }
  
  .sidebar-offcanvas {
    position: absolute;
    top: 0;
    width: 75%;
  }
}
```

#### 2.5 JavaScript Updates

**Update Tooltip Initialization** (`_includes/UVA_fonts.html`):
```javascript
{% if page.tooltips %}
<script type="text/javascript">
  // Wait for DOM ready
  document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // iOS touch fix (jQuery-free version)
    if ('ontouchstart' in document.documentElement || window.Touch) {
      document.body.style.cursor = 'pointer';
    }
  });
</script>
{% endif %}
```

**Update Collapse Toggle** (if using custom JS):
```javascript
// Old jQuery way
$('[data-toggle="collapse"]').collapse();

// New Bootstrap 5 way
document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(el => {
  new bootstrap.Collapse(el);
});
```

### Phase 3: Testing & Validation

#### 3.1 Automated Testing Checklist
- [ ] Run HTML validation on all pages
- [ ] Run CSS validation with Stylelint
- [ ] Run HTMLHint on all generated pages
- [ ] Check for console errors
- [ ] Run automated regression tests
- [ ] Check all responsive breakpoints
- [ ] Perform accessibility scans using Axe DevTools or WAVE

#### 3.2 Manual Testing Checklist

**Navigation**:
- [ ] Desktop menu dropdowns work
- [ ] Mobile hamburger menu opens/closes
- [ ] All navigation links functional
- [ ] Search box expands properly

**Responsive Layout**:
- [ ] Test at all breakpoints (xs, sm, md, lg, xl, xxl)
- [ ] Hidden/visible elements appear correctly
- [ ] Grid system maintains proper alignment
- [ ] Images scale appropriately

**Components**:
- [ ] Cards display correctly
- [ ] Buttons have proper styling
- [ ] Forms maintain functionality
- [ ] List groups styled correctly

**Accessibility**:
- [ ] Test keyboard-only navigation for all interactive elements
- [ ] Verify screen reader compatibility for key workflows
- [ ] Check for sufficient color contrast (WCAG 2.1 AA)
- [ ] Test focus indicators are visible
- [ ] Verify ARIA attributes are properly updated

**Pages to Test**:
- [ ] Homepage (carousel, news grid)
- [ ] People directory (cards, grid)
- [ ] Seminars (calendar, listings)
- [ ] Individual person pages
- [ ] News/post pages
- [ ] Documentation pages

#### 3.3 Browser Testing
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

### Phase 4: jQuery Evaluation

#### 4.1 jQuery Dependency Analysis
After Bootstrap 5 migration, jQuery is only needed for:
1. Legacy seminar pages with custom accordion code
2. IMS workshop schedule show/hide functionality
3. Tooltip initialization (can be replaced)
4. iOS touch cursor fix (can be replaced)

#### 4.2 jQuery Removal Plan
1. **Replace tooltip initialization** with vanilla JS (shown above)
2. **Replace iOS cursor fix** with vanilla JS (shown above)
3. **Legacy pages options**:
   - Keep jQuery only on specific legacy pages
   - Rewrite accordion functionality with Bootstrap 5 accordion
   - Convert to static content if rarely accessed

### Phase 5: Rollback Plan

#### 5.1 Git Strategy
```bash
# Create backup branch before starting
git checkout -b backup/pre-bootstrap5

# If rollback needed
git checkout main
git reset --hard backup/pre-bootstrap5
```

#### 5.2 Quick Rollback Files
Keep copies of original files:
- `_includes/bootjs.backup`
- `_includes/header.html.backup`
- `_includes/main_header.html.backup`
- `css/main.css.backup`

### Phase 6: Deployment Strategy

#### 6.1 Staged Deployment
1. **Development Environment**: Complete migration and testing
2. **Staging Environment**: Deploy to test subdomain
3. **Production Deployment**: 
   - Deploy during low-traffic period
   - Monitor for errors
   - Have rollback ready

#### 6.2 Monitoring
- Set up browser error logging (e.g., Sentry, LogRocket)
- Monitor 404s for missing resources
- Check Google Analytics for unusual bounce rates
- Have team test critical functionality
- Monitor Core Web Vitals for performance regression

## Risk Assessment

### High Risk Areas
1. **Navigation collapse** - Critical for mobile users
2. **Grid system changes** - Could break layouts
3. **Custom CSS overrides** - May conflict with Bootstrap 5
4. **Alpha version instability** - Unknown bugs or undocumented features

### Medium Risk Areas
1. **Responsive utilities** - Visual issues on certain devices
2. **JavaScript components** - Dropdowns, tooltips
3. **Legacy page compatibility** - Older seminar pages
4. **Third-party library compatibility** - May break with Bootstrap 5

### Mitigation Strategies
1. Extensive testing at each breakpoint
2. Visual regression testing with automated comparison
3. Gradual rollout with monitoring
4. Clear rollback procedure
5. Extra attention to alpha-specific quirks

## Timeline Estimate

- **Phase 1**: Preparation & Testing Setup (1-1.5 days)
- **Phase 2**: File Migration (3-4 days) *[increased due to alpha complexity]*
- **Phase 3**: Testing & Bug Fixes (3-4 days) *[increased for thorough testing]*
- **Phase 4**: jQuery Evaluation (1 day)
- **Phase 5**: Staging Deployment & Testing (2 days) *[increased for alpha uncertainty]*
- **Phase 6**: Production Deployment (0.5 day)

**Total**: 10.5-13 days of focused work

**Recommendation**: Add a 30-50% buffer to this estimate to account for:
- Complexities of migrating from an alpha version
- Debugging custom CSS/JS interactions
- Potential unforeseen issues
- Accessibility improvements

**Realistic Timeline**: 14-20 days

## Post-Migration Tasks

1. **Documentation Update**
   - Update CLAUDE.md with new Bootstrap 5 patterns
   - Document any custom compatibility layers
   - Create migration guide for content editors

2. **Performance Optimization**
   - Remove unused CSS with PurgeCSS
   - Implement lazy loading for images
   - Consider CDN with local fallback

3. **Long-term Refactoring**
   - Plan to refactor `.row-offcanvas` to use Bootstrap 5's native offcanvas component
   - Remove all `!important` declarations by improving selector specificity
   - Modernize any remaining jQuery-dependent code

4. **Maintenance Plan**
   - Set up automated dependency updates (e.g., Dependabot)
   - Regular Bootstrap security updates
   - Quarterly review of deprecated features
   - Annual accessibility audits

## Success Criteria

1. All pages render correctly at all breakpoints
2. No JavaScript errors in console
3. Navigation works on all devices
4. No visual regression from current design (verified by visual regression tests)
5. Page load time equal or better
6. Successful removal of jQuery (except legacy pages)
7. Clean HTML/CSS validation
8. **Significant improvement in accessibility, aiming for WCAG 2.1 AA compliance**
9. All third-party libraries functioning correctly
10. Successful comparison of before/after builds with documented changes

## Conclusion

This migration from Bootstrap 4 alpha to Bootstrap 5 is significant but manageable. The main challenges are:
1. Dealing with alpha version instabilities
2. Updating responsive utilities systematically
3. Ensuring mobile navigation continues to work
4. Managing third-party library compatibility

With proper testing, including the Jekyll build comparison technique for targeted human review, visual regression testing, and a staged deployment, the risk can be minimized while gaining the benefits of a modern, maintained framework with improved accessibility.