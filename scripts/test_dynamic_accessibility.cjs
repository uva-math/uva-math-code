// Browser regression checks for the rendered site. Requires Playwright and axe-core.
// Run against a completed local Jekyll build; TEST_SITE_URL defaults to http://127.0.0.1:4173.
const {chromium} = require('playwright');
const fs = require('fs');
const assert = require('assert');
const base = process.env.TEST_SITE_URL || 'http://127.0.0.1:4173';
const axePath = require.resolve('axe-core/axe.min.js');
(async () => {
  const browser = await chromium.launch({headless:true});
  const context = await browser.newContext({viewport:{width:1280,height:900}});
  let calendarItems = [{
    id:'test-talk', summary:'Juraj Foldes — stochastic extinction', start:{dateTime:'2026-09-15T11:00:00-04:00'},
    htmlLink:'https://calendar.google.com/calendar/event?eid=test', location:'Kerchof 111',
    description:'<p>We study $X_t \\to \\infty$ and \\(x^2\\).</p><p>Details <a href="javascript:window.badCalendar=1">unsafe link</a>.</p><script>window.badCalendar=1</script>'
  }];
  let calendarStatus = 200;
  await context.route('**/calendar/v3/calendars/**', route => route.fulfill({status:calendarStatus,json:{items:calendarItems}}));
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(base+'/',{waitUntil:'load'});
  await page.waitForFunction(() => document.querySelector('.swiper-container')?.swiper);
  const rotation = () => page.evaluate(() => document.querySelector('.swiper-container').swiper.autoplay.running);
  assert(await rotation(),'Autoplay should initially run without reduced motion');
  await page.locator('.swiper-container').hover();
  assert(!(await rotation()),'Hover must stop autoplay');
  await page.locator('.carousel-pause').click();
  assert(await rotation(),'Explicit play must resume autoplay');
  await page.locator('.carousel-next').focus();
  assert(!(await rotation()),'Keyboard focus must stop autoplay');
  await page.locator('.carousel-next').click();
  await page.waitForTimeout(400);
  await page.evaluate(() => document.querySelector('.swiper-container').swiper.slideTo(0, 0));
  await page.locator('.carousel-prev').click();
  await page.waitForTimeout(400);
  assert(await page.evaluate(() => {
    const swiper = document.querySelector('.swiper-container').swiper;
    return swiper.activeIndex === swiper.slides.length - 1;
  }), 'Previous must wrap to the final slide without creating duplicate slides');
  await page.locator('.carousel-next').click();
  await page.waitForTimeout(400);
  assert.equal(await page.evaluate(() => document.querySelector('.swiper-container').swiper.activeIndex),0);
  assert.equal(await page.locator('.swiper-slide:not([inert])').count(),1,'Only one slide may be active');
  assert.equal(await page.locator('.swiper-slide[inert] a:not([tabindex="-1"])').count(),0,'Inactive links must be untabbable');
  assert.equal(await page.locator('button.swiper-pagination-bullet').count(),await page.locator('.swiper-slide').count());
  const bulletSize = await page.locator('.swiper-pagination-bullet').first().boundingBox();
  assert(bulletSize.width>=24 && bulletSize.height>=24,'Pagination target must be >=24px');
  for(let i=0;i<25;i++){
    await page.keyboard.press('Tab');
    assert(!(await page.evaluate(()=>!!document.activeElement.closest('.swiper-slide[inert]'))),'Tab reached an inactive slide');
  }
  const results = [];
  const archivePaths = [
    '/seminars/algebra/AlgSeminarOld/', '/seminars/colloq/1998-99/',
    ...['2004-05','2005-06','2006-07','2008-09','2010-11'].map(year=>'/seminars/colloq/'+year+'/'),
    ...['2001-02','2007-08'].map(year=>'/seminars/mathphys/'+year+'/'),
    ...['Spring2007','Fall2010'].map(year=>'/seminars/probability/'+year+'/'),
    ...['2014-15','2015-16','2016-17'].map(year=>'/seminars/diffeq/'+year+'/'),
    ...['2010-11','2011-12','2012-13','2013-14','2014-15'].map(year=>'/seminars/geometry/'+year+'/'),
    ...['2006-07','2007-08','2008-09','2009-10','2010-11','2011-12','2012-13','2013-14','2014-15'].map(year=>'/seminars/topology/'+year+'/')
  ];
  for(const path of (process.env.TEST_INTERACTIONS_ONLY ? [] : ['/','/people/all/','/faculty/','/postdocs/','/research/PR/','/directory/','/deptvisitors/','/calendar/','/seminars/colloq/','/arxiv/','/kiosk/',...archivePaths])){
    console.log('Checking '+path);
    await page.goto(base+path,{waitUntil:'load'});
    await page.evaluate(() => document.fonts.ready);
    await page.waitForFunction(() => [...document.querySelectorAll('.seminar-status')].every(el => !/loading/i.test(el.textContent)));
    await page.addScriptTag({path:axePath});
    for(const width of [320,1280]){
      await page.setViewportSize({width,height:900});
      const violations = await page.evaluate(async()=> {
        const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
        return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>({html:n.html,summary:n.failureSummary}))}));
      });
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
      results.push({path,width,overflow,violations});
      fs.writeFileSync('/tmp/uva-dynamic-results.json',JSON.stringify({results,errors},null,2));
    }
    if(archivePaths.includes(path)){
      assert.equal(await page.locator('a[href^="javascript:"]').count(),0,'Historical abstracts must use native controls');
      const summary = page.locator('main details summary').first();
      if(await summary.count()){
        await summary.focus();
        await page.keyboard.press('Enter');
        assert(await summary.evaluate(node=>node.parentElement.open),'Enter must open the historical abstract');
        await page.keyboard.press('Space');
        assert(!(await summary.evaluate(node=>node.parentElement.open)),'Space must close the historical abstract');
      }
    }
    if(path==='/kiosk/'){
      assert(await page.locator('.seminar-event details[open]').count(),'Kiosk must display its abstracts');
    }
  }
  await page.goto(base+'/people/all/',{waitUntil:'load'});
  assert(await page.getByRole('search',{name:'People directory'}).count());
  assert.notEqual(await page.evaluate(()=>document.activeElement.id),'people-search-input','Page must not steal initial keyboard focus');
  await page.getByLabel('Search people',{exact:true}).fill('zzzz-no-person');
  await page.waitForTimeout(250);
  assert((await page.locator('#people-results-status').textContent()).startsWith('No people found'));
  assert.equal(await page.locator('.people-directory .row:visible').count(),0);
  await page.getByLabel('Search people',{exact:true}).press('Escape');
  await page.waitForTimeout(250);
  assert(await page.locator('.people-directory .row:visible').count()>20);
  await page.getByRole('button',{name:'Staff',exact:true}).click();
  await page.waitForTimeout(250);
  assert.equal(await page.getByRole('button',{name:'Staff',exact:true}).getAttribute('aria-pressed'),'true');
  assert.equal(await page.locator('.people-directory:not([data-category="staff"]) .row:visible').count(),0);
  assert((await page.locator('#people-results-status').textContent()).includes('Staff'));
  await page.goto(base+'/arxiv/',{waitUntil:'load'});
  await page.waitForSelector('#uva-arxiv-list li[data-id]');
  assert.equal(await page.locator('.uva-arxiv-title[role="button"],#uva-arxiv-app a[target]').count(),0);
  await page.locator('.uva-arxiv-abstract-toggle').first().focus();
  await page.keyboard.press('Enter');
  assert(await page.locator('.uva-arxiv-abstract-wrap').first().getAttribute('open')!==null);
  await page.locator('.uva-arxiv-author-name').first().click();
  assert.equal(await page.evaluate(()=>document.activeElement.id),'uva-arxiv-search-input');
  assert(await page.locator('#uva-arxiv-list h2').count()>0);
  await page.getByRole('button',{name:'Clear search and filters'}).click();
  await page.getByLabel('Filter by date',{exact:true}).selectOption('custom');
  await page.getByLabel('From year',{exact:true}).fill('2026');
  await page.getByLabel('To year',{exact:true}).fill('2020');
  await page.getByRole('button',{name:'Apply year range',exact:true}).click();
  assert(await page.locator('#uva-arxiv-year-error').isVisible());
  await page.getByRole('button',{name:'Clear search and filters'}).click();
  await page.getByRole('button',{name:'Filter by category',exact:true}).click();
  await page.locator('#uva-arxiv-cat-buttons button').nth(1).click();
  assert.equal(await page.evaluate(()=>document.activeElement.getAttribute('aria-pressed')),'true');
  await page.goto(base+'/seminars/colloq/',{waitUntil:'load'});
  await page.locator('.seminar-event summary').first().click();
  assert(await page.locator('.seminar-event math').count()>=2,'Dynamic math must include accessible MathML');
  assert.equal(await page.locator('.seminar-event script,.seminar-event a[href^="javascript:"]').count(),0);
  assert(!(await page.evaluate(()=>window.badCalendar)),'Calendar description executed code');
  assert((await page.locator('.seminar-event time').first().textContent()).includes('11:00'));
  assert.equal(await page.locator('.seminar-event a[target="_blank"]').count(),0);
  const untitledEvent = {...calendarItems[0], summary:''};
  const calendarCases = [
    {path:'/drp/calendar/',noun:'event',plural:'events',title:'Event',details:'Event details',calendar:'Event calendar'},
    {path:'/ams_chapter/',noun:'event',plural:'events',title:'Event',details:'Event details',calendar:'Event calendar'},
    {path:'/seminars/colloq/',noun:'talk',plural:'talks',title:'Seminar talk',details:'Talk abstract and details',calendar:'Seminar calendar'},
    {path:'/deptvisitors/',noun:'visit',plural:'visits',title:'Visit',details:'Visit details',calendar:'Visit calendar'},
    {path:'/awm/calendar/',noun:'activity',plural:'activities',title:'Activity',details:'Activity details',calendar:'Activity calendar'}
  ];
  const waitForCalendar = () => page.waitForFunction(() => {
    const status = document.querySelector('.seminar-status');
    return status && !/loading/i.test(status.textContent);
  });
  for(const fixture of calendarCases){
    calendarItems = [untitledEvent];
    calendarStatus = 200;
    await page.goto(base+fixture.path,{waitUntil:'load'});
    await waitForCalendar();
    assert.equal(await page.locator('.seminar-status').textContent(),'1 '+fixture.noun+' listed.',fixture.path);
    assert.equal(await page.locator('.seminar-event h2,.seminar-event h3').textContent(),fixture.title,fixture.path);
    assert.equal(await page.locator('.seminar-event summary').textContent(),fixture.details,fixture.path);
    assert.equal(await page.locator('.seminar-event summary').getAttribute('aria-label'),fixture.details+': '+fixture.title,fixture.path);
    assert((await page.locator('.seminar-calendar noscript').textContent()).includes('for '+fixture.noun+' details'),fixture.path);
    calendarItems = [untitledEvent,{...untitledEvent,id:'second-event'}];
    await page.reload({waitUntil:'load'});
    await waitForCalendar();
    assert.equal(await page.locator('.seminar-status').textContent(),'2 '+fixture.plural+' listed.',fixture.path);
    calendarItems = [];
    await page.reload({waitUntil:'load'});
    await waitForCalendar();
    assert.equal(await page.locator('.seminar-status').textContent(),'No '+fixture.plural+' are scheduled in this period.',fixture.path);
    calendarStatus = 503;
    await page.reload({waitUntil:'load'});
    await waitForCalendar();
    assert((await page.locator('.seminar-status').textContent()).includes('could not be loaded'),fixture.path);
    assert.equal(await page.locator('.seminar-calendar > p a').textContent(),fixture.calendar,fixture.path);
    calendarStatus = 200;
    calendarItems = [{...untitledEvent,start:{dateTime:'invalid-date'}}];
    await page.reload({waitUntil:'load'});
    await waitForCalendar();
    assert.equal(await page.locator('.seminar-status').textContent(),
      'The schedule could not be loaded. Please contact the organizers for '+fixture.noun+' details.',fixture.path);
  }
  const reduced=await context.newPage();
  await reduced.emulateMedia({reducedMotion:'reduce'});
  await reduced.goto(base+'/',{waitUntil:'load'});
  await reduced.waitForFunction(() => document.querySelector('.swiper-container')?.swiper);
  assert(!(await reduced.evaluate(()=>document.querySelector('.swiper-container').swiper.autoplay.running)),'Reduced motion must disable autoplay');
  fs.writeFileSync('/tmp/uva-dynamic-results.json',JSON.stringify({results,errors},null,2));
  console.log(JSON.stringify({assertions:'passed',errors,results:results.map(x=>({path:x.path,width:x.width,overflow:x.overflow,violations:x.violations.map(v=>v.id)}))},null,2));
  await browser.close();
  assert.equal(errors.length,0,'Unexpected JavaScript errors');
  assert(results.every(result => !result.overflow && result.violations.length === 0),'Automated accessibility or reflow checks failed');
})().catch(error=>{console.error(error);process.exit(1)});
