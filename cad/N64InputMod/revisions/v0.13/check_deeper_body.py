from pathlib import Path
import sys,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).parent;old=A.openDocument(str(r/'revisions/v0.9/N64InputMod.FCStd'));new=A.openDocument(str(r/'N64InputMod.FCStd'));V=A.Vector
box=lambda x,y,z,dx,dy,dz:Part.makeBox(dx,dy,dz,V(x,y,z))
def vol(s):return 0 if s.isNull() or not s.Solids else s.Volume
def change(a,b):return vol(a.cut(b))+vol(b.cut(a))
checks={};dims={}
for name in ['BoardKeeper','LightWindow','ESP32BoardEnvelope','USBCEnvelope']:
 checks[name+'_translated_shape_change_mm3']=change(old.getObject(name).Shape.translated(V(0,-10,0)),new.getObject(name).Shape)
for i,x in enumerate([-63.7,-36,36,63.7],1):
 checks[f'MalePort{i}_moved_mm3']=change(old.getObject(f'MalePort{i}').Shape,new.getObject(f'MalePort{i}').Shape)
 checks[f'FemalePort{i}_translated_shape_change_mm3']=change(old.getObject(f'FemalePort{i}').Shape.translated(V(0,-10,0)),new.getObject(f'FemalePort{i}').Shape)
 y=7+x*x/1450
 for local_y in [-34.5,-31.5]:
  probe=box(x-.05,y+local_y-.05,-12,.1,.1,12)
  a=old.LowerShell.Shape.common(probe);b=new.LowerShell.Shape.common(probe)
  amount=a.BoundBox.ZMax-b.BoundBox.ZMax
  dims[f'male_{i}_depth_increase_at_{local_y}_mm']=amount
  assert abs(amount-1.25)<.001,(i,local_y,amount)
 region=box(x-14,y-29.49,-17,28,40,35)
 for name in ['LowerShell','UpperShell']:
  checks[f'{name}_male_{i}_forward_seat_changed_mm3']=change(old.getObject(name).Shape.common(region),new.getObject(name).Shape.common(region))
for name in ['LowerShell','UpperShell']:
 dims[name+'_depth_increase_mm']=new.getObject(name).Shape.BoundBox.YLength-old.getObject(name).Shape.BoundBox.YLength
 assert abs(dims[name+'_depth_increase_mm']-10)<.001
checks['lid_assembly_sweep_overlap_mm3']=max(vol(new.UpperShell.Shape.translated(V(0,0,z)).common(new.LowerShell.Shape)) for z in [0,.5,1,2,4,8,16,30])
assert max(checks.values())<.005,checks
result={'checks':checks,'dimensions':dims};(r/'deeper-body-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
