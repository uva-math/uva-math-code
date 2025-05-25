# Library Update Plan for UVA Math Website

## Overview
This document outlines the plan for updating outdated libraries from 2017-2018 to modern versions.

## ✅ Completed
- [x] **Font Awesome 4.7.0 → 6.7.2** (Completed)
  - Updated from local files to CDN
  - Migrated all icon class names to v6 format
  - Removed old local Font Awesome directory

## 📋 Remaining Libraries to Update

### 1. Bootstrap (HIGH PRIORITY)
**Current:** 4.0.0-alpha.6 (alpha from 2017)
**Target:** 5.3.3 (latest stable)
**Breaking Changes:** Major - Bootstrap 5 has significant changes from v4

**Tasks:**
- [ ] Review Bootstrap 5 migration guide
- [ ] Update CDN link in header files
- [ ] Update Tether.js dependency (no longer needed in Bootstrap 5)
- [ ] Fix grid system changes (`.col-xs-*` → `.col-*`)
- [ ] Update utility classes (`.hidden-*` → `.d-none`, etc.)
- [ ] Update navbar components (significant changes)
- [ ] Update form controls
- [ ] Update JavaScript components initialization
- [ ] Test responsive layouts thoroughly

### 2. jQuery (MEDIUM PRIORITY)
**Current:** 3.2.1 (2017)
**Target:** 3.7.1 (latest)
**Note:** Bootstrap 5 no longer requires jQuery, consider removing

**Tasks:**
- [ ] Evaluate if jQuery is still needed after Bootstrap 5 upgrade
- [ ] If needed, update CDN link
- [ ] Test all jQuery-dependent functionality
- [ ] Consider migrating jQuery code to vanilla JavaScript

### 3. KaTeX (MEDIUM PRIORITY) ✅
**Current:** 0.7.1 (2016-2017)
**Updated to:** 0.16.22 (latest as of May 2025)
**Breaking Changes:** Minimal, mostly additive

**Tasks:**
- [x] Update KaTeX CDN links (CSS and JS) - Updated to jsDelivr CDN
- [ ] Test math rendering on various pages
- [ ] Update any custom KaTeX configurations
- [ ] Verify auto-render functionality

### 4. Swiper.js (LOW PRIORITY)
**Current:** 6.5.9 (2021 - relatively recent)
**Target:** 11.1.15 (latest)
**Breaking Changes:** Some API changes between v6 and v11

**Tasks:**
- [ ] Review Swiper migration guides (v6→v7→v8→v9→v10→v11)
- [ ] Update local Swiper files or switch to CDN
- [ ] Update initialization code
- [ ] Test carousel/slider functionality

### 5. HTML5 Shim (CLEANUP)
**Current:** Legacy Google Code link
**Status:** Deprecated - IE 6-8 support no longer needed

**Tasks:**
- [ ] Remove HTML5 shim completely (IE 6-8 market share ~0%)
- [ ] Clean up IE-specific code

## 🔧 General Tasks

### Pre-Update Preparation
- [ ] Set up local development environment
- [ ] Create git branch for updates
- [ ] Document current functionality for testing

### Testing Strategy
- [ ] Create comprehensive test checklist
- [ ] Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test responsive layouts on various screen sizes
- [ ] Test all interactive components
- [ ] Test math rendering
- [ ] Test form submissions
- [ ] Check browser console for errors

### Optimization Opportunities
- [ ] Consider using npm/webpack for dependency management
- [ ] Implement build process for asset optimization
- [ ] Consider lazy loading for heavy libraries
- [ ] Evaluate CDN vs local hosting for each library

## 📊 Priority Order

1. **Bootstrap + Tether** - Highest impact, most breaking changes
2. **jQuery** - May be eliminated with Bootstrap 5
3. **KaTeX** - Important for math content, relatively easy update
4. **HTML5 Shim** - Quick win, just remove
5. **Swiper.js** - Already relatively recent, lower priority

## 🚀 Deployment Strategy

1. Update libraries one at a time
2. Test thoroughly after each update
3. Deploy to staging environment first
4. Get approval from stakeholders
5. Deploy to production
6. Monitor for issues

## 📝 Notes

- Consider creating a `/legacy` branch before major updates
- Document all breaking changes and fixes
- Update any documentation or README files
- Consider setting up automated testing
- Plan for regular library updates going forward (quarterly/annually)

## 🔗 Resources

- [Bootstrap 5 Migration Guide](https://getbootstrap.com/docs/5.0/migration/)
- [jQuery Release Notes](https://blog.jquery.com/category/releases/)
- [KaTeX Changelog](https://katex.org/docs/CHANGELOG.html)
- [Swiper Migration Guides](https://swiperjs.com/migration-guide)
