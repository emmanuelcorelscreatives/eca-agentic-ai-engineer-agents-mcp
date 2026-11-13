"""One genuine ephemeral macOS course exercise, no installs/secrets/remote access."""
from pathlib import Path
import hashlib, json, os, platform, shlex, shutil, subprocess, time
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'macos-course-observations'; OUT.mkdir(exist_ok=False)
WORK=Path(os.environ['RUNNER_TEMP'])/'academy-s02-l03-macos-course'
if WORK.exists(): raise RuntimeError('Own exercise already exists; no replay')
shutil.copytree(ROOT,WORK,ignore=shutil.ignore_patterns('.git',OUT.name,'.venv','__pycache__'))
STAGES=OUT/'stages';STAGES.mkdir()
def save(n,v): (OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def call(a,timeout=12):
 try:
  p=subprocess.run(a,capture_output=True,text=True,timeout=timeout)
  return {'returncode':p.returncode,'stdout':p.stdout[:8000],'stderr':p.stderr[:2000]}
 except subprocess.TimeoutExpired:return {'returncode':None,'outcome':'TIMEOUT_UNKNOWN_NO_RETRY'}
def osa(code):return call(['/usr/bin/osascript','-e',code])
files=['examples/stages02-04/foundations.py','examples/stages02-04/sdk_adapter.py','tests/test_stages_02_04.py','labs/s02/s02-l03.md']
save('identity.json',{'platform':platform.platform(),'architecture':platform.machine(),'runnerLabel':'macos-15',
 'sourceCommit':call(['git','rev-parse','HEAD'])['stdout'].strip(),'workspace':str(WORK),
 'sourceFiles':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in files]})
if platform.system()!='Darwin':raise RuntimeError('Actual macOS required, no OS substitution')
has_window_server=call(['/usr/bin/pgrep','-x','WindowServer']).get('returncode')==0
script=r'''#!/bin/bash
set +e
cd "__WORK__" || exit 3
mkdir "__OUT__/execution-once" || exit 42
exec > >(/usr/bin/tee "__OUT__/actual-course-output.txt") 2>&1
run() { printf '\n$'; printf ' %q' "$@"; printf '\n'; "$@"; code=$?; printf '\n[actual exit status: %s]\n' "$code"; }
stage() {
 printf '\n[completed actual stage: %s]\n' "$1"
 /usr/bin/touch "__STAGES__/$1.done"
 if [ "__GUI__" = yes ]; then
  for i in {1..60}; do [ -f "__STAGES__/$1.ack" ] && break; /bin/sleep 0.1; done
 fi
 printf '\033[2J\033[H'
}
printf 'Academy public course: actual ephemeral macOS VM, not a personal Mac.\n'
run sw_vers
run uname -m
run python3 --version
run uv --version
run git --version
printf '\n$ command -v python3\n'; command -v python3
stage 01-versions-and-path
run pwd
run ls
stage 02-course-root
printf '\n$ python3 -m venv .venv\n'; python3 -m venv .venv
venv_status=$?; printf '[actual exit status: %s]\n' "$venv_status"
if [ "$venv_status" -eq 0 ]; then
 printf '\n$ source .venv/bin/activate\n'; source .venv/bin/activate
 printf '\n$ command -v python3\n'; command -v python3
 run python3 -c 'import sys; print(sys.executable)'
 stage 03-created-and-active-environment
 printf '\n$ deactivate\n'; deactivate
 printf '\n$ command -v python3\n'; command -v python3
 printf '\n$ source .venv/bin/activate\n'; source .venv/bin/activate
 printf '\n$ command -v python3\n'; command -v python3
 stage 04-deactivate-and-reactivate
 run python3 -c "import sys; sys.path.insert(0, 'examples/stages02-04'); from foundations import environment_report; print(environment_report())"
 stage 05-actual-environment-report
 run python3 examples/stages02-04/foundations.py
 stage 06-offline-synthetic-demo
 run python3 -m unittest discover -s tests -p test_stages_02_04.py -v
 stage 07-actual-test-summary
else
 printf 'Environment creation failed. Dependent commands were NOT executed.\n'
fi
/usr/bin/touch "__OUT__/course-shell-completed"
'''
script=script.replace('__WORK__',str(WORK)).replace('__OUT__',str(OUT)).replace('__STAGES__',str(STAGES)).replace('__GUI__','yes' if has_window_server else 'no')
shell=WORK/'academy-once.sh';shell.write_text(script)
path=os.environ['PATH'];terminal_id=None;cli=None;capture_enabled=has_window_server
if has_window_server:
 command='/usr/bin/env -i PATH='+shlex.quote(path)+' LANG=C.UTF-8 TERM=xterm-256color /bin/bash --noprofile --norc '+shlex.quote(str(shell))
 r=osa('tell application "Terminal"\nactivate\nset ownTab to do script '+json.dumps(command)+'\nset bounds of front window to {20, 40, 1400, 940}\nreturn id of front window\nend tell')
 save('terminal-launch.json',r)
 if r.get('returncode')==0 and r.get('stdout','').strip().isdigit():terminal_id=r['stdout'].strip()
 else:capture_enabled=False  # A potentially submitted Apple Event is never retried.
