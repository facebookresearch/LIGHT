(window.webpackJsonp=window.webpackJsonp||[]).push([[0],{15:function(e,t,a){e.exports=a(27)},20:function(e,t,a){},27:function(e,t,a){"use strict";a.r(t);var n=a(14),r=a(2),l=a(0),o=a.n(l),c=a(4),i=a.n(c),s=(a(20),a(21),a(22),a(3)),u=a(8),m=a(7),f=a.n(m),d=a(11),p=a(13);a(6),a(12);var E=function(e,t){var a=[].concat(Object(p.a)(e),[t]);return console.groupCollapsed("New message. Total: "+a.length),console.table(a),console.groupEnd(),a};function g(e){var t=o.a.useRef(),a=o.a.useState(!1),n=Object(r.a)(a,2),l=n[0],c=n[1],i=o.a.useState(!1),s=Object(r.a)(i,2),u=s[0],m=s[1],f=o.a.useReducer(E,[]),d=Object(r.a)(f,2),p=d[0],g=d[1],v=o.a.useState(null),h=Object(r.a)(v,2),b=h[0],y=h[1],N=o.a.useState(null),k=Object(r.a)(N,2),w=k[0],S=k[1],x=o.a.useState({}),O=Object(r.a)(x,2),C=O[0],T=O[1],R=o.a.useCallback(function(e){var t=JSON.parse(e.data);if("actions"===t.command){var a=[];t.data.forEach(function(e){var t="SpawnEvent"===e.caller,n="LookEvent"===e.caller;e.room=JSON.parse(e.room),e.actor=JSON.parse(e.actor),t?y({name:e.actor.name,description:e.actor.persona,id:e.actor.node_id}):(n?(S({name:e.room.name,description:e.room.desc+"\nYou notice: TODO add examine stuff here.",id:e.room.node_id}),a.push(e)):a.push(e),a.forEach(function(e){return g(e)}))})}},[g,y,T,S]);o.a.useEffect(function(){t.current.onmessage=R},[R]);var j=o.a.useCallback(function(e){g({caller:"say",text:e,is_self:!0,actors:[b.id]});var a=JSON.stringify({command:"act",data:e});return t.current.send(a)},[t,g,b]);return t.current||(t.current=new WebSocket(e),t.current.onopen=function(){console.log("opened"),c(!0)},t.current.onerror=t.current.onclose=function(){console.log("errored"),c(!1),m(!0),t.current=null}),{isConnected:l,messages:p,submitMessage:j,persona:b,location:w,isErrored:u,agents:C}}function v(){return o.a.createElement("div",{className:"header"},o.a.createElement("img",{alt:"logo",src:"/scribe.png"}),o.a.createElement("div",null,o.a.createElement("h1",null,"LIGHT"),o.a.createElement("span",null,"Learning in Interactive Games with Humans and Text")))}var h=function(){var e=o.a.useState(!1),t=Object(r.a)(e,2),a=t[0],n=t[1];return o.a.useEffect(function(){if(!a){var e=setTimeout(function(){n(!0)},1e4);return function(){return clearTimeout(e)}}},[a,n]),o.a.createElement("div",{style:{height:"100vh",width:"100vw",display:"flex",alignItems:"center",justifyContent:"center",flexDirection:"column"}},o.a.createElement("div",{style:{width:500}},o.a.createElement("div",{style:{width:300}},o.a.createElement(v,null)),o.a.createElement("div",{style:{fontSize:20,marginTop:50,fontStyle:"italic"}},a?o.a.createElement("span",null,"It's been ",10," seconds, there's likely a server issue."):o.a.createElement("span",null,"Hang tight. You are entering a new world..."))))},b={host:"http://localhost",hostname:"localhost",port:"35494"},y=function(e){var t="https:"===e.protocol?"wss":"ws",a=new URL(e).searchParams.get("server");return a&&console.log("Using user-provided server hostname:",a),t+"://"+(a||b.hostname)+":"+b.port+"/game/socket"},N=function(){return new URL(window.location).searchParams.get("builder")};function k(e){return o.a.createElement("div",{style:{clear:"both",overflow:"auto"}},o.a.createElement("div",{className:"message type-setting"},e.text.split("\n").map(function(e,t){return o.a.createElement("p",{key:t},e)})))}function w(e){var t=e.text,a=e.caller,n=e.actor,l=e.isSelf,c=e.onReply,i=o.a.useState(!1),u=Object(r.a)(i,2),m=u[0],f=u[1],d="message type-dialogue ";return["tell","say","whisper"].includes(a)&&(t="&ldquo;"+t+"&rdquo;",d="message type-dialogue "),d+=l?"me":"other",m?o.a.createElement("div",{className:d},o.a.createElement("div",{className:"agent"},o.a.createElement("span",null,n),l?null:o.a.createElement(o.a.Fragment,null,o.a.createElement("i",{className:"fa fa-reply",onClick:function(){return c(n)}})," ",o.a.createElement("i",{className:"fa fa-commenting-o ",onClick:function(){return f(!0)}}))),o.a.createElement("div",{style:{opacity:0,height:1,pointerEvents:"none"}},t),o.a.createElement("input",{className:"edit-message",defaultValue:t}),o.a.createElement("button",{type:"submit",onClick:function(){return f(!1)}},"Suggest edit")):o.a.createElement("div",{className:d},o.a.createElement("div",{className:"agent"},o.a.createElement("span",null,n),l?null:o.a.createElement(o.a.Fragment,null,o.a.createElement(s.Tooltip,{title:"tell ".concat(n,"..."),position:"top"},o.a.createElement("i",{className:"fa fa-reply",onClick:function(){return c(n)}}))," ",o.a.createElement(s.Tooltip,{title:"Do you think something else should have been said instead? Provide feedback via an edit...",position:"top"},o.a.createElement("i",{className:"fa fa-commenting-o ",onClick:function(){return f(!0)}})))),t)}function S(e){var t=e.msg,a=e.onReply,n=e.agents,r=e.selfId;return["LookEvent","GoEvent","ExamineEvent","ErrorEvent","HelpEvent","text"].includes(t.caller)||null===t.caller?o.a.createElement(k,{text:t.text}):o.a.createElement(w,{text:t.text,isSelf:t.is_self||t.actors[0]===r,actor:n[t.actors[0]],onReply:a})}function x(e){var t=e.messages,a=e.onSubmit,n=e.persona,l=e.location,c=e.agents,i=o.a.useState(""),m=Object(r.a)(i,2),d=m[0],p=m[1],E=o.a.useRef(null),g=function(e){return e.match(/\d+$/)[0]},h=N(),b=o.a.useCallback(function(){return setTimeout(function(){E.current&&(E.current.scrollTop=E.current.scrollHeight)},0)},[E]);o.a.useEffect(function(){b()},[b,t]);var y=function(e){var t=e.filter(function(e){return!0!==e.is_self&&null!==e.caller});if(0===t.length)return[null,[]];var a=t[t.length-1];return{currentRoom:a.room_id,presentAgents:a.present_agent_ids}}(t).presentAgents,k=o.a.useState(!1),w=Object(r.a)(k,2),x=w[0],O=w[1],T=o.a.useState("\u2753"),R=Object(r.a)(T,2),j=R[0],_=R[1],I=o.a.useRef();o.a.useLayoutEffect(function(){I.current.focus()},[]),o.a.useEffect(function(){if(null!==n&&null!==n.name){var e=["a","the","an","of","with","holding"],t=n?n.name.split(" ").filter(function(e){return!!e}).map(function(e){return e.replace(/\.$/,"")}).filter(function(t){return-1===e.indexOf(t.toLowerCase())}).flatMap(function(e){return u.b.search(e).map(function(e){return e.native})}):[],a=t.length>0?t[0]:"\u2753";_(a)}},[n,_]);var L=o.a.useCallback(function(e){var t="tell ".concat(e,' ""');p(t),setTimeout(function(){return function(e,t){if(null!=e)if(e.createTextRange){var a=e.createTextRange();a.move("character",t),a.select()}else e.selectionStart?(e.focus(),e.setSelectionRange(t,t)):e.focus()}(I.current,t.length-1)},0)},[p,I]);return o.a.createElement("div",{className:"App"},o.a.createElement("div",{className:"sidebar"},o.a.createElement(v,null),o.a.createElement("div",{className:"game-state"},n?o.a.createElement("div",{className:"persona"},o.a.createElement("div",{className:f()("icon",{editing:x}),style:{cursor:"pointer"}},o.a.createElement("div",{className:"overlay"},"edit"),o.a.createElement("span",{role:"img","aria-label":"avatar",onClick:function(){return O(!0)}},j),x?o.a.createElement("div",{style:{position:"absolute",top:"80px",left:"50%",transform:"translateX(-50%)",zIndex:999}},o.a.createElement(C,{autoFocus:!0,onBlur:function(){return O(!1)},onSelect:function(e){_(e.native),O(!1)}})):null),o.a.createElement("h3",null,"You are ",n.name),n.description,h&&o.a.createElement(s.Tooltip,{style:{position:"absolute",bottom:0,right:5},title:"suggest changes for ".concat(n.name),position:"bottom"},o.a.createElement("a",{className:"data-model-deep-link",href:"".concat(h,"/edit/").concat(g(n.id)),rel:"noopener noreferrer",target:"_blank"},o.a.createElement("i",{className:"fa fa-edit","aria-hidden":"true"})))):null,l?o.a.createElement("div",{className:"location"},o.a.createElement("h3",null,l.name),l.description.split("\n").map(function(e,t){return o.a.createElement("p",{key:t},e)}),h&&o.a.createElement(s.Tooltip,{style:{position:"absolute",bottom:0,right:5},title:"suggest changes for ".concat(l.name.split(" the ")[1]),position:"bottom"},o.a.createElement("a",{className:"data-model-deep-link",href:"".concat(h,"/edit/").concat(g(l.id)),rel:"noopener noreferrer",target:"_blank"},o.a.createElement("i",{className:"fa fa-edit","aria-hidden":"true"})))):null)),o.a.createElement("div",{className:"chat-wrapper"},o.a.createElement("div",{className:"chat",ref:E},o.a.createElement("div",{className:"chatlog"},t.map(function(e,t){return o.a.createElement(S,{key:t,msg:e,agents:c,onReply:function(e){return L(e)},selfId:n.id})}))),o.a.createElement("div",{className:"controls"},o.a.createElement("form",{style:{display:"flex"},onSubmit:function(e){e.preventDefault(),d&&(a(d),p(""),b())}},o.a.createElement("input",{ref:I,value:d,onChange:function(e){return p(e.target.value)},onKeyPress:function(e){if("Enter"===e.key&&e.shiftKey){var t=e.target.value.startsWith('"')?"":'"',a=e.target.value.endsWith('"')?"":'"';p(t+e.target.value+a)}},className:"chatbox",placeholder:"Enter text to interact with the world here..."})),o.a.createElement("div",{className:"actions"},o.a.createElement("div",{style:{float:"left"}},y.filter(function(e){return e!==n.id}).map(function(e){var t=function(e){return c?c[e]:e}(e),a=g(e);return o.a.createElement("span",{key:t,style:{backgroundColor:"#eee",borderRadius:3,padding:"1px 3px",marginRight:5}},o.a.createElement("span",{onClick:function(){L(t)}},t," ",o.a.createElement(s.Tooltip,{title:"tell ".concat(t,"..."),position:"bottom"},o.a.createElement("i",{className:"fa fa-comment-o","aria-hidden":"true"}))),h&&o.a.createElement(o.a.Fragment,null," ",o.a.createElement(s.Tooltip,{title:"suggest changes for ".concat(t),position:"bottom"},o.a.createElement("a",{className:"data-model-deep-link",href:"".concat(h,"/edit/").concat(a),rel:"noopener noreferrer",target:"_blank"},o.a.createElement("i",{className:"fa fa-edit","aria-hidden":"true"})))))})),o.a.createElement("div",{style:{display:"flex",alignItems:"center",float:"right"}},o.a.createElement("span",{className:f()("hint-message","fadeHidden",{fadeShow:d.length>0&&'"'===d[0]})},"Tip: Hit Shift+Enter to auto-wrap your entry in quotes")),[].map(function(e){return o.a.createElement("span",{className:"action",key:e},e)})))))}var O=function e(t){var a=t.onBlur,r=Object(n.a)(t,["onBlur"]);return e.handleClickOutside=function(){return a()},o.a.createElement(u.a,r)},C=Object(d.a)(O,{handleClickOutside:function(){return O.handleClickOutside}}),T=document.getElementById("root");i.a.render(o.a.createElement(function(){var e=g(o.a.useMemo(function(){return y(window.location)},[])),t=e.isErrored,a=e.messages,n=e.submitMessage,r=e.persona,l=e.location,c=e.agents;return t?o.a.createElement("div",{style:{textAlign:"center",marginTop:30,fontSize:30}},"Could not connect to the server."):0===a.length?o.a.createElement(h,null):o.a.createElement(x,{messages:a,onSubmit:n,persona:r,location:l,agents:c})},null),T)}},[[15,1,2]]]);
//# sourceMappingURL=main.124dc408.chunk.js.map