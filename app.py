"""Painel de otimização — janela desktop. Uso: python app.py
Ordem: 1) pywebview + WebView2 (sem borda)  2) Edge/Chrome modo app  3) navegador padrão."""
import ctypes, glob, hashlib, json, os, re, secrets, shutil, sqlite3, stat, subprocess, sys, tempfile, threading, time, uuid, webbrowser
from ctypes import wintypes as wt
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from pathlib import Path

try:
    import webview
except Exception:
    webview = None

HTML = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tellez</title>
<style>
:root{--bg:#d3d3d3;--fg:#0d0d0d;--bd:rgba(0,0,0,.2);--mut:rgba(0,0,0,.6);--e:cubic-bezier(.2,.8,.2,1);--dir:1;font-family:"Segoe UI",system-ui,sans-serif}
:root[data-theme=dark]{--bg:#0c0c0c;--fg:#f2f2f2;--bd:rgba(255,255,255,.13);--mut:rgba(255,255,255,.5)}
*{box-sizing:border-box;margin:0}
html,body{overflow:hidden}
body{background:var(--bg);color:var(--fg);height:100vh;overflow:hidden}
button,input{font:inherit;color:inherit}
button{cursor:pointer;position:relative;overflow:hidden;background:none;border:0;text-shadow:none}
#bg,#gl{position:fixed;inset:0;width:100%;height:100%}
::view-transition-old(root),::view-transition-new(root){animation:none;mix-blend-mode:normal}

/* topo */
.top{position:fixed;top:0;left:0;right:0;z-index:5;display:flex;align-items:center;justify-content:space-between;padding:18px 32px;animation:dn 1s var(--e) backwards}
.top::before{content:"";position:absolute;inset:0 0 -26px;background:linear-gradient(var(--bg) 35%,transparent);z-index:-1;pointer-events:none}
@keyframes dn{from{opacity:0;transform:translateY(-24px)}}
.logo{display:flex;align-items:center;gap:10px;font-size:19px;font-weight:600;width:190px;letter-spacing:.01em}
.logo i{width:22px;height:22px;border-radius:50%;border:2px solid var(--fg);position:relative}
.logo i::after{content:"";position:absolute;inset:4px;border-radius:50%;border:1.5px solid var(--fg);animation:rg 4s ease-in-out infinite}
@keyframes rg{50%{inset:1px;opacity:.3}}
.right{display:flex;align-items:center;gap:10px;width:190px;justify-content:flex-end}
.tg{width:40px;height:40px;border-radius:50%;border:1px solid var(--bd);background:color-mix(in srgb,var(--bg) 82%,transparent);display:grid;place-items:center;transition:transform .3s var(--e)}
.tg:hover{transform:scale(1.1)}
.tg b{width:18px;height:18px;border-radius:50%;border:2px solid var(--fg);background:linear-gradient(90deg,var(--fg) 50%,transparent 50%);transition:transform .9s cubic-bezier(.7,0,.2,1)}
:root[data-theme=dark] .tg b{transform:rotate(180deg)}
.wc{display:none;width:34px;height:34px;border-radius:50%;border:1px solid var(--bd);background:color-mix(in srgb,var(--bg) 82%,transparent);place-items:center;flex:none;transition:transform .3s var(--e),background .3s,color .3s,border-color .3s}
body.app .wc{display:grid}
.wc:hover{transform:scale(1.1);background:var(--fg);color:var(--bg);border-color:var(--fg)}
.wc svg{width:14px;height:14px;stroke:currentColor;stroke-width:2;stroke-linecap:round;fill:none}

/* conteúdo */
main{position:fixed;inset:0;z-index:2;padding:104px 32px 40px;overflow-y:auto;overflow-x:hidden;scrollbar-width:thin;scrollbar-color:var(--bd) transparent;text-shadow:0 0 14px var(--bg),0 0 5px var(--bg)}
.wrap{position:relative;max-width:960px;margin:0 auto}
.view{display:none}.view.on{display:block;position:relative}
.view.off{display:block;position:absolute;inset:0 0 auto 0;pointer-events:none;animation:lv .3s var(--e) forwards}
@keyframes lv{to{opacity:0;transform:translateX(calc(var(--dir)*-70px)) scale(.96);filter:blur(10px)}}
.view.drawing .lead,.view.drawing .ms,.view.drawing .row{border-bottom-color:transparent!important}
.ink{position:absolute;left:0;top:0;width:100%;height:100%;overflow:visible;pointer-events:none;z-index:4}
.ink *{fill:none;stroke:var(--fg);stroke-width:1.2;stroke-linecap:round;stroke-dasharray:1}
.ink circle{fill:var(--fg);stroke:none;stroke-dasharray:none;filter:drop-shadow(0 0 4px var(--fg))}
.lead{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;flex-wrap:wrap;padding-bottom:28px;border-bottom:1px solid var(--bd)}
.lb{color:var(--mut);font-size:14px;margin-bottom:8px}
.big{font-size:clamp(54px,8vw,84px);font-weight:200;line-height:1;font-variant-numeric:tabular-nums;letter-spacing:-.03em}
.mid{flex:1;text-align:center;color:var(--mut);transition:opacity .25s,transform .3s var(--e)}
.mid.out,.gt.out{opacity:0;transform:translateY(8px)}
.btn,.go{border-radius:99px;transition:background .35s,color .35s,transform .25s var(--e)}
.btn{border:1px solid var(--fg);padding:11px 24px}
.btn:hover,.btn.solid:hover{background:var(--fg);color:var(--bg)}
.btn.solid{background:var(--fg);color:var(--bg)}
.btn.solid:hover{background:none;color:var(--fg)}
.btn:hover{transform:translateY(-1px)}
.go{background:var(--fg);color:var(--bg);padding:15px 40px;min-width:210px;font-weight:600}
.btn:active,.go:active{transform:scale(.94)}
.go:hover{transform:scale(1.04)}
.gt{display:inline-flex;gap:8px;align-items:center;justify-content:center;position:relative;transition:opacity .22s,transform .25s var(--e);font-variant-numeric:tabular-nums}
.fill{position:absolute;inset:0;background:color-mix(in srgb,var(--bg) 24%,transparent);transform:scaleX(0);transform-origin:left;will-change:transform}
#pct{display:inline-block;min-width:3.2ch;text-align:left}
.gow{position:relative}
.rip{position:absolute;left:50%;top:50%;width:60px;height:60px;margin:-30px;border:1px solid var(--fg);border-radius:50%;pointer-events:none;animation:rp 2.2s var(--e) forwards}
@keyframes rp{to{transform:scale(8);opacity:0}}
.ck{fill:none;stroke:currentColor;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:24;stroke-dashoffset:24;animation:ck .6s .1s var(--e) forwards}
@keyframes ck{to{stroke-dashoffset:0}}
.rpl{position:absolute;border-radius:50%;background:currentColor;opacity:.22;transform:scale(0);animation:rpl .75s var(--e) forwards;pointer-events:none}
@keyframes rpl{to{transform:scale(1);opacity:0}}
.go.busy::after{content:"";position:absolute;inset:0;background:linear-gradient(100deg,transparent 30%,color-mix(in srgb,var(--bg) 35%,transparent) 50%,transparent 70%);transform:translateX(-100%);animation:sh 1.3s linear infinite}
@keyframes sh{to{transform:translateX(100%)}}
.pop{animation:pop .9s var(--e);transform-origin:left center}
.go.pop{transform-origin:center}
@keyframes pop{35%{transform:scale(1.07)}}

/* nav */
nav{position:relative;display:flex;gap:2px;padding:5px;border:1px solid var(--bd);border-radius:99px;background:color-mix(in srgb,var(--bg) 82%,transparent)}
nav button{padding:9px 18px;border-radius:99px;color:var(--mut);z-index:1;transition:color .5s var(--e),transform .3s var(--e)}
nav button:active{transform:scale(.94)}
nav button:hover{color:var(--fg)}
.inv{position:absolute;inset:0;display:flex;gap:2px;padding:5px;color:var(--bg);pointer-events:none;z-index:2;clip-path:inset(100%)}
.inv span{padding:9px 18px;white-space:nowrap}
.pill{position:absolute;top:5px;left:0;height:calc(100% - 10px);border-radius:99px;background:var(--fg);will-change:transform,width}
body.locked nav{visibility:hidden}
body:not(.locked) nav{animation:li .9s var(--e) .35s backwards}
/* lista de limpeza */
.acts{display:flex;gap:10px}
.btn:disabled{opacity:.4;pointer-events:none}
.grp{padding:26px 8px 8px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--mut)}
.row{position:relative;display:flex;align-items:center;gap:16px;padding:15px 8px;border-bottom:1px solid var(--bd);overflow:hidden;cursor:pointer;transition:opacity .45s,background-color .5s var(--e),box-shadow .5s var(--e)}
.row:hover{background-color:color-mix(in srgb,var(--fg) 4%,transparent)}
.row.act{background-color:color-mix(in srgb,var(--fg) 7%,transparent)}
.row.chg{box-shadow:inset 2px 0 0 var(--fg);background-color:color-mix(in srgb,var(--fg) 4%,transparent)}
.row.dim{opacity:.45}
.row .n{flex:1;min-width:0}
.row small{display:block;color:var(--mut);margin-top:2px;font-size:13px;line-height:1.4}
.row small.av{opacity:.85}
.val{color:var(--mut);font-variant-numeric:tabular-nums;min-width:84px;text-align:right}
.tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:7px}
.tag{font-size:11px;padding:2px 9px;border:1px solid var(--bd);border-radius:99px;color:var(--mut)}
.tag.st:empty{display:none}
.row.sweep::after{content:"";position:absolute;left:0;right:0;top:50%;height:2px;background:var(--fg);animation:sw .9s var(--e) forwards}
@keyframes sw{0%{transform:scaleX(0);transform-origin:left}50%{transform:scaleX(1);transform-origin:left}51%{transform-origin:right}100%{transform:scaleX(0);transform-origin:right}}
.bar{height:2px;background:var(--bd);margin-bottom:6px}
.bar i{display:block;height:100%;width:0;background:var(--fg);transition:width .6s var(--e)}
.sw{appearance:none;width:46px;height:26px;border-radius:99px;border:1px solid var(--fg);position:relative;background:none;transition:background .4s;cursor:pointer;flex:none}
.sw::after{content:"";position:absolute;left:3px;top:3px;width:18px;height:18px;border-radius:50%;background:var(--fg);transition:left .5s cubic-bezier(.3,1.6,.5,1),background .4s,transform .25s}
.sw:checked{background:var(--fg)}.sw:checked::after{left:23px;background:var(--bg)}
.sw:active::after{transform:scale(1.2)}.sw:disabled{cursor:default}
.sw:focus-visible{outline:2px solid var(--fg);outline-offset:3px}
.ms.three{grid-template-columns:repeat(3,1fr)}
.ms.three .v{font-size:32px}
.note{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:18px;padding:12px 16px;border-radius:14px;background:var(--bd);font-size:13px;color:var(--mut)}
.note[hidden]{display:none}
.tips{list-style:none;padding:18px 0 4px;display:grid;gap:6px;font-size:13px;color:var(--mut)}
.tips li::before{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--fg);margin-right:10px;vertical-align:middle}
.tips:empty{display:none}
/* métricas */
.ms{display:grid;grid-template-columns:repeat(5,1fr);gap:28px;padding:32px 0;border-bottom:1px solid var(--bd)}
.m{transition:transform .6s var(--e)}.m:hover{transform:translateY(-2px)}
.m h3{font-size:13px;font-weight:400;color:var(--mut)}
.m .nm{font-size:12px;line-height:1.35;color:var(--mut);opacity:.75;margin-top:3px;min-height:2.7em;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;word-break:break-word}
.v{position:relative;display:inline-block;font-size:38px;font-weight:200;margin:8px 0 12px;font-variant-numeric:tabular-nums}
.t{height:2px;background:var(--bd);border-radius:2px;overflow:hidden}
.t i{display:block;height:100%;width:0;background:var(--fg);border-radius:2px;transition:width 1.4s var(--e)}
.dl{position:absolute;left:100%;top:6px;margin-left:8px;font-size:13px;color:var(--mut);white-space:nowrap;animation:dl 2s var(--e) forwards}
@keyframes dl{from{opacity:0;transform:translateY(10px)}20%{opacity:1}to{opacity:0;transform:translateY(-26px)}}
.chart{padding-top:26px}
.lg{display:flex;gap:20px;font-size:13px;color:var(--mut);margin-bottom:8px}
.lg span::before{content:"";display:inline-block;width:18px;border-top:2px solid var(--fg);vertical-align:middle;margin-right:8px}
.lg .d::before{border-top-style:dashed}
canvas#spark{width:100%;height:120px;display:block}

/* configurações */
.row[hidden]{display:none}
#cfgl .row{flex-wrap:wrap;cursor:default}
.seg{display:flex;gap:2px;padding:3px;border:1px solid var(--bd);border-radius:99px;flex:none}
.seg button{padding:6px 14px;border-radius:99px;color:var(--mut);font-size:13px;transition:background .35s,color .35s}
.seg button:hover{color:var(--fg)}
.seg button.on{background:var(--fg);color:var(--bg)}
.pal{display:flex;gap:10px;flex:none}
.dot{width:24px;height:24px;border-radius:50%;background:var(--c);box-shadow:0 0 0 1px var(--bd);transition:transform .3s var(--e),box-shadow .3s}
.dot:hover{transform:scale(1.15)}
.dot.on{box-shadow:0 0 0 2px var(--bg),0 0 0 4px var(--fg)}
.rng{appearance:none;-webkit-appearance:none;width:170px;height:2px;background:var(--bd);border-radius:2px;outline:none;flex:none;cursor:pointer}
.rng::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;border-radius:50%;background:var(--fg);border:0;transition:transform .25s var(--e)}
.rng::-webkit-slider-thumb:hover{transform:scale(1.25)}
body.compact .row{padding:9px 8px}
body.compact .grp{padding-top:16px}
body.compact .row small{font-size:12px}
body.calm *,body.calm *::before,body.calm *::after{animation-duration:.01s!important;transition-duration:.01s!important}

/* toast e modal */
#toast{position:fixed;left:50%;bottom:28px;z-index:9;padding:12px 24px;border-radius:99px;background:var(--fg);color:var(--bg);text-shadow:none;transform:translate(-50%,220%);opacity:0;transition:transform .7s cubic-bezier(.3,1.5,.5,1),opacity .4s}
#toast.on{transform:translate(-50%,0);opacity:1}
.mdl{position:fixed;inset:0;z-index:20;display:grid;place-items:center;padding:20px;visibility:hidden;pointer-events:none}
.mdl::before{content:"";position:absolute;inset:0;background:color-mix(in srgb,var(--bg) 78%,transparent);opacity:0;transition:opacity .45s var(--e)}
.mdl.on{visibility:visible;pointer-events:auto}
.mdl.show::before{opacity:1}
.mdl .card.wide{width:min(580px,100%);max-height:88vh;display:flex;flex-direction:column}
.mlist{overflow-y:auto;flex:1;min-height:0;margin:0 -8px;padding:0 8px;scrollbar-width:thin;scrollbar-color:var(--bd) transparent}
.mlist .grp{padding:16px 0 4px}
.mlist label{display:flex;gap:14px;align-items:center;padding:11px 0;border-bottom:1px solid var(--bd);cursor:pointer}
.mlist label .n{flex:1;min-width:0}
.mlist label small{display:block;color:var(--mut);font-size:12px;line-height:1.35;margin-top:2px}
.mdl.show .mlist{animation:li .7s var(--e) .3s backwards}
.mdl .card{position:relative;width:min(460px,100%);padding:28px;border:1px solid var(--bd);border-radius:24px;background:var(--bg);opacity:0;transform:translateY(40px) scale(.9);transition:transform .8s cubic-bezier(.2,1.2,.35,1),opacity .4s var(--e)}
.mdl.show .card{opacity:1;transform:none}
.mdl.out .card{transform:translateY(16px) scale(.96);transition:transform .32s var(--e),opacity .25s}
.mdl h2{font-size:22px;font-weight:300}
.mdl .sub{color:var(--mut);font-size:14px;margin:4px 0 14px}
.mdl ul{list-style:none;padding:0}
.mdl li{display:flex;gap:14px;align-items:flex-start;padding:12px 0;border-bottom:1px solid var(--bd)}
.mdl li div{flex:1}
.mdl li small{display:block;color:var(--mut);margin-top:2px;font-size:13px;line-height:1.4}
.mdl li svg{flex:none;width:22px;height:22px;margin-top:1px;stroke:var(--fg);fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:60;transition:transform .5s cubic-bezier(.3,1.6,.5,1)}
.mdl li:hover svg{transform:scale(1.15) rotate(-6deg)}
.mdl .warn{margin:18px 0 22px;padding:12px 14px;border-radius:14px;background:var(--bd);font-size:13px;line-height:1.45;color:var(--mut)}
.mdl .warn b{color:var(--fg);font-weight:600}
.mdl .macts{display:flex;gap:10px;justify-content:flex-end}
.mdl.show h2{animation:li .7s var(--e) .12s backwards}
.mdl.show .sub{animation:li .7s var(--e) .2s backwards}
.mdl.show li{animation:li .7s var(--e) backwards;animation-delay:calc(.3s + var(--i)*.1s)}
.mdl.show li svg{animation:dr 1.1s var(--e) backwards;animation-delay:calc(.45s + var(--i)*.1s)}
.mdl.show .warn{animation:li .7s var(--e) .72s backwards}
.mdl.show .macts{animation:li .7s var(--e) .84s backwards}
@keyframes li{from{opacity:0;transform:translateY(12px)}}
@keyframes dr{from{stroke-dashoffset:60}}
button:focus-visible{outline:2px solid var(--fg);outline-offset:3px}

/* login */
body.locked main{visibility:hidden}
#lg{position:fixed;inset:0;z-index:15;display:grid;place-items:center;padding:20px;pointer-events:none;transition:opacity .6s var(--e),transform .8s var(--e)}
body:not(.locked) #lg{opacity:0;transform:scale(1.05);visibility:hidden;transition:opacity .6s var(--e),transform .8s var(--e),visibility 0s .8s}
#lf{width:min(360px,100%);display:flex;flex-direction:column;gap:34px;pointer-events:auto}
#lf>*{animation:li 1s var(--e) backwards}
#lf>:nth-child(1){animation-delay:.3s}#lf>:nth-child(2){animation-delay:.5s}
.fld{position:relative;display:block;border-bottom:1px solid var(--bd)}
.fld input{width:100%;background:none;border:0;outline:none;padding:22px 0 9px;font-size:20px;font-weight:300}
.fld span{position:absolute;left:0;top:22px;font-size:20px;font-weight:300;color:var(--mut);pointer-events:none;transform-origin:left;transition:transform .5s var(--e),color .4s}
.fld input:focus+span,.fld input:not(:placeholder-shown)+span{transform:translateY(-20px) scale(.65);color:var(--fg)}
.fld i{position:absolute;left:0;right:0;bottom:-1px;height:1px;background:var(--fg);transform:scaleX(0);transform-origin:left;transition:transform .7s var(--e)}
.fld input:focus~i{transform:scaleX(1)}
#lf .go{width:100%}
#lf .go canvas{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
#lf .go b{position:relative;font-weight:inherit}

@media(max-width:820px){.top{padding:12px 14px}.logo{width:auto}.logo span{display:none}.right{width:auto}nav button,.inv span{padding:8px 10px;font-size:13px}main{padding:84px 16px 30px}.ms,.ms.three{grid-template-columns:repeat(2,1fr)}.val{min-width:60px}}
@media(prefers-reduced-motion:reduce){*{animation-duration:.01s!important;transition-duration:.01s!important}}
</style>
</head>
<body class="locked">
<canvas id="gl"></canvas><canvas id="bg"></canvas>
<header class="top pywebview-drag-region">
  <div class="logo"><i></i><span>Tellez</span></div>
  <nav id="nav"><span class="pill" id="pill"></span>
    <button class="on" data-v="dash">Painel</button><button data-v="clean">Limpeza</button><button data-v="win">Windows</button><button data-v="per">Periféricos</button><button data-v="cfg">Configurações</button>
    <div class="inv" id="inv" aria-hidden="true"><span>Painel</span><span>Limpeza</span><span>Windows</span><span>Periféricos</span><span>Configurações</span></div>
  </nav>
  <div class="right"><button class="tg" id="tg" aria-label="Alternar tema"><b></b></button>
    <button class="wc" id="wmin" aria-label="Minimizar"><svg viewBox="0 0 14 14"><path d="M2 7h10"/></svg></button>
    <button class="wc" id="wcls" aria-label="Fechar"><svg viewBox="0 0 14 14"><path d="M2.5 2.5l9 9M11.5 2.5l-9 9"/></svg></button></div>
</header>
<div id="lg"><form id="lf" autocomplete="off" novalidate>
  <label class="fld"><input id="lu" type="text" placeholder=" " maxlength="24" spellcheck="false" autocomplete="off"><span>Usuário</span><i></i></label>
  <button class="go" type="submit"><canvas id="lgb"></canvas><b>Login</b></button>
</form></div>
<main id="main"><div class="wrap">
  <section class="view on" id="v-dash">
    <div class="lead"><div><div class="lb">Saúde do sistema</div><div class="big" id="score">0</div></div>
      <div class="mid" id="mid">Tudo pronto para otimizar</div>
      <div class="gow" id="gow"><button class="go" id="go"><i class="fill" id="fill"></i><span class="gt" id="gt">Otimizar agora</span></button></div></div>
    <div class="ms" id="ms"></div>
    <div class="chart"><div class="lg"><span>Processador</span><span class="d">Memória</span></div><canvas id="spark"></canvas></div>
  </section>
  <section class="view" id="v-clean">
    <div class="lead"><div><div class="lb">Selecionado para limpar</div><div class="big" id="ctot">0 MB</div></div>
      <div class="mid" id="cmid">Preparando…</div>
      <div class="acts"><button class="btn" id="scan">Escanear</button><button class="btn solid" id="clean">Limpar</button></div></div>
    <div class="ms three">
      <div class="m"><h3>Espaço livre agora</h3><div class="nm" id="t1n">&nbsp;</div><div class="v"><span id="t1v">—</span></div></div>
      <div class="m"><h3>Depois da limpeza</h3><div class="nm" id="t2n">&nbsp;</div><div class="v"><span id="t2v">—</span></div></div>
      <div class="m"><h3>Impacto no desempenho</h3><div class="nm" id="t3n">&nbsp;</div><div class="v"><span id="t3v">—</span></div></div>
    </div>
    <div class="note" id="cadm" hidden><span>Alguns itens (Windows, DISM, SFC, TRIM) precisam de permissão de administrador.</span><button class="btn" id="celev">Reiniciar como administrador</button></div>
    <ul class="tips" id="ctips"></ul>
    <div class="bar"><i id="cbar"></i></div><div id="cl"></div>
  </section>
  <section class="view" id="v-win">
    <div class="lead"><div><div class="lb">Otimizações ativas</div><div class="big" id="wtot">0</div></div>
      <div class="mid" id="wmid">Preparando…</div>
      <div class="acts"><button class="btn" id="wana">Reanalisar</button><button class="btn" id="wrec">Recomendadas</button><button class="btn solid" id="wapl">Aplicar</button></div></div>
    <div class="ms three">
      <div class="m"><h3>Ajustes ativos</h3><div class="nm" id="w1n">&nbsp;</div><div class="v"><span id="w1v">—</span></div></div>
      <div class="m"><h3>Seu PC</h3><div class="nm" id="w2n">&nbsp;</div><div class="v"><span id="w2v">—</span></div></div>
      <div class="m"><h3>Nível de otimização</h3><div class="nm" id="w3n">&nbsp;</div><div class="v"><span id="w3v">—</span></div></div>
    </div>
    <div class="note" id="wadm" hidden><span>Ajustes de sistema, serviços e jogos precisam de permissão de administrador.</span><button class="btn" id="welev">Reiniciar como administrador</button></div>
    <ul class="tips" id="wtips"></ul>
    <div class="bar"><i id="wbar"></i></div><div id="wl"></div>
  </section>
<section class="view" id="v-per">
    <div class="lead"><div><div class="lb">Otimizações ativas</div><div class="big" id="xtot">0</div></div>
      <div class="mid" id="xmid">Preparando…</div>
      <div class="acts"><button class="btn" id="xana">Reanalisar</button><button class="btn" id="xrec">Recomendadas</button><button class="btn solid" id="xapl">Aplicar</button></div></div>
    <div class="ms three">
      <div class="m"><h3>Ajustes ativos</h3><div class="nm" id="x1n">&nbsp;</div><div class="v"><span id="x1v">—</span></div></div>
      <div class="m"><h3>Seu monitor</h3><div class="nm" id="x2n">&nbsp;</div><div class="v"><span id="x2v">—</span></div></div>
      <div class="m"><h3>Nível de otimização</h3><div class="nm" id="x3n">&nbsp;</div><div class="v"><span id="x3v">—</span></div></div>
    </div>
    <div class="note" id="xadm" hidden><span>Ajustes de energia, USB e sistema precisam de permissão de administrador.</span><button class="btn" id="xelev">Reiniciar como administrador</button></div>
    <ul class="tips" id="xtips"></ul>
    <div class="bar"><i id="xbar"></i></div><div id="xl"></div>
  </section>
  <section class="view" id="v-cfg">
    <div class="lead"><div><div class="lb">Personalizar o app</div><div class="big">Ajustes</div></div>
      <div class="mid">As alterações são salvas na hora</div>
      <div class="acts"><button class="btn" id="cfgreset">Restaurar padrões</button></div></div>
    <div id="cfgl"></div>
  </section>
</div></main>
<div id="toast"></div>
<div class="mdl" id="xmdl" role="dialog" aria-modal="true"><div class="card wide">
  <h2>Aplicar ajustes</h2><p class="sub">Confira as alterações. Desmarque o que não quiser:</p>
  <div class="mlist" id="xlist"></div>
  <p class="warn" id="xwarn"></p>
  <div class="macts"><button class="btn" id="xno">Cancelar</button><button class="btn solid" id="xyes">Aplicar</button></div>
