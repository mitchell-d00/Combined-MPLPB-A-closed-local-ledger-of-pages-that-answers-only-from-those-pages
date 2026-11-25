#!/usr/bin/env node
// Optional browser-agent CLI. No answer-generation layer: always return MPLPB data.
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

function usage() {
 return 'Usage: node tools/mplpb_agent_bridge.mjs <GitHub-repo-or-PR-or-live-site-URL> (--handshake | --betty | --al | --question TEXT | --chat TEXT | --pages | --read PAGE) [--corpus KEY] [--session ID] [--profile-dir PATH] [--suggest] [--allow-network] [--auto-wiki]';
}
function siteFrom(url) {
 const u = new URL(url);
 if (u.protocol !== 'https:' || u.username || u.password) throw Error('Use a public HTTPS URL');
 if (u.hostname === 'github.com') {
  const parts = u.pathname.split('/').filter(Boolean);
  if (parts.length < 2) throw Error('GitHub repository URL requires owner and repository');
  return 'https://' + parts[0] + '.github.io/' + parts[1] + '/';
 }
 return u.origin + u.pathname.replace(/\/?$/, '/');
}
function argsOf(argv) {
 if (argv.includes('--help') || argv.length === 0) return {help:true};
 const opts={url:argv[0]};
 const allowed = new Set(['handshake','betty','al','question','chat','pages','read','corpus','session','profile-dir','suggest','allow-network','auto-wiki']);
 for (let i=1;i<argv.length;i++) {
  const key=argv[i].replace(/^--/,'');
  if (!argv[i].startsWith('--') || !allowed.has(key)) throw Error('Unknown argument '+argv[i]);
  if (['handshake','betty','al','pages','suggest','allow-network','auto-wiki'].includes(key)) opts[key]=true;
  else {if (i+1>=argv.length || argv[i+1].startsWith('--')) throw Error('Missing value for --'+key);opts[key]=argv[++i];}
 }
 const modes=['handshake','betty','al','question','chat','pages','read'].filter(k=>opts[k]!==undefined);
 if (modes.length!==1) throw Error('Choose exactly one mode: '+modes.join(', '));
 if (!['handshake','betty','al'].includes(modes[0]) && !opts.corpus) throw Error('Live calls require --corpus');
 return opts;
}
function roleManifest(url, site) {
 const repo = new URL(url);
 if (repo.hostname !== 'github.com') return new URL('.well-known/mplpb.json', site);
 const [owner, name, view, pin] = repo.pathname.split('/').filter(Boolean);
 const ref = ['tree','blob'].includes(view) && /^[a-f0-9]{40}$/.test(pin) ? pin : 'HEAD';
 return new URL(`https://raw.githubusercontent.com/${encodeURIComponent(owner)}/${encodeURIComponent(name)}/${ref}/.well-known/mplpb.json`);
}
async function githubPullRequest(url, repository) {
 const input = new URL(url);
 const repo = input.hostname === 'github.com' ? input : new URL(repository);
 const [owner, name, view, explicitNumber] = repo.pathname.split('/').filter(Boolean);
 if (repo.protocol !== 'https:' || repo.hostname !== 'github.com' || !owner || !name)
  throw Error('Role manifest requires a public GitHub repository');
 const path = `${encodeURIComponent(owner)}/${encodeURIComponent(name)}`;
 const pulls = `https://api.github.com/repos/${path}/pulls`;
 const request = async endpoint => {
  const response = await fetch(new URL(endpoint),{redirect:'error',cache:'no-store'});
  if (!response.ok) throw Error('Pull request HTTP '+response.status);
  return response.json();
 };
 let number;
 if (view === 'pull') {
  if (!/^[1-9][0-9]{0,9}$/.test(explicitNumber)) throw Error('Invalid GitHub PR number');
  number = Number(explicitNumber);
 } else {
  const newest = await request(pulls+'?state=all&sort=created&direction=desc&per_page=1');
  if (!Array.isArray(newest)) throw Error('Invalid GitHub pull request listing');
  if (!newest.length) return null;
  number = newest[0].number;
  if (!Number.isSafeInteger(number) || number < 1) throw Error('Invalid GitHub PR number');
 }
 const pr = await request(pulls+'/'+number);
 const head = pr.head?.sha;
 if (!/^[a-f0-9]{40}$/.test(head)) throw Error('Pull request response has no valid head');
 const body = pr.body || '';
 const headRepository = pr.head.repo?.full_name;
 const handoffPath = /^[\w.-]+\/[\w.-]+$/.test(headRepository) ? headRepository : path;
 const reportedHead = body.match(/^\*\*(?:Current PR head|Public evidence pin)\*\* `([a-f0-9]{40})`[ 	]*$/m)?.[1] || null;
 return {
  pull_request: pr.html_url, state: pr.state, draft: pr.draft, merged: pr.merged,
  updated_at: pr.updated_at, current_head: head, report_head: reportedHead,
  report_matches_current_head: reportedHead === head,
  handoff_at_current_head: `https://github.com/${handoffPath}/blob/${head}/HANDOFF.md#betty-report-for-al`,
  report: body,
 };
}
async function run() {
 const o=argsOf(process.argv.slice(2));
 if(o.help){console.log(usage());return;}
 const site=siteFrom(o.url);
 if(o.handshake || o.betty || o.al) {
  const role=o.betty?'betty':o.al?'al':null;
  const url=role?roleManifest(o.url,site):new URL('.well-known/mplpb.json',site);
  const response=await fetch(url,{redirect:'error'});
  if (!response.ok) throw Error('Manifest HTTP '+response.status);
  const manifest=await response.json();
  if (!role) {
   console.log(JSON.stringify(manifest,null,2));return;
  }
  const {roles,...team}=manifest.team_building||{};
  if (!roles?.[role]) throw Error('Manifest does not advertise the '+role+' role');
  const live = await githubPullRequest(o.url,manifest.repository);
  console.log(JSON.stringify({...team,role:roles[role],live_pull_request:live},null,2));return;
 }
 let chromium;
 try{({chromium}=await import('playwright'));}catch{throw Error('Install optional browser support: npm install playwright && npx playwright install chromium');}
 const temporary=!o['profile-dir'];
 const dir=o['profile-dir']||await mkdtemp(join(tmpdir(),'mplpb-agent-'));
 let context;
 try{
  context=await chromium.launchPersistentContext(dir,{headless:true});
  const page=context.pages()[0]||await context.newPage();
  await page.goto(site,{waitUntil:'domcontentloaded',timeout:120000});
  await page.waitForFunction(()=>Boolean(window.MPLPB),null,{timeout:120000});
  const response=await page.evaluate(async o=>{
   const api=window.MPLPB;
   const ready=await api.ready();
   if(!ready.ok)return ready;
   if(o.pages)return api.listPages({corpus:o.corpus,profile:'external'});
   if(o.read)return api.readPage(o.read,{corpus:o.corpus,profile:'external'});
   return api.relay(o.question||o.chat,{
    corpus:o.corpus,mode:o.chat?'chat':'query',
    ...(o.session?{session:o.session}:{}),
    ...(o.suggest?{includeSuggestions:true}:{}),
    ...(o['allow-network']?{allowNetwork:true}:{}),
    ...(o['auto-wiki']?{autoWiki:true}:{}),
   });
  },o);
  console.log(JSON.stringify(response,null,2));
  if(!response.ok)process.exitCode=2;
 }finally{
  if(context)await context.close();
  if(temporary)await rm(dir,{recursive:true,force:true});
 }
}
run().catch(e=>{console.error(e.message);process.exitCode=1;});
