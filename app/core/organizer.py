from pathlib import Path
import shutil

def plan_copy(paths, destination):
    plan=[]
    for item in paths:
        src=Path(item)
        folder=Path(destination)/"05 - POR CLASIFICAR"
        dst=folder/src.name
        if dst.exists():
            dst=folder/f"{src.stem}__{src.stat().st_size}{src.suffix}"
        plan.append((src,dst))
    return plan

def execute_plan(plan, move=False):
    done=[]
    for src,dst in plan:
        dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():
            raise FileExistsError(str(dst))
        shutil.move(str(src),str(dst)) if move else shutil.copy2(src,dst)
        done.append((str(src),str(dst)))
    return done