</div></div>
<div class="mdl" id="mdl" role="dialog" aria-modal="true"><div class="card">
  <h2>Otimizar agora</h2><p class="sub">Veja o que será feito:</p>
  <ul>
    <li style="--i:0"><svg viewBox="0 0 24 24"><rect x="5" y="5" width="14" height="14" rx="3"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/></svg><div>Liberar memória RAM<small>Pede aos programas abertos que devolvam a memória que não estão usando agora. Nenhum programa é fechado.</small></div></li>
    <li style="--i:1"><svg viewBox="0 0 24 24"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/></svg><div>Limpar arquivos temporários<small>Apaga arquivos da pasta temporária com mais de 1 dia. Arquivos em uso são ignorados.</small></div></li>
    <li style="--i:2"><svg viewBox="0 0 24 24"><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8M21 3v5h-5M21 12a9 9 0 0 1-15.5 6.2L3 16M3 21v-5h5"/></svg><div>Mostrar a diferença<small>O painel é atualizado com os números reais depois da limpeza.</small></div></li>
  </ul>
  <p class="warn"><b>Efeito temporário.</b> Os programas voltam a pedir memória conforme você os usa, então a RAM tende a subir de novo e pode ficar parecida com a de antes. Os temporários apagados são só lixo que o Windows recria quando precisa.</p>
  <div class="macts"><button class="btn" id="mno">Cancelar</button><button class="btn solid" id="myes">Confirmar</button></div>
</div></div>

<div class="mdl" id="cmdl" role="dialog" aria-modal="true"><div class="card wide">
  <h2>Limpar agora</h2><p class="sub">Marque ou desmarque o que deve ser limpo:</p>
  <div class="mlist" id="mlist"></div>
  <p class="warn" id="mwarn"></p>
  <div class="macts"><button class="btn" id="cno">Cancelar</button><button class="btn solid" id="cyes">Limpar</button></div>
</div></div>

<div class="mdl" id="wmdl" role="dialog" aria-modal="true"><div class="card wide">
  <h2>Aplicar ajustes</h2><p class="sub">Confira as alterações. Desmarque o que não quiser:</p>
  <div class="mlist" id="wlist"></div>
  <p class="warn" id="wwarn"></p>
  <div class="macts"><button class="btn" id="wno">Cancelar</button><button class="btn solid" id="wyes">Aplicar</button></div>
</div></div>

<script>
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],R=(a,b)=>a+Math.random()*(b-a),cl=(v,a=0,b=100)=>Math.max(a,Math.min(b,v)),
root=document.documentElement,wait=ms=>new Promise(r=>setTimeout(r,ms)),mb=v=>v>=1000?(v/1000).toFixed(2)+' GB':Math.round(v)+' MB',
main=$('#main'),score=$('#score'),toastEl=$('#toast');
/* aparência fixa (sem tela de ajustes): só o tema é salvo */
const cfg={theme:matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light',speed:.5,dens:16,int:1,themeMode:'auto',pal:'cinza',bg:1,anim:1,rip:1,vt:1,calm:0,compact:0,autologin:0,confirm:1,autoscan:1,toast:1,top:0,poll:1000,startTab:'dash'};
try{Object.assign(cfg,JSON.parse(localStorage.painel_cfg||'{}'))}catch(e){}
const save=()=>{try{localStorage.painel_cfg=JSON.stringify(cfg)}catch(e){}};
root.dataset.theme=cfg.theme;

function tween(el,to,fmt=Math.round,ms=800){const f=el._c??0,t0=performance.now();cancelAnimationFrame(el._r);
  (function s(t){const p=cl((t-t0)/ms,0,1),v=f+(to-f)*(1-Math.pow(1-p,3));el._c=v;el.textContent=fmt(v);if(p<1)el._r=requestAnimationFrame(s)})(t0)}
function toast(t){if(!cfg.toast)return;toastEl.textContent=t;toastEl.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(()=>toastEl.classList.remove('on'),3200)}
const setText=async(el,html,c='out')=>{el.classList.add(c);await wait(240);el.innerHTML=html;el.classList.remove(c)};

addEventListener('pointerdown',e=>{if(!cfg.rip||e.target.matches('input'))return;const h=e.target.closest('button,.row');if(!h)return;
  const r=h.getBoundingClientRect(),d=Math.max(r.width,r.height)*2.2,s=document.createElement('span');s.className='rpl';
  s.style.cssText=`width:${d}px;height:${d}px;left:${e.clientX-r.left-d/2}px;top:${e.clientY-r.top-d/2}px`;h.append(s);setTimeout(()=>s.remove(),800)});

/* tema */
let morph=0;
function setTheme(t,x=innerWidth/2,y=innerHeight/2){
  const go=()=>{cfg.theme=t;root.dataset.theme=t;save();GL&&uni();window.applyPal&&applyPal()};morph=2.2;
  if(!document.startViewTransition||!cfg.vt)return go();
  const vt=document.startViewTransition(go),r=Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y));
  vt.ready.then(()=>root.animate({clipPath:[`circle(0px at ${x}px ${y}px)`,`circle(${r}px at ${x}px ${y}px)`]},{duration:1500,easing:'cubic-bezier(.7,0,.2,1)',pseudoElement:'::view-transition-new(root)'}));
}
$('#tg').onclick=e=>setTheme(cfg.theme=='dark'?'light':'dark',e.clientX,e.clientY);

/* relevo: WebGL2 (uniformes estáticos só quando mudam) com plano B em canvas 2D */
const gc=$('#gl'),cv=$('#bg'),ctx=cv.getContext('2d'),DPR=Math.min(devicePixelRatio||1,2),U={};
let GL=gc.getContext('webgl2',{alpha:true,premultipliedAlpha:true,antialias:false}),W,H,mx=-999,my=-999,sx=-999,sy=-999,T=0,grid;
if(GL){const mk=(t,src)=>{const x=GL.createShader(t);GL.shaderSource(x,src);GL.compileShader(x);return x},pr=GL.createProgram();
  GL.attachShader(pr,mk(GL.VERTEX_SHADER,`#version 300 es
void main(){vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2);gl_Position=vec4(p*2.-1.,0,1);}`));
  GL.attachShader(pr,mk(GL.FRAGMENT_SHADER,`#version 300 es
precision highp float;uniform vec2 uR,uM;uniform float uT,uD,uI,uK,uP;out vec4 o;
float h(vec2 p,float t){vec2 d=p-uM;return sin(p.x*.0042+t*.6)*1.6+sin(p.y*.0055-t*.45)*1.5+sin((p.x+p.y)*.0031+t*.35)*1.8+sin(length(p-vec2(uR.x*.7,uR.y*.3))*.006-t*.5)*1.6+sin(p.x*.009+p.y*.006-t*.5)*1.1+sin(p.y*.013+t*.4+sin(p.x*.006+t*.3)*2.2)*.9+sin(p.x*.016-p.y*.011+t)*.35+.4*exp(-dot(d,d)/45000.);}
void main(){vec2 p=vec2(gl_FragCoord.x,uR.y*uP-gl_FragCoord.y)/uP;float v=(h(p,uT)+6.5)*uD/13.,w=max(fwidth(v),1e-5),id=floor(v+.5);
float major=step(mod(id,4.),.5),hw=mix(.55,.85,major)*uP,a=1.-smoothstep(hw-.7,hw+.7,abs(v-id)/w);
a*=mix(.15,.34,major)*uI*step(0.,id)*step(id,uD-1.);o=vec4(vec3(uK)*a,a);}`));
  GL.linkProgram(pr);
  if(!GL.getProgramParameter(pr,GL.LINK_STATUS))GL=null;
  else{GL.useProgram(pr);for(const n of ['uR','uM','uT','uD','uI','uK','uP'])U[n]=GL.getUniformLocation(pr,n);GL.bindVertexArray(GL.createVertexArray());GL.clearColor(0,0,0,0)}}
gc.style.display=GL?'block':'none';cv.style.display=GL?'none':'block';
function uni(){GL.uniform2f(U.uR,W,H);GL.uniform1f(U.uD,cfg.dens);GL.uniform1f(U.uI,cfg.int);GL.uniform1f(U.uK,cfg.theme=='dark'?1:0);GL.uniform1f(U.uP,DPR)}
const resize=()=>{W=cv.width=innerWidth;H=cv.height=innerHeight;if(GL){gc.width=W*DPR;gc.height=H*DPR;GL.viewport(0,0,gc.width,gc.height);uni()}};
resize();addEventListener('resize',()=>{resize();pill(true)});
addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY});
const E=[[],[3,2],[2,1],[3,1],[0,1],[0,1,3,2],[0,2],[0,3],[0,3],[0,2],[0,3,2,1],[0,1],[3,1],[2,1],[3,2],[]];
const fld=(x,y,t)=>{const dx=x-sx,dy=y-sy;
  return Math.sin(x*.0042+t*.6)*1.6+Math.sin(y*.0055-t*.45)*1.5+Math.sin((x+y)*.0031+t*.35)*1.8+Math.sin(Math.hypot(x-W*.7,y-H*.3)*.006-t*.5)*1.6+Math.sin(x*.009+y*.006-t*.5)*1.1+Math.sin(y*.013+t*.4+Math.sin(x*.006+t*.3)*2.2)*.9+Math.sin(x*.016-y*.011+t)*.35+.4*Math.exp(-(dx*dx+dy*dy)/45000)};
function contours(g,gr,cx,cy,s,k,am,ai){
  const n=cfg.dens,step=13/n;
  for(let L=0;L<n;L++){
    const lv=-6.5+L*step,major=L%4==0;g.beginPath();
    for(let j=0;j<cy;j++)for(let i=0;i<cx;i++){
      const q=j*(cx+1)+i,a=gr[q],b=gr[q+1],c=gr[q+cx+2],d=gr[q+cx+1],e=E[(a>lv?8:0)|(b>lv?4:0)|(c>lv?2:0)|(d>lv?1:0)];if(!e.length)continue;
      const x=i*s,y=j*s;
      for(let u=0;u<e.length;u++){const o=e[u];let px,py;
        if(o==0){px=x+s*(lv-a)/(b-a);py=y}else if(o==1){px=x+s;py=y+s*(lv-b)/(c-b)}else if(o==2){px=x+s*(lv-d)/(c-d);py=y+s}else{px=x;py=y+s*(lv-a)/(d-a)}
        u%2?g.lineTo(px,py):g.moveTo(px,py)}
    }
    g.strokeStyle=`rgba(${k},${(major?am:ai)*cfg.int})`;g.lineWidth=major?1.5:1;g.stroke();
  }
}
function draw2d(){
  const s=Math.max(10,Math.round(Math.max(W,H)/110)),cx=Math.ceil(W/s)+1,cy=Math.ceil(H/s)+1,len=(cx+1)*(cy+1);
  if(!grid||grid.length!=len)grid=new Float32Array(len);
  for(let j=0;j<=cy;j++)for(let i=0;i<=cx;i++)grid[j*(cx+1)+i]=fld(i*s,j*s,T);
  ctx.clearRect(0,0,W,H);ctx.lineJoin='round';
  contours(ctx,grid,cx,cy,s,cfg.theme=='dark'?'255,255,255':'0,0,0',.34,.15);
}
/* arte do botão de login: mesma paisagem do fundo, em cor invertida */
let artUntil=1/0,artGrid;const lgb=$('#lgb'),lgg=lgb.getContext('2d');
function art(){
  const r=lgb.getBoundingClientRect();if(!r.width)return;
  const w=Math.round(r.width*DPR),h=Math.round(r.height*DPR);if(lgb.width!=w||lgb.height!=h){lgb.width=w;lgb.height=h}
  const s=6,cx=Math.ceil(r.width/s)+1,cy=Math.ceil(r.height/s)+1,len=(cx+1)*(cy+1);
  if(!artGrid||artGrid.length!=len)artGrid=new Float32Array(len);
  for(let j=0;j<=cy;j++)for(let i=0;i<=cx;i++)artGrid[j*(cx+1)+i]=fld(r.left+i*s,r.top+j*s,T);
  lgg.setTransform(DPR,0,0,DPR,0,0);lgg.clearRect(0,0,r.width,r.height);lgg.lineJoin='round';
  contours(lgg,artGrid,cx,cy,s,cfg.theme=='dark'?'12,12,12':'211,211,211',.7,.35);
}
function frame(){
  morph*=.985;T+=.0011*(cfg.speed+morph);
  if(sx<-900){sx=mx;sy=my}else{sx+=(mx-sx)*.035;sy+=(my-sy)*.035}
  if(!cfg.bg){}else if(GL){GL.uniform2f(U.uM,sx,sy);GL.uniform1f(U.uT,T);GL.clear(GL.COLOR_BUFFER_BIT);GL.drawArrays(GL.TRIANGLES,0,3)}else draw2d();
  stepPill();if(cur=='dash')spark();if(performance.now()<artUntil)art();
  requestAnimationFrame(frame);
}

/* dados */
const PCData={real:false,base:{cpu:34,ram:58,gpu:22,disk:46,temp:52},m:{cpu:34,ram:58,gpu:22,disk:46,temp:52},
  tick(){if(!this.real)for(const k in this.m)this.m[k]=cl(this.m[k]+R(-5,5)+(this.base[k]-this.m[k])*.25,3,98);return this.m}};
const lab={cpu:'Processador',ram:'Memória',gpu:'Placa de vídeo',disk:'Disco',temp:'Temperatura'};
$('#ms').innerHTML=Object.keys(lab).map(k=>`<div class="m" data-k="${k}"><h3>${lab[k]}</h3><div class="nm">&nbsp;</div><div class="v"><span class="num">0</span></div><div class="t"><i></i></div></div>`).join('');
const mEls=$$('.m'),hc=[],hr=[],sparkEl=$('#spark'),sctx=sparkEl.getContext('2d');let tickAt=performance.now(),lastSc=0;
function paint(){const m=PCData.m;mEls.forEach(e=>{const k=e.dataset.k,v=m[k],num=e.querySelector('.num');
  e.querySelector('i').style.width=(v==null?0:(k=='temp'?cl((v-30)/70*100):v))+'%';
  if(v==null){cancelAnimationFrame(num._r);num._c=0;num.textContent='—'}else tween(num,v,x=>Math.round(x)+(k=='temp'?'°':'%'),700)})}
function showNames(n){mEls.forEach(e=>{const t=n&&n[e.dataset.k],el=e.querySelector('.nm');if(!t)return;el.textContent=t;el.title=t})}
function update(){
  const m=PCData.tick();tickAt=performance.now();hc.push(m.cpu??0);hr.push(m.ram??0);if(hc.length>60){hc.shift();hr.shift()}
  lastSc=cl(100-((m.cpu||0)+(m.ram||0)+(m.gpu||0)+(m.disk||0))/4*.7-((m.temp??45)-40)*.4);tween(score,lastSc,Math.round,900);
  paint();
}
function spark(){const d=devicePixelRatio||1,c=sparkEl,w=c.clientWidth*d,h=c.clientHeight*d;if(c.width!=w||c.height!=h){c.width=w;c.height=h}
  const f=cl((performance.now()-tickAt)/((cfg.poll||1000)+100),0,1);sctx.clearRect(0,0,w,h);sctx.lineWidth=2*d;sctx.lineJoin='round';sctx.strokeStyle=cfg.theme=='dark'?'#f2f2f2':'#0d0d0d';
  [[hc,[]],[hr,[6*d,7*d]]].forEach(([a,dash])=>{sctx.setLineDash(dash);sctx.beginPath();a.forEach((v,i)=>{const px=(i+60-a.length+1-f)/59*w,py=h-6*d-v/100*(h-12*d);i?sctx.lineTo(px,py):sctx.moveTo(px,py)});sctx.stroke()})}

/* navegação e pílula elástica */
const order=['dash','clean','win','per','cfg'],navBtns=$$('#nav button'),nav=$('#nav'),pillEl=$('#pill'),inv=$('#inv');let cur='dash';
const sp={l:0,r:0,vl:0,vr:0,tl:0,tr:0,kl:220,kr:220,on:0,t:0};
function pill(snap){const b=$('#nav .on');sp.tl=b.offsetLeft;sp.tr=b.offsetLeft+b.offsetWidth;const d=sp.tl>sp.l?1:-1;sp.kl=d>0?140:340;sp.kr=d>0?340:140;
  if(snap===true||!sp.on){sp.l=sp.tl;sp.r=sp.tr;sp.vl=sp.vr=0;sp.on=1;drawPill()}}
function drawPill(){pillEl.style.cssText=`transform:translateX(${sp.l}px);width:${Math.max(sp.r-sp.l,10)}px`;
  inv.style.clipPath=`inset(5px ${Math.max(nav.offsetWidth-sp.r,0)}px 5px ${sp.l}px round 99px)`}
function stepPill(){if(!sp.on)return;const n=performance.now(),dt=Math.min((n-(sp.t||n))/1000,.033),h=dt/4;sp.t=n;
  for(let i=0;i<4;i++){sp.vl+=(sp.kl*(sp.tl-sp.l)-2*Math.sqrt(sp.kl)*.6*sp.vl)*h;sp.l+=sp.vl*h;sp.vr+=(sp.kr*(sp.tr-sp.r)-2*Math.sqrt(sp.kr)*.6*sp.vr)*h;sp.r+=sp.vr*h}
  if(Math.abs(sp.vl)+Math.abs(sp.vr)+Math.abs(sp.tl-sp.l)+Math.abs(sp.tr-sp.r)>.02)drawPill()}
const finishDraw=v=>{if(v&&v._fin){clearTimeout(v._t);v._fin()}};
navBtns.forEach(b=>b.onclick=()=>{const v=b.dataset.v;if(v==cur)return;
  root.style.setProperty('--dir',order.indexOf(v)>order.indexOf(cur)?1:-1);
  $$('.view.off').forEach(x=>x.classList.remove('off'));
  const old=$('#v-'+cur);old.classList.remove('on');old.classList.add('off');setTimeout(()=>old.classList.remove('off'),420);
  $('#nav .on').classList.remove('on');b.classList.add('on');cur=v;pill();
  const el=$('#v-'+v);finishDraw(old);el.classList.add('on');drawView(el);main.scrollTop=0;morph=1.8;
  if(v=='clean')enterClean();if(v=='win')enterWin();if(v=='per')enterPer();if(v=='cfg')enterCfg();
  if(v=='dash'){$$('.t i').forEach(i=>i.style.width='0');$$('.num').forEach(n=>n._c=0);score._c=0;score.textContent='0';setTimeout(()=>{paint();tween(score,lastSc,Math.round,1200)},1000)}});

/* limpeza: tudo vem do servidor (descoberta automática de pastas e navegadores no PC de cada usuário) */
let S=null,built=false,seeded=false,rows={},sel=new Set(),lT=0,pS='ocioso',pL='ocioso',lastTips='';
const cList=$('#cl'),cbar=$('#cbar'),ctotEl=$('#ctot'),cmid=$('#cmid'),
RISK={baixo:'Risco baixo',medio:'Risco médio',alto:'Risco alto'},PERF=['Sem ganho de velocidade','Ganho leve','Ganho moderado','Ganho alto'],
fb=v=>v>=2**30?(v/2**30).toFixed(2)+' GB':v>=2**20?Math.round(v/2**20)+' MB':Math.round(v/1024)+' KB',
post=(p,b)=>fetch(p,{method:'POST',headers:{'X-Token':TOKEN,'Content-Type':'application/json'},body:JSON.stringify(b||{})}).then(r=>r.json()).catch(()=>null),
usable=c=>c.pode,tw=(el,v,f)=>{if(el._t!==v){el._t=v;tween(el,v,f,700)}};
function build(){built=true;let g='',h='';
  S.cats.forEach(c=>{if(c.grupo!=g){g=c.grupo;h+=`<div class="grp">${g}</div>`}
    h+=`<label class="row" data-id="${c.id}"><div class="n">${c.nome}<small>${c.info}</small>${c.aviso?`<small class="av">Atenção: ${c.aviso}</small>`:''}<div class="tags"><span class="tag">${PERF[c.perf]}</span><span class="tag">${RISK[c.risco]}</span>${c.adm?'<span class="tag">Administrador</span>':''}${c.lixeira?'<span class="tag">Vai para a Lixeira</span>':''}<span class="tag st"></span></div></div><span class="val">—</span><input type="checkbox" class="sw"></label>`});
  cList.innerHTML=h;
  $$('#cl .row').forEach(el=>{const id=el.dataset.id,r=rows[id]={el,v:el.querySelector('.val'),sw:el.querySelector('.sw'),st:el.querySelector('.st')};
    r.sw.onchange=()=>{r.sw.checked?sel.add(id):sel.delete(id);totalsUI()}})}
function calc(){let b=0,free=0,e=0;const gan=[];
  S.cats.forEach(c=>{if(!sel.has(c.id)||!usable(c))return;const by=c.bytes||0;b+=by;if(!c.lixeira||sel.has('recycle'))free+=by;
    const k=c.perf*(c.manut?1:cl(by/c.ref,.15,1));if(k>0){e+=k;gan.push([k,c.ganho])}});
  const d=S.disco,used=(d.total-d.livre)/d.total*100,after=(d.total-d.livre-free)/d.total*100;
  if(used>85&&after<used){e+=1;gan.push([1,'disco abaixo de 85% de uso deixa o Windows mais ágil'])}
  return{b,free,e,gan,used,after,d}}
function totalsUI(){if(!S||!built)return;const t=calc(),d=t.d;
  S.cats.forEach(c=>rows[c.id].sw.checked=sel.has(c.id));
  tw(ctotEl,t.b,fb);tw($('#t1v'),d.livre,fb);tw($('#t2v'),d.livre+t.free,fb);
  $('#t1n').textContent=`${t.used.toFixed(0)}% do disco ${d.letra} em uso`;$('#t2n').textContent=`${t.after.toFixed(0)}% do disco ${d.letra} em uso`;
  $('#t3v').textContent=t.e<.4?'Nenhum':t.e<2?'Leve':t.e<4.5?'Moderado':'Alto';
  $('#t3n').textContent=t.gan.length?t.gan.sort((a,b)=>b[0]-a[0]).slice(0,2).map(x=>x[1]).join('; '):'Marque itens para ver o efeito';
  const tips=[];
  if(t.used>85)tips.push(`Seu disco está ${t.used.toFixed(0)}% cheio. Acima de 85% o Windows fica mais lento.`);
  const big=S.cats.filter(c=>usable(c)&&c.bytes>0).sort((a,b)=>b.bytes-a.bytes)[0];if(big)tips.push(`Maior item encontrado: ${big.nome} (${fb(big.bytes)}).`);
  const dup=S.cats.filter(c=>(c.id=='dup_fot'||c.id=='dup_vid')&&c.bytes>0).reduce((a,c)=>a+c.bytes,0);if(dup)tips.push(`Cópias duplicadas de fotos e vídeos ocupam ${fb(dup)}.`);
  if(S.cats.some(c=>c.lixeira&&sel.has(c.id))&&!sel.has('recycle'))tips.push('Arquivos pessoais vão para a Lixeira: esvazie-a para realmente liberar o espaço.');
  if(sel.has('cookies'))tips.push('Limpar cookies desconecta você dos sites.');
  if(sel.has('shaders'))tips.push('Jogos podem travar um pouco na primeira abertura após limpar os shaders.');
  if(!S.admin)tips.push('Sem permissão de administrador, itens do Windows ficam de fora.');
  const h=tips.map(x=>`<li>${x}</li>`).join('');if(h!=lastTips){lastTips=h;$('#ctips').innerHTML=h}}
function applyL(s){S=s;if(!built)build();
  const sc=s.scan,lm=s.limpeza,scanning=sc.estado=='esc',cleaning=lm.estado=='exe';
  if(sc.estado=='ok'&&!seeded){seeded=true;s.cats.forEach(c=>{if(c.padrao&&usable(c))sel.add(c.id)})}
  s.cats.forEach(c=>{const r=rows[c.id],res=lm.res[c.id],u=usable(c);
    r.sw.disabled=!u||scanning||cleaning;r.el.classList.toggle('dim',sc.estado=='ok'&&!u);r.el.classList.toggle('act',cleaning&&lm.atual==c.id);
    let b=null,t;
    if(res)t=res.liberado>0?fb(res.liberado):res.movido>0?fb(res.movido):'Concluído';
    else if(c.bloq)t='—';else if(c.st=='esc')t='…';else if(c.bytes==null)t='—';
    else if(c.bytes>0)b=c.bytes;else if(c.manut)t=c.tempo;else if(c.n>0)t=c.n+' itens';else t=c.st=='ok'&&c.obs?'—':'Nada';
    if(b!==null){if(r.v._t!==b){r.v._t=b;tween(r.v,b,fb,600)}}else{cancelAnimationFrame(r.v._r);r.v._t=null;r.v._c=0;r.v.textContent=t}
    let st='';
    if(res){st=[res.liberado>0?fb(res.liberado)+' liberados':'',res.movido>0?fb(res.movido)+' enviados à Lixeira':'',res.ign>0?res.ign+' em uso (ignorados)':'',res.obs].filter(Boolean).join(' · ')||'concluído';
      if(!r.el._d){r.el._d=1;r.el.classList.add('sweep');setTimeout(()=>r.el.classList.remove('sweep'),1000)}}
    else{r.el._d=0;st=cleaning&&lm.atual==c.id?'limpando…':c.bloq?'requer administrador':c.st=='esc'?'analisando…':c.st=='pend'?'':[c.bytes>0&&c.n>0?c.n+' itens':'',c.obs].filter(Boolean).join(' · ')}
    r.st.textContent=st});
  let pct=0,txt='Pronto';
  if(scanning){pct=sc.i/sc.n*100;txt='Escaneando: '+sc.atual}
  else if(cleaning){const c=s.cats.find(x=>x.id==lm.atual);pct=lm.i/lm.n*100;txt=`Limpando (${lm.i+1} de ${lm.n}): ${c?c.nome:''}`}
  else if(sc.estado=='ok')txt=lm.estado=='ok'?'Limpeza concluída':'Escaneamento concluído';
  if(cmid.textContent!=txt)cmid.textContent=txt;cbar.style.width=pct+'%';
  $('#cadm').hidden=s.admin;$('#scan').disabled=scanning||cleaning;$('#clean').disabled=scanning||cleaning;
  $('#scan').textContent=scanning?'Escaneando…':'Escanear';$('#clean').textContent=cleaning?'Limpando…':'Limpar';
  totalsUI();
  if(pS=='esc'&&sc.estado=='ok')toast(fb(calc().b)+' selecionados para limpar');
  if(pL=='exe'&&lm.estado=='ok'){let l=0,m=0;Object.values(lm.res).forEach(x=>{l+=x.liberado||0;m+=x.movido||0});
    toast((l?fb(l)+' liberados':'Limpeza concluída')+(m?' · '+fb(m)+' na Lixeira':''));morph=2}
  pS=sc.estado;pL=lm.estado}
async function pollL(){clearTimeout(lT);
  try{const r=await fetch('/api/limpeza/estado',{cache:'no-store'});if(r.ok)applyL(await r.json())}catch(e){}
  const run=S&&(S.scan.estado=='esc'||S.limpeza.estado=='exe');
  if(run||cur=='clean')lT=setTimeout(pollL,run?600:3000)}