else:
 cli=subprocess.Popen(['/bin/bash','--noprofile','--norc',str(shell)],cwd=WORK,env={'PATH':path,'LANG':'C.UTF-8','TERM':'dumb'},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
save('gui-capability.json',{'windowServerObserved':has_window_server,'TerminalWindowId':terminal_id,
 'AboutThisMac':'Not captured: privacy-safe serial-excluding geometry not established',
 'Installer':'Not run: first observe installed tools; no forced reinstall',
 'remoteAccess':'No SSH/RDP/tunnel/persistent access'})
deadline=time.monotonic()+420;seen=set();images=[]
while time.monotonic()<deadline:
 for marker in sorted(STAGES.glob('*.done')):
  if marker.name in seen:continue
  seen.add(marker.name)
  if capture_enabled and terminal_id:
   time.sleep(.6)
   image=OUT/(marker.stem+'.png');r=call(['/usr/sbin/screencapture','-x','-l',terminal_id,str(image)])
   save(marker.stem+'-capture-status.json',r)
   if r.get('returncode')==0 and image.exists():images.append({'path':image.name,'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'kind':'actual-macOS-Terminal-window','sameOriginalExecution':True})
   else:capture_enabled=False
  marker.with_suffix('.ack').touch()
 if (OUT/'course-shell-completed').exists() or (cli is not None and cli.poll() is not None):break
 time.sleep(.2)
def view(app,code,label):
 r=osa(code);save(label+'-launch.json',r)
 if r.get('returncode')!=0 or not r.get('stdout','').strip().isdigit():return
 time.sleep(4);image=OUT/(label+'.png');shot=call(['/usr/sbin/screencapture','-x','-l',r['stdout'].strip(),str(image)])
 save(label+'-capture-status.json',shot)
 if shot.get('returncode')==0 and image.exists():images.append({'path':image.name,'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'kind':'actual-macOS-'+app+'-window'})
if capture_enabled and terminal_id:
 view('Safari','tell application "Safari"\nactivate\nmake new document with properties {URL:"https://www.python.org/downloads/macos/"}\nset bounds of front window to {20, 40, 1400, 940}\nreturn id of front window\nend tell','08-official-python-macos-page')
 view('Finder','tell application "Finder"\nactivate\nopen POSIX file '+json.dumps(str(WORK))+'\nset bounds of front window to {20, 40, 1400, 940}\nreturn id of front window\nend tell','09-own-course-folder')
complete=(OUT/'course-shell-completed').exists()
save('outcome.json',{'actualMacOS':True,'courseStarted':(OUT/'execution-once').exists(),'courseCompleted':complete,
 'stages':sorted(seen),'captures':images,'CLIOnly':terminal_id is None,'newProviderRequests':0,'newInstalls':0,'noAutomaticRerun':True,
 'limitations':['Ephemeral hosted course VM, not a personal Mac','No About This Mac/serial-bearing screenshot','No installer execution/completion claim','No second Terminal window or translation/external model claim','Only actual saved commands/windows may be reviewed']})
print(json.dumps({'actualMacOS':True,'courseCompleted':complete,'nativeImages':len(images)}))
if not complete:raise SystemExit(2)
