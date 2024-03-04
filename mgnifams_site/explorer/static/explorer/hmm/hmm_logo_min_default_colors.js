/*! hmm_logo 2014-04-30 */
/** @license
 * HMM logo
 * https://github.com/Janelia-Farm-Xfam/hmm_logo_js
 * Copyright 2013, Jody Clements.
 * Licensed under the MIT License.
 * https://github.com/Janelia-Farm-Xfam/hmm_logo_js/blob/master/LICENSE.txt
 */
!function(a){"use strict";function b(){if(!f){var a=document.createElement("canvas");f=!(!a.getContext||!a.getContext("2d"))}return f}function c(a,b){b=b||{},this.value=a,this.width=parseInt(b.width,10)||100,"W"===this.value&&(this.width+=30*this.width/100),this.height=parseInt(b.height,10)||100,this.color=b.color||"#000000",this.fontSize=b.fontSize||138,this.scaled=function(){},this.draw=function(a,b,c,d,e,f){var g=b/this.height,h=c/this.width,i=a.font;a.transform(h,0,0,g,d,e),a.fillStyle=f||this.color,a.textAlign="center",a.font="bold "+this.fontSize+"px Arial",a.fillText(this.value,0,0),a.setTransform(1,0,0,1,0,0),a.fillStyle="#000000",a.font=i}}function d(){function a(a,b){var c=".",d=0,e=null,f=null,g=null,h={".":20,h:11,"+":3,"-":2,o:2,p:2};for(e in b)b.hasOwnProperty(e)&&b[e]>=a&&(f=h[e]||1,g=h[c]||1,g>f?(c=e,d=b[e]):f===g&&b[e]>d&&(c=e,d=b[e]));return c}this.grey="#7a7a7a",this.check_PG=function(a,b,c){return c[a].P="#ffff11",c[a].G="#ff7f11",1},this.check_R=function(a,b,c){c[a].R=this.grey;var d="#FF9999",e=["Q","K","R"],f=0;for(f=0;f<e.length;f++)if(b[.85][a]===e[f])return c[a].R=d,1;return"+"===b["0.60"][a]||"R"===b["0.60"][a]||"K"===b["0.60"][a]?(c[a].R=d,1):1},this.check_Q=function(a,b,c){c[a].Q=this.grey;var d="#99FF99",e=["Q","T","K","R"],f=0;if("b"===b["0.50"][a]||"E"===b["0.50"][a]||"Q"===b["0.50"][a])return c[a].Q=d,1;for(f=0;f<e.length;f++)if(b[.85][a]===e[f])return c[a].Q=d,1;return"+"===b["0.60"][a]||"K"===b["0.60"][a]||"R"===b["0.50"][a]?(c[a].Q=d,1):1},this.check_N=function(a,b,c){c[a].N=this.grey;var d="#99FF99";return"N"===b["0.50"][a]?(c[a].N=d,1):"D"===b[.85][a]?(c[a].N=d,1):1},this.check_K=function(a,b,c){c[a].K=this.grey;var d="#FF9999",e=["K","R","Q"],f=0;if("+"===b["0.60"][a]||"R"===b["0.60"][a]||"K"===b["0.60"][a])return c[a].K=d,1;for(f=0;f<e.length;f++)if(b[.85][a]===e[f])return c[a].K=d,1;return 1},this.check_E=function(a,b,c){c[a].E=this.grey;var d="#FF9999",e=["D","E"],f=0;if("+"===b["0.60"][a]||"R"===b["0.60"][a]||"K"===b["0.60"][a])return c[a].E=d,1;for(f=0;f<e.length;f++)if(b[.85][a]===e[f])return c[a].E=d,1;return"b"===b["0.50"][a]||"E"===b["0.50"][a]||"Q"===b["0.50"][a]?(c[a].E=d,1):1},this.check_D=function(a,b,c){c[a].D=this.grey;var d="#FF9999",e=["D","E","N"],f=0;if("+"===b["0.60"][a]||"R"===b["0.60"][a]||"K"===b["0.60"][a])return c[a].D=d,1;for(f=0;f<e.length;f++)if(b[.85][a]===e[f])return c[a].D=d,1;return"-"===b["0.50"][a]||"E"===b["0.60"][a]||"D"===b["0.60"][a]?(c[a].D=d,1):1},this.check_ACFILMVW=function(a,b,c){var d=["A","C","F","L","I","M","V","W"],e=["A","C","F","H","I","L","M","V","W","Y","P","Q","h"],f=0,g=0;for(f=0;f<d.length;f++)for(c[a][d[f]]=this.grey,g=0;g<e.length;g++)b["0.60"][a]===e[g]&&(c[a][d[f]]="#9999FF");return 1},this.check_ST=function(a,b,c){c[a].S=this.grey,c[a].T=this.grey;var d=["A","C","F","H","I","L","M","V","W","Y","P","Q"],e=0;if("a"===b["0.50"][a]||"S"===b["0.50"][a]||"T"===b["0.50"][a])return c[a].S="#99FF99",c[a].T="#99FF99",1;for(e=0;e<d.length;e++)if(b[.85][a]===d[e])return c[a].S="#99FF99",c[a].T="#99FF99",1},this.check_HY=function(a,b,c){c[a].H=this.grey,c[a].Y=this.grey;var d=["A","C","F","H","I","L","M","V","W","Y","P","Q","h"],e=0,f="#99FFFF";if("h"===b["0.60"][a])return c[a].H=f,c[a].Y=f,1;for(e=0;e<d.length;e++)if(b[.85][a]===d[e])return c[a].H=f,c[a].Y=f,1;return 1},this.color_map=function(b){var c=["0.50","0.60","0.80","0.85"],d={W:1,L:1,V:1,I:1,M:1,A:1,F:1,C:1,Y:1,H:1,P:1},e={Q:1,N:1},f={K:1,R:1,H:1},g={S:1,T:1},h={E:1,D:1},i={},j=[],k=0,l=0,m=0,n=0,o=[],p=null,q={},r=null,s=null;for(l=0;l<b.length;l++)for(p=b[l],m=0;m<c.length;m++){for(s=c[m],q={p:0,o:0,"-":0,"+":0,h:0},n=0;n<p.length;n++)o=[],o=p[n].split(":"),q[o[0]]=parseFloat(o[1],10),e[o[0]]?q.p=q.p+parseFloat(o[1],10):g[o[0]]?q.o=q.o+parseFloat(o[1],10):h[o[0]]?q["-"]=q["-"]+parseFloat(o[1],10):(f[o[0]]&&(q["+"]=q["+"]+parseFloat(o[1],10)),d[o[0]]&&(q.h=q.h+parseFloat(o[1],10)));r=a(s,q),i[s]||(i[s]=[]),i[s].push(r)}for(k=0;k<b.length;k++)j[k]={},this.check_D(k,i,j),this.check_R(k,i,j),this.check_Q(k,i,j),this.check_N(k,i,j),this.check_K(k,i,j),this.check_E(k,i,j),this.check_HY(k,i,j),this.check_ACFILMVW(k,i,j),this.check_ST(k,i,j),this.check_PG(k,i,j);return j}}function e(e){function f(a,b,c,d,e,f,g,h){var i="#ffffff";h?(e>.1?i="#d7301f":e>.05?i="#fc8d59":e>.03&&(i="#fdcc8a"),a.fillStyle=i,a.fillRect(b,c+15,d,10),i="#ffffff",f>9?i="#d7301f":f>7?i="#fc8d59":f>4&&(i="#fdcc8a"),a.fillStyle=i,a.fillRect(b,c+30,d,10)):c+=30,i="#ffffff",.75>g?i="#2171b5":.85>g?i="#6baed6":.95>g&&(i="#bdd7e7"),a.fillStyle=i,a.fillRect(b,c,d,10)}function g(a,b,c){a.beginPath(),a.moveTo(0,b),a.lineTo(c,b),a.lineWidth=1,a.strokeStyle="#999999",a.stroke()}function h(a,b,c,d,e){e=e||"#999999",a.beginPath(),a.moveTo(b,c),a.lineTo(b,c+d),a.lineWidth=1,a.strokeStyle=e,a.stroke()}function i(a,b,c,d,e,f,g,h){a.font=e+"px Arial",a.fillStyle=g,a.fillRect(b,c-10,f,14),a.textAlign="center",a.fillStyle=h,a.fillText(d,b+f/2,c)}function j(a,b,c,d,e,f){var g=c-20,j="#ffffff",k="#555555";e>.1?(j="#d7301f",k="#ffffff"):e>.05?j="#fc8d59":e>.03&&(j="#fdcc8a"),i(a,b,g,e,f,d,j,k),e>.03&&h(a,b+d,c-30,-30-c,j)}function k(a,b,c,d,e,f){var g="#ffffff",h="#555555";e>9?(g="#d7301f",h="#ffffff"):e>7?g="#fc8d59":e>4&&(g="#fdcc8a"),i(a,b,c,e,f,d,g,h)}function l(a,b,c,d,e,f,g){var h=c-4,j="#ffffff",k="#555555";g&&(h=c-35),.75>e?(j="#2171b5",k="#ffffff"):.85>e?j="#6baed6":.95>e&&(j="#bdd7e7"),i(a,b,h,e,f,d,j,k)}function m(a,b,c,d,e,f,g){a.font=f+"px Arial",a.textAlign=g?"right":"center",a.fillStyle="#666666",a.fillText(e,b+d/2,c)}function n(c,d,e,f,g){var h=a(c).find("#canv_"+f);return h.length||(a(c).append('<canvas class="canvas_logo" id="canv_'+f+'"  height="'+d+'" width="'+e+'" style="left:'+g*f+'px"></canvas>'),h=a(c).find("#canv_"+f)),a(h).attr("width",e).attr("height",d),b()||(h[0]=G_vmlCanvasManager.initElement(h[0])),h[0]}e=e||{},this.column_width=e.column_width||34,this.height=e.height||300,this.data=e.data||null,this.debug=e.debug||null,this.scale_height_enabled=e.height_toggle||null,this.zoom_enabled=e.zoom_buttons&&"disabled"===e.zoom_buttons?null:!0,this.colorscheme=e.colorscheme||"default",this.display_ali_map=0,this.alphabet=e.data.alphabet||"dna",this.dom_element=e.dom_element||a("body"),this.called_on=e.called_on||null,this.start=e.start||1,this.end=e.end||this.data.height_arr.length,this.zoom=parseFloat(e.zoom)||.4,this.default_zoom=this.zoom,this.data.processing&&/^observed|weighted/.test(this.data.processing)?(this.show_inserts=0,this.info_content_height=286):(this.show_inserts=1,this.info_content_height=256),this.data.max_height=e.scaled_max?e.data.max_height_obs||this.data.max_height||2:e.data.max_height_theory||this.data.max_height||2,this.dna_colors={A:"#cbf751",C:"#5ec0cc",G:"#ffdf59",T:"#b51f16",U:"#b51f16"},this.aa_colors={A:"#FF9966",C:"#009999",D:"#FF0000",E:"#CC0033",F:"#00FF00",G:"#f2f20c",H:"#660033",I:"#CC9933",K:"#663300",L:"#FF9933",M:"#CC99CC",N:"#336666",P:"#0099FF",Q:"#6666CC",R:"#990000",S:"#0000FF",T:"#00FFFF",V:"#FFCC33",W:"#66CC66",Y:"#006600"},this.colors=this.dna_colors,"aa"===this.alphabet&&(this.colors=this.aa_colors),this.canvas_width=5e3;var o=null,p=null,q=null,r=null;"aa"===this.alphabet&&(p=this.data.probs_arr,p&&(r=new d,this.cmap=r.color_map(p))),this.letters={};for(o in this.colors)this.colors.hasOwnProperty(o)&&(q={color:this.colors[o]},this.letters[o]=new c(o,q));this.scrollme=null,this.previous_target=0,this.rendered=[],this.previous_zoom=0,this.render=function(c){if(this.data){c=c||{};var d=c.zoom||this.zoom,e=c.target||1,f=(c.scaled||null,a(this.dom_element).parent().width()),g=1,h=null,i=null,j=0;if(e!==this.previous_target){if(this.previous_target=e,c.start&&(this.start=c.start),c.end&&(this.end=c.end),.1>=d?d=.1:d>=1&&(d=1),this.zoom=d,h=this.end||this.data.height_arr.length,i=this.start||1,h=h>this.data.height_arr.length?this.data.height_arr.length:h,h=i>h?i:h,i=i>h?h:i,i=i>1?i:1,this.y=this.height-20,this.max_width=this.column_width*(h-i+1),f>this.max_width&&(d=1,this.zoom_enabled=!1),this.zoom=d,this.zoomed_column=this.column_width*d,this.total_width=this.zoomed_column*(h-i+1),1>d)for(;this.total_width<f&&(this.zoom+=.1,this.zoomed_column=this.column_width*this.zoom,this.total_width=this.zoomed_column*(h-i+1),this.zoom_enabled=!1,!(d>=1)););e>this.total_width&&(e=this.total_width),a(this.dom_element).attr({width:this.total_width+"px"}).css({width:this.total_width+"px"});var k=Math.ceil(this.total_width/this.canvas_width);for(this.columns_per_canvas=Math.ceil(this.canvas_width/this.zoomed_column),this.previous_zoom!==this.zoom&&(a(this.dom_element).find("canvas").remove(),this.previous_zoom=this.zoom,this.rendered=[]),this.canvases=[],this.contexts=[],j=0;k>j;j++){var l=this.columns_per_canvas*j+i,m=l+this.columns_per_canvas-1;m>h&&(m=h);var o=(m-l+1)*this.zoomed_column;o>g&&(g=o);var p=g*j,q=p+o;if(q+q/2>e&&e>p-p/2&&1!==this.rendered[j]){if(this.canvases[j]=n(this.dom_element,this.height,o,j,g),this.contexts[j]=this.canvases[j].getContext("2d"),this.contexts[j].setTransform(1,0,0,1,0,0),this.contexts[j].clearRect(0,0,o,this.height),this.contexts[j].fillStyle="#ffffff",this.contexts[j].fillRect(0,0,q,this.height),this.zoomed_column>12){var r=parseInt(10*d,10);r=r>10?10:r,this.debug&&this.render_with_rects(l,m,j,1),this.render_with_text(l,m,j,r)}else this.render_with_rects(l,m,j);this.rendered[j]=1}}this.scrollme||b()&&(this.scrollme=new EasyScroller(a(this.dom_element)[0],{scrollingX:1,scrollingY:0,eventTarget:this.called_on})),1!==e&&b()&&this.scrollme.reflow()}}},this.render_x_axis_label=function(){var b="";this.display_ali_map&&(b="Alignment Column"),a(this.called_on).find(".logo_xaxis").remove(),a(this.called_on).prepend('<div class="logo_xaxis" class="centered" style="margin-left:40px"><p class="xaxis_text" style="width:10em;margin:1em auto">'+b+"</p></div>")},this.render_y_axis_label=function(){a(this.dom_element).parent().before('<canvas class="logo_yaxis" height="300" width="55"></canvas>');var c=a(this.called_on).find(".logo_yaxis"),d=(Math.abs(this.data.max_height),isNaN(this.data.min_height_obs)?0:parseInt(this.data.min_height_obs,10),null),e="Information Content (bits)";b()||(c[0]=G_vmlCanvasManager.initElement(c[0])),d=c[0].getContext("2d"),d.beginPath(),d.moveTo(55,1),d.lineTo(40,1),d.moveTo(55,this.info_content_height),d.lineTo(40,this.info_content_height),d.moveTo(55,this.info_content_height/2),d.lineTo(40,this.info_content_height/2),d.lineWidth=1,d.strokeStyle="#666666",d.stroke(),d.fillStyle="#666666",d.textAlign="right",d.font="bold 10px Arial",d.textBaseline="top",d.fillText(parseFloat(this.data.max_height).toFixed(1),38,0),d.textBaseline="middle",d.fillText(parseFloat(this.data.max_height/2).toFixed(1),38,this.info_content_height/2),d.fillText("0",38,this.info_content_height),"score"===this.data.height_calc&&(e="Score (bits)"),d.save(),d.translate(5,this.height/2-20),d.rotate(-Math.PI/2),d.textAlign="center",d.font="normal 12px Arial",d.fillText(e,1,0),d.restore(),d.fillText("occupancy",55,this.info_content_height+7),this.show_inserts&&(d.fillText("ins. prob.",50,280),d.fillText("ins. len.",46,296))},this.render_x_axis_label(),this.render_y_axis_label(),this.render_with_text=function(a,c,d,e){{var f=0,i=a,m=null,n=0,o=Math.abs(this.data.max_height),p=isNaN(this.data.min_height_obs)?0:parseInt(this.data.min_height_obs,10),q=o+Math.abs(p),r=Math.round(100*Math.abs(this.data.max_height)/q),s=Math.round(this.info_content_height*r/100),t=this.info_content_height-s;s/this.info_content_height,t/this.info_content_height}for(c+3<=this.end&&(c+=3),n=a;c>=n;n++){if(this.data.mmline&&1===this.data.mmline[n-1])this.contexts[d].fillStyle="#cccccc",this.contexts[d].fillRect(f,10,this.zoomed_column,this.height-40);else{var u=this.data.height_arr[n-1],v=[];if(u){var w=0,x=u.length,y=0,z=null;for(y=0;x>y;y++){var A=u[y],B=A.split(":",2),C=f+this.zoomed_column/2,D=null;if(B[1]>.01){D=parseFloat(B[1])/this.data.max_height;var E=this.info_content_height-2-w,F=(this.info_content_height-2)*D;b()||(E+=F*(D/2)),v[y]=[F,this.zoomed_column,C,E],w+=F}}for(y=x;y>=0;y--)v[y]&&this.letters[u[y][0]]&&(z="consensus"===this.colorscheme?this.cmap[n-1][u[y][0]]||"#7a7a7a":null,this.letters[u[y][0]].draw(this.contexts[d],v[y][0],v[y][1],v[y][2],v[y][3],z))}}m=this.display_ali_map?this.data.ali_map[n-1]:i,this.zoom<.7?n%5===0&&this.draw_column_divider({context_num:d,x:f,fontsize:10,column_num:m,ralign:!0}):this.draw_column_divider({context_num:d,x:f,fontsize:e,column_num:m}),l(this.contexts[d],f,this.height,this.zoomed_column,this.data.delete_probs[n-1],e,this.show_inserts),h(this.contexts[d],f,this.height-15,5),this.show_inserts&&(j(this.contexts[d],f,this.height,this.zoomed_column,this.data.insert_probs[n-1],e),k(this.contexts[d],f,this.height-5,this.zoomed_column,this.data.insert_lengths[n-1],e),h(this.contexts[d],f,this.height-45,5),h(this.contexts[d],f,this.height-30,5)),f+=this.zoomed_column,i++}this.show_inserts&&(g(this.contexts[d],this.height-30,this.total_width),g(this.contexts[d],this.height-45,this.total_width)),g(this.contexts[d],this.height-15,this.total_width),g(this.contexts[d],0,this.total_width)},this.draw_column_divider=function(a){var b=a.ralign?a.x+this.zoomed_column:a.x,c=a.ralign?a.x+2:a.x;h(this.contexts[a.context_num],b,this.height-30,-30-this.height,"#dddddd"),h(this.contexts[a.context_num],b,0,5),m(this.contexts[a.context_num],c,10,this.zoomed_column,a.column_num,a.fontsize,a.ralign)},this.render_with_rects=function(a,b,c,d){var e=0,i=a,j=null,k=0,l=Math.abs(this.data.max_height),n=Math.abs(this.data.min_height_obs),o=l+n,p=Math.round(100*Math.abs(this.data.max_height)/o),q=Math.round(this.info_content_height*p/100),r=(this.info_content_height-q,10);for(k=a;b>=k;k++){if(this.data.mmline&&1===this.data.mmline[k-1])this.contexts[c].fillStyle="#cccccc",this.contexts[c].fillRect(e,10,this.zoomed_column,this.height-40);else{var s=this.data.height_arr[k-1],t=0,u=s.length,v=0;for(v=0;u>v;v++){var w=s[v],x=w.split(":",2);if(x[1]>.01){var y=parseFloat(x[1])/this.data.max_height,z=e,A=(this.info_content_height-2)*y,B=this.info_content_height-2-t-A,C=null;C="consensus"===this.colorscheme?this.cmap[k-1][x[0]]||"#7a7a7a":this.colors[x[0]],d?(this.contexts[c].strokeStyle=C,this.contexts[c].strokeRect(z,B,this.zoomed_column,A)):(this.contexts[c].fillStyle=C,this.contexts[c].fillRect(z,B,this.zoomed_column,A)),t+=A}}}this.zoom<.2?r=20:this.zoom<.3&&(r=10),k%r===0&&(h(this.contexts[c],e+this.zoomed_column,this.height-30,parseFloat(this.height),"#dddddd"),h(this.contexts[c],e+this.zoomed_column,0,5),j=this.display_ali_map?this.data.ali_map[k-1]:i,m(this.contexts[c],e-2,10,this.zoomed_column,j,10,!0)),f(this.contexts[c],e,this.height-42,this.zoomed_column,this.data.insert_probs[k-1],this.data.insert_lengths[k-1],this.data.delete_probs[k-1],this.show_inserts),this.show_inserts?g(this.contexts[c],this.height-45,this.total_width):g(this.contexts[c],this.height-15,this.total_width),g(this.contexts[c],0,this.total_width),e+=this.zoomed_column,i++}},this.toggle_colorscheme=function(a){var b=this.current_column();this.colorscheme=a?"default"===a?"default":"consensus":"default"===this.colorscheme?"consensus":"default",this.rendered=[],this.scrollme.reflow(),this.scrollToColumn(b+1),this.scrollToColumn(b)},this.toggle_scale=function(b){var c=this.current_column();this.data.max_height=b?"obs"===b?this.data.max_height_obs:this.data.max_height_theory:this.data.max_height===this.data.max_height_obs?this.data.max_height_theory:this.data.max_height_obs,this.rendered=[],a(this.called_on).find(".logo_yaxis").remove(),this.render_y_axis_label(),this.scrollme.reflow(),this.scrollToColumn(c+1),this.scrollToColumn(c)},this.toggle_ali_map=function(a){var b=this.current_column();this.display_ali_map=a?"model"===a?0:1:1===this.display_ali_map?0:1,this.render_x_axis_label(),this.rendered=[],this.scrollme.reflow(),this.scrollToColumn(b+1),this.scrollToColumn(b)},this.current_column=function(){var b=this.scrollme.scroller.getValues().left,c=this.column_width*this.zoom,d=b/c,e=a(this.called_on).find(".logo_container").width()/c/2,f=Math.ceil(d+e);return f},this.change_zoom=function(b){var c=.3,d=null;if(b.target?c=b.target:b.distance&&(c=(parseFloat(this.zoom)-parseFloat(b.distance)).toFixed(1),"+"===b.direction&&(c=(parseFloat(this.zoom)+parseFloat(b.distance)).toFixed(1))),c>1?c=1:.1>c&&(c=.1),d=a(this.called_on).find(".logo_graphic").width()*c/this.zoom,d>a(this.called_on).find(".logo_container").width())if(b.column){this.zoom=c,this.render({zoom:this.zoom}),this.scrollme.reflow();var e=this.coordinatesFromColumn(b.column);this.scrollme.scroller.scrollTo(e-b.offset)}else{var f=this.current_column();this.zoom=c,this.render({zoom:this.zoom}),this.scrollme.reflow(),this.scrollToColumn(f)}return this.zoom},this.columnFromCoordinates=function(a){var b=Math.ceil(a/(this.column_width*this.zoom));return b},this.coordinatesFromColumn=function(a){var b=a-1,c=b*this.column_width*this.zoom+this.column_width*this.zoom/2;return c},this.scrollToColumn=function(b,c){var d=a(this.called_on).find(".logo_container").width()/2,e=this.coordinatesFromColumn(b);this.scrollme.scroller.scrollTo(e-d,0,c)}}var f=null;a.fn.hmm_logo=function(c){var d=null,f=a('<div class="logo_graphic">');if(b()){if(c=c||{},a(this).append(a('<div class="logo_container">').append(f).append('<div class="logo_divider">')),c.data=a(this).data("logo"),null===c.data)return;c.dom_element=f,c.called_on=this;var g=c.zoom||.4,h=a('<form class="logo_form"><fieldset><label for="position">Column number</label><input type="text" name="position" class="logo_position"></input><button class="button logo_change">Go</button></fieldset></form>'),i=a('<div class="logo_controls">'),j=a('<div class="logo_settings">');if(j.append('<span class="close">x</span>'),d=new e(c),d.render(c),d.zoom_enabled&&i.append('<button class="logo_zoomout button">-</button><button class="logo_zoomin button">+</button>'),d.scale_height_enabled&&d.data.max_height_obs<d.data.max_height_theory){var k="",l="",m="",n="";d.data.max_height_obs===d.data.max_height?k="checked":l="checked",c.help&&(n='<a class="help" href="/help#scale_obs" title="Set the y-axis maximum to the maximum observed height."><span aria-hidden="true" data-icon="?"></span><span class="reader-text">help</span></a>',m='<a class="help" href="/help#scale_theory" title="Set the y-axis maximum to the theoretical maximum height"><span aria-hidden="true" data-icon="?"></span><span class="reader-text">help</span></a>');var o='<fieldset><legend>Scale</legend><label><input type="radio" name="scale" class="logo_scale" value="obs" '+k+"/>Maximum Observed "+n+'</label></br><label><input type="radio" name="scale" class="logo_scale" value="theory" '+l+"/>Maximum Theoretical "+m+"</label></fieldset>";j.append(o)}if("score"!==d.data.height_calc&&"aa"===d.data.alphabet&&d.data.probs_arr){var p=null,q=null,r="",s="";"default"===d.colorscheme?p="checked":q="checked",c.help&&(r='<a class="help" href="/help#colors_default" title="Each letter receives its own color."><span aria-hidden="true" data-icon="?"></span><span class="reader-text">help</span></a>',s='<a class="help" href="/help#colors_consensus" title="Letters are colored as in Clustalx and Jalview, with colors depending on composition of the column."><span aria-hidden="true" data-icon="?"></span><span class="reader-text">help</span></a>');var t='<fieldset><legend>Color Scheme</legend><label><input type="radio" name="color" class="logo_color" value="default" '+p+"/>Default "+r+'</label></br><label><input type="radio" name="color" class="logo_color" value="consensus" '+q+"/>Consensus Colors "+s+"</label></fieldset>";j.append(t)}if(d.data.ali_map){var u=null,v=null,w="",x="";0===d.display_ali_map?u="checked":v="checked",c.help&&(w='<a class="help" href="/help#coords_model" title="The coordinates along the top of the plot show the model position."><span aria-hidden="true" data-icon="?"></span><span class="reader-text">help</span></a>',x='<a class="help" href="/help#coords_ali" title="The coordinates along the top of the plot show the column in the alignment associated with the model"><span aria-hidden="true" data-icon="?"></span><span class="reader-text">help</span></a>');var y='<fieldset><legend>Coordinates</legend><label><input type="radio" name="coords" class="logo_ali_map" value="model" '+u+"/>Model "+w+'</label></br><label><input type="radio" name="coords" class="logo_ali_map" value="alignment" '+v+"/>Alignment "+x+"</label></fieldset>";j.append(y)}j.children().length>0&&(i.append('<button class="logo_settings_switch button">Settings</button>'),i.append(j)),h.append(i),a(this).append(h),a(this).find(".logo_settings_switch, .logo_settings .close").bind("click",function(b){b.preventDefault(),a(".logo_settings").toggle()}),a(this).find(".logo_reset").bind("click",function(a){a.preventDefault();var b=d;b.change_zoom({target:b.default_zoom})}),a(this).find(".logo_change").bind("click",function(a){a.preventDefault()}),a(this).find(".logo_zoomin").bind("click",function(a){a.preventDefault();var b=d;b.change_zoom({distance:.1,direction:"+"})}),a(this).find(".logo_zoomout").bind("click",function(a){a.preventDefault();var b=d;b.change_zoom({distance:.1,direction:"-"})}),a(this).find(".logo_scale").bind("change",function(){var a=d;a.toggle_scale(this.value)}),a(this).find(".logo_color").bind("change",function(){var a=d;a.toggle_colorscheme(this.value)}),a(this).find(".logo_ali_map").bind("change",function(){var a=d;a.toggle_ali_map(this.value)}),a(this).find(".logo_position").bind("change",function(){var a=d;this.value.match(/^\d+$/m)&&a.scrollToColumn(this.value,1)}),f.bind("dblclick",function(b){var c=d,e=a(this).offset(),f=parseInt(b.pageX-e.left,10),g=b.pageX-a(this).parent().offset().left,h=c.columnFromCoordinates(f),i=c.zoom;c.change_zoom(1>i?{target:1,offset:g,column:h}:{target:.3,offset:g,column:h})}),c.column_info&&f.bind("click",function(b){var e=d,f=a('<table class="logo_col_info"></table>'),g="<tr>",h="",i=a(this).offset(),j=parseInt(b.pageX-i.left,10),k=(b.pageX-a(this).parent().offset().left,e.columnFromCoordinates(j)),l=[],m=0,n=0,o=0,p="Probability";for(d.data.height_calc&&"score"===d.data.height_calc?(p="Score",l=d.data.height_arr[k-1].slice(0).reverse()):l=d.data.probs_arr[k-1].slice(0).reverse(),m=Math.ceil(l.length/5),n=0;m>n;n++)g+=m>1&&m-1>n?'<th>Residue</th><th class="odd">'+p+"</th>":"<th>Residue</th><th>"+p+"</th>";for(g+="</tr>",f.append(a(g)),n=0;5>n;n++){for(h+="<tr>",o=n;l[o];){var q=l[o].split(":",2),r="";"default"===d.colorscheme&&(r=d.alphabet+"_"+q[0]),h+=m>1&&15>o?'<td class="'+r+'"><div></div>'+q[0]+'</td><td class="odd">'+q[1]+"</td>":'<td class="'+r+'"><div></div>'+q[0]+"</td><td>"+q[1]+"</td>",o+=5}h+="</tr>"}f.append(a(h)),a(c.column_info).empty().append(a("<p> Column:"+k+"</p><div><p>Occupancy: "+d.data.delete_probs[k-1]+"</p><p>Insert Probability: "+d.data.insert_probs[k-1]+"</p><p>Insert Length: "+d.data.insert_lengths[k-1]+"</p></div>")).append(f).show()}),a(document).bind(this.attr("id")+".scrolledTo",function(a,b){var c=d;c.render({target:b})}),a(document).keydown(function(a){a.ctrlKey||((61===a.which||107===a.which)&&(g+=.1,d.change_zoom({distance:.1,direction:"+"})),(109===a.which||0===a.which)&&(g-=.1,d.change_zoom({distance:.1,direction:"-"})))})}else a("#logo").replaceWith(a("#no_canvas").html());return d}}(jQuery),/** @license
 * Scroller
 * http://github.com/zynga/scroller
 *
 * Copyright 2011, Zynga Inc.
 * Licensed under the MIT License.
 * https://raw.github.com/zynga/scroller/master/MIT-LICENSE.txt
 *
 * Based on the work of: Unify Project (unify-project.org)
 * http://unify-project.org
 * Copyright 2011, Deutsche Telekom AG
 * License: MIT + Apache (V2)
 *
 * Inspired by: https://github.com/inexorabletash/raf-shim/blob/master/raf.js
 */