async function scanNow(){const r=await post('/api/limpeza/escanear');if(!r||!r.ok)toast('Já existe uma tarefa em andamento');pollL()}
async function enterClean(){
  if(!PCData.real){cmid.textContent='Disponível apenas no Windows';$('#scan').disabled=$('#clean').disabled=true;return}
  await pollL();if(S&&S.scan.estado=='ocioso'&&cfg.autoscan)scanNow()}
$('#scan').onclick=scanNow;
$('#celev').onclick=async()=>{const r=await post('/api/admin/elevar');toast(r&&r.ok?'Reabrindo como administrador…':'Permissão não concedida')};
const cmdl=$('#cmdl'),mlist=$('#mlist'),ids=()=>S.cats.filter(c=>sel.has(c.id)&&usable(c)).map(c=>c.id);
function warnUI(){const x=ids(),has=i=>x.includes(i),pess=S.cats.some(c=>c.lixeira&&has(c.id)),w=[];
  if(pess)w.push(has('recycle')?'<b>Atenção:</b> a Lixeira será esvaziada junto, então os arquivos pessoais selecionados serão apagados de vez.':'<b>Arquivos pessoais</b> vão para a Lixeira e podem ser recuperados. Esvazie-a para liberar o espaço.');
  if(has('cookies'))w.push('Limpar cookies desconecta você dos sites.');
  if(has('shaders'))w.push('Jogos podem travar um pouco na primeira abertura.');
  if(['dism_cleanup','sfc','dism_repair'].some(has))w.push('Manutenção do Windows pode levar vários minutos. <b>Não desligue o computador.</b>');
  w.push('Feche os navegadores antes de limpar para que cache, cookies e históricos em uso também sejam apagados.');
  $('#mwarn').innerHTML=w.join(' ');$('#cyes').disabled=!x.length}
function modalUI(){let g='',h='';
  S.cats.filter(usable).forEach(c=>{if(c.grupo!=g){g=c.grupo;h+=`<div class="grp">${g}</div>`}
    const v=c.bytes>0?fb(c.bytes):c.manut?c.tempo:c.n+' itens';
    h+=`<label><div class="n">${c.nome}<small>${c.aviso||c.ganho||c.info}</small></div><span class="val">${v}</span><input type="checkbox" class="sw" data-id="${c.id}" ${sel.has(c.id)?'checked':''}></label>`});
  mlist.innerHTML=h;warnUI()}
mlist.onchange=e=>{const i=e.target.dataset.id;e.target.checked?sel.add(i):sel.delete(i);totalsUI();warnUI()};
$('#clean').onclick=async()=>{if(!S||S.limpeza.estado=='exe'||S.scan.estado=='esc')return;
  if(!S.cats.some(usable)){toast('Nada para limpar. Escaneie primeiro.');return}
  modalUI();if(!await askOpt(cmdl,'#cyes','#cno'))return;
  const r=await post('/api/limpeza/limpar',{ids:ids()});if(!r||!r.ok)toast('Não foi possível iniciar a limpeza');pollL()};


/* windows: ajustes de desempenho */
let WS=null,wBuilt=false,wSeed=false,wDes={},wRows={},wT=0,pWl='ocioso',pWa='ocioso',wTips='';
const wBar=$('#wbar'),wList=$('#wl'),wMid=$('#wmid'),wtot=$('#wtot'),
wPend=()=>WS.tweaks.filter(t=>t.pode&&wDes[t.id]!==t.ativo);
function buildW(){wBuilt=true;let g='',h='';
  WS.tweaks.forEach(c=>{if(c.grupo!=g){g=c.grupo;h+=`<div class="grp">${g}</div>`}
    h+=`<label class="row" data-id="${c.id}"><div class="n">${c.nome}<small>${c.info}</small>${c.aviso?`<small class="av">Atenção: ${c.aviso}</small>`:''}<div class="tags"><span class="tag">${PERF[c.perf]}</span><span class="tag">${RISK[c.risco]}</span>${c.adm?'<span class="tag">Administrador</span>':''}${c.reboot?'<span class="tag">Aplica ao reiniciar</span>':''}<span class="tag st"></span></div></div><span class="val">—</span><input type="checkbox" class="sw"></label>`});
  wList.innerHTML=h;
  $$('#wl .row').forEach(el=>{const id=el.dataset.id,r=wRows[id]={el,v:el.querySelector('.val'),sw:el.querySelector('.sw'),st:el.querySelector('.st')};
    r.sw.onchange=()=>{wDes[id]=r.sw.checked;wUI()}})}
function wUI(){if(!WS||!wBuilt)return;const T=WS.tweaks,ok=T.filter(t=>t.pode),pend=wPend(),inf=WS.info||{};
  WS.tweaks.forEach(t=>{const r=wRows[t.id];if(!r)return;r.sw.checked=!!wDes[t.id];r.el.classList.toggle('chg',t.pode&&wDes[t.id]!==t.ativo)});
  const on=ok.filter(t=>t.ativo).length,fin=ok.filter(t=>wDes[t.id]),sc=fin.reduce((a,t)=>a+t.perf,0),mx=ok.filter(t=>t.rec).reduce((a,t)=>a+t.perf,0)||1,pct=Math.min(100,Math.round(sc/mx*100));
  tw(wtot,on,Math.round);$('#w1v').textContent=`${on} de ${ok.length}`;$('#w1n').textContent=pend.length?`${pend.length} alterações pendentes`:'Nenhuma alteração pendente';
  $('#w2v').textContent=inf.ram?inf.ram+' GB':'—';$('#w2n').textContent=[inf.windows,inf.ssd?'SSD':'HDD',inf.notebook?'notebook':'desktop',inf.nucleos?inf.nucleos+' núcleos':''].filter(Boolean).join(' · ')||'\u00a0';
  $('#w3v').textContent=pct+'%';
  const nov=pend.filter(t=>wDes[t.id]).sort((a,b)=>b.perf-a.perf).slice(0,2).map(t=>t.ganho).filter(Boolean);
  $('#w3n').textContent=nov.length?'Ao aplicar: '+nov.join('; '):(pct>=90?'Windows já está bem otimizado':'Marque as recomendadas para ver o ganho');
  const tips=[],su=T.filter(t=>t.id.startsWith('su:')&&!t.ativo).length;
  if(inf.notebook)tips.push('Notebook detectado: as opções de energia máxima ficam desmarcadas por padrão para poupar a bateria.');
  if(inf.ssd===false&&inf.windows)tips.push('Windows em HDD: mantenha o SysMain (Superfetch) ligado, ele ajuda nesse tipo de disco.');
  if(inf.ram&&inf.ram<8)tips.push('Com menos de 8 GB de RAM, bloquear apps em segundo plano e programas de inicialização faz mais diferença.');
  if(su>=5)tips.push(`${su} programas iniciam junto com o Windows. Cada um a menos deixa o boot mais rápido.`);
  if(!WS.admin)tips.push('Sem permissão de administrador, ajustes de sistema, serviços e jogos ficam de fora.');
  if(T.some(t=>t.ativo&&t.reboot))tips.push('Alguns ajustes só têm efeito depois de reiniciar o PC.');
  const h=tips.map(x=>`<li>${x}</li>`).join('');if(h!=wTips){wTips=h;$('#wtips').innerHTML=h}
  $('#wapl').disabled=!pend.length||WS.apl.estado=='exe'||WS.estado=='ler'}
function applyW(s){WS=s;if(!wBuilt)buildW();
  const ler=s.estado=='ler',exe=s.apl.estado=='exe',a=s.apl;
  if(s.estado=='ok'&&!wSeed){wSeed=true;s.tweaks.forEach(t=>wDes[t.id]=t.ativo)}
  if(pWa=='exe'&&a.estado=='ok'){s.tweaks.forEach(t=>wDes[t.id]=t.ativo)}
  s.tweaks.forEach(t=>{const r=wRows[t.id],res=a.res[t.id];if(!r)return;
    r.sw.disabled=!t.pode||ler||exe;r.el.classList.toggle('dim',s.estado=='ok'&&!t.pode);r.el.classList.toggle('act',exe&&a.atual==t.id);
    r.v.textContent=res?(res.ok?'Aplicado':'Falhou'):!t.ok?'—':t.ativo?'Ativo':'Inativo';
    let st='';
    if(res){st=res.obs||'concluído';if(!r.el._d){r.el._d=1;r.el.classList.add('sweep');setTimeout(()=>r.el.classList.remove('sweep'),1000)}}
    else{r.el._d=0;st=exe&&a.atual==t.id?'aplicando…':t.bloq?'requer administrador':!t.ok?t.obs:''}
    r.st.textContent=st});
  let pct=0,txt=s.estado=='ok'?'Pronto':s.estado=='ocioso'?'Clique em Reanalisar':'Preparando…';
  if(ler){pct=s.i/Math.max(s.n,1)*100;txt='Analisando o Windows…'}
  else if(exe){const t=s.tweaks.find(x=>x.id==a.atual);pct=a.i/a.n*100;txt=a.atual=='ponto'?'Criando ponto de restauração…':a.atual=='explorer'?'Reiniciando o Explorer…':`Aplicando (${a.i+1} de ${a.n}): ${t?t.nome:''}`}
  else if(pWa=='exe')txt='Alterações aplicadas';
  if(wMid.textContent!=txt)wMid.textContent=txt;wBar.style.width=pct+'%';
  $('#wadm').hidden=s.admin;$('#wana').disabled=ler||exe;$('#wrec').disabled=ler||exe;
  wUI();
  if(pWa=='exe'&&a.estado=='ok'){const v=Object.values(a.res),okn=v.filter(x=>x.ok).length,bad=v.length-okn;
    toast(`${okn} ${okn==1?'ajuste aplicado':'ajustes aplicados'}${bad?` · ${bad} bloqueados`:''}${a.reboot?' · reinicie o PC para concluir':''}`);morph=2}
  pWl=s.estado;pWa=a.estado}
async function pollW(){clearTimeout(wT);
  try{const r=await fetch('/api/windows/estado',{cache:'no-store'});if(r.ok)applyW(await r.json())}catch(e){}
  const run=WS&&(WS.estado=='ler'||WS.apl.estado=='exe');
  if(run||cur=='win')wT=setTimeout(pollW,run?600:3000)}
async function analyzeNow(){wSeed=false;const r=await post('/api/windows/analisar');if(!r||!r.ok)toast('Já existe uma tarefa em andamento');pollW()}
async function enterWin(){
  if(!PCData.real){wMid.textContent='Disponível apenas no Windows';$('#wana').disabled=$('#wapl').disabled=$('#wrec').disabled=true;return}
  await pollW();if(WS&&WS.estado=='ocioso'&&cfg.autoscan)analyzeNow()}
$('#wana').onclick=analyzeNow;
$('#welev').onclick=async()=>{const r=await post('/api/admin/elevar');toast(r&&r.ok?'Reabrindo como administrador…':'Permissão não concedida')};
$('#wrec').onclick=()=>{if(!WS)return;let n=0;WS.tweaks.forEach(t=>{if(t.pode&&t.rec&&!wDes[t.id]){wDes[t.id]=true;n++}});wUI();toast(n?`${n} recomendadas marcadas. Clique em Aplicar.`:'As recomendadas já estão marcadas')};
const wmdl=$('#wmdl'),wlist=$('#wlist');
function wWarn(){const p=wPend(),w=[];if(WS.admin)w.push('Um <b>ponto de restauração</b> será criado antes (se o Windows permitir).');
  w.push('Tudo pode ser revertido aqui mesmo, o valor original fica guardado.');
  if(p.some(t=>t.exp))w.push('O Explorer reinicia por um instante (a barra de tarefas some e volta).');
  if(p.some(t=>t.reboot))w.push('Alguns itens só fazem efeito depois de <b>reiniciar o PC</b>.');
  if(p.some(t=>t.risco!='baixo'&&wDes[t.id]))w.push('Há itens de risco médio: leia os avisos antes.');
  $('#wwarn').innerHTML=w.join(' ');$('#wyes').disabled=!p.length}
function wModal(){let g='',h='';
  wPend().forEach(t=>{if(t.grupo!=g){g=t.grupo;h+=`<div class="grp">${g}</div>`}
    h+=`<label><div class="n">${wDes[t.id]?'Ativar':'Reverter'}: ${t.nome.replace(/^Não iniciar: /,'')}<small>${t.aviso||t.ganho||t.info}</small></div><span class="val">${wDes[t.id]?'Ativar':'Reverter'}</span><input type="checkbox" class="sw" data-id="${t.id}" checked></label>`});
  wlist.innerHTML=h;wWarn()}
wlist.onchange=e=>{const t=WS.tweaks.find(x=>x.id==e.target.dataset.id);if(!e.target.checked)wDes[t.id]=t.ativo;else wDes[t.id]=!t.ativo;wUI();wWarn()};
$('#wapl').onclick=async()=>{if(!WS||!wPend().length)return;wModal();if(!await askOpt(wmdl,'#wyes','#wno'))return;
  const m={};wPend().forEach(t=>m[t.id]=wDes[t.id]);const r=await post('/api/windows/aplicar',{mudancas:m});if(!r||!r.ok)toast('Não foi possível iniciar');pollW()};


/* configurações do app: aparência, animações, comportamento */
const PAL={
 cinza:{n:'Cinza',c:'#8a8a8a'},
 azul:{n:'Azul',c:'#5b8def',L:['#cdd6e6','#0a1428'],D:['#090e18','#e6edfb']},
 verde:{n:'Verde',c:'#4fae6b',L:['#cfdccf','#0c1f12'],D:['#0a120c','#e5f5e8']},
 roxo:{n:'Roxo',c:'#8e6bd8',L:['#d8d0e6','#1a0f2e'],D:['#100b1a','#efe8fb']},
 ambar:{n:'Âmbar',c:'#d99a2b',L:['#e6dcc6','#2a1a05'],D:['#16100a','#fbefdc']},
 rosa:{n:'Rosa',c:'#d86b92',L:['#e6cfd8','#2e0f1c'],D:['#1a0b11','#fbe6ee']}};
function applyPal(){const p=PAL[cfg.pal]||PAL.cinza,m=p[cfg.theme=='dark'?'D':'L'];
  if(m){root.style.setProperty('--bg',m[0]);root.style.setProperty('--fg',m[1])}else{root.style.removeProperty('--bg');root.style.removeProperty('--fg')}}
