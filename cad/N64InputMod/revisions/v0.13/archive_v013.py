from pathlib import Path
import shutil
r=Path(__file__).resolve().parent
out=r/'revisions/v0.13';out.mkdir(exist_ok=True)
for p in r.iterdir():
 if p.is_file() and (p.suffix in ['.py','.FCMacro','.json','.md','.stl'] or p.name in ['N64InputMod.FCStd','N64InputMod-v0.13.FCStd','N64InputMod.step']):
  target=out/p.name
  if not target.exists(): shutil.copy2(p,target)
print(out)
