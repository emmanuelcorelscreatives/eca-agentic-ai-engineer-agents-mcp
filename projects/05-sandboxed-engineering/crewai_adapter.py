"""Optional real four-agent CrewAI code generation with Docker-only execution."""
import argparse
import json
import re
from pathlib import Path
import subprocess
import tempfile
import uuid
import zipfile
from team import Specification, plan, safe_path, TESTS

ALLOWED_FILES = {'expense_app.py', 'test_expense_app.py', 'README.md', 'requirements.txt'}


def validate_files(files: dict[str, str]):
    if set(files) != ALLOWED_FILES: raise ValueError('exact four artifact files are required')
    if any(not isinstance(v, str) or len(v.encode()) > 50_000 for v in files.values()):
        raise ValueError('artifact must be bounded text')
    if any(line.strip() and not line.lstrip().startswith('#') for line in files['requirements.txt'].splitlines()):
        raise ValueError('network/dependency installation is forbidden for this stdlib-only task')
    for name in ('expense_app.py', 'test_expense_app.py'):
        compile(files[name], name, 'exec')  # Syntax check only; no host execution.
    if 'total_expenses' not in files['expense_app.py']:
        raise ValueError('required application function missing')
    return files


def build_crew(model: str, spec: Specification):
    from crewai import Agent, Crew, Task, Process, LLM
    from pydantic import BaseModel, ConfigDict

    class SourceBundle(BaseModel):
        model_config = ConfigDict(extra='forbid')
        files: dict[str, str]
        review_notes: str

    llm = LLM(model=model, temperature=0)
    roles = [('Product manager', 'Translate the approved specification into exact acceptance criteria.'),
             ('Software architect', 'Design a small standard-library application and tests.'),
             ('Developer', 'Generate the exact required source, tests, documentation and empty dependency declaration.'),
             ('Quality assurance engineer', 'Review code against criteria and return the complete corrected bundle.')]
    agents = [Agent(role=role, goal=goal, backstory='A specialist in a bounded Academy engineering team.',
                    llm=llm, allow_delegation=False, max_iter=5) for role, goal in roles]
    tasks = []
    descriptions = [
        'Produce acceptance criteria from this approved plan: '+json.dumps(plan(spec)),
        'Design expense_app.py total_expenses(amounts), no third-party dependencies, integer minor units only.',
        'Generate expense_app.py, test_expense_app.py, README.md, requirements.txt. Include tests for empty, '
        'sum, zero, negatives, floats and booleans. No file/network/process operations in the generated application.',
        'Review the complete code. Return files mapping containing exactly expense_app.py, test_expense_app.py, '
        'README.md, requirements.txt, plus review_notes. Requirements must be empty or comments only. '
        'Do not claim actual test execution: execution occurs in Docker after your output.']
    for i, (agent, description) in enumerate(zip(agents, descriptions)):
        kwargs = dict(description=description, agent=agent, context=list(tasks),
                      expected_output='Complete reviewed source bundle.' if i == 3 else roles[i][1])
        if i == 3: kwargs['output_pydantic'] = SourceBundle
        tasks.append(Task(**kwargs))
    return Crew(agents=agents, tasks=tasks, process=Process.sequential, memory=False,
                verbose=False, max_rpm=10)


def docker_qa(root: Path, image: str, timeout: float = 30) -> dict:
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/:~-]*@sha256:[0-9a-f]{64}', image):
        raise ValueError('preloaded digest-pinned Docker image required')
    if not 0 < timeout <= 60: raise ValueError('bounded timeout 0..60 required')
    # The copied inputs are made readable for the unprivileged container, not host homes.
    root.chmod(0o755)
    for p in root.iterdir(): p.chmod(0o444)
    name = 'eca-live-engineering-'+uuid.uuid4().hex
    cmd = ['docker','run','--rm','--name',name,'--pull=never','--network=none','--read-only',
           '--cap-drop=ALL','--security-opt=no-new-privileges','--pids-limit=64','--memory=256m',
           '--cpus=1','--user=65534:65534','--mount',f'type=bind,source={root.resolve()},target=/workspace,readonly',
           '--tmpfs','/tmp:rw,noexec,nosuid,size=16m','--workdir=/workspace',image,
           'python','-B','-m','unittest','-v']
    try:
        result = subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
        count = re.search(r'Ran (\d+) tests?', result.stderr)
        return dict(passed=result.returncode == 0 and count is not None and int(count.group(1)) >= 6, returncode=result.returncode,
                    stdout=result.stdout,stderr=result.stderr)
    finally:
        removed = subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=10)
        if removed.returncode:
            inspected = subprocess.run(['docker','container','inspect',name],capture_output=True,timeout=10)
            if inspected.returncode != 1 or b'No such container' not in inspected.stderr:
                raise RuntimeError('owned container cleanup unproven; held')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-live',action='store_true');p.add_argument('--model',required=True)
    p.add_argument('--docker-image',required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if not args.run_live:p.error('--run-live required: this calls a provider and executes code in Docker')
    # Validate digest and Docker availability before spending provider tokens.
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/:~-]*@sha256:[0-9a-f]{64}', args.docker_image):p.error('use a preloaded digest-pinned image')
    subprocess.run(['docker','image','inspect',args.docker_image],check=True,stdout=subprocess.DEVNULL,timeout=10)
    crew=build_crew(args.model,Specification())
    result=crew.kickoff()
    if result.pydantic is None:raise RuntimeError('missing structured bundle')
    bundle=result.pydantic.model_dump();files=validate_files(bundle['files'])
    with tempfile.TemporaryDirectory(prefix='eca-live-engineering-') as temp:
        root=Path(temp)
        for name,content in files.items():safe_path(root,name).write_text(content)
        # Course-owned acceptance suite cannot be omitted by the generated bundle.
        safe_path(root,'test_course_acceptance.py').write_text(TESTS.replace('class ExpenseTests', 'class CourseAcceptanceTests'))
        qa=docker_qa(root,args.docker_image)
        if not qa['passed']:raise RuntimeError('actual Docker QA failed: '+json.dumps(qa))
        with zipfile.ZipFile(args.output,'x',compression=zipfile.ZIP_DEFLATED) as archive:
            for name in sorted(files):archive.write(safe_path(root,name),name)
            archive.write(safe_path(root,'test_course_acceptance.py'),'test_course_acceptance.py')
            archive.writestr('actual-qa.json',json.dumps(qa,indent=2))
    print(json.dumps(dict(package=str(args.output),qa=qa),indent=2))

if __name__=='__main__':main()