function applyBg(){gc.style.display=cfg.bg&&GL?'block':'none';cv.style.display=cfg.bg&&!GL?'block':'none';if(!cfg.bg&&!GL)ctx.clearRect(0,0,W,H)}
function applyCfg(k){
  if(k=='themeMode'){const t=cfg.themeMode=='auto'?(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'):cfg.themeMode;if(t!=cfg.theme)setTheme(t)}
  else if(k=='pal')applyPal();
  else if(k=='bg')applyBg();
  else if(k=='dens'||k=='int'){GL&&uni()}
  else if(k=='calm')document.body.classList.toggle('calm',!!cfg.calm);
  else if(k=='compact')document.body.classList.toggle('compact',!!cfg.compact);
  else if(k=='top'){try{pywebview.api.topo(!!cfg.top)}catch(e){}}}
const cfgSet=(k,v)=>{cfg[k]=v;save();applyCfg(k)},
CFG=[
 ['Aparência',[
  {k:'themeMode',t:'seg',n:'Tema',i:'Automático acompanha o tema do Windows.',o:[['auto','Automático'],['light','Claro'],['dark','Escuro']]},
  {k:'pal',t:'pal',n:'Paleta de cores',i:'Dá um tom a todo o app, no tema claro e no escuro.'},
  {k:'compact',t:'sw',n:'Listas compactas',i:'Reduz o espaçamento das linhas para mostrar mais itens de uma vez.'}]],
 ['Fundo animado',[
  {k:'bg',t:'sw',n:'Relevo animado',i:'Desligue para poupar GPU e bateria.'},
  {k:'speed',t:'rng',n:'Velocidade',i:'Quão rápido o relevo se move.',min:.1,max:1.5,step:.05,f:v=>Math.round(v*100)+'%'},
  {k:'dens',t:'rng',n:'Quantidade de linhas',i:'Mais linhas deixam o relevo mais detalhado.',min:8,max:28,step:1,f:v=>String(v)},
  {k:'int',t:'rng',n:'Intensidade',i:'O quanto as linhas aparecem sobre o fundo.',min:.3,max:1.6,step:.05,f:v=>Math.round(v*100)+'%'}]],
 ['Animações',[
  {k:'anim',t:'sw',n:'Desenho de entrada das telas',i:'Linhas e textos se desenham ao abrir cada aba.'},
  {k:'rip',t:'sw',n:'Ondulação ao clicar',i:'Efeito de onda em botões e linhas.'},
  {k:'vt',t:'sw',n:'Transição circular do tema',i:'Animação ao trocar entre claro e escuro.'},
  {k:'calm',t:'sw',n:'Modo sem animações',i:'Desliga transições e animações. Ideal para PCs mais fracos.'}]],
 ['Comportamento',[
  {k:'startTab',t:'seg',n:'Aba inicial',i:'Aba aberta logo depois do login.',o:[['dash','Painel'],['clean','Limpeza'],['win','Windows'],['per','Periféricos']]},
  {k:'autologin',t:'sw',n:'Entrar automaticamente',i:'Pula a tela de login usando o último usuário.'},
  {k:'confirm',t:'sw',n:'Confirmar antes de Otimizar agora',i:'Mostra o resumo do que será feito. Limpeza e ajustes sempre pedem confirmação.'},
  {k:'autoscan',t:'sw',n:'Analisar ao abrir as abas',i:'Escaneia sozinho ao abrir Limpeza, Windows e Periféricos. Desligado, use os botões.'},
  {k:'toast',t:'sw',n:'Avisos na tela',i:'Mostra o resultado depois de cada ação.'},
  {k:'poll',t:'seg',n:'Atualização do painel',i:'Intervalo de leitura de CPU, memória, GPU e disco.',o:[['1000','1 s'],['2000','2 s'],['5000','5 s']]}]],
 ['Janela',[
  {k:'top',t:'sw',n:'Sempre no topo',i:'Mantém o Tellez acima das outras janelas. Funciona só no app, não no navegador.'}]],
 ['Dados e segurança',[
  {t:'btn',a:'revall',b:'Reverter',n:'Reverter todos os ajustes',i:'Desfaz tudo que o Tellez aplicou nas abas Windows e Periféricos, usando os valores originais guardados.'},
  {t:'btn',a:'folder',b:'Abrir',n:'Pasta de backups',i:'Abre a pasta com os valores originais guardados antes de cada ajuste.'},
  {t:'btn',a:'logout',b:'Sair',n:'Trocar de usuário',i:'Volta para a tela de login.'},
  {t:'btn',a:'elev',b:'Reiniciar como administrador',n:'Permissão de administrador',i:'Libera ajustes de sistema, serviços, energia e DISM/SFC.'}]],
 ['Sobre',[
  {t:'txt',id:'cfgadm',n:'Tellez',i:'Painel de otimização para Windows. Tudo que é alterado pode ser revertido.'}]]],
cfgFind=k=>CFG.flatMap(g=>g[1]).find(r=>r.k==k),
cfgRow=r=>{let c='';
  if(r.t=='sw')c=`<input type="checkbox" class="sw" data-k="${r.k}"${cfg[r.k]?' checked':''}>`;
  else if(r.t=='seg')c=`<div class="seg" data-k="${r.k}">${r.o.map(o=>`<button type="button" data-v="${o[0]}" class="${String(cfg[r.k])==o[0]?'on':''}">${o[1]}</button>`).join('')}</div>`;
  else if(r.t=='pal')c=`<div class="pal" data-k="pal">${Object.keys(PAL).map(id=>`<button type="button" class="dot${cfg.pal==id?' on':''}" data-v="${id}" title="${PAL[id].n}" aria-label="${PAL[id].n}" style="--c:${PAL[id].c}"></button>`).join('')}</div>`;
  else if(r.t=='rng')c=`<input type="range" class="rng" data-k="${r.k}" min="${r.min}" max="${r.max}" step="${r.step}" value="${cfg[r.k]}"><span class="val" style="min-width:52px">${r.f(cfg[r.k])}</span>`;
  else if(r.t=='btn')c=`<button type="button" class="btn" data-a="${r.a}" data-l="${r.b}">${r.b}</button>`;
  else c=`<span class="val" id="${r.id}" style="min-width:0">—</span>`;
  return `<div class="row"><div class="n">${r.n}<small>${r.i}</small></div>${c}</div>`},
cfgl=$('#cfgl'),
cfgSync=()=>$$('#cfgl .seg,#cfgl .pal').forEach(g=>[...g.children].forEach(b=>b.classList.toggle('on',String(cfg[g.dataset.k])==b.dataset.v)));
cfgl.innerHTML=CFG.map(g=>`<div class="grp">${g[0]}</div>`+g[1].map(cfgRow).join('')).join('');
cfgl.onclick=e=>{const b=e.target.closest('button');
  if(b&&b.closest('.seg,.pal')){const g=b.closest('[data-k]'),raw=b.dataset.v;cfgSet(g.dataset.k,/^\d+$/.test(raw)?+raw:raw);cfgSync();return}
  if(b&&b.dataset.a){cfgAct(b);return}
  const row=e.target.closest('.row'),sw=row&&row.querySelector('.sw');if(sw&&e.target!==sw)sw.click()};
cfgl.onchange=e=>{const t=e.target;if(t.classList.contains('sw'))cfgSet(t.dataset.k,t.checked?1:0)};
cfgl.oninput=e=>{const t=e.target;if(t.classList.contains('rng')){const r=cfgFind(t.dataset.k);t.nextElementSibling.textContent=r.f(+t.value);cfgSet(t.dataset.k,+t.value)}};
async function cfgAct(b){const a=b.dataset.a;
  if(a=='revall'){
    if(!b._c){b._c=1;b.textContent='Confirmar';clearTimeout(b._t);b._t=setTimeout(()=>{b._c=0;b.textContent=b.dataset.l},4000);return}
    b._c=0;b.textContent=b.dataset.l;
    if(!PCData.real){toast('Disponível apenas no Windows');return}
    const r=await post('/api/cfg/reverter');
    if(!r||!r.ok){toast(r&&r.motivo=='ocupado'?'Aguarde a tarefa em andamento terminar':'Não foi possível reverter');return}
    if(!r.revertidos&&!r.admin&&!r.falhas){toast('Nenhum ajuste do Tellez para reverter');return}
    wSeed=xSeed=false;post('/api/windows/analisar');
    toast(`${r.revertidos} ${r.revertidos==1?'ajuste revertido':'ajustes revertidos'}${r.admin?` · ${r.admin} exigem administrador`:''}${r.falhas?` · ${r.falhas} falharam`:''}${r.revertidos?' · reinicie o PC para concluir':''}`)}
  else if(a=='folder'){if(!PCData.real){toast('Disponível apenas no Windows');return}const r=await post('/api/cfg/pasta');if(!r||!r.ok)toast('Não foi possível abrir a pasta')}
  else if(a=='logout'){document.body.classList.add('locked');lu.value=cfg.user||'';setTimeout(()=>lu.focus({preventScroll:true}),400)}
  else if(a=='elev'){const r=await post('/api/admin/elevar');toast(r&&r.ok?'Reabrindo como administrador…':'Permissão não concedida')}}
$('#cfgreset').onclick=()=>{try{localStorage.painel_cfg=JSON.stringify({user:cfg.user})}catch(e){}location.reload()};
async function enterCfg(){let adm=null;
  if(PCData.real){try{adm=(await (await fetch('/api/limpeza/estado',{cache:'no-store'})).json()).admin}catch(e){}}
  const el=$('#cfgadm');if(el)el.textContent=adm===null?(PCData.real?'—':'Simulado'):adm?'Administrador':'Usuário padrão';
  const r=$('[data-a=elev]');if(r)r.closest('.row').hidden=adm!==false}
$('#tg').onclick=e=>{const t=cfg.theme=='dark'?'light':'dark';cfg.themeMode=t;save();setTheme(t,e.clientX,e.clientY);cfgSync()};
(function(){const dk=matchMedia('(prefers-color-scheme:dark)');
  if(cfg.themeMode=='auto')cfg.theme=dk.matches?'dark':'light';else cfg.theme=cfg.themeMode;
  root.dataset.theme=cfg.theme;GL&&uni();applyPal();applyBg();
  document.body.classList.toggle('calm',!!cfg.calm);document.body.classList.toggle('compact',!!cfg.compact);
  try{dk.addEventListener('change',e=>{if(cfg.themeMode=='auto')setTheme(e.matches?'dark':'light')})}catch(x){}
  addEventListener('pywebviewready',()=>{if(cfg.top)applyCfg('top')})})();

/* periféricos: mesmo motor dos ajustes do Windows, outra lista (mouse, teclado, monitor, input lag) */
let XS=null,xBuilt=false,xSeed=false,xDes={},xRows={},xT=0,xA='ocioso',xTips='';
const xBar=$('#xbar'),xList=$('#xl'),xMid=$('#xmid'),xtot=$('#xtot'),
xPend=()=>XS.tweaks.filter(t=>t.pode&&xDes[t.id]!==t.ativo);
function buildX(){xBuilt=true;let g='',h='';
  XS.tweaks.forEach(c=>{if(c.grupo!=g){g=c.grupo;h+=`<div class="grp">${g}</div>`}
    h+=`<label class="row" data-id="${c.id}"><div class="n">${c.nome}<small>${c.info}</small>${c.aviso?`<small class="av">Atenção: ${c.aviso}</small>`:''}<div class="tags"><span class="tag">${PERF[c.perf]}</span><span class="tag">${RISK[c.risco]}</span>${c.adm?'<span class="tag">Administrador</span>':''}${c.reboot?'<span class="tag">Aplica ao reentrar</span>':''}<span class="tag st"></span></div></div><span class="val">—</span><input type="checkbox" class="sw"></label>`});
  xList.innerHTML=h;
  $$('#xl .row').forEach(el=>{const id=el.dataset.id,r=xRows[id]={el,v:el.querySelector('.val'),sw:el.querySelector('.sw'),st:el.querySelector('.st')};
    r.sw.onchange=()=>{xDes[id]=r.sw.checked;xUI()}})}
function xUI(){if(!XS||!xBuilt)return;const T=XS.tweaks,ok=T.filter(t=>t.pode),pend=xPend(),inf=XS.info||{},hz=inf.hz||{};
  T.forEach(t=>{const r=xRows[t.id];if(!r)return;r.sw.checked=!!xDes[t.id];r.el.classList.toggle('chg',t.pode&&xDes[t.id]!==t.ativo)});
  const on=ok.filter(t=>t.ativo).length,fin=ok.filter(t=>xDes[t.id]),sc=fin.reduce((a,t)=>a+t.perf,0),mx=ok.filter(t=>t.rec).reduce((a,t)=>a+t.perf,0)||1,pct=Math.min(100,Math.round(sc/mx*100));
  tw(xtot,on,Math.round);$('#x1v').textContent=`${on} de ${ok.length}`;$('#x1n').textContent=pend.length?`${pend.length} alterações pendentes`:'Nenhuma alteração pendente';
  $('#x2v').textContent=hz.atual?hz.atual+' Hz':'—';$('#x2n').textContent=hz.atual?`${hz.w}×${hz.h} · máximo ${hz.max} Hz`:'\u00a0';
  $('#x3v').textContent=pct+'%';
  const nov=pend.filter(t=>xDes[t.id]).sort((a,b)=>b.perf-a.perf).slice(0,2).map(t=>t.ganho).filter(Boolean);
  $('#x3n').textContent=nov.length?'Ao aplicar: '+nov.join('; '):(pct>=90?'Periféricos já estão bem ajustados':'Marque as recomendadas para ver o ganho');
  const tips=[];
  if(hz.atual&&hz.max>hz.atual)tips.push(`Seu monitor está em ${hz.atual} Hz, mas aceita ${hz.max} Hz nesta resolução. Usar a taxa máxima é a melhora mais perceptível de fluidez e de input lag.`);
  if(inf.notebook)tips.push('Notebook detectado: os ajustes de energia máxima ficam desmarcados por padrão para poupar a bateria.');
  if(!XS.admin)tips.push('Sem permissão de administrador, ajustes de energia, USB e sistema ficam de fora.');
  if(T.some(t=>t.ativo&&t.reboot))tips.push('Alguns ajustes só têm efeito depois de sair e entrar no Windows ou reiniciar o PC.');
  tips.push('Para o menor input lag: taxa máxima do monitor, aceleração do mouse desligada e, nos jogos, tela cheia exclusiva com V-Sync desligado.');
  const h=tips.map(x=>`<li>${x}</li>`).join('');if(h!=xTips){xTips=h;$('#xtips').innerHTML=h}
  $('#xapl').disabled=!pend.length||XS.apl.estado=='exe'||XS.estado=='ler'}
function applyX(s){XS=s;if(!xBuilt)buildX();
  const ler=s.estado=='ler',exe=s.apl.estado=='exe',a=s.apl;
  if(s.estado=='ok'&&!xSeed){xSeed=true;s.tweaks.forEach(t=>xDes[t.id]=t.ativo)}
  if(xA=='exe'&&a.estado=='ok'){s.tweaks.forEach(t=>xDes[t.id]=t.ativo)}
  s.tweaks.forEach(t=>{const r=xRows[t.id],res=a.res[t.id];if(!r)return;
    r.sw.disabled=!t.pode||ler||exe;r.el.classList.toggle('dim',s.estado=='ok'&&!t.pode);r.el.classList.toggle('act',exe&&a.atual==t.id);
    r.v.textContent=res?(res.ok?'Aplicado':'Falhou'):!t.ok?'—':t.ativo?'Ativo':'Inativo';
    let st='';
    if(res){st=res.obs||'concluído';if(!r.el._d){r.el._d=1;r.el.classList.add('sweep');setTimeout(()=>r.el.classList.remove('sweep'),1000)}}
    else{r.el._d=0;st=exe&&a.atual==t.id?'aplicando…':t.bloq?'requer administrador':!t.ok?t.obs:''}
    r.st.textContent=st});
  let pct=0,txt=s.estado=='ok'?'Pronto':s.estado=='ocioso'?'Clique em Reanalisar':'Preparando…';
  if(ler){pct=s.i/Math.max(s.n,1)*100;txt='Analisando o Windows…'}
  else if(exe){const t=s.tweaks.find(x=>x.id==a.atual);pct=a.i/a.n*100;txt=a.atual=='ponto'?'Criando ponto de restauração…':a.atual=='explorer'?'Reiniciando o Explorer…':`Aplicando (${a.i+1} de ${a.n})${t?': '+t.nome:''}`}
  else if(xA=='exe')txt='Alterações aplicadas';
  if(xMid.textContent!=txt)xMid.textContent=txt;xBar.style.width=pct+'%';
  $('#xadm').hidden=s.admin;$('#xana').disabled=ler||exe;$('#xrec').disabled=ler||exe;
  xUI();
  if(xA=='exe'&&a.estado=='ok'){const v=Object.values(a.res),okn=v.filter(x=>x.ok).length,bad=v.length-okn;
    toast(`${okn} ${okn==1?'ajuste aplicado':'ajustes aplicados'}${bad?` · ${bad} bloqueados`:''}${a.reboot?' · saia e entre no Windows (ou reinicie) para concluir':''}`);morph=2}
  xA=a.estado}
async function pollX(){clearTimeout(xT);
  try{const r=await fetch('/api/perifericos/estado',{cache:'no-store'});if(r.ok)applyX(await r.json())}catch(e){}
  const run=XS&&(XS.estado=='ler'||XS.apl.estado=='exe');
  if(run||cur=='per')xT=setTimeout(pollX,run?600:3000)}
async function analyzeX(){xSeed=false;const r=await post('/api/windows/analisar');if(!r||!r.ok)toast('Já existe uma tarefa em andamento');pollX()}
async function enterPer(){
  if(!PCData.real){xMid.textContent='Disponível apenas no Windows';$('#xana').disabled=$('#xapl').disabled=$('#xrec').disabled=true;return}
  await pollX();if(XS&&XS.estado=='ocioso'&&cfg.autoscan)analyzeX()}
$('#xana').onclick=analyzeX;
$('#xelev').onclick=async()=>{const r=await post('/api/admin/elevar');toast(r&&r.ok?'Reabrindo como administrador…':'Permissão não concedida')};
$('#xrec').onclick=()=>{if(!XS)return;let n=0;XS.tweaks.forEach(t=>{if(t.pode&&t.rec&&!xDes[t.id]){xDes[t.id]=true;n++}});xUI();toast(n?`${n} recomendadas marcadas. Clique em Aplicar.`:'As recomendadas já estão marcadas')};
const xmdl=$('#xmdl'),xlist=$('#xlist');
function xWarn(){const p=xPend(),w=[];if(XS.admin)w.push('Um <b>ponto de restauração</b> será criado antes (se o Windows permitir).');
  w.push('Tudo pode ser revertido aqui mesmo: o valor original fica guardado.');
  if(p.some(t=>t.id=='hz'&&xDes[t.id]))w.push('A tela pode piscar por um instante ao trocar a taxa de atualização.');
  if(p.some(t=>t.exp))w.push('O Explorer reinicia por um instante (a barra de tarefas some e volta).');
  if(p.some(t=>t.reboot))w.push('Alguns itens só fazem efeito depois de <b>sair e entrar no Windows</b> ou reiniciar.');
  if(p.some(t=>t.risco!='baixo'&&xDes[t.id]))w.push('Há itens de risco médio ou alto: leia os avisos antes.');
  $('#xwarn').innerHTML=w.join(' ');$('#xyes').disabled=!p.length}
function xModal(){let g='',h='';
  xPend().forEach(t=>{if(t.grupo!=g){g=t.grupo;h+=`<div class="grp">${g}</div>`}
    h+=`<label><div class="n">${xDes[t.id]?'Ativar':'Reverter'}: ${t.nome}<small>${t.aviso||t.ganho||t.info}</small></div><span class="val">${xDes[t.id]?'Ativar':'Reverter'}</span><input type="checkbox" class="sw" data-id="${t.id}" checked></label>`});
  xlist.innerHTML=h;xWarn()}
xlist.onchange=e=>{const t=XS.tweaks.find(x=>x.id==e.target.dataset.id);xDes[t.id]=e.target.checked?!t.ativo:t.ativo;xUI();xWarn()};
$('#xapl').onclick=async()=>{if(!XS||!xPend().length)return;xModal();if(!await askOpt(xmdl,'#xyes','#xno'))return;
  const m={};xPend().forEach(t=>m[t.id]=xDes[t.id]);const r=await post('/api/windows/aplicar',{mudancas:m});if(!r||!r.ok)toast('Não foi possível iniciar');pollX()};

/* otimizar */
let busy=0;
const mdl=$('#mdl'),TOKEN='__TOKEN__',api=e=>fetch('/api/otimizar?etapa='+e,{method:'POST',headers:{'X-Token':TOKEN}}).then(r=>r.json()).catch(()=>null),
pop=e=>{e.classList.remove('pop');void e.offsetWidth;e.classList.add('pop')},
askOpt=(m=mdl,y='#myes',n='#mno')=>new Promise(res=>{let fim=0;const done=v=>{if(fim)return;fim=1;removeEventListener('keydown',key);m.onclick=$(y).onclick=$(n).onclick=null;
    m.classList.replace('show','out');setTimeout(()=>m.classList.remove('on','out'),400);res(v)},
  key=e=>{if(e.key=='Escape')done(false);else if(e.key=='Enter'){e.preventDefault();if(!$(y).disabled)done(true)}};
  m.classList.add('on');void m.offsetWidth;m.classList.add('show');addEventListener('keydown',key);
  $(y).onclick=()=>done(true);$(n).onclick=()=>done(false);m.onclick=e=>e.target==m&&done(false)});
/* progresso fluido: o alvo avança devagar enquanto a etapa roda e o valor mostrado o persegue com suavização */
function progress(fill,pct){let v=0,t=0,cap=0,fast=0,on=1,last=performance.now(),shown=-1,fin;
  (function f(n){if(!on)return;const dt=Math.min((n-last)/1000,.05);last=n;
    t+=(cap-t)*(1-Math.exp(-dt*(fast?5:.9)));v+=(t-v)*(1-Math.exp(-dt*5));
    fill.style.transform=`scaleX(${v})`;const p=Math.min(100,Math.round(v*100));if(p!=shown){shown=p;pct.textContent=p+'%'}
    if(fin&&v>.995){v=1;fill.style.transform='scaleX(1)';pct.textContent='100%';fin();fin=0}
    requestAnimationFrame(f)})(last);
  return{cap:(c,f)=>{cap=c;fast=!!f},done:()=>new Promise(r=>fin=r),stop:()=>on=0}}
$('#go').onclick=async()=>{if(busy)return;busy=1;if(cfg.confirm&&!await askOpt()){busy=0;return}await wait(220);$('#go').classList.add('busy');
  const mid=$('#mid'),fill=$('#fill'),gt=$('#gt'),B=PCData.base,old={...B},antes=PCData.m.ram,real=PCData.real,res=[],
  dl=(k,d)=>{pop($(`.m[data-k=${k}] .v`));const s=document.createElement('span');s.className='dl';s.textContent=d+(k=='temp'?'°':'%');$(`.m[data-k=${k}] .v`).append(s);setTimeout(()=>s.remove(),2100)},
  fases=[['Medindo o estado atual',()=>0],['Liberando memória',()=>real&&api('memoria')],['Limpando temporários',()=>real&&api('temp')],['Atualizando o painel',()=>wait(real?1500:0)]];
  await setText(gt,'Otimizando<span id="pct">0%</span>');
  const pg=progress(fill,$('#pct'));
  for(let i=0;i<fases.length;i++){setText(mid,fases[i][0]);pg.cap((i+1)/fases.length*.96);
    const r=document.createElement('div');r.className='rip';$('#gow').append(r);setTimeout(()=>r.remove(),2300);morph=1.4;
    res[i]=(await Promise.all([fases[i][1](),wait(1000)]))[0]}
  let msg;
  if(real){const d=Math.round(PCData.m.ram-antes);if(d<0)dl('ram',d);
    const a=res[1],t=res[2];msg=a?(a.liberado_mb>=1?mb(a.liberado_mb)+' de RAM liberados':'A memória já estava enxuta')+(t?' · '+mb(t.mb)+' de temporários apagados':''):'Não foi possível otimizar'}
  else{B.cpu=cl(B.cpu-9,8);B.ram=cl(B.ram-14,20);B.gpu=cl(B.gpu-4,6);B.disk=cl(B.disk-5,15);B.temp=cl(B.temp-6,38);
    update();for(const k in old){const d=Math.round(B[k]-old[k]);if(d)dl(k,d)}msg='Otimizado · '+R(1.2,3.4).toFixed(1)+' GB de RAM liberados'}
  pg.cap(1,1);await pg.done();$('#go').classList.remove('busy');pop($('#go'));pop(score);setText(mid,'Sistema otimizado');setText(gt,'<svg width="18" height="18" viewBox="0 0 24 24"><path class="ck" d="M5 12l5 5L19 7"/></svg>Concluído');
  await wait(1500);fill.style.transition='opacity .5s';fill.style.opacity=0;await wait(520);pg.stop();fill.style.transform='scaleX(0)';fill.style.opacity='';fill.style.transition='';
  setText(gt,'Otimizar agora');setText(mid,'Tudo pronto para otimizar');busy=0;toast(msg)};

/* desenho de entrada da tela */
const EZ='cubic-bezier(.35,.6,.2,1)',NS='http://www.w3.org/2000/svg',reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;
function drawView(v){
  if(reduce||!cfg.anim)return;
  if(v._fin){clearTimeout(v._t);v._fin()}
  const vr=v.getBoundingClientRect(),Hh=Math.max(vr.height,320),Wd=Math.max(vr.width,1),S=getComputedStyle(root),fg=S.getPropertyValue('--fg').trim(),bd=S.getPropertyValue('--bd').trim(),anims=[],strokes=[];let end=0;
  const an=(el,kf,o)=>{end=Math.max(end,(o.delay||0)+o.duration);anims.push(el.animate(kf,{fill:'backwards',easing:EZ,...o}))},
  rel=q=>({x:q.left-vr.left,y:q.top-vr.top,w:q.width,h:q.height}),dly=(x,y)=>120+cl(y/Hh,0,1)*620+cl(x/Wd,0,1)*120,
  svg=document.createElementNS(NS,'svg'),clipX=(a,b)=>[{clipPath:`inset(-12px ${a} -12px 0)`},{clipPath:`inset(-12px ${b} -12px 0)`}];
  svg.setAttribute('class','ink');
  const mk=(t,a)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);svg.append(e);return e};
  v.querySelectorAll('.lead,.ms,.row').forEach(el=>{const q=rel(el.getBoundingClientRect());if(!q.w||!q.h)return;
    const y=q.y+q.h-.5,x2=q.x+q.w,d=dly(q.x,q.y+q.h),dur=cl(380+q.w*1.1,380,1300),l=mk('line',{x1:q.x,y1:y,x2,y2:y,pathLength:1});
    an(l,[{strokeDashoffset:1},{strokeDashoffset:0}],{duration:dur,delay:d});
    an(l,[{stroke:fg},{stroke:bd}],{duration:400,delay:d+dur,fill:'both'});
    const c=mk('circle',{r:2.2}),A=`translate(${q.x}px,${y}px)`,B=`translate(${x2}px,${y}px)`;
    an(c,[{transform:A,opacity:0},{transform:A,opacity:1,offset:.01},{transform:B,opacity:1,offset:.93},{transform:B,opacity:0}],{duration:dur,delay:d,fill:'both'})});
  v.querySelectorAll('.btn,.go,.sw').forEach(el=>{const q=rel(el.getBoundingClientRect());if(!q.w)return;
    const d=dly(q.x,q.y),dur=cl(380+(q.w+q.h)*2,380,1100),p=mk('rect',{x:q.x+.6,y:q.y+.6,width:q.w-1.2,height:q.h-1.2,rx:Math.max(q.h/2-.6,0),pathLength:1});
    an(p,[{strokeDashoffset:1},{strokeDashoffset:0}],{duration:dur,delay:d});
    an(el,[{opacity:0,transform:'scale(.9)'},{opacity:1,transform:'scale(1)'}],{duration:420,delay:d+dur*.7})});
  v.querySelectorAll('.lb,.big,.mid,.m h3,.m .nm,.m .v,.row .n,.val,.lg,.grp').forEach(el=>{
    const er=el.getBoundingClientRect(),rg=document.createRange();rg.selectNodeContents(el);const tr=rg.getBoundingClientRect();if(!er.width||!tr.width)return;
    const q=rel(er),off=tr.left-er.left,tw=tr.width,big=el.classList.contains('big'),d=dly(q.x+off,q.y)+(big?0:160),dur=big?1000:cl(260+tw*2.2,260,1000);
    an(el,[{clipPath:`inset(-30% ${q.w-off}px -30% 0)`},{clipPath:`inset(-30% ${Math.max(q.w-off-tw-4,0)}px -30% 0)`}],{duration:dur,delay:d});
    if(big){const col=getComputedStyle(el).color;el.style.webkitTextStroke='1.2px '+col;strokes.push(el);
      an(el,[{color:'transparent'},{color:'transparent',offset:.7},{color:col}],{duration:dur+400,delay:d})}});
  v.querySelectorAll('.t,.bar').forEach(el=>{const q=rel(el.getBoundingClientRect());if(!q.w)return;
    an(el,clipX('100%','0'),{duration:cl(300+q.w*1.6,300,1100),delay:dly(q.x,q.y)+200})});
  const ch=v.querySelector('#spark');if(ch){const q=rel(ch.getBoundingClientRect());an(ch,clipX('100%','0'),{duration:1200,delay:dly(q.x,q.y)})}
  v.append(svg);v.classList.add('drawing');
  v._fin=()=>{svg.remove();v.classList.remove('drawing');strokes.forEach(e=>e.style.webkitTextStroke='');anims.forEach(a=>a.cancel());v._fin=null};
  v._t=setTimeout(v._fin,end+150);
}

/* início */
const callApi=n=>{try{pywebview.api[n]()}catch(e){}},showWC=()=>document.body.classList.add('app');
$('#wmin').onclick=()=>callApi('minimizar');$('#wcls').onclick=()=>callApi('fechar');
if(window.pywebview)showWC();addEventListener('pywebviewready',showWC);
try{const w=Math.round(screen.width*.5385),h=Math.round(screen.height*.6657);
  if(Math.abs(outerWidth-w)>6||Math.abs(outerHeight-h)>6){resizeTo(w,h);moveTo(Math.round((screen.width-w)/2),Math.round((screen.height-h)/2))}}catch(e){}
(async function poll(){
  try{
    const r=await fetch('/api/dados',{cache:'no-store'});if(!r.ok)throw 0;
    const d=await r.json();PCData.real=true;
    for(const k in lab)PCData.m[k]=typeof d[k]=='number'?d[k]:null;
    if(!poll.named&&d.pronto){poll.named=1;showNames(d.nomes)}else if(d.nomes&&d.nomes.temp)showNames({temp:d.nomes.temp});
    update();if(!poll.cl){poll.cl=1;pollL()}
  }catch(e){
    if(!PCData.real){showNames({cpu:'Valores simulados',ram:'Valores simulados',gpu:'Valores simulados',disk:'Valores simulados',temp:'Valores simulados'});update();setInterval(update,1100);return}
  }
  setTimeout(poll,cfg.poll||1000);
})();
const lu=$('#lu');lu.value=cfg.user||'';if(cfg.autologin&&cfg.user)setTimeout(()=>$('#lf').requestSubmit(),80);
$('#lf').onsubmit=e=>{e.preventDefault();const u=lu.value.trim();
  if(!u){$('.fld').animate([{transform:'translateX(0)'},{transform:'translateX(-8px)'},{transform:'translateX(8px)'},{transform:'translateX(0)'}],{duration:350});lu.focus();return}
  cfg.user=u;save();lu.blur();document.body.classList.remove('locked');artUntil=performance.now()+900;pill(true);drawView($('#v-dash'));if(cfg.startTab&&cfg.startTab!='dash'){const b=$('#nav button[data-v="'+cfg.startTab+'"]');b&&setTimeout(()=>b.click(),60)}};
