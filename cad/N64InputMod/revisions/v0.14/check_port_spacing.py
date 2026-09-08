"""v0.13 regression against the archived, physically tested v0.12."""
from pathlib import Path
import sys,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).resolve().parent
old=A.openDocument(str(r/'revisions/v0.12/N64InputMod.FCStd'))
new=A.openDocument(str(r/'N64InputMod.FCStd'))
V=A.Vector
checks={}
def volume(s):return 0. if s.isNull() or not s.Solids else s.Volume
def difference(a,b):return volume(a.cut(b))+volume(b.cut(a))
p=json.loads((r/'parameters.json').read_text())
for i,(x,previous) in enumerate(zip(p['male_port_x'],p['port_x']),1):
 for prefix in ['MalePort','MaleClampShoe','MaleClampPad']:
  name=prefix+str(i)
  expected=old.getObject(name).Shape.translated(V(x-previous,0,0))
  checks[name+'_translation_error_mm3']=difference(expected,new.getObject(name).Shape)
for name in ['FemalePort1','FemalePort2','FemalePort3','FemalePort4','BoardKeeper','LightWindow','ESP32BoardEnvelope','ESP32ComponentKeepout','USBCEnvelope','BoardCradle','USBSeamTongue','OuterContourLoft']:
 checks[name+'_change_mm3']=difference(old.getObject(name).Shape,new.getObject(name).Shape)
regions=[Part.makeBox(29,35,50,V(x,-30,-20)) for x in [-79,50]]
region=regions[0].fuse(regions[1])
for name in ['LowerShell','UpperShell']:
 a=old.getObject(name).Shape;b=new.getObject(name).Shape
 checks[name+'_outside_outer_mounts_change_mm3']=difference(a.cut(region),b.cut(region))
 # Verify the core seat translates exactly, including tail relief and clamp guides.
 for x,dx in [(-63.7,-.34),(63.7,.34)]:
  crop=Part.makeBox(23,14,26,V(x-11.5,-25,-13))
  expected=a.common(crop).translated(V(dx,0,0))
  actual=b.common(crop.translated(V(dx,0,0)))
  checks[name+f'_seat_{x}_translation_error_mm3']=difference(expected,actual)
checks['lid_assembly_sweep_collision_mm3']=max(volume(new.UpperShell.Shape.translated(V(0,0,z)).common(new.LowerShell.Shape)) for z in [0,.16,.5,1,2,4,8,16,25])
face=new.USBCEnvelope.Shape.BoundBox.YMax
path=Part.makeBox(8.4,25,2.4,V(-4.2,face,9))
checks['USB_path_collision_mm3']=sum(volume(path.common(o.Shape)) for o in [new.LowerShell,new.UpperShell])
assert all(v<.005 for v in checks.values()),checks
measure=json.loads((r/'port-spacing-measurements.json').read_text())
errors=[x-y for x,y in zip(p['male_port_x'],measure['mean_centres_relative_to_symmetry_mm'])]
assert max(abs(e) for e in errors)<.025,errors
validation=json.loads((r/'validation.json').read_text())
assert not validation['collisions']
assert all(s['valid'] and s['solids']==1 for s in validation['parts'].values())
result={'revision':'v0.13','checks':checks,'scan_centred_x_residuals_mm':errors,'physical_fit_verified':False}
(r/'port-spacing-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
