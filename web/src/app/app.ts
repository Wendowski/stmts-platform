import {Component,inject,signal,PLATFORM_ID} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ActivatedRoute,RouterLink} from '@angular/router';
import {Blocks} from './blocks';
import {Post} from './models';
import {DatePipe,isPlatformServer} from '@angular/common';
@Component({selector:'stmts-page',imports:[RouterLink,Blocks,DatePipe],templateUrl:'./app.html'})
export class App {
 private server=isPlatformServer(inject(PLATFORM_ID));private http=inject(HttpClient);private route=inject(ActivatedRoute);
 post=signal<Post|null>(null);state=signal<'loading'|'ready'|'unavailable'|'error'>('loading');
 reader=signal(false);demo=signal(false);dark=signal(false);
 constructor(){this.route.queryParamMap.subscribe(q=>{this.demo.set(q.get('demo')==='1');this.reader.set(q.has('reader'));this.load(q.get('id'));});}
 load(id:string|null=null){this.state.set('loading');this.post.set(null);
 const url=this.demo()?'/development-post.json':'/v1/posts/'+(id || '11111111-1111-4111-8111-111111111111');
 this.http.get<Post>(this.server&&!this.demo()?'http://127.0.0.1:8000'+url:url).subscribe({next:p=>{this.post.set(p);this.state.set('ready');},error:e=>this.state.set(e.status===404?'unavailable':'error')});}
 text(nodes:any[]):string{return nodes.map(n=>n.text+this.text(n.children)).join('');}
}
