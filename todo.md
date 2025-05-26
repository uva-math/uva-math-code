# Library Update Plan for UVA Math Website

## Overview
This document outlines the plan for updating outdated libraries from 2017-2018 to modern versions.

## ✅ Completed
- [x] **Font Awesome 4.7.0 → 6.7.2** (Completed)
  - Updated from local files to CDN
  - Migrated all icon class names to v6 format
  - Removed old local Font Awesome directory

- [x] **KaTeX 0.7.1 → 0.16.22** (Completed May 2025)
  - Updated from Cloudflare CDN to jsDelivr CDN
  - Updated CSS and JS files in headers and includes
  - Tested math rendering - working correctly

- [x] **Bootstrap 4.0.0-alpha.6 → 5.3.3** (Completed May 2025)
  - Updated CDN links in all header files
  - Migrated all data attributes (data-toggle → data-bs-toggle)
  - Updated navbar classes (navbar-toggleable → navbar-expand, navbar-inverse → navbar-dark)
  - Migrated responsive utilities (hidden-*-up/down → Bootstrap 5 display utilities)
  - Updated margin utilities (mr-*/ml-* → me-*/ms-*)
  - Added CSS compatibility layer for smooth transition
  - Preserved all custom UVA styling
  - Improved mobile hamburger menu design
  - Kept jQuery for legacy compatibility

## 📋 Remaining Libraries to Update

### 1. jQuery (COMPLETED)
**Current:** 3.7.1 (latest - updated May 2025)
**Status:** ✅ Updated to latest version
**Note:** Bootstrap 5 no longer requires jQuery, but kept for legacy compatibility

**Remaining Tasks:**
- [ ] Evaluate if jQuery can be removed entirely
- [ ] Consider migrating jQuery code to vanilla JavaScript

### 2. Swiper.js (LOW PRIORITY)
**Current:** 6.5.9 (2021 - relatively recent)
**Target:** 11.1.15 (latest)
**Breaking Changes:** Some API changes between v6 and v11

**Tasks:**
- [ ] Review Swiper migration guides (v6→v7→v8→v9→v10→v11)
- [ ] Update local Swiper files or switch to CDN
- [ ] Update initialization code
- [ ] Test carousel/slider functionality

### 3. HTML5 Shim (CLEANUP)
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

1. **HTML5 Shim** - Quick win, just remove (IE 6-8 no longer relevant)
2. **Swiper.js** - Already relatively recent (2021), lower priority
3. **jQuery Removal** - Consider removing entirely since Bootstrap 5 doesn't require it

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
