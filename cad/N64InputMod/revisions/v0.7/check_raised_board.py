from pathlib import Path
import sys,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).parent;old=A.openDocument(str(r/'revisions/v0.5/N64InputMod.FCStd'));new=A.openDocument(str(r/'N64InputMod.FCStd'));V=A.Vector
box=lambda x,y,z,dx,dy,dz:Part.makeBox(dx,dy,dz,V(x,y,z))
def vol(s):return 0 if s.isNull() or not s.Solids else s.Volume
def change(a,b):return vol(a.cut(b))+vol(b.cut(a))
z=7.;lift=15.6;uz=10.2;out={}
out['keeper_shape_change_mm3']=change(old.BoardKeeper.Shape.translated(V(0,0,lift)),new.BoardKeeper.Shape)
out['window_shape_change_mm3']=change(old.LightWindow.Shape,new.LightWindow.Shape)
for x in [-63.7,-36,36,63.7]:
 region=box(x-13.61,-68,-17,27.22,70,35)
 for name in ['LowerShell','UpperShell']:
  out[f'{name}_connector_region_{x}_change_mm3']=change(old.getObject(name).Shape.common(region),new.getObject(name).Shape.common(region))
out['lower_USB_notch_blocked_mm3']=vol(new.LowerShell.Shape.common(box(-4.29,-63,uz,8.58,4,8)))
out['upper_USB_notch_blocked_mm3']=vol(new.UpperShell.Shape.common(box(-4.29,-63,-17,8.58,4,27.36)))
out['lid_assembly_sweep_collision_mm3']=max(vol(new.UpperShell.Shape.translated(V(0,0,dz)).common(new.LowerShell.Shape)) for dz in [0,.16,.5,1,2,4,8,16,25])
heads=[Part.makeCylinder(2.0,1.7,V(x,-47.74,10.55)) for x in [-13,13]]
out['keeper_screw_head_lid_collision_mm3']=sum(vol(h.common(new.UpperShell.Shape)) for h in heads)
assert all(v<.005 for v in out.values()),out
out['board_lift_mm']=lift
out['PCB_top_to_window_underside_mm']=new.LightWindow.Shape.BoundBox.ZMin-new.ESP32BoardEnvelope.Shape.BoundBox.ZMax
out['component_envelope_to_lid_min_distance_mm']=new.ESP32ComponentKeepout.Shape.distToShape(new.UpperShell.Shape)[0]
out['keeper_screw_head_to_lid_min_distance_mm']=min(h.distToShape(new.UpperShell.Shape)[0] for h in heads)
(r/'raised-board-validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