function(a){if(!a.requestAnimationFrame){var b=Date.now||function(){return+new Date},c=Object.keys||function(a){var b={};for(var c in a)b[c]=!0;return b},d=Object.empty||function(a){for(var b in a)return!1;return!0},e="RequestAnimationFrame",f=function(){for(var b="webkit,moz,o,ms".split(","),c=0;4>c;c++)if(null!=a[b[c]+e])return b[c]}();if(f)return a.requestAnimationFrame=a[f+e],void(a.cancelRequestAnimationFrame=a[f+"Cancel"+e]);var g=60,h={},i=1,j=null;a.requestAnimationFrame=function(a){var d=i++;return h[d]=a,null===j&&(j=setTimeout(function(){var a=b(),d=h,e=c(d);h={},j=null;for(var f=0,g=e.length;g>f;f++)d[e[f]](a)},1e3/g)),d},a.cancelRequestAnimationFrame=function(a){delete h[a],d(h)&&(clearTimeout(j),j=null)}}}(this),function(a){var b=Date.now||function(){return+new Date},c=60,d=1e3,e={},f=1;a.core?core.effect||(core.effect={}):a.core={effect:{}},core.effect.Animate={stop:function(a){var b=null!=e[a];return b&&(e[a]=null),b},isRunning:function(a){return null!=e[a]},start:function(a,g,h,i,j,k){var l=b(),m=l,n=0,o=0,p=f++;if(k||(k=document.body),p%20===0){var q={};for(var r in e)q[r]=!0;e=q}var s=function(f){var q=f!==!0,r=b();if(!e[p]||g&&!g(p))return e[p]=null,void(h&&h(c-o/((r-l)/d),p,!1));if(q)for(var t=Math.round((r-m)/(d/c))-1,u=0;u<Math.min(t,4);u++)s(!0),o++;i&&(n=(r-l)/i,n>1&&(n=1));var v=j?j(n):n;a(v,r,q)!==!1&&1!==n||!q?q&&(m=r,requestAnimationFrame(s,k)):(e[p]=null,h&&h(c-o/((r-l)/d),p,1===n||null==i))};return e[p]=!0,requestAnimationFrame(s,k),p}}}(this);var EasyScroller=function(a,b){this.content=a,this.container=a.parentNode,this.options=b||{};var c=this;this.scroller=new Scroller(function(a,b,d){c.render(a,b,d)},b),this.bindEvents(),this.content.style[EasyScroller.vendorPrefix+"TransformOrigin"]="left top",this.reflow()};EasyScroller.prototype.render=function(){var a,b=document.documentElement.style;window.opera&&"[object Opera]"===Object.prototype.toString.call(opera)?a="presto":"MozAppearance"in b?a="gecko":"WebkitAppearance"in b?a="webkit":"string"==typeof navigator.cpuClass&&(a="trident");var c,d=EasyScroller.vendorPrefix={trident:"ms",gecko:"Moz",webkit:"Webkit",presto:"O"}[a],e=document.createElement("div"),f=d+"Perspective",g=d+"Transform";return e.style[f]!==c?function(a,b,c){this.content.style[g]="translate3d("+-a+"px,"+-b+"px,0) scale("+c+")"}:e.style[g]!==c?function(a,b,c){this.content.style[g]="translate("+-a+"px,"+-b+"px) scale("+c+")"}:function(a,b,c){this.content.style.marginLeft=a?-a/c+"px":"",this.content.style.marginTop=b?-b/c+"px":"",this.content.style.zoom=c||""}}(),EasyScroller.prototype.reflow=function(){this.scroller.setDimensions(this.container.clientWidth,this.container.clientHeight,this.content.offsetWidth,this.content.offsetHeight);var a=this.container.getBoundingClientRect();this.scroller.setPosition(a.left+this.container.clientLeft,a.top+this.container.clientTop)},EasyScroller.prototype.bindEvents=function(){var a=this;if($(window).bind("resize",function(){a.reflow()}),$("#modelTab").bind("click",function(){a.reflow()}),"ontouchstart"in window)this.container.addEventListener("touchstart",function(b){b.touches[0]&&b.touches[0].target&&b.touches[0].target.tagName.match(/input|textarea|select/i)||(a.scroller.doTouchStart(b.touches,(new Date).getTime()),b.preventDefault())},!1),document.addEventListener("touchmove",function(b){a.scroller.doTouchMove(b.touches,(new Date).getTime(),b.scale)},!1),document.addEventListener("touchend",function(){a.scroller.doTouchEnd((new Date).getTime())},!1),document.addEventListener("touchcancel",function(){a.scroller.doTouchEnd((new Date).getTime())},!1);else{var b=!1;$(this.container).bind("mousedown",function(c){c.target.tagName.match(/input|textarea|select/i)||(a.scroller.doTouchStart([{pageX:c.pageX,pageY:c.pageY}],(new Date).getTime()),b=!0,c.preventDefault())}),$(document).bind("mousemove",function(c){b&&(a.scroller.doTouchMove([{pageX:c.pageX,pageY:c.pageY}],(new Date).getTime()),b=!0)}),$(document).bind("mouseup",function(){b&&(a.scroller.doTouchEnd((new Date).getTime()),b=!1)}),$(this.container).bind("mousewheel",function(b){a.options.zooming&&(a.scroller.doMouseZoom(b.wheelDelta,(new Date).getTime(),b.pageX,b.pageY),b.preventDefault())})}};var Scroller;!function(){Scroller=function(a,b){this.__callback=a,this.options={scrollingX:!0,scrollingY:!0,animating:!0,bouncing:!0,locking:!0,paging:!1,snapping:!1,zooming:!1,minZoom:.5,maxZoom:3,eventTarget:null};for(var c in b)this.options[c]=b[c]};var a=function(a){return Math.pow(a-1,3)+1},b=function(a){return(a/=.5)<1?.5*Math.pow(a,3):.5*(Math.pow(a-2,3)+2)},c={__isSingleTouch:!1,__isTracking:!1,__isGesturing:!1,__isDragging:!1,__isDecelerating:!1,__isAnimating:!1,__clientLeft:0,__clientTop:0,__clientWidth:0,__clientHeight:0,__contentWidth:0,__contentHeight:0,__snapWidth:100,__snapHeight:100,__refreshHeight:null,__refreshActive:!1,__refreshActivate:null,__refreshDeactivate:null,__refreshStart:null,__zoomLevel:1,__scrollLeft:0,__scrollTop:0,__maxScrollLeft:0,__maxScrollTop:0,__scheduledLeft:0,__scheduledTop:0,__scheduledZoom:0,__lastTouchLeft:null,__lastTouchTop:null,__lastTouchMove:null,__positions:null,__minDecelerationScrollLeft:null,__minDecelerationScrollTop:null,__maxDecelerationScrollLeft:null,__maxDecelerationScrollTop:null,__decelerationVelocityX:null,__decelerationVelocityY:null,setDimensions:function(a,b,c,d){var e=this;a&&(e.__clientWidth=a),b&&(e.__clientHeight=b),c&&(e.__contentWidth=c),d&&(e.__contentHeight=d),e.__computeScrollMax(),e.scrollTo(e.__scrollLeft,e.__scrollTop,!0)},setPosition:function(a,b){var c=this;c.__clientLeft=a||0,c.__clientTop=b||0},setSnapSize:function(a,b){var c=this;c.__snapWidth=a,c.__snapHeight=b},activatePullToRefresh:function(a,b,c,d){var e=this;e.__refreshHeight=a,e.__refreshActivate=b,e.__refreshDeactivate=c,e.__refreshStart=d},finishPullToRefresh:function(){var a=this;a.__refreshActive=!1,a.__refreshDeactivate&&a.__refreshDeactivate(),a.scrollTo(a.__scrollLeft,a.__scrollTop,!0)},getValues:function(){var a=this;return{left:a.__scrollLeft,top:a.__scrollTop,zoom:a.__zoomLevel}},getScrollMax:function(){var a=this;return{left:a.__maxScrollLeft,top:a.__maxScrollTop}},zoomTo:function(a,b,c,d){var e=this;if(!e.options.zooming)throw new Error("Zooming is not enabled!");e.__isDecelerating&&(core.effect.Animate.stop(e.__isDecelerating),e.__isDecelerating=!1);var f=e.__zoomLevel;null==c&&(c=e.__clientWidth/2),null==d&&(d=e.__clientHeight/2),a=Math.max(Math.min(a,e.options.maxZoom),e.options.minZoom),e.__computeScrollMax(a);var g=(c+e.__scrollLeft)*a/f-c,h=(d+e.__scrollTop)*a/f-d;g>e.__maxScrollLeft?g=e.__maxScrollLeft:0>g&&(g=0),h>e.__maxScrollTop?h=e.__maxScrollTop:0>h&&(h=0),e.__publish(g,h,a,b)},zoomBy:function(a,b,c,d){var e=this;e.zoomTo(e.__zoomLevel*a,b,c,d)},scrollTo:function(a,b,c,d){$(document).trigger(this.options.eventTarget.attr("id")+".scrolledTo",[a,b,d]);var e=this;if(e.__isDecelerating&&(core.effect.Animate.stop(e.__isDecelerating),e.__isDecelerating=!1),null!=d&&d!==e.__zoomLevel){if(!e.options.zooming)throw new Error("Zooming is not enabled!");a*=d,b*=d,e.__computeScrollMax(d)}else d=e.__zoomLevel;e.options.scrollingX?e.options.paging?a=Math.round(a/e.__clientWidth)*e.__clientWidth:e.options.snapping&&(a=Math.round(a/e.__snapWidth)*e.__snapWidth):a=e.__scrollLeft,e.options.scrollingY?e.options.paging?b=Math.round(b/e.__clientHeight)*e.__clientHeight:e.options.snapping&&(b=Math.round(b/e.__snapHeight)*e.__snapHeight):b=e.__scrollTop,a=Math.max(Math.min(e.__maxScrollLeft,a),0),b=Math.max(Math.min(e.__maxScrollTop,b),0),a===e.__scrollLeft&&b===e.__scrollTop&&(c=!1),e.__publish(a,b,d,c)},scrollBy:function(a,b,c){var d=this,e=d.__isAnimating?d.__scheduledLeft:d.__scrollLeft,f=d.__isAnimating?d.__scheduledTop:d.__scrollTop;d.scrollTo(e+(a||0),f+(b||0),c)},doMouseZoom:function(a,b,c,d){var e=this,f=a>0?.97:1.03;return e.zoomTo(e.__zoomLevel*f,!1,c-e.__clientLeft,d-e.__clientTop)},doTouchStart:function(a,b){if(null==a.length)throw new Error("Invalid touch list: "+a);if(b instanceof Date&&(b=b.valueOf()),"number"!=typeof b)throw new Error("Invalid timestamp value: "+b);var c=this;c.__isDecelerating&&(core.effect.Animate.stop(c.__isDecelerating),c.__isDecelerating=!1),c.__isAnimating&&(core.effect.Animate.stop(c.__isAnimating),c.__isAnimating=!1);var d,e,f=1===a.length;f?(d=a[0].pageX,e=a[0].pageY):(d=Math.abs(a[0].pageX+a[1].pageX)/2,e=Math.abs(a[0].pageY+a[1].pageY)/2),c.__initialTouchLeft=d,c.__initialTouchTop=e,c.__zoomLevelStart=c.__zoomLevel,c.__lastTouchLeft=d,c.__lastTouchTop=e,c.__lastTouchMove=b,c.__lastScale=1,c.__enableScrollX=!f&&c.options.scrollingX,c.__enableScrollY=!f&&c.options.scrollingY,c.__isTracking=!0,c.__isDragging=!f,c.__isSingleTouch=f,c.__positions=[]},doTouchMove:function(a,b,c){if(null==a.length)throw new Error("Invalid touch list: "+a);if(b instanceof Date&&(b=b.valueOf()),"number"!=typeof b)throw new Error("Invalid timestamp value: "+b);var d=this;if(d.__isTracking){var e,f;2===a.length?(e=Math.abs(a[0].pageX+a[1].pageX)/2,f=Math.abs(a[0].pageY+a[1].pageY)/2):(e=a[0].pageX,f=a[0].pageY);var g=d.__positions;if(d.__isDragging){var h=e-d.__lastTouchLeft,i=f-d.__lastTouchTop,j=d.__scrollLeft,k=d.__scrollTop,l=d.__zoomLevel;if(null!=c&&d.options.zooming){var m=l;if(l=l/d.__lastScale*c,l=Math.max(Math.min(l,d.options.maxZoom),d.options.minZoom),m!==l){var n=e-d.__clientLeft,o=f-d.__clientTop;j=(n+j)*l/m-n,k=(o+k)*l/m-o,d.__computeScrollMax(l)}}if(d.__enableScrollX){j-=h;var p=d.__maxScrollLeft;(j>p||0>j)&&(d.options.bouncing?j+=h/2:j=j>p?p:0)}if(d.__enableScrollY){k-=i;var q=d.__maxScrollTop;(k>q||0>k)&&(d.options.bouncing?(k+=i/2,d.__enableScrollX||null==d.__refreshHeight||(!d.__refreshActive&&k<=-d.__refreshHeight?(d.__refreshActive=!0,d.__refreshActivate&&d.__refreshActivate()):d.__refreshActive&&k>-d.__refreshHeight&&(d.__refreshActive=!1,d.__refreshDeactivate&&d.__refreshDeactivate()))):k=k>q?q:0)}g.length>60&&g.splice(0,30),g.push(j,k,b),d.__publish(j,k,l)}else{var r=d.options.locking?3:0,s=5,t=Math.abs(e-d.__initialTouchLeft),u=Math.abs(f-d.__initialTouchTop);d.__enableScrollX=d.options.scrollingX&&t>=r,d.__enableScrollY=d.options.scrollingY&&u>=r,g.push(d.__scrollLeft,d.__scrollTop,b),d.__isDragging=(d.__enableScrollX||d.__enableScrollY)&&(t>=s||u>=s)}d.__lastTouchLeft=e,d.__lastTouchTop=f,d.__lastTouchMove=b,d.__lastScale=c}},doTouchEnd:function(a){if(a instanceof Date&&(a=a.valueOf()),"number"!=typeof a)throw new Error("Invalid timestamp value: "+a);var b=this;if(b.__isTracking){if(b.__isTracking=!1,b.__isDragging&&(b.__isDragging=!1,b.__isSingleTouch&&b.options.animating&&a-b.__lastTouchMove<=100)){for(var c=b.__positions,d=c.length-1,e=d,f=d;f>0&&c[f]>b.__lastTouchMove-100;f-=3)e=f;if(e!==d){var g=c[d]-c[e],h=b.__scrollLeft-c[e-2],i=b.__scrollTop-c[e-1];b.__decelerationVelocityX=h/g*(1e3/60),b.__decelerationVelocityY=i/g*(1e3/60);var j=b.options.paging||b.options.snapping?4:1;(Math.abs(b.__decelerationVelocityX)>j||Math.abs(b.__decelerationVelocityY)>j)&&(b.__refreshActive||b.__startDeceleration(a))}}b.__isDecelerating||(b.__refreshActive&&b.__refreshStart?(b.__publish(b.__scrollLeft,-b.__refreshHeight,b.__zoomLevel,!0),b.__refreshStart&&b.__refreshStart()):(b.scrollTo(b.__scrollLeft,b.__scrollTop,!0,b.__zoomLevel),b.__refreshActive&&(b.__refreshActive=!1,b.__refreshDeactivate&&b.__refreshDeactivate()))),b.__positions.length=0}},__publish:function(c,d,e,f){var g=this,h=g.__isAnimating;if(h&&(core.effect.Animate.stop(h),g.__isAnimating=!1),f&&g.options.animating){g.__scheduledLeft=c,g.__scheduledTop=d,g.__scheduledZoom=e;var i=g.__scrollLeft,j=g.__scrollTop,k=g.__zoomLevel,l=c-i,m=d-j,n=e-k,o=function(a,b,c){c&&(g.__scrollLeft=i+l*a,g.__scrollTop=j+m*a,g.__zoomLevel=k+n*a,g.__callback&&g.__callback(g.__scrollLeft,g.__scrollTop,g.__zoomLevel))},p=function(a){return g.__isAnimating===a},q=function(a,b){b===g.__isAnimating&&(g.__isAnimating=!1),g.options.zooming&&g.__computeScrollMax()};g.__isAnimating=core.effect.Animate.start(o,p,q,250,h?a:b)}else g.__scheduledLeft=g.__scrollLeft=c,g.__scheduledTop=g.__scrollTop=d,g.__scheduledZoom=g.__zoomLevel=e,g.__callback&&g.__callback(c,d,e),g.options.zooming&&g.__computeScrollMax()},__computeScrollMax:function(a){var b=this;null==a&&(a=b.__zoomLevel),b.__maxScrollLeft=Math.max(b.__contentWidth*a-b.__clientWidth,0),b.__maxScrollTop=Math.max(b.__contentHeight*a-b.__clientHeight,0)},__startDeceleration:function(){var a=this;if(a.options.paging){var b=Math.max(Math.min(a.__scrollLeft,a.__maxScrollLeft),0),c=Math.max(Math.min(a.__scrollTop,a.__maxScrollTop),0),d=a.__clientWidth,e=a.__clientHeight;a.__minDecelerationScrollLeft=Math.floor(b/d)*d,a.__minDecelerationScrollTop=Math.floor(c/e)*e,a.__maxDecelerationScrollLeft=Math.ceil(b/d)*d,a.__maxDecelerationScrollTop=Math.ceil(c/e)*e}else a.__minDecelerationScrollLeft=0,a.__minDecelerationScrollTop=0,a.__maxDecelerationScrollLeft=a.__maxScrollLeft,a.__maxDecelerationScrollTop=a.__maxScrollTop;var f=function(b,c,d){a.__stepThroughDeceleration(d)},g=a.options.snapping?4:.1,h=function(){return Math.abs(a.__decelerationVelocityX)>=g||Math.abs(a.__decelerationVelocityY)>=g},i=function(){a.__isDecelerating=!1,a.scrollTo(a.__scrollLeft,a.__scrollTop,a.options.snapping)};a.__isDecelerating=core.effect.Animate.start(f,h,i)},__stepThroughDeceleration:function(a){var b=this,c=b.__scrollLeft+b.__decelerationVelocityX,d=b.__scrollTop+b.__decelerationVelocityY;if(!b.options.bouncing){var e=Math.max(Math.min(b.__maxScrollLeft,c),0);e!==c&&(c=e,b.__decelerationVelocityX=0);var f=Math.max(Math.min(b.__maxScrollTop,d),0);f!==d&&(d=f,b.__decelerationVelocityY=0)}if(a?b.__publish(c,d,b.__zoomLevel):(b.__scrollLeft=c,b.__scrollTop=d),!b.options.paging){var g=.95;b.__decelerationVelocityX*=g,b.__decelerationVelocityY*=g}if(b.options.bouncing){var h=0,i=0,j=.03,k=.08;c<b.__minDecelerationScrollLeft?h=b.__minDecelerationScrollLeft-c:c>b.__maxDecelerationScrollLeft&&(h=b.__maxDecelerationScrollLeft-c),d<b.__minDecelerationScrollTop?i=b.__minDecelerationScrollTop-d:d>b.__maxDecelerationScrollTop&&(i=b.__maxDecelerationScrollTop-d),0!==h&&(h*b.__decelerationVelocityX<=0?b.__decelerationVelocityX+=h*j:b.__decelerationVelocityX=h*k),0!==i&&(i*b.__decelerationVelocityY<=0?b.__decelerationVelocityY+=i*j:b.__decelerationVelocityY=i*k)}}};for(var d in c)Scroller.prototype[d]=c[d]}();