setTimeout(()=>lu.focus({preventScroll:true}),900);pill(true);document.fonts&&document.fonts.ready.then(()=>pill(true));
frame();
</script>
</body>
</html>
'''

FRACAO_LARGURA, FRACAO_ALTURA = 0.5385, 0.6657
_janela = None
_ultimo = time.time()
REAL = False
NO_WINDOW = 0x08000000
DADOS = {"cpu": None, "ram": None, "gpu": None, "disk": None, "temp": None, "pronto": False,
         "nomes": {"temp": "Sem sensor de temperatura (abra o LibreHardwareMonitor)"}}


# ---------- dados reais do Windows (mesmas fontes do Gerenciador de Tarefas) ----------
class _Val(ctypes.Union):
    _fields_ = [("l", ctypes.c_long), ("d", ctypes.c_double), ("i", ctypes.c_longlong)]


class _Fmt(ctypes.Structure):
    _fields_ = [("status", wt.DWORD), ("v", _Val)]


class _Item(ctypes.Structure):
    _fields_ = [("name", wt.LPWSTR), ("val", _Fmt)]


class _MemStatus(ctypes.Structure):
    _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [(n, ctypes.c_ulonglong) for n in ("tot", "av", "pt", "pa", "vt", "va", "ve")]


def memoria():
    m = _MemStatus()
    m.l = ctypes.sizeof(m)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.tot, m.av


class Pdh:
    """Contadores de desempenho do Windows (PDH)."""
    DBL, MAIS = 0x200, 0x800007D2

    def __init__(s):
        s.pdh, s.q, s.c = ctypes.windll.pdh, ctypes.c_void_p(), {}
        s.pdh.PdhOpenQueryW(None, 0, ctypes.byref(s.q))

    def add(s, k, caminho):
        h = ctypes.c_void_p()
        if s.pdh.PdhAddEnglishCounterW(s.q, caminho, ctypes.c_size_t(0), ctypes.byref(h)) == 0:
            s.c[k] = h

    def coletar(s):
        s.pdh.PdhCollectQueryData(s.q)

    def fechar(s):
        s.pdh.PdhCloseQuery(s.q)

    def valor(s, k):
        if k not in s.c:
            return None
        v = _Fmt()
        if s.pdh.PdhGetFormattedCounterValue(s.c[k], s.DBL, None, ctypes.byref(v)) != 0 or v.status not in (0, 1):
            return None
        return v.v.d

    def lista(s, k):
        if k not in s.c:
            return {}
        tam, n = wt.DWORD(0), wt.DWORD(0)
        if s.pdh.PdhGetFormattedCounterArrayW(s.c[k], s.DBL, ctypes.byref(tam), ctypes.byref(n), None) & 0xFFFFFFFF != s.MAIS:
            return {}
        buf = ctypes.create_string_buffer(tam.value)
        if s.pdh.PdhGetFormattedCounterArrayW(s.c[k], s.DBL, ctypes.byref(tam), ctypes.byref(n), buf) != 0:
            return {}
        it = ctypes.cast(buf, ctypes.POINTER(_Item))
        return {it[i].name: it[i].val.v.d for i in range(n.value)}


def novo_pdh():
    p = Pdh()
    p.add("cpu", r"\Processor Information(_Total)\% Processor Utility")
    if "cpu" not in p.c:
        p.add("cpu", r"\Processor(_Total)\% Processor Time")
    p.add("idle", r"\PhysicalDisk(_Total)\% Idle Time")
    p.add("gpu", r"\GPU Engine(*)\Utilization Percentage")
    p.coletar()
    return p


def amostrar():
    global REAL
    lim = lambda x: round(min(100.0, max(0.0, x)), 1)
    try:
        p = novo_pdh()
        REAL = True
    except Exception as e:
        print(f"Dados reais indisponíveis: {e}")
        return
    n = 0
    while True:
        time.sleep(1)
        n += 1
        try:
            if n % 30 == 0:  # recria os contadores para enxergar processos novos na GPU
                p.fechar()
                p = novo_pdh()
                continue
            p.coletar()
            c, i = p.valor("cpu"), p.valor("idle")
            t, a = memoria()
            DADOS["cpu"] = None if c is None else lim(c)
            DADOS["ram"] = lim((t - a) / t * 100)
            DADOS["disk"] = None if i is None else lim(100 - i)
            if "gpu" in p.c:
                tipos = {}
                for nome, v in p.lista("gpu").items():
                    k = nome.rsplit("engtype_", 1)[-1]
                    tipos[k] = tipos.get(k, 0) + v
                DADOS["gpu"] = lim(max(tipos.values(), default=0))
        except Exception:
            pass


def ps(cmd, limite=20):
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                            "[Console]::OutputEncoding=[Text.Encoding]::UTF8;" + cmd],
                           capture_output=True, text=True, encoding="utf-8", timeout=limite, creationflags=NO_WINDOW)
        return r.stdout.strip()
    except Exception:
        return ""


def carregar_nomes():
    s = ps("$o=@{c=(Get-CimInstance Win32_Processor|select -First 1 -Expand Name);"
           "g=@(Get-CimInstance Win32_VideoController|?{$_.Name -notmatch 'Basic|Remote|Virtual'}|%{$_.Name});"
           "d=@(Get-CimInstance Win32_DiskDrive|%{$_.Model});"
           "r=(Get-CimInstance Win32_PhysicalMemory|select -First 1 -Expand Speed)};$o|ConvertTo-Json -Compress")
    try:
        j = json.loads(s)
    except Exception:
        j = {}
    lim = lambda v: " ".join(str(v).split())
    juntar = lambda v, sep: sep.join(lim(x) for x in ([v] if isinstance(v, str) else v or []))
    try:
        ram = f"{round(memoria()[0] / 2**30)} GB" + (f" · {j['r']} MHz" if j.get("r") else "")
    except Exception:
        ram = "Memória"
    DADOS["nomes"].update(cpu=lim(j.get("c") or "Processador"), ram=ram,
                          gpu=juntar(j.get("g"), " + ") or "Placa de vídeo", disk=juntar(j.get("d"), " · ") or "Disco")
    DADOS["pronto"] = True


TEMP_PS = (
    "$v=$null;$n='';"
    "foreach($ns in 'root/LibreHardwareMonitor','root/OpenHardwareMonitor'){try{"
    "$s=Get-CimInstance -Namespace $ns -ClassName Sensor -EA Stop|?{$_.SensorType -eq 'Temperature' -and $_.Value -gt 0};"
    "$k=$s|?{$_.Name -match 'Package|Tctl|Tdie|CPU'}|select -First 1;if(!$k){$k=$s|select -First 1};"
    "if($k){$v=$k.Value;$n=$k.Name;break}}catch{}};"
    "if($v -eq $null){try{$z=Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -EA Stop|"
    "%{$_.CurrentTemperature/10-273.15}|?{$_ -gt 0 -and $_ -lt 120}|sort -Descending|select -First 1;"
    "if($z){$v=$z;$n='Zona térmica ACPI'}}catch{}};"
    "if($v -ne $null){[string]::Format([Globalization.CultureInfo]::InvariantCulture,'{0:F1}|{1}',$v,$n)}"
)


def amostrar_temp():
    while True:
        try:
            v, _, nome = ps(TEMP_PS, 25).partition("|")
            DADOS["temp"] = round(float(v), 1) if v else None
            DADOS["nomes"]["temp"] = nome or "Sem sensor de temperatura (abra o LibreHardwareMonitor)"
        except Exception:
            DADOS["temp"] = None
        time.sleep(10)


TOKEN = secrets.token_hex(16)


def liberar_memoria():
    """Pede a cada processo que devolva as páginas ociosas (EmptyWorkingSet). Não fecha nada."""
    k, p = ctypes.windll.kernel32, ctypes.windll.psapi
    k.OpenProcess.restype, k.OpenProcess.argtypes = ctypes.c_void_p, [wt.DWORD, wt.BOOL, wt.DWORD]
    k.CloseHandle.argtypes = [ctypes.c_void_p]
    p.EmptyWorkingSet.argtypes = [ctypes.c_void_p]
    pids, n = (wt.DWORD * 4096)(), wt.DWORD()
    p.EnumProcesses(pids, ctypes.sizeof(pids), ctypes.byref(n))
    antes, ok = memoria()[1], 0
    for pid in pids[: n.value // 4]:
        if pid < 5:
            continue
        h = k.OpenProcess(0x0100 | 0x0400, False, pid)  # SET_QUOTA | QUERY_INFORMATION
        if h:
            ok += bool(p.EmptyWorkingSet(h))
            k.CloseHandle(h)
    time.sleep(0.7)
    t, a = memoria()
    DADOS["ram"] = round((t - a) / t * 100, 1)
    return {"liberado_mb": max(0, (a - antes) / 2**20), "processos": ok}


def limpar_temp():
    """Apaga arquivos temporários com mais de 1 dia (poupa os dados do próprio painel)."""
    limite, livre, n = time.time() - 86400, 0, 0
    pastas = {os.path.normcase(x): x for x in (tempfile.gettempdir(), os.environ.get("TEMP"), os.environ.get("TMP"), r"C:\Windows\Temp") if x}
    for raiz in pastas.values():
        for dp, _, fs in os.walk(raiz, topdown=False):
            if "painel_otimizacao" in dp.lower():
                continue
            for f in fs:
                c = os.path.join(dp, f)
                try:
                    st = os.lstat(c)
                    if st.st_mtime < limite:
                        os.remove(c)
                        livre, n = livre + st.st_size, n + 1
                except OSError:
                    pass
            try:
                if os.path.normcase(dp) not in pastas and os.lstat(dp).st_mtime < limite:
                    os.rmdir(dp)
            except OSError:
                pass
    return {"mb": livre / 2**20, "arquivos": n}


# ---------- limpeza (tudo descoberto em tempo de execução: nada de caminho fixo por usuário) ----------
def eh_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


ADMIN = eh_admin()
CACHE, CLAIM, CATS, LIMPA = {}, set(), [], {}
L = {"lock": threading.Lock(), "scan": {"estado": "ocioso", "i": 0, "n": 0, "atual": ""}, "dados": {}, "cs": {},
     "limpa": {"estado": "ocioso", "i": 0, "n": 0, "atual": "", "res": {}}}
env = lambda k, d="": os.environ.get(k) or d
SKIPD = {"node_modules", ".git", "$recycle.bin", "system volume information", "__pycache__"}
SKIPN = {"packages", "temp", "programs", "crashdumps", "d3dscache", "pip", "npm", "python", "nuget", "jetbrains", "fontcache", "comms", "publishers"}
KF = [("{374DE290-123F-4565-9164-39C4925E467B}", "Downloads"), ("{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}", "Desktop"),
      ("{FDD39AD0-238F-46AF-ADB4-6C85480369C7}", "Documents"), ("{33E28130-4E1E-4676-835A-98395C3BC3BB}", "Pictures"),
      ("{18989B1D-99B5-455B-841C-AB7C74E4DDFC}", "Videos"), ("{4BD8D571-6D19-48D3-BE97-422220080E43}", "Music")]


class _GUID(ctypes.Structure):
    _fields_ = [("a", wt.DWORD), ("b", wt.WORD), ("c", wt.WORD), ("d", ctypes.c_ubyte * 8)]

    def __init__(s, u):
        super().__init__()
        x = uuid.UUID(u)
        s.a, s.b, s.c = x.fields[0], x.fields[1], x.fields[2]
        s.d = (ctypes.c_ubyte * 8)(*x.bytes[8:])


class _RB(ctypes.Structure):
    _fields_ = [("cb", wt.DWORD), ("size", ctypes.c_longlong), ("n", ctypes.c_longlong)]


_PK = {"_pack_": 1} if ctypes.sizeof(ctypes.c_void_p) == 4 else {}
_SHOP = type("SHOP", (ctypes.Structure,), {**_PK, "_fields_": [
    ("hwnd", ctypes.c_void_p), ("op", wt.UINT), ("src", ctypes.c_void_p), ("dst", ctypes.c_void_p),
    ("flags", ctypes.c_ushort), ("abort", wt.BOOL), ("maps", ctypes.c_void_p), ("title", ctypes.c_void_p)]})


def caminhos():
    lad = env("LOCALAPPDATA")
    return dict(lad=lad, rad=env("APPDATA"), pd=env("ProgramData"), win=env("SystemRoot", env("windir", r"C:\Windows")),
                sd=env("SystemDrive", "C:") + "\\", low=os.path.join(os.path.dirname(lad), "LocalLow") if lad else "")


def pasta_usuario(guid, nome):
    try:
        p = ctypes.c_void_p()
        if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(_GUID(guid)), 0, None, ctypes.byref(p)) == 0:
            r = ctypes.wstring_at(p.value)
            ctypes.windll.ole32.CoTaskMemFree(ctypes.c_void_p(p.value))
            return r
    except Exception:
        pass
    return str(Path.home() / nome)


def cmd(args, limite=60):
    try:
        r = subprocess.run(args, capture_output=True, timeout=limite, creationflags=NO_WINDOW)
        b = r.stdout or b""
        t = b.decode("utf-16-le", "replace") if b[:200].count(b"\x00") > 20 else b.decode("oem", "replace")
        return r.returncode, t
    except Exception as e:
        return -1, str(e)


def livre():
    try:
        return shutil.disk_usage(caminhos()["sd"]).free
    except OSError:
        return 0


def reparse(p):
    try:
        return bool(os.lstat(p).st_file_attributes & 0x400)
    except (OSError, AttributeError):
        return False


def percorrer(raiz, excl=()):
    if not raiz or not os.path.isdir(raiz):
        return
    for dp, dn, fs in os.walk(raiz):
        dn[:] = [d for d in dn if d.lower() not in SKIPD and not reparse(os.path.join(dp, d))]
        if excl and any(x in dp.lower() for x in excl):
            continue
        for f in fs:
            c = os.path.join(dp, f)
            try:
                st = os.lstat(c)
            except OSError:
                continue
            if stat.S_ISREG(st.st_mode):
                yield c, st


def varrer(raizes, dias=0, exts=None, nome=None, excl=("painel_otimizacao",)):
    lim, out, vistos = time.time() - dias * 86400, [], set()
    for r in raizes:
        for c, st in percorrer(r, excl):
            k = os.path.normcase(c)
            if k in vistos or (dias and st.st_mtime >= lim):
                continue
            if exts and not c.lower().endswith(exts) or nome and not nome(os.path.basename(c)):
                continue
            vistos.add(k)
            out.append((c, st.st_size))
    return out


def itens_de(paths):
    out = []
    for x in paths:
        if os.path.isdir(x):
            out += varrer([x])
        elif os.path.isfile(x):
            try:
                out.append((x, os.path.getsize(x)))
            except OSError:
                pass
    return out


def res(itens, obs="", n=None, ok=True, extra=0, **kw):
    return dict(itens=itens, bytes=sum(s for _, s in itens) + extra, n=len(itens) if n is None else n, obs=obs, ok=ok, **kw)


def cat(id, grupo, nome, info, perf=0, ganho="", ref=1 << 29, risco="baixo", adm=False, padrao=True, lixeira=False, aviso="", manut=False, tempo=""):
    def d(f):
        CATS.append(dict(id=id, grupo=grupo, nome=nome, info=info, perf=perf, ganho=ganho, ref=ref, risco=risco, adm=adm,
                         padrao=padrao, lixeira=lixeira, aviso=aviso, manut=manut, tempo=tempo, achar=f))
        return f
    return d


def limpa(id):
    def d(f):
        LIMPA[id] = f
        return f
    return d


def subdirs(p):
    try:
        return [e.path for e in os.scandir(p) if e.is_dir(follow_symlinks=False)]
    except OSError:
        return []


def descer(base, prof, nivel=1):
    for d in subdirs(base):
        if os.path.basename(d).lower() in SKIPN:
            continue
        yield d
        if nivel < prof:
            yield from descer(d, prof, nivel + 1)


# ----- navegadores: descobertos pela estrutura de pastas (Chrome, Edge, Brave, Opera, Vivaldi, Firefox e derivados) -----
def alt(p):
    c = caminhos()
    r, l = c["rad"], c["lad"]
    return l + p[len(r):] if r and l and p.lower().startswith(r.lower()) else p


def nome_nav(p):
    l = p.lower()
    for k, n in (("edge", "Edge"), ("chrome", "Chrome"), ("brave", "Brave"), ("vivaldi", "Vivaldi"), ("opera", "Opera"), ("chromium", "Chromium"), ("yandex", "Yandex")):
        if k in l:
            return n
    return os.path.basename(os.path.dirname(p)) or "Navegador"


def navegadores():
    if "nav" in CACHE:
        return CACHE["nav"]
    c, out, vistos = caminhos(), [], set()
    for base in (c["lad"], c["rad"]):
        for d in (descer(base, 3) if base else ()):
            k = os.path.normcase(d)
            if os.path.basename(d).lower() == "profiles":
                for pf in subdirs(d):
                    if any(os.path.exists(os.path.join(pf, x)) for x in ("places.sqlite", "cookies.sqlite", "cache2")):
                        out.append({"nome": "Firefox" if "firefox" in pf.lower() else os.path.basename(os.path.dirname(os.path.dirname(pf))), "tipo": "f", "raiz": pf, "perfis": [pf]})
            elif os.path.isfile(os.path.join(d, "Local State")) and k not in vistos:
                pr = [x for x in subdirs(d) if re.fullmatch(r"Default|Profile \d+|Guest Profile", os.path.basename(x))
                      and (os.path.exists(os.path.join(x, "History")) or os.path.isdir(os.path.join(x, "Network")))]
                if not pr and os.path.exists(os.path.join(d, "History")):
                    pr = [d]
                if pr:
                    vistos.add(k)
                    out.append({"nome": nome_nav(d), "tipo": "c", "raiz": d, "perfis": pr})
    CACHE["nav"] = out
    return out


CH = {"img": ["Cache"], "geral": ["Code Cache", "GPUCache", "DawnCache", "DawnGraphiteCache", "DawnWebGPUCache", r"Service Worker\CacheStorage", r"Service Worker\ScriptCache"],
      "ck": [r"Network\Cookies", r"Network\Cookies-journal", "Cookies", "Cookies-journal"]}
FF = {"img": ["cache2"], "geral": ["startupCache", "shader-cache", "thumbnails", "OfflineCache"], "ck": ["cookies.sqlite", "cookies.sqlite-wal", "cookies.sqlite-shm"]}


def alvos_nav(k):
    out = []
    for b in navegadores():
        ff = b["tipo"] == "f"
        for pf in b["perfis"]:
            for base in ({pf} if ff else {pf, alt(pf)}):
                out += [os.path.join(base, x) for x in (FF if ff else CH)[k]]
        if not ff and k == "geral":
            for base in {b["raiz"], alt(b["raiz"])}:
                out += [os.path.join(base, x) for x in ("GrShaderCache", "ShaderCache", "GraphiteDawnCache")]
    return out


def nomes_nav():
    return ", ".join(sorted({b["nome"] for b in navegadores()}))


def hist_dbs():
    r = []
    for b in navegadores():
        for pf in b["perfis"]:
            f = os.path.join(pf, "places.sqlite" if b["tipo"] == "f" else "History")
            if os.path.exists(f):
                r.append((f, b["tipo"]))
    return r


SQL = {("c", "nav"): ["DELETE FROM visits", "DELETE FROM visit_source", "DELETE FROM keyword_search_terms", "DELETE FROM segment_usage", "DELETE FROM segments", "DELETE FROM urls"],
       ("c", "dl"): ["DELETE FROM downloads", "DELETE FROM downloads_url_chains", "DELETE FROM downloads_slices"],
       ("f", "nav"): ["DELETE FROM moz_historyvisits", "DELETE FROM moz_inputhistory",
                      "DELETE FROM moz_places WHERE id NOT IN (SELECT fk FROM moz_bookmarks WHERE fk IS NOT NULL) AND foreign_count=0"],
       ("f", "dl"): ["DELETE FROM moz_annos WHERE anno_attribute_id IN (SELECT id FROM moz_anno_attributes WHERE name LIKE 'downloads/%')"]}


def contar_dl(dbs):
    tot = 0
    for f, t in dbs:
        try:
            con = sqlite3.connect(Path(f).as_uri() + "?mode=ro&immutable=1", uri=True, timeout=1)
            q = "SELECT COUNT(*) FROM downloads" if t == "c" else "SELECT COUNT(*) FROM moz_annos WHERE anno_attribute_id IN (SELECT id FROM moz_anno_attributes WHERE name LIKE 'downloads/%')"
            tot += con.execute(q).fetchone()[0]
            con.close()
        except Exception:
            pass
    return tot


def sql_limpar(dbs, quais):
    lib = n = ign = 0
    for f, t in dbs:
        con = None
        try:
            a = os.path.getsize(f)
            con = sqlite3.connect(f, timeout=1)
            for q in SQL[(t, quais)]:
                try:
                    con.execute(q)
                except sqlite3.OperationalError as e:
                    if "lock" in str(e).lower() or "busy" in str(e).lower():
                        raise
            con.commit()
            try:
                con.execute("VACUUM")
            except sqlite3.Error:
                pass
            con.close()
            lib += max(0, a - os.path.getsize(f))
            n += 1
        except Exception:
            ign += 1
            try:
                con and con.close()
            except Exception:
                pass
    return lib, n, ign


# ----- índice dos arquivos pessoais (pastas conhecidas do Windows, mesmo se o usuário as moveu) -----
def raizes_usuario():
    r, vis = [], set()
    for g, n in KF:
        p = pasta_usuario(g, n)
        k = os.path.normcase(os.path.abspath(p))
        if os.path.isdir(p) and k not in vis:
            vis.add(k)
            r.append(p)
    return r


def indice_usuario():
    if "idx" in CACHE:
        return CACHE["idx"]
    out, vistos = [], set()
    for r in raizes_usuario():
        for c, st in percorrer(r, ("painel_otimizacao",)):
            k = os.path.normcase(c)
            if k in vistos or getattr(st, "st_file_attributes", 0) & (0x400000 | 0x40000 | 0x1000):  # ignora placeholders da nuvem
                continue
            vistos.add(k)
            out.append((c, st.st_size, st.st_mtime))
            if len(out) > 600000:
                break
    CACHE["idx"] = out
    return out


def novos(lista):
    r = []
    for c, s in lista:
        k = os.path.normcase(c)
        if k not in CLAIM:
            CLAIM.add(k)
            r.append((c, s))
    return r


def do_indice(exts=None, dias=0, minimo=0, so=None, nome=None):
    lim, r = time.time() - dias * 86400, []
    for c, s, m in indice_usuario():
        b = os.path.basename(c).lower()
        if (exts or nome) and not ((exts and b.endswith(exts)) or (nome and nome(b))):
            continue
        if s < minimo or (dias and m >= lim) or (so and not os.path.normcase(c).startswith(os.path.normcase(so))):
            continue
        r.append((c, s))
    return novos(r)


def downloads():
    return pasta_usuario(KF[0][0], "Downloads")


def hq(c):
    with open(c, "rb") as f:
        return hashlib.blake2b(f.read(16384), digest_size=16).digest()


def hf(c, s):
    h = hashlib.blake2b(digest_size=16)
    with open(c, "rb") as f:
        if s <= 64 << 20:
            while True:
                b = f.read(1 << 20)
                if not b:
                    break
                h.update(b)
        else:
            for off in (0, s // 2, max(s - (1 << 20), 0)):
                f.seek(off)
                h.update(f.read(1 << 20))
    return h.digest()


def duplicados(exts, minimo):
    por = {}
    for c, s, m in indice_usuario():
        if c.lower().endswith(exts) and s >= minimo and os.path.normcase(c) not in CLAIM:
            por.setdefault(s, []).append((c, m))
    itens, grupos = [], 0
    for s, g in por.items():
        if len(g) < 2:
            continue
        h1 = {}
        for c, m in g:
            try:
                h1.setdefault(hq(c), []).append((c, m))
            except OSError:
                pass
        for g1 in h1.values():
            if len(g1) < 2:
                continue
            h2 = {}
            for c, m in g1:
                try:
                    h2.setdefault(hf(c, s), []).append((c, m))
                except OSError:
                    pass
            for g2 in h2.values():
                if len(g2) > 1:
                    g2.sort(key=lambda x: (len(x[0]), x[1]))
                    grupos += 1
                    itens += [(c, s) for c, _ in g2[1:]]
    return res(novos(itens), obs=f"{grupos} grupos de cópias; uma de cada é mantida")


def lixeira_info():
    try:
        r = _RB()
        r.cb = ctypes.sizeof(r)
        if ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(r)) == 0:
            return r.size, r.n
    except Exception:
        pass
    return 0, 0


# ----- categorias: Sistema -----
def pastas_temp():
    return [tempfile.gettempdir(), env("TEMP"), env("TMP"), os.path.join(caminhos()["lad"], "Temp")]


@cat("temp_user", "Sistema", "Temporários do usuário", "Sobras de programas na pasta temporária do seu usuário (com mais de 1 dia). Arquivos em uso são ignorados.",
     perf=1, ganho="menos lixo acumulado no disco", ref=1 << 30)
def _():
    return res(varrer(pastas_temp(), 1))


@cat("temp_win", "Sistema", "Temporários do Windows", "Arquivos temporários do próprio sistema (com mais de 1 dia).", perf=1, ganho="menos lixo acumulado no disco", ref=1 << 30, adm=True)
def _():
    return res(varrer([os.path.join(caminhos()["win"], "Temp")], 1))


@cat("thumbs", "Sistema", "Cache de miniaturas e ícones", "Miniaturas de imagens e ícones que o Explorer guarda. O Windows recria sozinho conforme você abre as pastas.",
     aviso="Pode reiniciar o Explorer por um instante.", ref=1 << 28)
def _():
    d = os.path.join(caminhos()["lad"], "Microsoft", "Windows", "Explorer")
    return res(varrer([d], nome=lambda n: bool(re.match(r"(thumbcache|iconcache)_.*\.db$", n.lower()))))


@cat("shaders", "Sistema", "Cache de shaders DirectX", "Shaders pré-compilados de jogos e do DirectX (NVIDIA, AMD, Intel). São recompilados quando necessário.",
     aviso="Jogos podem travar um pouco na primeira abertura depois de limpar.", padrao=False)
def _():
    c = caminhos()
    r = [os.path.join(c["lad"], x) for x in ("D3DSCache", r"NVIDIA\DXCache", r"NVIDIA\GLCache", r"AMD\DxCache", r"AMD\GLCache", r"AMD\VkCache", r"Intel\ShaderCache")]
    r += [os.path.join(c["low"], r"NVIDIA\PerDriverVersion\DXCache"), os.path.join(c["pd"], r"NVIDIA Corporation\NV_Cache")]
    return res(varrer(r))


@cat("dns", "Sistema", "Cache de DNS", "Lista de endereços de sites que o Windows lembra. Limpar resolve sites que não abrem após troca de rede ou de provedor.",
     perf=1, ganho="corrige sites que não abrem e conexões instáveis", adm=True, manut=True, tempo="segundos")
def _():
    rc, t = cmd(["powershell", "-NoProfile", "-NonInteractive", "-Command", "(Get-DnsClientCache | Measure-Object).Count"], 20)
    n = int(t.strip()) if t.strip().isdigit() else 0
    return res([], obs=f"{n} entradas" if n else "", n=n, pode=True)


@cat("store", "Sistema", "Cache da Microsoft Store", "Arquivos temporários da Loja. Limpar ajuda quando a Store trava ou não baixa apps.", perf=1, ganho="Store mais estável", ref=1 << 27)
def _():
    lad = caminhos()["lad"]
    r = []
    for d in glob.glob(os.path.join(lad, "Packages", "Microsoft.WindowsStore_*")):
        r += [os.path.join(d, "LocalCache"), os.path.join(d, "TempState")]
    return res(itens_de(r))


@cat("werr", "Sistema", "Relatórios de erro antigos", "Relatórios de travamento e despejos de memória do seu usuário com mais de 7 dias.", ref=1 << 28)
def _():
    c = caminhos()
    r = [os.path.join(c["lad"], "Microsoft", "Windows", "WER", x) for x in ("ReportArchive", "ReportQueue", "Temp")] + [os.path.join(c["lad"], "CrashDumps"), os.path.join(c["win"], "Minidump")]
    return res(varrer(r, 7))


@cat("werr_sys", "Sistema", "Relatórios WER do sistema", "Relatórios de erros e despejos do Windows (inclui MEMORY.DMP) com mais de 7 dias.", ref=1 << 30, adm=True)
def _():
    c = caminhos()
    r = [os.path.join(c["pd"], "Microsoft", "Windows", "WER", x) for x in ("ReportArchive", "ReportQueue", "Temp")] + [os.path.join(c["win"], "LiveKernelReports")]
    it = varrer(r, 7)
    m = os.path.join(c["win"], "MEMORY.DMP")
    try:
        if os.path.isfile(m) and os.path.getmtime(m) < time.time() - 7 * 86400:
            it.append((m, os.path.getsize(m)))
    except OSError:
        pass
    return res(it)


@cat("delivery", "Sistema", "Arquivos de otimização de entrega", "Cache que o Windows usa para compartilhar atualizações com outros PCs. Pode ficar com vários GB.",
     perf=1, ganho="menos disco e rede usados em segundo plano", ref=1 << 30, adm=True)
def _():
    w = caminhos()["win"]
    return res(varrer([os.path.join(w, "ServiceProfiles", "NetworkService", "AppData", "Local", "Microsoft", "Windows", "DeliveryOptimization", "Cache"), os.path.join(w, "SoftwareDistribution", "DeliveryOptimization")]))


@cat("win_logs", "Sistema", "Logs antigos do Windows", "Logs de instalação, atualização e componentes com mais de 7 dias.", ref=1 << 28, adm=True)
def _():
    w = caminhos()["win"]
    r = [os.path.join(w, "Logs", x) for x in ("CBS", "DISM", "WindowsUpdate", "SIH")] + [os.path.join(w, "Debug"), os.path.join(w, "Panther")]
    return res(varrer(r, 7, exts=(".log", ".etl", ".cab", ".old", ".txt")))


@cat("setup_tmp", "Sistema", "Temporários de instalação do Windows", "Sobras de atualizações de versão do Windows ($WINDOWS.~BT, $WINDOWS.~WS).",
     perf=1, ganho="libera vários GB de disco", ref=2 << 30, risco="medio", adm=True, padrao=False, aviso="Não use se uma atualização do Windows estiver pendente.")
def _():
    sd = caminhos()["sd"]
    return res(varrer([os.path.join(sd, x) for x in ("$Windows.~BT", "$Windows.~WS", "$GetCurrent", "ESD")]))


@cat("update_old", "Sistema", "Arquivos de atualização antigos", "Pacotes de atualização já baixados (SoftwareDistribution\\Download). O Windows baixa de novo se precisar.",
     perf=1, ganho="libera espaço e evita atualizações travadas", ref=1 << 30, adm=True)
def _():
    return res(varrer([os.path.join(caminhos()["win"], "SoftwareDistribution", "Download")]))


@cat("diag", "Sistema", "Arquivos de diagnóstico antigos", "Registros de telemetria e diagnóstico do Windows com mais de 7 dias.", ref=1 << 28, adm=True)
def _():
    pd = caminhos()["pd"]
    return res(varrer([os.path.join(pd, "Microsoft", "Diagnosis", x) for x in ("ETLLogs", "FeedbackHub")], 7))


# ----- Navegadores -----
@cat("nav_cache", "Navegadores", "Cache de navegadores", "Código e dados em cache dos sites (Chrome, Edge, Firefox, Brave, Opera e outros instalados).",
     perf=1, ganho="navegador mais leve", ref=1 << 30, aviso="Feche o navegador para limpar o que está em uso.")
def _():
    n = nomes_nav()
    return res(itens_de(alvos_nav("geral")), obs=n if n else "Nenhum navegador encontrado", ok=bool(n))


@cat("nav_imgs", "Navegadores", "Cache de imagens dos navegadores", "Imagens e mídias de sites já visitados. Voltam a ser baixadas quando você reabrir os sites.",
     perf=1, ganho="navegador mais leve", ref=1 << 30, aviso="Feche o navegador para limpar o que está em uso.")
def _():
    n = nomes_nav()
    return res(itens_de(alvos_nav("img")), obs=n if n else "Nenhum navegador encontrado", ok=bool(n))


@cat("cookies", "Navegadores", "Cookies dos navegadores", "Dados que os sites guardam sobre você (logins, carrinhos, preferências).",
     risco="medio", padrao=False, ref=1 << 26, aviso="Você será desconectado dos sites. Feche o navegador antes.")
def _():
    n = nomes_nav()
    return res(itens_de(alvos_nav("ck")), obs=n if n else "Nenhum navegador encontrado", ok=bool(n))


@cat("hist_nav", "Navegadores", "Histórico de navegação", "Lista de sites visitados e favicons. Favoritos e senhas não são tocados.",
     risco="medio", padrao=False, ref=1 << 26, aviso="Feche o navegador antes, senão o histórico não é apagado.")
def _():
    dbs = hist_dbs()
    extra, itens = 0, []
    for f, t in dbs:
        try:
            extra += os.path.getsize(f)
        except OSError:
            pass
        if t == "c":
            itens += itens_de([os.path.join(os.path.dirname(f), x) for x in ("Top Sites", "Visited Links", "Favicons")])
    return res(itens, extra=extra, ok=bool(dbs), obs="" if dbs else "Nenhum navegador encontrado", sql=dbs)


@cat("hist_dl", "Navegadores", "Histórico de downloads do navegador", "Só a lista de downloads feitos. Os arquivos baixados continuam nas suas pastas.",
     risco="medio", padrao=False, aviso="Feche o navegador antes, senão o histórico não é apagado.")
def _():
    dbs = hist_dbs()
    n = contar_dl(dbs)
    return res([], n=n, ok=bool(dbs), pode=bool(dbs), sql=dbs, obs="" if dbs else "Nenhum navegador encontrado")


# ----- Arquivos pessoais (vão para a Lixeira, nunca são apagados direto) -----
@cat("old_inst", "Arquivos pessoais", "Instaladores antigos", "Instaladores (.exe, .msi, .msix) parados na pasta Downloads há mais de 30 dias.",
     risco="medio", padrao=False, lixeira=True, ref=1 << 30)
def _():
    return res(do_indice((".exe", ".msi", ".msix", ".msixbundle", ".appx", ".appxbundle"), 30, so=downloads()))


@cat("zips", "Arquivos pessoais", "ZIP/RAR esquecidos", "Arquivos compactados (.zip, .rar, .7z) parados na pasta Downloads há mais de 30 dias.",
     risco="medio", padrao=False, lixeira=True, ref=1 << 30)
def _():
    return res(do_indice((".zip", ".rar", ".7z", ".tar", ".gz", ".tgz"), 30, so=downloads()))


@cat("tmp_pess", "Arquivos pessoais", "Arquivos temporários pessoais", "Restos como .tmp, downloads incompletos (.crdownload, .part) e travas de Office (~$) em suas pastas, com mais de 7 dias.",
     risco="medio", padrao=False, lixeira=True, ref=1 << 27)
def _():
    return res(do_indice((".tmp", ".temp", ".crdownload", ".part", ".partial"), 7, nome=lambda b: b.startswith("~$")))


@cat("dup_fot", "Arquivos pessoais", "Fotos duplicadas", "Imagens idênticas (mesmo conteúdo) em Imagens, Documentos, Downloads e Desktop. Uma cópia de cada é mantida.",
     risco="medio", padrao=False, lixeira=True, ref=1 << 30)
def _():
    return duplicados((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic", ".tif", ".tiff"), 10240)


@cat("dup_vid", "Arquivos pessoais", "Vídeos duplicados", "Vídeos idênticos em suas pastas. Uma cópia de cada é mantida.",
     risco="medio", padrao=False, lixeira=True, ref=2 << 30)
def _():
    return duplicados((".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".m4v", ".flv"), 1 << 20)


@cat("grandes", "Arquivos pessoais", "Arquivos grandes esquecidos", "Arquivos acima de 500 MB que você não modifica há mais de 6 meses.",
     risco="alto", padrao=False, lixeira=True, ref=4 << 30, aviso="Confira antes: podem ser arquivos importantes (máquinas virtuais, backups).")
def _():
    return res(do_indice(None, 180, 500 << 20, nome=lambda b: True))


@cat("recycle", "Arquivos pessoais", "Lixeira", "Tudo que está na Lixeira de todas as unidades. Se marcada junto com arquivos pessoais, eles serão apagados de vez.",
     ref=1 << 30)
def _():
    t, n = lixeira_info()
    return res([], n=n, extra=t)


# ----- Manutenção -----
def analisar_dism():
    c = CACHE.get("dism")
    if c and time.time() - c[0] < 3600:
        return c[1]
    rc, t = cmd(["Dism.exe", "/Online", "/Cleanup-Image", "/AnalyzeComponentStore"], 300)
    m = list(re.finditer(r"(\d+(?:[.,]\d+)?)\s*(KB|MB|GB|TB)", t, re.I))
    v = lambda x: int(float(x.group(1).replace(",", ".")) * {"KB": 1 << 10, "MB": 1 << 20, "GB": 1 << 30, "TB": 1 << 40}[x.group(2).upper()])
    est = v(m[3]) + v(m[4]) if len(m) >= 5 else 0
    CACHE["dism"] = (time.time(), est)
    return est


@cat("dism_cleanup", "Manutenção", "Limpeza de componentes antigos do Windows (DISM)", "Remove versões antigas de componentes do sistema (WinSxS) que já foram substituídas por atualizações.",
     perf=1, ganho="libera espaço do sistema", ref=1 << 30, adm=True, padrao=False, manut=True, tempo="5 a 20 min", aviso="Demora; não desligue o computador durante o processo.")
def _():
    return res([], extra=analisar_dism(), n=0)


@cat("sfc", "Manutenção", "Verificação de integridade do Windows (SFC)", "Confere os arquivos do sistema e repara os que estiverem corrompidos. Sistema travando ou com erros estranhos costuma melhorar.",
     perf=2, ganho="repara arquivos corrompidos (menos erros e travamentos)", adm=True, padrao=False, manut=True, tempo="10 a 30 min", aviso="Demora; não desligue o computador durante o processo.")
def _():
    return res([], pode=True)


@cat("dism_repair", "Manutenção", "Reparação da imagem do Windows (DISM)", "Repara a base que o próprio Windows usa para se consertar. Use se o SFC achar problemas que não consegue reparar.",
     perf=2, ganho="repara a imagem do sistema", adm=True, padrao=False, manut=True, tempo="10 a 30 min", aviso="Precisa de internet e demora; não desligue o computador.")
def _():
    return res([], pode=True)


SSD_PS = ("$r=@();foreach($v in Get-Volume|?{$_.DriveType -eq 'Fixed' -and $_.DriveLetter}){try{"
          "$d=Get-Partition -DriveLetter $v.DriveLetter|Get-Disk|Get-PhysicalDisk;if($d.MediaType -eq 'SSD'){$r+=[string]$v.DriveLetter}}catch{}};$r -join ','")


@cat("trim", "Manutenção", "Otimização do SSD (TRIM)", "Avisa ao SSD quais blocos estão livres, mantendo a velocidade de escrita. Só roda em unidades SSD.",
     perf=2, ganho="SSD mantém a velocidade de escrita", adm=True, manut=True, tempo="1 a 2 min")
def _():
    letras = [x for x in ps(SSD_PS, 40).split(",") if x.strip()]
    CACHE["ssd"] = letras
    return res([], ok=bool(letras), pode=bool(letras), obs=("SSD em " + ", ".join(l + ":" for l in letras)) if letras else "Nenhum SSD detectado")


# ----- limpeza: execução -----
def apagar(itens):
    lib = n = 0
    rest = []
    for c, s in itens:
        try:
            os.remove(c)
            lib, n = lib + s, n + 1
        except FileNotFoundError:
            pass
        except OSError:
            try:
                os.chmod(c, stat.S_IWRITE)
                os.remove(c)
                lib, n = lib + s, n + 1
            except OSError:
                rest.append((c, s))
    return dict(liberado=lib, n=n, ign=len(rest), rest=rest)


def lixo(itens):
    """Envia para a Lixeira (recuperável)."""
    mov = n = 0
    rest = []
    for i in range(0, len(itens), 100):
        lote = itens[i:i + 100]
        buf = ctypes.create_unicode_buffer("\0".join(c for c, _ in lote) + "\0\0")
        op = _SHOP()
        op.op, op.src, op.flags = 3, ctypes.cast(buf, ctypes.c_void_p).value, 0x40 | 0x10 | 0x400 | 0x4
        try:
            ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
        except Exception:
            pass
        for c, s in lote:
            if os.path.exists(c):
                rest.append((c, s))
            else:
                mov, n = mov + s, n + 1
    return dict(liberado=0, movido=mov, n=n, ign=len(rest), rest=rest)


def podar(raizes, tudo=False):
    lim = time.time() - 86400
    for r in raizes:
        if not r or not os.path.isdir(r):
            continue
        for dp, _, _ in os.walk(r, topdown=False):
            if dp == r and not tudo:
                continue
            try:
                if os.lstat(dp).st_mtime < lim or tudo:
                    os.rmdir(dp)
            except OSError:
                pass


PODAR = {"temp_user": lambda: pastas_temp(), "temp_win": lambda: [os.path.join(caminhos()["win"], "Temp")],
         "update_old": lambda: [os.path.join(caminhos()["win"], "SoftwareDistribution", "Download")],
         "setup_tmp": lambda: [os.path.join(caminhos()["sd"], x) for x in ("$Windows.~BT", "$Windows.~WS", "$GetCurrent", "ESD")]}


@limpa("thumbs")
def _(d):
    r = apagar(d["itens"])
    if r["rest"]:  # o Explorer segura os arquivos: reinicia por um instante
        cmd(["taskkill", "/f", "/im", "explorer.exe"], 20)
        time.sleep(1.2)
        r2 = apagar(r["rest"])
        r.update(liberado=r["liberado"] + r2["liberado"], n=r["n"] + r2["n"], ign=r2["ign"], rest=r2["rest"])
        reabrir_explorer()
    return r


@limpa("setup_tmp")
def _(d):
    for x in PODAR["setup_tmp"]():
        if os.path.isdir(x):
            cmd(["takeown", "/f", x, "/r", "/d", "Y"], 300)
            cmd(["icacls", x, "/grant", "*S-1-5-32-544:F", "/t", "/c", "/q"], 300)
    return apagar(d["itens"])


@limpa("update_old")
def _(d):
    ativos = []
    for n in ("wuauserv", "bits"):
        if "RUNNING" in cmd(["sc", "query", n], 20)[1].upper():
            ativos.append(n)
            cmd(["net", "stop", n, "/y"], 60)
    r = apagar(d["itens"])
    for n in ativos:
        cmd(["net", "start", n], 60)
    return r


@limpa("dns")
def _(d):
    rc, t = cmd(["ipconfig", "/flushdns"], 30)
    return dict(liberado=0, n=d["n"], ign=0, obs="Cache limpo" if rc == 0 else "Não foi possível limpar")


def _hist(q):
    def f(d):
        r = apagar(d["itens"]) if d["itens"] else dict(liberado=0, n=0, ign=0, rest=[])
        lib, n, ign = sql_limpar(d["sql"], q)
        r.update(liberado=r["liberado"] + lib, n=r["n"] + n, ign=r["ign"] + ign, rest=[], obs="Feche o navegador para limpar tudo" if r["ign"] + ign else "")
        return r
    return f


LIMPA["hist_nav"], LIMPA["hist_dl"] = _hist("nav"), _hist("dl")


@limpa("recycle")
def _(d):
    t, n = lixeira_info()
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x7)
    except Exception:
        pass
    return dict(liberado=max(0, t - lixeira_info()[0]), n=n, ign=0)


@limpa("dism_cleanup")
def _(d):
    a = livre()
    rc, _t = cmd(["Dism.exe", "/Online", "/Cleanup-Image", "/StartComponentCleanup"], 3600)
    CACHE.pop("dism", None)
    return dict(liberado=max(0, livre() - a), n=0, ign=0, obs="Concluído" if rc == 0 else f"Falhou (código {rc})")


@limpa("sfc")
def _(d):
    rc, t = cmd(["sfc", "/scannow"], 3600)
    l = t.lower()
    if re.search(r"unable to fix|n[aã]o foi poss[ií]vel reparar|n[aã]o p[oô]de reparar|n[aã]o conseguiu reparar", l):
        o = "Problemas encontrados que não puderam ser reparados. Rode o reparo da imagem (DISM)."
    elif re.search(r"did not find|n[aã]o encontrou", l):
        o = "Nenhum problema encontrado"
    elif re.search(r"successfully repaired|reparou com|reparados? com", l):
        o = "Problemas encontrados e reparados"
    else:
        o = "Concluído" if rc == 0 else f"Terminou com código {rc}"
    return dict(liberado=0, n=0, ign=0, obs=o)


@limpa("dism_repair")
def _(d):
    rc, _t = cmd(["Dism.exe", "/Online", "/Cleanup-Image", "/RestoreHealth"], 3600)
    return dict(liberado=0, n=0, ign=0, obs="Imagem do Windows íntegra" if rc == 0 else f"Falhou (código {rc}). Verifique a internet.")


@limpa("trim")
def _(d):
    ok = []
    for l in CACHE.get("ssd", []):
        if l.strip().isalpha() and "OK" in ps(f"try{{Optimize-Volume -DriveLetter {l.strip()} -ReTrim -ErrorAction Stop;'OK'}}catch{{'ERRO'}}", 900):
            ok.append(l.strip() + ":")
    return dict(liberado=0, n=len(ok), ign=0, obs=("TRIM executado em " + ", ".join(ok)) if ok else "Não foi possível executar o TRIM")


# ----- orquestração -----
CAMPOS = ("id", "grupo", "nome", "info", "perf", "ganho", "ref", "risco", "adm", "padrao", "lixeira", "aviso", "manut", "tempo")


def ocupado():
    return L["scan"]["estado"] == "esc" or L["limpa"]["estado"] == "exe"


def escanear():
    with L["lock"]:
        if ocupado():
            return False
        L["scan"].update(estado="esc", i=0, n=len(CATS), atual="")
        L["limpa"].update(estado="ocioso", res={})
        L["dados"].clear()
        L["cs"].clear()
        CACHE.pop("idx", None)
        CACHE.pop("nav", None)
        CLAIM.clear()

    def run():
        for i, c in enumerate(CATS):
            L["cs"][c["id"]] = "esc"
            L["scan"].update(i=i, atual=c["nome"])
            try:
                d = res([], ok=False, obs="Requer administrador") if c["adm"] and not ADMIN else c["achar"]()
            except Exception as e:
                d = res([], ok=False, obs="Erro ao analisar: " + type(e).__name__)
            L["dados"][c["id"]] = d
            L["cs"][c["id"]] = "ok"
        L["scan"].update(estado="ok", i=len(CATS), atual="")

    threading.Thread(target=run, daemon=True).start()
    return True


def limpar(ids):
    with L["lock"]:
        fila = [c for c in CATS if c["id"] in ids and (not c["adm"] or ADMIN) and c["id"] in L["dados"]]
        if ocupado() or not fila:
            return False
        L["limpa"].update(estado="exe", i=0, n=len(fila), atual="", res={})

    def run():
        for i, c in enumerate(fila):
            id = c["id"]
            d = L["dados"][id]
            L["limpa"].update(i=i, atual=id)
            try:
                f = LIMPA.get(id)
                r = f(d) if f else (lixo if c["lixeira"] else apagar)(d["itens"])
                if id in PODAR and not r.get("ign"):
                    podar(PODAR[id](), id == "setup_tmp")
                elif id in PODAR:
                    podar(PODAR[id](), False)
            except Exception as e:
                r = dict(liberado=0, n=0, ign=0, obs="Erro: " + type(e).__name__, rest=d["itens"])
            rest = r.pop("rest", [])
            d.update(itens=rest, bytes=sum(s for _, s in rest), n=len(rest))
            L["limpa"]["res"][id] = r
        L["limpa"].update(estado="ok", i=len(fila), atual="")

    threading.Thread(target=run, daemon=True).start()
    return True


def estado():
    c0 = caminhos()
    try:
        du = shutil.disk_usage(c0["sd"])
        disco = dict(total=du.total, livre=du.free, letra=c0["sd"][:2])
    except OSError:
        disco = dict(total=1, livre=1, letra="")
    cats = []
    for c in CATS:
        d = L["dados"].get(c["id"])
        bloq = c["adm"] and not ADMIN
        it = {k: c[k] for k in CAMPOS}
        it.update(bloq=bloq, st=L["cs"].get(c["id"], "pend"), bytes=None if d is None else d["bytes"], n=0 if d is None else d["n"],
                  obs="" if d is None else d.get("obs", ""),
                  pode=bool(d) and d["ok"] and not bloq and bool(c["manut"] or d["bytes"] > 0 or d["n"] > 0 or d.get("pode")))
        cats.append(it)
    return dict(admin=ADMIN, disco=disco, cats=cats, scan=dict(L["scan"]), limpeza=dict(L["limpa"]))


def elevar():
    if ADMIN:
        return {"ok": False}
    try:
        args = "" if getattr(sys, "frozen", False) else f'"{os.path.abspath(sys.argv[0])}"'
        if ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, args, None, 1) > 32:
            threading.Timer(1.0, lambda: os._exit(0)).start()
            return {"ok": True}
    except Exception:
        pass
    return {"ok": False}



# ---------- Windows: ajustes de desempenho (reversíveis; original salvo em %LOCALAPPDATA%\Tellez) ----------
try:
    import winreg
except ImportError:
    winreg = None

TW, DYN = [], []
W = {"estado": "ocioso", "i": 0, "n": 0, "dados": {}, "info": {},
     "apl": {"estado": "ocioso", "i": 0, "n": 0, "atual": "", "res": {}, "ponto": "", "reboot": False}}
TIPO = {}
if winreg:
    TIPO = {winreg.REG_DWORD: "d", winreg.REG_SZ: "s", winreg.REG_EXPAND_SZ: "s", winreg.REG_BINARY: "b"}


def bk_arq():
    d = Path(env("LOCALAPPDATA") or Path.home()) / "Tellez"
    d.mkdir(parents=True, exist_ok=True)
    return d / "backup_ajustes.json"


def bk_ler():
    try:
        return json.loads(bk_arq().read_text(encoding="utf-8"))
    except Exception:
        return {}


def bk_salvar():
    try:
        bk_arq().write_text(json.dumps(BK), encoding="utf-8")
    except Exception:
        pass


BK = bk_ler()
rk = lambda h: winreg.HKEY_CURRENT_USER if h == "HKCU" else winreg.HKEY_LOCAL_MACHINE
ACC = lambda: winreg.KEY_WOW64_64KEY


def reg_ler(h, p, n):
    try:
        with winreg.OpenKey(rk(h), p, 0, winreg.KEY_READ | ACC()) as k:
            return winreg.QueryValueEx(k, n)
    except OSError:
        return None


def reg_esc(h, p, n, t, v):
    with winreg.CreateKeyEx(rk(h), p, 0, winreg.KEY_SET_VALUE | ACC()) as k:
        winreg.SetValueEx(k, n, 0, {"d": winreg.REG_DWORD, "s": winreg.REG_SZ, "b": winreg.REG_BINARY}[t], v)


def reg_del(h, p, n):
    try:
        with winreg.OpenKey(rk(h), p, 0, winreg.KEY_SET_VALUE | ACC()) as k:
            winreg.DeleteValue(k, n)
    except OSError:
        pass


def reg_subkeys(h, p):
    r = []
    try:
        with winreg.OpenKey(rk(h), p, 0, winreg.KEY_READ | ACC()) as k:
            i = 0
            while True:
                try:
                    r.append(winreg.EnumKey(k, i))
                    i += 1
                except OSError:
                    break
    except OSError:
        pass
    return r


def reg_valores(h, p):
    r = []
    try:
        with winreg.OpenKey(rk(h), p, 0, winreg.KEY_READ | ACC()) as k:
            i = 0
            while True:
                try:
                    r.append(winreg.EnumValue(k, i))
                    i += 1
                except OSError:
                    break
    except OSError:
        pass
    return r


def T(h, p, n, t, v, pad=None, bit=False):
    return dict(h=h, p=p, n=n, t=t, v=v, pad=pad, bit=bit)


def alvo_ok(a):
    c = reg_ler(a["h"], a["p"], a["n"])
    if c is None:
        return False
    if a["bit"]:
        return int(c[0]) & 1 == 1
    return str(c[0]) == str(a["v"]) if a["t"] == "s" else int(c[0]) == int(a["v"])


def tw(id, grupo, nome, info, ler, ap, rv, perf=0, ganho="", risco="baixo", adm=False, rec=True, aviso="", reboot=False, exp=False, cond=None):
    TW.append(dict(id=id, grupo=grupo, nome=nome, info=info, ler=ler, apply=ap, revert=rv, perf=perf, ganho=ganho, risco=risco,
                   adm=adm, rec=rec, aviso=aviso, reboot=reboot, exp=exp, cond=cond))


def reg(id, grupo, nome, info, alvos, **kw):
    A = lambda: alvos() if callable(alvos) else alvos
    kw.setdefault("adm", callable(alvos) or any(a["h"] == "HKLM" for a in alvos))

    def ler():
        a = A()
        return bool(a) and all(alvo_ok(x) for x in a)

    def ap():
        b = BK.setdefault(id, {})
        for a in A():
            k = f'{a["h"]}|{a["p"]}|{a["n"]}'
            if k not in b:
                c = reg_ler(a["h"], a["p"], a["n"])
                b[k] = None if c is None else [c[0].hex() if isinstance(c[0], bytes) else c[0], TIPO.get(c[1], "d")]
            reg_esc(a["h"], a["p"], a["n"], a["t"], a["v"])
        bk_salvar()

    def rv():
        b = BK.get(id, {})
        for a in A():
            o = b.get(f'{a["h"]}|{a["p"]}|{a["n"]}', "?")
            if o == "?" or (o is not None and (str(o[0]) == str(a["v"]) or (a["bit"] and int(o[0]) & 1))):
                o = None if a["pad"] is None else [a["pad"], a["t"]]
            if o is None:
                reg_del(a["h"], a["p"], a["n"])
            else:
                reg_esc(a["h"], a["p"], a["n"], o[1], o[0])
        BK.pop(id, None)
        bk_salvar()

    tw(id, grupo, nome, info, ler, ap, rv, **kw)


# ----- serviços -----
SVC = r"SYSTEM\CurrentControlSet\Services\%s"


def svc(id, grupo, nome, info, nomes, **kw):
    auto = kw.pop("auto", False)
    ex = lambda: [n for n in nomes if reg_ler("HKLM", SVC % n, "Start")]

    def ler():
        e = ex()
        return bool(e) and all(int(reg_ler("HKLM", SVC % n, "Start")[0]) == 4 for n in e)

    def ap():
        b = BK.setdefault(id, {})
        for n in ex():
            if n not in b:
                b[n] = [int(reg_ler("HKLM", SVC % n, "Start")[0]), int((reg_ler("HKLM", SVC % n, "DelayedAutostart") or (0,))[0])]
            cmd(["sc", "config", n, "start=", "disabled"], 30)
            cmd(["sc", "stop", n], 30)
        bk_salvar()

    def rv():
        b = BK.get(id, {})
        for n in ex():
            s, d = b.get(n, [2 if auto else 3, 0])
            cmd(["sc", "config", n, "start=", "delayed-auto" if s == 2 and d else {2: "auto", 3: "demand", 4: "disabled"}[s]], 30)
            if s == 2:
                cmd(["sc", "start", n], 30)
        BK.pop(id, None)
        bk_salvar()

    tw(id, grupo, nome, info, ler, ap, rv, adm=True, cond=lambda: (bool(ex()), "" if ex() else "Serviço não existe neste Windows"), **kw)


# ----- energia -----
GRE = re.compile(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})")
HIGH, ULT, BAL = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", "e9a42b02-d5df-448d-aa00-03f14749eb61", "381b4222-f694-41f0-9685-ff5bb260df2e"


def plano_ativo():
    m = GRE.search(cmd(["powercfg", "/getactivescheme"], 15)[1])
    return m.group(1).lower() if m else ""


def plano_ler():
    return plano_ativo() in (HIGH, ULT, BK.get("plano", {}).get("novo", "-"))


def plano_ap():
    a, b = plano_ativo(), BK.setdefault("plano", {})
    if "orig" not in b and a and a not in (HIGH, ULT, b.get("novo")):
        b["orig"] = a
    for src in (ULT, HIGH):
        if cmd(["powercfg", "/setactive", src], 15)[0] == 0:
            return bk_salvar()
    for src in (ULT, HIGH):
        m = GRE.search(cmd(["powercfg", "-duplicatescheme", src], 15)[1])
        if m and cmd(["powercfg", "/setactive", m.group(1)], 15)[0] == 0:
            b["novo"] = m.group(1).lower()
            return bk_salvar()
    raise RuntimeError("plano indisponível")


def plano_rv():
    b = BK.get("plano", {})
    if cmd(["powercfg", "/setactive", b.get("orig") or BAL], 15)[0] != 0:
        cmd(["powercfg", "/setactive", BAL], 15)
    if b.get("novo"):
        cmd(["powercfg", "/delete", b["novo"]], 15)
    BK.pop("plano", None)
    bk_salvar()


def pw(id, grupo, nome, info, sub, setg, val, pad, **kw):
    def q():
        h = re.findall(r"0x([0-9a-fA-F]{8})", cmd(["powercfg", "/query", "SCHEME_CURRENT", sub, setg], 15)[1])
        return int(h[-2], 16) if len(h) >= 2 else None

    def setac(v):
        cmd(["powercfg", "/setacvalueindex", "SCHEME_CURRENT", sub, setg, str(v)], 15)
        cmd(["powercfg", "/setactive", "SCHEME_CURRENT"], 15)

    def ap():
        b = BK.setdefault(id, {})
        if "o" not in b:
            b["o"] = q()
        setac(val)
        bk_salvar()

    def rv():
        o = BK.get(id, {}).get("o")
        setac(pad if o is None or o == val else o)
        BK.pop(id, None)
        bk_salvar()

    tw(id, grupo, nome, info, lambda: q() == val, ap, rv, cond=lambda: (q() is not None, "" if q() is not None else "Não disponível neste PC"), **kw)


# ----- tarefas agendadas de telemetria -----
TAREFAS = [("\\Microsoft\\Windows\\Application Experience\\", "Microsoft Compatibility Appraiser"), ("\\Microsoft\\Windows\\Application Experience\\", "ProgramDataUpdater"),
           ("\\Microsoft\\Windows\\Customer Experience Improvement Program\\", "Consolidator"), ("\\Microsoft\\Windows\\Customer Experience Improvement Program\\", "UsbCeip"),
           ("\\Microsoft\\Windows\\Windows Error Reporting\\", "QueueReporting")]


def tarefas_estado():
    sc = "".join(f"$x=Get-ScheduledTask -TaskPath '{p}' -TaskName '{n}' -EA SilentlyContinue;if($x){{'{p}|{n}|'+$x.State}};" for p, n in TAREFAS)
    r = {}
    for l in ps(sc, 40).splitlines():
        x = l.strip().split("|")
        if len(x) == 3:
            r[(x[0], x[1])] = x[2]
    return r


def tarefas_set(ativar, so=None):
    for (p, n), _ in tarefas_estado().items():
        if so is None or (p, n) in so:
            ps(f"{'Enable' if ativar else 'Disable'}-ScheduledTask -TaskPath '{p}' -TaskName '{n}' | Out-Null", 30)


def tarefas_ap():
    st = tarefas_estado()
    BK["tarefas"] = [[p, n] for (p, n), s in st.items() if s != "Disabled"] or BK.get("tarefas", [])
    tarefas_set(False)
    bk_salvar()


def tarefas_rv():
    so = {tuple(x) for x in BK.get("tarefas", [])}
    tarefas_set(True, so or None)
    BK.pop("tarefas", None)
    bk_salvar()


def hib_ap():
    cmd(["powercfg", "-h", "off"], 30)


def hib_rv():
    cmd(["powercfg", "-h", "on"], 30)


def reabrir_explorer():
    for _ in range(8):  # o próprio Windows reabre o Explorer com a conta normal do usuário
        time.sleep(1)
        if "explorer.exe" in cmd(["tasklist", "/fi", "imagename eq explorer.exe"], 15)[1].lower():
            return
    try:
        subprocess.Popen(["explorer.exe"], creationflags=NO_WINDOW)
    except Exception:
        pass


def reiniciar_explorer():
    cmd(["taskkill", "/f", "/im", "explorer.exe"], 20)
    reabrir_explorer()


# ----- informações do PC -----
class _SPS(ctypes.Structure):
    _fields_ = [("ac", ctypes.c_ubyte), ("flag", ctypes.c_ubyte), ("pct", ctypes.c_ubyte), ("sf", ctypes.c_ubyte), ("life", wt.DWORD), ("full", wt.DWORD)]


def coletar_info():
    b = sys.getwindowsversion().build if hasattr(sys, "getwindowsversion") else 0
    nome = (reg_ler("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductName") or ("Windows",))[0]
    if b >= 22000:
        nome = nome.replace("Windows 10", "Windows 11")
    dv = (reg_ler("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "DisplayVersion") or ("",))[0]
    try:
        ram = round(memoria()[0] / 2 ** 30, 1)
    except Exception:
        ram = 0
    if "ssd" not in CACHE:
        CACHE["ssd"] = [x.strip().upper() for x in ps(SSD_PS, 40).split(",") if x.strip()]
    ssd = caminhos()["sd"][0].upper() in CACHE["ssd"]
    nb = False
    try:
        s = _SPS()
        if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s)):
            nb = s.flag not in (128, 255)
    except Exception:
        pass
    return dict(windows=f"{nome} {dv}".strip(), build=b, ram=ram, ssd=ssd, notebook=nb, nucleos=os.cpu_count() or 0, hz=_hz_info())


I = lambda: W["info"]
mais_que = lambda mn, mx=10 ** 9: (lambda: (mn <= I().get("build", 0) < mx, "" if mn <= I().get("build", 0) < mx else ("Somente Windows 11" if mn >= 22000 else "Somente Windows 10" if mx <= 22000 else "Versão do Windows não compatível")))
HK = r"Software\Microsoft\Windows\CurrentVersion"
ADV = HK + r"\Explorer\Advanced"
SP = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
POL = r"SOFTWARE\Policies\Microsoft\Windows"

# Energia
G = "Energia"
tw("plano", G, "Plano de energia de desempenho máximo", "Troca o plano Equilibrado pelo Ultimate/Alto desempenho: o processador não reduz o clock sob carga.",
   plano_ler, plano_ap, plano_rv, perf=3, ganho="CPU responde na hora, sem esperar o clock subir", rec=lambda: not I().get("notebook"),
   aviso="Em notebook aumenta o consumo de bateria.")
pw("proc", G, "Processador sempre a 100% (na tomada)", "Estado mínimo do processador em 100% quando ligado na energia. Elimina a latência de subida de clock.",
   "SUB_PROCESSOR", "PROCTHROTTLEMIN", 100, 5, perf=2, ganho="menos engasgos em tarefas curtas", rec=lambda: not I().get("notebook"), aviso="Aumenta calor e consumo.", risco="medio")
pw("disco", G, "Nunca desligar o disco (na tomada)", "Evita o disco parar de girar e demorar para acordar (HDD) ou entrar em estados de baixa energia.",
   "SUB_DISK", "DISKIDLE", 0, 1200, perf=1, ganho="sem atraso ao acessar o disco depois de ocioso", rec=lambda: not I().get("notebook"))
pw("aspm", G, "Desativar economia de energia do PCIe", "Impede o link PCIe (GPU, NVMe) de entrar em estados de economia (ASPM), que adicionam latência.",
   "SUB_PCIEXPRESS", "ASPM", 0, 2, perf=1, ganho="menos latência em GPU e SSD NVMe", rec=lambda: not I().get("notebook"), aviso="Pequeno aumento de consumo.")
tw("hiber", G, "Desativar hibernação", "Apaga o hiberfil.sys (≈ 40–75% da RAM) e libera esse espaço. Desativa também a inicialização rápida.",
   lambda: (reg_ler("HKLM", r"SYSTEM\CurrentControlSet\Control\Power", "HibernateEnabled") or (1,))[0] == 0, hib_ap, hib_rv, perf=0, ganho="libera vários GB de disco",
   adm=True, rec=False, risco="medio", aviso="Você perde a opção de hibernar.")

# Interface e animações
G = "Interface e animações"
reg("transp", G, "Desativar transparência", "Tira o efeito de vidro (acrílico) do menu Iniciar, barra e janelas. Reduz uso de GPU e RAM de vídeo.",
    [T("HKCU", HK + r"\Themes\Personalize", "EnableTransparency", "d", 0, 1)], perf=2, ganho="menos carga na GPU e interface mais leve")
reg("animjan", G, "Desativar animações de janelas", "Minimizar e maximizar sem animação.", [T("HKCU", r"Control Panel\Desktop\WindowMetrics", "MinAnimate", "s", "0", "1")],
    perf=1, ganho="janelas abrem e fecham instantaneamente", reboot=True)
reg("animbarra", G, "Desativar animações da barra e das listas", "Remove animações da barra de tarefas e o efeito de seleção translúcida e sombras nas listas.",
    [T("HKCU", ADV, "TaskbarAnimations", "d", 0, 1), T("HKCU", ADV, "ListviewAlphaSelect", "d", 0, 1), T("HKCU", ADV, "ListviewShadow", "d", 0, 1)],
    perf=1, ganho="Explorer mais ágil", exp=True)
reg("menudelay", G, "Menus sem atraso", "Os menus abrem na hora (o padrão espera 400 ms).", [T("HKCU", r"Control Panel\Desktop", "MenuShowDelay", "s", "0", "400")],
    perf=1, ganho="sensação de resposta mais rápida", reboot=True)
reg("fechar", G, "Fechar programas travados mais rápido", "Reduz o tempo que o Windows espera antes de encerrar programas que não respondem e fecha os pendentes ao desligar.",
    [T("HKCU", r"Control Panel\Desktop", "AutoEndTasks", "s", "1", "0"), T("HKCU", r"Control Panel\Desktop", "WaitToKillAppTimeout", "s", "2000", "20000"),
     T("HKCU", r"Control Panel\Desktop", "HungAppTimeout", "s", "1000", "5000")], perf=1, ganho="desligar e sair do Windows mais rápido",
    aviso="Programas com arquivo aberto podem fechar sem perguntar.", risco="medio", rec=False, reboot=True)
reg("svcfechar", G, "Desligar serviços mais rápido", "Diminui o tempo de espera para encerrar serviços ao desligar (5 s para 2 s).",
    [T("HKLM", r"SYSTEM\CurrentControlSet\Control", "WaitToKillServiceTimeout", "s", "2000", "5000")], perf=1, ganho="desligamento mais rápido", reboot=True)
reg("thispc", G, "Explorer abre em \"Este Computador\"", "Evita carregar o Acesso Rápido (arquivos recentes e pastas de rede) ao abrir o Explorer.",
    [T("HKCU", ADV, "LaunchTo", "d", 1, None)], perf=0, ganho="Explorer abre mais rápido", exp=True)
reg("recentes", G, "Sem arquivos recentes no Acesso Rápido", "O Explorer para de montar a lista de recentes e frequentes (e de consultar arquivos de rede para isso).",
    [T("HKCU", HK + r"\Explorer", "ShowRecent", "d", 0, 1), T("HKCU", HK + r"\Explorer", "ShowFrequent", "d", 0, 1)], perf=0, ganho="Explorer mais leve e mais privacidade", exp=True)
reg("startdelay", G, "Programas de inicialização sem atraso", "Por padrão o Windows espera ~10 s para abrir os programas de inicialização. Isso remove a espera.",
    [T("HKCU", HK + r"\Explorer\Serialize", "StartupDelayInMSec", "d", 0, None), T("HKCU", HK + r"\Explorer\Serialize", "WaitforIdleState", "d", 0, None)],
    perf=2, ganho="área de trabalho pronta mais cedo após ligar", reboot=True)
reg("widgets", G, "Desativar Widgets e Chat", "Widgets roda processos WebView em segundo plano o tempo todo.",
    [T("HKCU", ADV, "TaskbarDa", "d", 0, 1), T("HKCU", ADV, "TaskbarMn", "d", 0, 1)], perf=2, ganho="menos RAM e CPU em segundo plano", exp=True, cond=mais_que(22000))
reg("noticias", G, "Desativar Notícias e Interesses", "Remove o widget de notícias e clima da barra, que consome rede e memória.",
    [T("HKCU", HK + r"\Feeds", "ShellFeedsTaskbarViewMode", "d", 2, 0)], perf=2, ganho="menos RAM e rede em segundo plano", exp=True, cond=mais_que(10240, 22000))
reg("copilot", G, "Desativar Copilot", "Remove o botão e o processo do Copilot.",
    [T("HKCU", ADV, "ShowCopilotButton", "d", 0, 1), T("HKCU", r"Software\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot", "d", 1, None)],
    perf=1, ganho="menos processos em segundo plano", exp=True, cond=mais_que(22000))

# Jogos
G = "Jogos e foco no desempenho"
reg("gamedvr", G, "Desativar Game DVR e captura em segundo plano", "A gravação de jogo em segundo plano do Xbox Game Bar custa FPS. Isso desliga a captura.",
    [T("HKCU", r"System\GameConfigStore", "GameDVR_Enabled", "d", 0, 1), T("HKCU", HK + r"\GameDVR", "AppCaptureEnabled", "d", 0, 1),
     T("HKCU", r"Software\Microsoft\GameBar", "UseNexusForGameBarEnabled", "d", 0, 1)], perf=2, ganho="mais FPS e menos uso de GPU em jogos")
reg("gamemode", G, "Modo de Jogo ligado", "Prioriza o jogo em primeiro plano e segura atualizações e drivers durante a partida.",
    [T("HKCU", r"Software\Microsoft\GameBar", "AllowAutoGameMode", "d", 1, None), T("HKCU", r"Software\Microsoft\GameBar", "AutoGameModeEnabled", "d", 1, None)],
    perf=1, ganho="jogo ganha prioridade sobre o resto")
reg("hags", G, "Agendamento de GPU acelerado por hardware", "A GPU gerencia a própria memória de vídeo, aliviando a CPU. Ajuda principalmente em GPUs recentes.",
    [T("HKLM", r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", "d", 2, None)], perf=1, ganho="menos carga na CPU em jogos", reboot=True, rec=False, risco="medio",
    aviso="Exige GPU e driver compatíveis. Reverta se notar travadas.", cond=mais_que(19041))
reg("mmcss", G, "Prioridade máxima para jogos", "Aumenta a prioridade de CPU e GPU para jogos no agendador multimídia do Windows.",
    [T("HKLM", SP + r"\Tasks\Games", "GPU Priority", "d", 8, 8), T("HKLM", SP + r"\Tasks\Games", "Priority", "d", 6, 2),
     T("HKLM", SP + r"\Tasks\Games", "Scheduling Category", "s", "High", "Medium"), T("HKLM", SP + r"\Tasks\Games", "SFIO Priority", "s", "High", "Normal")],
    perf=1, ganho="jogos recebem CPU primeiro")
reg("sysresp", G, "Sem reserva de CPU para multimídia e sem limite de rede", "Libera os 20% de CPU reservados ao multimídia em segundo plano e remove o limitador de rede.",
    [T("HKLM", SP, "SystemResponsiveness", "d", 0, 20), T("HKLM", SP, "NetworkThrottlingIndex", "d", 0xFFFFFFFF, 10)], perf=1, ganho="mais CPU para o programa em uso e rede sem limitador")
reg("prio", G, "Prioridade para o programa em primeiro plano", "Ajusta o agendador do Windows para dar fatias de CPU maiores ao programa que você está usando.",
    [T("HKLM", r"SYSTEM\CurrentControlSet\Control\PriorityControl", "Win32PrioritySeparation", "d", 38, 2)], perf=1, ganho="programa ativo responde melhor com PC ocupado")

# Rede
G = "Rede"


def alvos_nagle():
    base, out = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces", []
    for g in reg_subkeys("HKLM", base):
        ip = (reg_ler("HKLM", base + "\\" + g, "DhcpIPAddress") or reg_ler("HKLM", base + "\\" + g, "IPAddress") or (None,))[0]
        if ip and ip not in ("0.0.0.0", ["0.0.0.0"], [""]):
            out += [T("HKLM", base + "\\" + g, "TcpAckFrequency", "d", 1, None), T("HKLM", base + "\\" + g, "TCPNoDelay", "d", 1, None)]
    return out


reg("nagle", G, "Menos latência de rede (sem algoritmo de Nagle)", "Envia pacotes pequenos na hora em vez de agrupá-los. Reduz o ping em jogos online e chamadas.",
    alvos_nagle, perf=1, ganho="ping menor em jogos online", reboot=True, cond=lambda: (bool(alvos_nagle()), "" if alvos_nagle() else "Sem conexão ativa para ajustar"))
reg("dopt", G, "Sem compartilhar atualizações com outros PCs", "O Windows para de usar sua internet e disco para enviar atualizações a outros computadores.",
    [T("HKLM", POL + r"\DeliveryOptimization", "DODownloadMode", "d", 0, None)], perf=1, ganho="menos uso de internet e disco em segundo plano")

# Segundo plano e privacidade
G = "Segundo plano e privacidade"
reg("bgapps", G, "Bloquear apps em segundo plano", "Impede apps da Loja de rodarem, sincronizarem e atualizarem tiles quando não estão em uso.",
    [T("HKCU", HK + r"\BackgroundAccessApplications", "GlobalUserDisabled", "d", 1, 0), T("HKCU", HK + r"\Search", "BackgroundAppGlobalToggle", "d", 0, 1)],
    perf=2, ganho="menos RAM, CPU e bateria usados à toa", aviso="Apps de mensagem da Loja podem parar de notificar com o app fechado.")
CD = HK + r"\ContentDeliveryManager"
reg("dicas", G, "Sem sugestões, anúncios e instalação automática de apps", "Desliga anúncios no menu Iniciar e na tela de bloqueio e a instalação silenciosa de apps patrocinados.",
    [T("HKCU", CD, n, "d", 0, 1) for n in ("SubscribedContent-338388Enabled", "SubscribedContent-338389Enabled", "SubscribedContent-338387Enabled", "SubscribedContent-353694Enabled",
     "SubscribedContent-353696Enabled", "SubscribedContent-310093Enabled", "SystemPaneSuggestionsEnabled", "SoftLandingEnabled", "RotatingLockScreenEnabled",
     "OemPreInstalledAppsEnabled", "PreInstalledAppsEnabled", "SilentInstalledAppsEnabled", "ContentDeliveryAllowed", "FeatureManagementEnabled")]
    + [T("HKCU", ADV, "ShowSyncProviderNotifications", "d", 0, 1), T("HKCU", ADV, "Start_IrisRecommendations", "d", 0, 1)], perf=1, ganho="menos downloads e processos em segundo plano")
reg("bing", G, "Pesquisa do Iniciar só no PC (sem Bing)", "A busca do menu Iniciar deixa de consultar a web a cada letra digitada.",
    [T("HKCU", HK + r"\Search", "BingSearchEnabled", "d", 0, 1), T("HKCU", HK + r"\Search", "CortanaConsent", "d", 0, 1),
     T("HKCU", r"Software\Policies\Microsoft\Windows\Explorer", "DisableSearchBoxSuggestions", "d", 1, None)], perf=1, ganho="busca do Iniciar mais rápida", exp=True)
reg("telemetria", G, "Reduzir telemetria", "Reduz ao mínimo o envio de dados de diagnóstico à Microsoft.",
    [T("HKLM", POL + r"\DataCollection", "AllowTelemetry", "d", 0, None), T("HKLM", POL + r"\DataCollection", "DoNotShowFeedbackNotifications", "d", 1, None)],
    perf=1, ganho="menos coleta e envio em segundo plano")
reg("atividades", G, "Desativar histórico de atividades", "O Windows para de registrar e sincronizar o que você abre.",
    [T("HKLM", POL + r"\System", n, "d", 0, None) for n in ("EnableActivityFeed", "PublishUserActivities", "UploadUserActivities")], perf=0, ganho="menos gravação em segundo plano")

# Serviços e tarefas
G = "Serviços e tarefas"
svc("s_diag", G, "Desativar serviço de telemetria (DiagTrack)", "Serviço \"Experiências do Usuário Conectado e Telemetria\": uma das maiores fontes de uso de disco e rede em segundo plano.",
    ["DiagTrack", "dmwappushservice"], perf=1, ganho="menos disco, CPU e rede em segundo plano", auto=True)
svc("s_sysmain", G, "Desativar SysMain (Superfetch)", "Pré-carrega programas na RAM. Em SSD quase não ajuda e causa uso de disco e CPU.",
    ["SysMain"], perf=2, ganho="menos uso de disco e RAM ocupada", rec=lambda: I().get("ssd") and I().get("ram", 0) >= 4, risco="medio", aviso="Mantenha ativo se o Windows estiver em HDD.", auto=True)
svc("s_search", G, "Desativar indexador de pesquisa", "Para o Windows Search de indexar seus arquivos o tempo todo.",
    ["WSearch"], perf=1, ganho="menos disco e CPU em segundo plano", rec=False, risco="medio", aviso="A busca do Explorer e do Outlook fica mais lenta.", auto=True)
svc("s_maps", G, "Desativar mapas offline", "Serviço que baixa mapas em segundo plano, útil só se você usa o app Mapas.", ["MapsBroker"], perf=0, ganho="menos rede em segundo plano", auto=True)
svc("s_wer", G, "Desativar relatório de erros do Windows", "Para de coletar e enviar relatórios de travamento.", ["WerSvc"], perf=0, ganho="menos gravação de relatórios")
svc("s_xbox", G, "Desativar serviços Xbox", "Serviços de login, nuvem e acessórios Xbox. Só use se não joga Game Pass nem jogos da Microsoft Store.",
    ["XblAuthManager", "XblGameSave", "XboxNetApiSvc", "XboxGipSvc"], perf=1, ganho="menos processos em segundo plano", rec=False, risco="medio",
    aviso="Quebra o login e salvamento em nuvem de jogos Xbox/Game Pass.")
tw("t_telem", G, "Desativar tarefas agendadas de telemetria", "Desliga as tarefas que coletam dados de compatibilidade e experiência e que acordam o disco.",
   lambda: (lambda s: bool(s) and all(v == "Disabled" for v in s.values()))(tarefas_estado()), tarefas_ap, tarefas_rv, perf=1, ganho="menos picos de disco e CPU", adm=True,
   cond=lambda: (bool(tarefas_estado()), "" if tarefas_estado() else "Tarefas não existem neste Windows"))

# Disco e memória
G = "Disco e memória"
reg("lastacc", G, "Parar de gravar a data de último acesso", "O NTFS grava uma data a cada arquivo lido. Desligar reduz escrita no disco.",
    [T("HKLM", r"SYSTEM\CurrentControlSet\Control\FileSystem", "NtfsDisableLastAccessUpdate", "d", 1, 0x80000002, bit=True)], perf=1, ganho="menos escritas, bom para SSD e HDD", reboot=True)
reg("n8dot3", G, "Desativar nomes de arquivo 8.3", "Para de criar o nome curto antigo (ARQUIV~1) para cada arquivo novo.",
    [T("HKLM", r"SYSTEM\CurrentControlSet\Control\FileSystem", "NtfsDisable8dot3NameCreation", "d", 1, 2)], perf=1, ganho="criação de arquivos mais rápida em pastas grandes", reboot=True,
    rec=False, aviso="Programas muito antigos (16 bits) podem precisar dos nomes curtos.")
reg("pagexec", G, "Manter o núcleo do Windows na RAM", "Impede o kernel e os drivers de irem para o arquivo de paginação. Mais respostas rápidas.",
    [T("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "DisablePagingExecutive", "d", 1, 0)], perf=1, ganho="sistema responde melhor sob carga", reboot=True,
    cond=lambda: (I().get("ram", 0) >= 8, "" if I().get("ram", 0) >= 8 else "Requer 8 GB ou mais de RAM"))

# ===== Periféricos: mouse, teclado, monitor e input lag (aba própria) =====
_n0 = len(TW)


class _DM(ctypes.Structure):
    _fields_ = [("dmDeviceName", ctypes.c_wchar * 32), ("dmSpecVersion", wt.WORD), ("dmDriverVersion", wt.WORD), ("dmSize", wt.WORD),
                ("dmDriverExtra", wt.WORD), ("dmFields", wt.DWORD), ("dmPositionX", ctypes.c_long), ("dmPositionY", ctypes.c_long),
                ("dmDisplayOrientation", wt.DWORD), ("dmDisplayFixedOutput", wt.DWORD), ("dmColor", ctypes.c_short), ("dmDuplex", ctypes.c_short),
                ("dmYResolution", ctypes.c_short), ("dmTTOption", ctypes.c_short), ("dmCollate", ctypes.c_short), ("dmFormName", ctypes.c_wchar * 32),
                ("dmLogPixels", wt.WORD), ("dmBitsPerPel", wt.DWORD), ("dmPelsWidth", wt.DWORD), ("dmPelsHeight", wt.DWORD), ("dmDisplayFlags", wt.DWORD),
                ("dmDisplayFrequency", wt.DWORD), ("dmICMMethod", wt.DWORD), ("dmICMIntent", wt.DWORD), ("dmMediaType", wt.DWORD), ("dmDitherType", wt.DWORD),
                ("dmReserved1", wt.DWORD), ("dmReserved2", wt.DWORD), ("dmPanningWidth", wt.DWORD), ("dmPanningHeight", wt.DWORD)]


def tela_atual():
    d = _DM()
    d.dmSize = ctypes.sizeof(d)
    ctypes.windll.user32.EnumDisplaySettingsW(None, ctypes.c_uint(0xFFFFFFFF), ctypes.byref(d))  # ENUM_CURRENT_SETTINGS
    return d


def tela_hz():
    # (taxa atual, maior taxa que o monitor aceita na resolução e profundidade atuais); só o monitor principal
    cur = tela_atual()
    mx, i = cur.dmDisplayFrequency, 0
    while i < 4000:
        d = _DM()
        d.dmSize = ctypes.sizeof(d)
        if not ctypes.windll.user32.EnumDisplaySettingsW(None, ctypes.c_uint(i), ctypes.byref(d)):
            break
        if ((d.dmPelsWidth, d.dmPelsHeight, d.dmBitsPerPel, d.dmDisplayOrientation) == (cur.dmPelsWidth, cur.dmPelsHeight, cur.dmBitsPerPel, cur.dmDisplayOrientation)
                and not d.dmDisplayFlags & 2):  # ignora modos entrelaçados
            mx = max(mx, d.dmDisplayFrequency)
        i += 1
    return cur.dmDisplayFrequency, mx


def tela_set(hz):
    d = tela_atual()
    d.dmDisplayFrequency = hz
    d.dmFields |= 0x400000  # DM_DISPLAYFREQUENCY
    u = ctypes.windll.user32
    if u.ChangeDisplaySettingsExW(None, ctypes.byref(d), None, 2, None) != 0:  # CDS_TEST
        return False
    return u.ChangeDisplaySettingsExW(None, ctypes.byref(d), None, 1, None) == 0  # CDS_UPDATEREGISTRY


def _hz_info():
    try:
        a, m = tela_hz()
        d = tela_atual()
        return dict(atual=a, max=m, w=d.dmPelsWidth, h=d.dmPelsHeight)
    except Exception:
        return {}


def hz_ler():
    a, m = tela_hz()
    return m > 0 and a >= m


def hz_ap():
    atual, mx = tela_hz()
    b = BK.setdefault("hz", {})
    if "orig" not in b:
        b["orig"] = atual
    if not tela_set(mx):
        raise RuntimeError("monitor recusou")
    bk_salvar()


def hz_rv():
    o = BK.get("hz", {}).get("orig")
    if o:
        tela_set(o)
    BK.pop("hz", None)
    bk_salvar()


def atualizar_entrada():
    # aplica na hora mouse e teclado, sem precisar sair do Windows
    u = ctypes.windll.user32
    MS_, KB_ = r"Control Panel\Mouse", r"Control Panel\Keyboard"

    def rd(p, n, d):
        try:
            return int(str((reg_ler("HKCU", p, n) or (d,))[0]).strip())
        except (ValueError, TypeError):
            return d
    try:
        m = (ctypes.c_int * 3)(rd(MS_, "MouseThreshold1", 6), rd(MS_, "MouseThreshold2", 10), rd(MS_, "MouseSpeed", 1))
        u.SystemParametersInfoW(0x0004, 0, m, 2)  # SPI_SETMOUSE
        u.SystemParametersInfoW(0x0071, 0, ctypes.c_void_p(rd(MS_, "MouseSensitivity", 10)), 2)  # SPI_SETMOUSESPEED
        u.SystemParametersInfoW(0x0066, rd(MS_, "MouseHoverTime", 400), None, 2)  # SPI_SETMOUSEHOVERTIME
        u.SystemParametersInfoW(0x0017, rd(KB_, "KeyboardDelay", 1), None, 2)  # SPI_SETKEYBOARDDELAY
        u.SystemParametersInfoW(0x000B, rd(KB_, "KeyboardSpeed", 31), None, 2)  # SPI_SETKEYBOARDSPEED
    except Exception:
        pass


# USB/HID: "permitir que o computador desligue este dispositivo para economizar energia"
PNP = r"Get-CimInstance -Namespace root/wmi -ClassName MSPower_DeviceEnable -EA SilentlyContinue|?{$_.InstanceName -match '^(USB|HID)\\'}"


def pnp_ler():
    r = ps(PNP + "|%{if($_.Enable){'1'}else{'0'}}", 45).split()
    return bool(r) and all(x == "0" for x in r)


def pnp_ap():
    b = BK.setdefault("pnp", {})
    if "on" not in b:
        b["on"] = [x.strip() for x in ps(PNP + "|?{$_.Enable}|%{$_.InstanceName}", 45).splitlines() if x.strip()]
    ps(PNP + "|%{$_.Enable=$false;Set-CimInstance -InputObject $_ -EA SilentlyContinue}", 90)
    bk_salvar()


def pnp_rv():
    nomes = ",".join("'" + x.replace("'", "''") + "'" for x in BK.get("pnp", {}).get("on", []))
    if nomes:
        ps("$on=@(" + nomes + ");" + PNP + "|?{$on -contains $_.InstanceName}|%{$_.Enable=$true;Set-CimInstance -InputObject $_ -EA SilentlyContinue}", 90)
    BK.pop("pnp", None)
    bk_salvar()


# ----- Mouse -----
G = "Mouse"
MS = r"Control Panel\Mouse"
reg("m_accel", G, "Desativar a aceleração do ponteiro", "Desliga o \"Aprimorar precisão do ponteiro\": o cursor anda sempre na mesma proporção do movimento da mão (1:1) e a velocidade fica em 6/11. Deixa a mira previsível e a memória muscular consistente.",
    [T("HKCU", MS, "MouseSpeed", "s", "0", "1"), T("HKCU", MS, "MouseThreshold1", "s", "0", "6"), T("HKCU", MS, "MouseThreshold2", "s", "0", "10"),
     T("HKCU", MS, "MouseSensitivity", "s", "10", "10")], perf=3, ganho="mira e cursor 1:1, sem aceleração")
reg("m_hover", G, "Dicas e miniaturas aparecem mais rápido", "Reduz o tempo que o mouse precisa ficar parado sobre um item para mostrar dicas e pré-visualizações (de 400 ms para 100 ms).",
    [T("HKCU", MS, "MouseHoverTime", "s", "100", "400")], perf=0, ganho="interface com resposta mais imediata")
reg("m_shake", G, "Desativar Aero Shake", "Evita que sacudir uma janela com o mouse minimize todas as outras sem querer.",
    [T("HKCU", ADV, "DisallowShaking", "d", 1, None)], perf=0, ganho="menos janelas minimizadas por acidente", rec=False, exp=True)
reg("m_snap", G, "Desativar encaixe automático de janelas (Snap)", "Arrastar uma janela até a borda deixa de redimensioná-la sozinha.",
    [T("HKCU", r"Control Panel\Desktop", "WindowArrangementActive", "s", "0", "1")], perf=0, ganho="arrastar janelas sem surpresas", rec=False, reboot=True,
    aviso="Desliga também Win+setas e o encaixe em colunas.")

# ----- Teclado -----
G = "Teclado"
KB = r"Control Panel\Keyboard"
AC = r"Control Panel\Accessibility"
reg("k_rep", G, "Repetição de teclas mais rápida", "Remove a pausa antes de a tecla começar a repetir e usa a taxa de repetição máxima. Útil em jogos, edição de texto e navegação em listas.",
    [T("HKCU", KB, "KeyboardDelay", "s", "0", "1"), T("HKCU", KB, "KeyboardSpeed", "s", "31", "31")], perf=2, ganho="teclado responde sem espera inicial")
reg("k_filtro", G, "Sem janelas de Teclas de Aderência, Filtro e Alternância", "Desliga os atalhos que abrem esses avisos ao apertar Shift cinco vezes ou segurar Shift. Evita que o jogo perca o foco no meio da partida.",
    [T("HKCU", AC + r"\StickyKeys", "Flags", "s", "506", "510"), T("HKCU", AC + r"\Keyboard Response", "Flags", "s", "122", "126"),
     T("HKCU", AC + r"\ToggleKeys", "Flags", "s", "58", "62")], perf=1, ganho="jogo não perde o foco com Shift repetido", reboot=True)
reg("k_idioma", G, "Desativar troca de idioma por atalho", "Desliga Alt+Shift e Ctrl+Shift para trocar o idioma do teclado, que costumam ser acionados sem querer em jogos.",
    [T("HKCU", r"Keyboard Layout\Toggle", "Hotkey", "s", "3", "1"), T("HKCU", r"Keyboard Layout\Toggle", "Language Hotkey", "s", "3", "1"),
     T("HKCU", r"Keyboard Layout\Toggle", "Layout Hotkey", "s", "3", "2")], perf=0, ganho="sem troca de layout acidental", reboot=True,
    aviso="Se você usa dois idiomas de teclado, troque pela barra de idioma ou por Win+Espaço.")
reg("k_num", G, "Num Lock ligado ao entrar", "O teclado numérico já começa ativo depois do login.",
    [T("HKCU", KB, "InitialKeyboardIndicators", "s", "2", "0")], perf=0, ganho="conveniência", rec=False, reboot=True)
reg("k_win", G, "Desativar atalhos com a tecla Windows", "Desliga combinações como Win+E e Win+D. A tecla sozinha continua abrindo o menu Iniciar.",
    [T("HKCU", HK + r"\Policies\Explorer", "NoWinKeys", "d", 1, None)], perf=0, ganho="sem atalhos acidentais durante jogos", rec=False, exp=True,
    aviso="Você perde todos os atalhos Win+letra enquanto estiver ativo.")

# ----- Monitor e tela -----
G = "Monitor e tela"
tw("hz", G, "Taxa de atualização máxima do monitor", "Muitos monitores de 120, 144 ou 240 Hz ficam presos em 60 Hz depois de instalar driver ou trocar cabo. Isto coloca na maior taxa aceita na resolução atual (monitor principal).",
   hz_ler, hz_ap, hz_rv, perf=3, ganho="imagem mais fluida e menos input lag", cond=lambda: (tela_hz()[1] > 0, "" if tela_hz()[1] > 0 else "Não foi possível ler o monitor"),
   aviso="A tela pisca por um instante ao trocar.")
reg("d_fso", G, "Tela cheia exclusiva (sem otimizações de tela cheia)", "Faz os jogos usarem tela cheia de verdade em vez de janela sem borda disfarçada. Pode reduzir a latência de entrada em alguns jogos.",
    [T("HKCU", r"System\GameConfigStore", "GameDVR_FSEBehaviorMode", "d", 2, 0), T("HKCU", r"System\GameConfigStore", "GameDVR_HonorUserFSEBehaviorMode", "d", 1, 0),
     T("HKCU", r"System\GameConfigStore", "GameDVR_FSEBehavior", "d", 2, 0), T("HKCU", r"System\GameConfigStore", "GameDVR_DXGIHonorFSEWindowsCompatible", "d", 1, 0)],
    perf=2, ganho="menos latência de entrada em jogos")
reg("d_flip", G, "Otimizações para jogos em janela", "Faz jogos em janela e sem borda usarem o modo de apresentação mais eficiente do Windows e a taxa variável (G-Sync/FreeSync).",
    [T("HKCU", r"Software\Microsoft\DirectX\UserGpuPreferences", "DirectXUserGlobalSettings", "s", "SwapEffectUpgradeEnable=1;VRROptimizeEnable=1;", None)],
    perf=2, ganho="jogos em janela com menos latência", cond=mais_que(19041))
reg("d_mpo", G, "Desativar sobreposição multiplano (MPO)", "Corrige piscadas, tremidas e tela preta em alguns monitores com drivers NVIDIA e AMD. Use só se tiver esses sintomas.",
    [T("HKLM", r"SOFTWARE\Microsoft\Windows\Dwm", "OverlayTestMode", "d", 5, None)], perf=1, ganho="corrige piscadas e travadas de imagem", rec=False, risco="medio", reboot=True,
    aviso="Pode aumentar um pouco o uso de GPU na área de trabalho.")
reg("d_dpi", G, "Corrigir aplicativos borrados em telas com escala", "Pede ao Windows que reescale cada aplicativo na escala do monitor em que ele está, em vez de esticar a imagem e borrar.",
    [T("HKCU", r"Control Panel\Desktop", "EnablePerProcessSystemDPI", "d", 1, None)], perf=0, ganho="texto nítido em programas antigos", rec=False, reboot=True, cond=mais_que(18362))
reg("d_saver", G, "Desativar protetor de tela", "O protetor de tela deixa de entrar durante vídeos, apresentações e jogos parados.",
    [T("HKCU", r"Control Panel\Desktop", "ScreenSaveActive", "s", "0", "1")], perf=0, ganho="tela não é interrompida", rec=False)
pw("d_tela", G, "Nunca apagar a tela (na tomada)", "A tela não apaga sozinha enquanto o PC está ligado na energia.",
   "SUB_VIDEO", "VIDEOIDLE", 0, 600, perf=0, ganho="tela não apaga em filmes e jogos parados", rec=False, aviso="Em tela OLED pode causar marcas com imagem parada.")

# ----- Input lag e latência -----
G = "Input lag e latência"
reg("l_timer", G, "Relógio do sistema mais preciso", "Faz o Windows respeitar o pedido de timer de 0,5 ms que jogos e programas de áudio fazem, melhorando o ritmo dos quadros.",
    [T("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "GlobalTimerResolutionRequests", "d", 1, None)], perf=1, ganho="frametimes mais estáveis", reboot=True, cond=mais_que(22000),
    aviso="Aumenta um pouco o consumo de energia em ociosidade.")
pw("l_park", G, "Núcleos do processador sempre ativos (sem Core Parking)", "Impede o Windows de \"estacionar\" núcleos ociosos. Cada núcleo estacionado leva tempo para acordar quando o jogo pede.",
   "SUB_PROCESSOR", "CPMINCORES", 100, 10, perf=2, ganho="menos engasgos quando a carga sobe de repente", rec=lambda: not I().get("notebook"), aviso="Aumenta o consumo de energia.")
reg("l_throt", G, "Sem limitação de energia para processos", "Desliga o Power Throttling, que reduz o clock de processos que o Windows julga serem de segundo plano. Jogos e ferramentas em janela minimizada rendem mais.",
    [T("HKLM", r"SYSTEM\CurrentControlSet\Control\Power\PowerThrottling", "PowerThrottlingOff", "d", 1, None)], perf=1, ganho="processos mantêm o clock mesmo sem foco",
    rec=lambda: not I().get("notebook"), cond=mais_que(16299), aviso="Em notebook reduz a duração da bateria.")
reg("l_fast", G, "Desligamento completo (sem inicialização rápida)", "Faz o Windows desligar de verdade em vez de hibernar o núcleo. Resolve mouse, teclado e headset que não reconhecem depois de ligar.",
    [T("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Power", "HiberbootEnabled", "d", 0, 1)], perf=1, ganho="periféricos reiniciam limpos a cada boot", rec=False, reboot=True,
    aviso="O boot fica alguns segundos mais lento em HDD.")
reg("l_vbs", G, "Desativar Integridade de memória (VBS/HVCI)", "A proteção por virtualização do núcleo pode custar de 5% a 10% de desempenho em jogos, principalmente em processadores mais antigos.",
    [T("HKLM", r"SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity", "Enabled", "d", 0, None)], perf=2, ganho="mais FPS em alguns jogos",
    risco="alto", rec=False, reboot=True, cond=mais_que(19041), aviso="Reduz a proteção contra malware no nível do núcleo. Só desative se souber o que está fazendo.")

# ----- Energia dos periféricos -----
G = "Energia dos periféricos"
pw("e_usb", G, "Desativar suspensão seletiva de USB", "O Windows deixa de \"adormecer\" portas USB ociosas. Evita o primeiro movimento do mouse ou toque do teclado demorar ou se perder.",
   "2a737441-1930-4402-8d77-b2bebba308a3", "48e6b7a6-50f5-4782-a5d4-53bb8f07e226", 0, 1, perf=2, ganho="mouse e teclado acordam na hora", rec=lambda: not I().get("notebook"),
   aviso="Pequeno aumento de consumo em notebook.")
tw("e_pnp", G, "Impedir o Windows de desligar USB e HID para poupar energia", "Desmarca, em cada mouse, teclado, hub e controle, a opção \"permitir que o computador desligue este dispositivo\".",
   pnp_ler, pnp_ap, pnp_rv, perf=2, ganho="periféricos nunca \"dormem\"", adm=True, rec=lambda: not I().get("notebook"),
   cond=lambda: (bool(ps(PNP + "|select -First 1 -Expand InstanceName", 45)), "" if ps(PNP + "|select -First 1 -Expand InstanceName", 45) else "Nenhum dispositivo compatível"))

for _t in TW[_n0:]:
    _t["aba"] = "per"

# ----- programas que iniciam com o Windows (descobertos no PC) -----
RUNS = [("HKCU", HK + r"\Run", "Run"), ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "Run"), ("HKLM", r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run", "Run32")]
SAP = HK + r"\Explorer\StartupApproved"
SEG = re.compile(r"defender|security|antiv|avast|kaspersky|norton|mcafee|bitdefender|eset|realtek|nvidia|amd|intel|synaptics|touchpad|audio|bluetooth|driver", re.I)
BLOAT = re.compile(r"spotify|discord|teams|skype|zoom|steam|epic|adobe|onedrive|dropbox|googledrive|itunes|ccx|acrotray|java|launcher|overwolf|razer|corsair|logi|cloud", re.I)


def habilitado(h, sub, nome):
    b = reg_ler(h, SAP + "\\" + sub, nome)
    return not (b and isinstance(b[0], bytes) and b[0] and b[0][0] & 1)


def apps_inicio():
    itens = []
    for h, p, sub in RUNS:
        for n, v, _ in reg_valores(h, p):
            itens.append((h, sub, n, str(v)))
    c = caminhos()
    for h, d in (("HKCU", os.path.join(c["rad"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")), ("HKLM", os.path.join(c["pd"], "Microsoft", "Windows", "Start Menu", "Programs", "StartUp"))):
        try:
            for f in os.listdir(d):
                if f.lower() != "desktop.ini":
                    itens.append((h, "StartupFolder", f, os.path.join(d, f)))
        except OSError:
            pass
    out = []
    for h, sub, n, cm in itens:
        seg = bool(SEG.search(n + " " + cm))
        out.append(dict(id="su:" + hashlib.md5(f"{h}|{sub}|{n}".encode()).hexdigest()[:10], grupo="Programas que iniciam com o Windows",
                        nome="Não iniciar: " + (os.path.splitext(n)[0] if sub == "StartupFolder" else n), info=cm[:110] + ("…" if len(cm) > 110 else ""),
                        ler=lambda h=h, sub=sub, n=n: not habilitado(h, sub, n),
                        apply=lambda h=h, sub=sub, n=n: reg_esc(h, SAP + "\\" + sub, n, "b", b"\x03" + b"\x00" * 11),
                        revert=lambda h=h, sub=sub, n=n: reg_esc(h, SAP + "\\" + sub, n, "b", b"\x02" + b"\x00" * 11),
                        perf=1, ganho="Windows liga mais rápido", risco="medio" if seg else "baixo", adm=h == "HKLM", rec=bool(BLOAT.search(n + " " + cm)) and not seg,
                        aviso="Parece ser driver ou segurança. Mantenha ativo se não tiver certeza." if seg else "", reboot=False, exp=False, cond=None))
    return out


# ----- orquestração -----
def analisar():
    with L["lock"]:
        if W["estado"] == "ler" or W["apl"]["estado"] == "exe":
            return False
        W.update(estado="ler", i=0, n=len(TW))

    def run():
        W["info"] = coletar_info()
        DYN[:] = apps_inicio()
        todos = TW + DYN
        W["n"] = len(todos)
        for i, t in enumerate(todos):
            W["i"] = i
            try:
                ok, obs = t["cond"]() if t["cond"] else (True, "")
                ativo = bool(t["ler"]()) if ok else False
            except Exception as e:
                ok, obs, ativo = False, "Erro: " + type(e).__name__, False
            W["dados"][t["id"]] = dict(ok=ok, obs=obs, ativo=ativo)
        W["estado"] = "ok"

    threading.Thread(target=run, daemon=True).start()
    return True


def aplicar(mud):
    todos = {t["id"]: t for t in TW + DYN}
    with L["lock"]:
        fila = [(todos[i], bool(v)) for i, v in mud.items() if i in todos and W["dados"].get(i, {}).get("ok")
                and (not todos[i]["adm"] or ADMIN) and bool(W["dados"][i]["ativo"]) != bool(v)]
        if not fila or W["estado"] == "ler" or W["apl"]["estado"] == "exe":
            return False
        W["apl"].update(estado="exe", i=0, n=len(fila), atual="", res={}, ponto="", reboot=False)

    def run():
        a = W["apl"]
        if ADMIN:
            a["atual"] = "ponto"
            a["ponto"] = "criado" if "OK" in ps("try{Checkpoint-Computer -Description 'Tellez - antes das otimizações' -RestorePointType MODIFY_SETTINGS -EA Stop;'OK'}catch{'NO'}", 120) else "não criado"
        exp = False
        for i, (t, want) in enumerate(fila):
            a.update(i=i, atual=t["id"])
            try:
                (t["apply"] if want else t["revert"])()
                ativo = bool(t["ler"]())
                ok = ativo == want
                obs = "" if ok else "O Windows bloqueou a alteração"
            except Exception as e:
                ok, ativo, obs = False, W["dados"][t["id"]]["ativo"], "Não foi possível: " + type(e).__name__
            W["dados"][t["id"]]["ativo"] = ativo
            a["res"][t["id"]] = dict(ok=ok, obs=obs)
            if ok:
                _ap = set(BK.get("_aplicados", []))
                _ap.add(t["id"]) if want else _ap.discard(t["id"])
                BK["_aplicados"] = sorted(_ap)
                bk_salvar()
            exp = exp or (ok and t["exp"])
            a["reboot"] = a["reboot"] or (ok and t["reboot"])
        if any(t.get("aba") == "per" and a["res"].get(t["id"], {}).get("ok") for t, _ in fila):
            atualizar_entrada()
        if exp:
            a["atual"] = "explorer"
            reiniciar_explorer()
        a.update(estado="ok", i=len(fila), atual="")

    threading.Thread(target=run, daemon=True).start()
    return True


def estado_w(aba="win"):
    info, lst = W["info"], []
    for t in TW + DYN:
        if t.get("aba", "win") != aba:
            continue
        d = W["dados"].get(t["id"])
        bloq = t["adm"] and not ADMIN
        rec = t["rec"]() if callable(t["rec"]) else t["rec"]
        lst.append(dict(id=t["id"], grupo=t["grupo"], nome=t["nome"], info=t["info"], perf=t["perf"], ganho=t["ganho"], risco=t["risco"], adm=t["adm"], reboot=t["reboot"],
                        exp=t["exp"], aviso=t["aviso"], rec=bool(rec), ok=bool(d and d["ok"]), obs=d["obs"] if d else "", ativo=bool(d and d["ativo"]), bloq=bloq,
                        pode=bool(d and d["ok"] and not bloq)))
    return dict(admin=ADMIN, info=info, estado=W["estado"], i=W["i"], n=W["n"], tweaks=lst, apl=dict(W["apl"]))



def abrir_pasta_dados():
    try:
        os.startfile(str(bk_arq().parent))
        return True
    except Exception:
        return False


def reverter_tudo():
    # desfaz o que o Tellez aplicou (lista em backup_ajustes.json), usando os valores originais salvos
    if W["estado"] == "ler" or W["apl"]["estado"] == "exe":
        return {"ok": False, "motivo": "ocupado"}
    if not DYN:
        DYN[:] = apps_inicio()
    todos = {t["id"]: t for t in TW + DYN}
    ok = falhas = adm = 0
    per = False
    for i in list(BK.get("_aplicados", [])):
        t = todos.get(i)
        if not t:
            continue
        if t["adm"] and not ADMIN:
            adm += 1
            continue
        try:
            t["revert"]()
            ok += 1
            per = per or t.get("aba") == "per"
            ap = set(BK.get("_aplicados", []))
            ap.discard(i)
            BK["_aplicados"] = sorted(ap)
        except Exception:
            falhas += 1
    bk_salvar()
    if per:
        atualizar_entrada()
    return {"ok": True, "revertidos": ok, "falhas": falhas, "admin": adm}


class Handler(BaseHTTPRequestHandler):
    def _enviar(s, corpo, tipo):
        s.send_response(200)
        s.send_header("Content-Type", tipo)
        s.send_header("Content-Length", str(len(corpo)))
        s.send_header("Cache-Control", "no-store")
        s.end_headers()
        s.wfile.write(corpo)

    def do_POST(s):
        u = urlparse(s.path)
        q = parse_qs(u.query)
        if not REAL or s.headers.get("X-Token") != TOKEN:
            return s.send_error(403)
        n = int(s.headers.get("Content-Length") or 0)
        try:
            corpo = json.loads(s.rfile.read(n) or b"{}") if n else {}
        except Exception:
            corpo = {}
        try:
            if u.path == "/api/otimizar":
                f = {"memoria": liberar_memoria, "temp": limpar_temp}.get(q.get("etapa", [""])[0])
                if not f:
                    return s.send_error(403)
                r = f()
            elif u.path == "/api/limpeza/escanear":
                r = {"ok": escanear()}
            elif u.path == "/api/limpeza/limpar":
                r = {"ok": limpar(set(corpo.get("ids", [])))}
            elif u.path == "/api/windows/analisar":
                r = {"ok": analisar()}
            elif u.path == "/api/windows/aplicar":
                r = {"ok": aplicar(corpo.get("mudancas", {}))}
            elif u.path == "/api/cfg/pasta":
                r = {"ok": abrir_pasta_dados()}
            elif u.path == "/api/cfg/reverter":
                r = reverter_tudo()
            elif u.path == "/api/admin/elevar":
                r = elevar()
            else:
                return s.send_error(404)
        except Exception as e:
            r = {"erro": str(e)}
        s._enviar(json.dumps(r).encode(), "application/json")

    def do_GET(s):
        global _ultimo
        if s.path.startswith("/api/dados"):
            _ultimo = time.time()
            if not REAL:
                return s.send_error(404)
            corpo, tipo = json.dumps(DADOS).encode(), "application/json"
        elif s.path.startswith("/api/perifericos/estado"):
            if not REAL:
                return s.send_error(404)
            corpo, tipo = json.dumps(estado_w("per")).encode(), "application/json"
        elif s.path.startswith("/api/windows/estado"):
            if not REAL:
                return s.send_error(404)
            corpo, tipo = json.dumps(estado_w()).encode(), "application/json"
        elif s.path.startswith("/api/limpeza/estado"):
            if not REAL:
                return s.send_error(404)
            corpo, tipo = json.dumps(estado()).encode(), "application/json"
        elif s.path in ("/", "/index.html"):
            corpo, tipo = HTML.replace("__TOKEN__", TOKEN).encode("utf-8"), "text/html; charset=utf-8"
        else:
            return s.send_error(404)
        s._enviar(corpo, tipo)

    def log_message(s, *a):
        pass


def iniciar_servidor():
    for porta in (8765, 0):  # porta fixa mantém tema salvo
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", porta), Handler)
            break
        except OSError:
            continue
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    for f in (amostrar, carregar_nomes, amostrar_temp):
        threading.Thread(target=f, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/"


# ---------- janela ----------
def tamanho_janela():
    w, h = 1920, 1080
    try:
        u = ctypes.windll.user32
        w, h = u.GetSystemMetrics(0) or w, u.GetSystemMetrics(1) or h
    except Exception:
        pass
    lw, lh = round(w * FRACAO_LARGURA), round(h * FRACAO_ALTURA)
    return lw, lh, (w - lw) // 2, (h - lh) // 2


def _bases():
    return [b for b in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), os.environ.get("LocalAppData")) if b]


def abrir_modo_aplicativo(url: str, pasta: Path) -> bool:
    exe = next((str(p) for b in _bases() for p in (
        Path(b) / "Microsoft/Edge/Application/msedge.exe", Path(b) / "Google/Chrome/Application/chrome.exe") if p.exists()),
        None) or shutil.which("msedge") or shutil.which("chrome")
    if not exe:
        return False
    w, h, x, y = tamanho_janela()
    try:
        subprocess.Popen([exe, f"--app={url}", f"--window-size={w},{h}", f"--window-position={x},{y}",
                          f"--user-data-dir={pasta / 'perfil_navegador'}", "--no-first-run", "--no-default-browser-check"])
        return True
    except Exception as e:
        print(f"Não foi possível abrir em modo aplicativo: {e}")
        return False


class Api:
    def minimizar(self):
        _janela and _janela.minimize()

    def fechar(self):
        _janela and _janela.destroy()

    def topo(self, v):
        try:
            _janela.on_top = bool(v)
        except Exception:
            pass


def abrir_com_pywebview(url: str, pasta: Path) -> bool:
    global _janela
    try:
        w, h, _, _ = tamanho_janela()
        _janela = webview.create_window("Tellez", url=url, width=w, height=h, frameless=True,
                                        easy_drag=False, resizable=False, background_color="#0c0c0c", text_select=False, js_api=Api())
        webview.start(gui="edgechromium", private_mode=False, storage_path=str(pasta / "dados"))
        return True
    except Exception as e:
        print(f"\nWebView2 indisponível: {type(e).__name__}: {e}")
        return False


def webview2_instalado() -> bool:
    try:
        import winreg
        g = r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
        for raiz, c in ((winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node" + g[8:]), (winreg.HKEY_LOCAL_MACHINE, g), (winreg.HKEY_CURRENT_USER, g)):
            try:
                with winreg.OpenKey(raiz, c) as k:
                    v, _ = winreg.QueryValueEx(k, "pv")
                    if v and v != "0.0.0.0":
                        return True
            except OSError:
                pass
    except Exception:
        pass
    return any((Path(b) / "Microsoft/EdgeWebView/Application").exists() for b in _bases())


def instalar_webview2() -> bool:
    print("\nA janela sem borda precisa do 'WebView2 Runtime' da Microsoft (gratuito, instalação rápida).")
    try:
        if input("Baixar e instalar agora? [S/n] ").strip().lower() in ("n", "nao", "não"):
            return False
        import urllib.request
        inst = Path(tempfile.gettempdir()) / "MicrosoftEdgeWebview2Setup.exe"
        print("Baixando...")
        urllib.request.urlretrieve("https://go.microsoft.com/fwlink/p/?LinkId=2124703", inst)
        print("Instalando (se o Windows pedir permissão, clique em Sim)...")
        subprocess.run([str(inst), "/silent", "/install"], check=False)
    except EOFError:
        return False
    except Exception as e:
        print(f"Não foi possível instalar o WebView2: {type(e).__name__}: {e}")
        return False
    return webview2_instalado()


def esperar_janela():
    """No modo navegador o servidor precisa continuar vivo; encerra quando a página para de consultar."""
    global _ultimo
    _ultimo = time.time()
    try:
        while time.time() - _ultimo < 90:
            time.sleep(2)
    except KeyboardInterrupt:
        pass


def main():
    pasta = Path(tempfile.gettempdir()) / "painel_otimizacao"
    pasta.mkdir(exist_ok=True)
    url = iniciar_servidor()
    if webview is None:
        print("pywebview não está instalado. Para a janela sem borda: python -m pip install pywebview")
    elif (webview2_instalado() or instalar_webview2()) and abrir_com_pywebview(url, pasta):
        return
    print("Usando o Edge/Chrome em modo aplicativo...")
    if not abrir_modo_aplicativo(url, pasta):
        print("Abrindo no navegador padrão...")
        webbrowser.open(url)
    esperar_janela()


if __name__ == "__main__":
    main()
