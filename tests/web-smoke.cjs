const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const evidence=[];
 for(const width of [320,390,834,1440]){
 const page=await browser.newPage({viewport:{width,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:4200/');
 await page.getByRole('link',{name:/Continue reading/}).click();
 await page.getByRole('heading',{name:'A little more room to think.',exact:true}).waitFor();
 await page.getByRole('heading',{name:'A quieter kind of conversation',exact:true}).waitFor();
 await page.getByRole('button',{name:'Dark appearance'}).click();
 if(await page.locator('h1').count()!==1)throw new Error('Expected one h1');
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 if(overflow)throw new Error('Overflow at '+width);
 if(errors.length)throw new Error(errors.join('\n'));
 evidence.push({width,reader:true,dark:true,pageOverflow:false,consoleErrors:errors});
 if(width===1440)await page.screenshot({path:require('path').join(__dirname,'../docs/reader-desktop.png'),fullPage:true});
 if(width===390)await page.screenshot({path:require('path').join(__dirname,'../docs/reader-mobile.png'),fullPage:true});
 await page.goto('http://127.0.0.1:4200/?id=00000000-0000-4000-8000-000000000000');
 await page.getByRole('heading',{name:'Statement unavailable',exact:true}).waitFor();
 await page.close();
 }
 require('fs').writeFileSync(require('path').join(__dirname,'../docs/web-smoke-results.json'),JSON.stringify(evidence,null,2));
 console.log('PASS: API-backed reader, heading semantics, dark appearance, unavailable state and no horizontal overflow at 320/390/834/1440.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
