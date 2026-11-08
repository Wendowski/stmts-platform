import {Component,input} from '@angular/core';
import {Block} from './models';
@Component({selector:'stmts-blocks',standalone:true,template:`
@for(n of nodes();track n.id){
@switch(n.type){
@case('paragraph'){<p dir="auto"><stmts-blocks [nodes]="n.children"/></p>}
@case('text'){<span>{{n.text}}</span>}
@case('strong'){<strong><stmts-blocks [nodes]="n.children"/></strong>}
@case('emphasis'){<em><stmts-blocks [nodes]="n.children"/></em>}
@case('strike'){<s><stmts-blocks [nodes]="n.children"/></s>}
@case('codeInline'){<code dir="ltr">{{n.text}}</code>}
@case('heading'){
@switch(n.depth){
@case(1){<h2 [id]="n.id" dir="auto"><stmts-blocks [nodes]="n.children"/></h2>}
@case(2){<h3 [id]="n.id" dir="auto"><stmts-blocks [nodes]="n.children"/></h3>}
@case(3){<h4 [id]="n.id" dir="auto"><stmts-blocks [nodes]="n.children"/></h4>}
@case(4){<h5 [id]="n.id" dir="auto"><stmts-blocks [nodes]="n.children"/></h5>}
@default{<h6 [id]="n.id" dir="auto"><stmts-blocks [nodes]="n.children"/></h6>}}
}
@case('link'){@if(safe(n.url)){<a [href]="n.url" rel="noopener noreferrer"><stmts-blocks [nodes]="n.children"/></a>}@else{<stmts-blocks [nodes]="n.children"/>}}
@case('quote'){<blockquote><stmts-blocks [nodes]="n.children"/></blockquote>}
@case('list'){<ul>@for(i of n.children;track i.id){<li><stmts-blocks [nodes]="i.children"/></li>}</ul>}
@case('orderedList'){<ol [start]="n.start || 1">@for(i of n.children;track i.id){<li><stmts-blocks [nodes]="i.children"/></li>}</ol>}
@case('code'){<pre tabindex="0" aria-label="Code" dir="ltr"><code>{{n.text}}</code></pre>}
@case('rule'){<hr/>}
@case('table'){<div class="table-scroll" tabindex="0" role="region" aria-label="Data table"><table>
@for(section of n.children;track section.id){@for(row of section.children;track row.id){<tr>@for(cell of row.children;track cell.id){@if(cell.type==='headerCell'){<th scope="col"><stmts-blocks [nodes]="cell.children"/></th>}@else{<td><stmts-blocks [nodes]="cell.children"/></td>}}</tr>}}
</table></div>}
@default{<span>{{n.text}}</span><stmts-blocks [nodes]="n.children"/>}
}}
`})
export class Blocks {nodes=input.required<Block[]>();safe(url?:string){return !!url && /^(https?:\/\/|mailto:)/i.test(url) && !/[\u0000-\u0020]/.test(url);}}
