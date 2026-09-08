"""Regression and access-clearance checks for the console-facing USB revision."""
from pathlib import Path
import sys,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=Path(__file__).parent;V=A.Vector
old=A.openDocument(str(r/'revisions/v0.10/N64InputMod.FCStd'))
new=A.openDocument(str(r/'N64InputMod.FCStd'))
p=json.loads((r/'parameters.json').read_text())
box=lambda x,y,z,dx,dy,dz:Part.makeBox(dx,dy,dz,V(x,y,z))
def vol(s):return 0 if s.isNull() or not s.Solids else s.Volume
def change(a,b):return vol(a.cut(b))+vol(b.cut(a))
def moved(s):
 s=s.copy();s.rotate(V(),V(0,0,1),180);s.translate(V(0,p['front_y']+p['rear_y']-p['pcb_console_inset'],0));return s
checks={}
for name in ['BoardKeeper','LightWindow','ESP32BoardEnvelope','ESP32ComponentKeepout','USBCEnvelope']:
 checks[name+'_rigid_transform_error_mm3']=change(moved(old.getObject(name).Shape),new.getObject(name).Shape)
for i in range(1,5):
 for prefix in ['MalePort','FemalePort','MaleClampShoe','MaleClampPad']:
  name=prefix+str(i);checks[name+'_change_mm3']=change(old.getObject(name).Shape,new.getObject(name).Shape)
# All connector seats and fasteners outside the central board region stay fixed.
for name in ['LowerShell','UpperShell']:
 for x in [-100,18]:
  region=box(x,-100,-20,82,130,45)
  checks[name+f'_outside_centre_{x}_change_mm3']=change(old.getObject(name).Shape.common(region),new.getObject(name).Shape.common(region))
checks['lid_vertical_assembly_sweep_mm3']=max(vol(new.UpperShell.Shape.translated(V(0,0,dz)).common(new.LowerShell.Shape)) for dz in [0,.16,.5,1,2,4,8,16,25])
# The previous front socket aperture must be solid wall again.
front_probe=box(-4,p['front_y']+.6,9,8,.8,2.4)
checks['front_USB_aperture_missing_wall_mm3']=vol(front_probe.cut(new.LowerShell.Shape.fuse(new.UpperShell.Shape)))
# The new metal-plug path passes from socket face to outside the shroud.
face=new.USBCEnvelope.Shape.BoundBox.YMax
plug=box(-4.2,face,9,8.4,25,2.4)
checks['new_USB_axial_path_blocked_by_enclosure_mm3']=vol(plug.common(new.LowerShell.Shape))+vol(plug.common(new.UpperShell.Shape))
# Retained keeper screw heads, and room around the moved keeper.
cy=new.BoardKeeper.Shape.BoundBox.Center.y
# Use transformed original screw centres (keeper bounding box is asymmetric).
cy=p['front_y']+p['rear_y']-p['pcb_console_inset']-(p['pcb_front_y']+p['pcb_length']/2)
heads=[Part.makeCylinder(2,1.7,V(x,cy,10.55)) for x in [-13,13]]
checks['keeper_screw_head_lid_collision_mm3']=sum(vol(h.common(new.UpperShell.Shape)) for h in heads)
assert all(v<.005 for v in checks.values()),checks
assert abs(new.UpperShell.Shape.BoundBox.ZMax-p['top_z'])<1e-6,'Upper shell must keep its flat roof print plane'
result={'revision':'v0.11','checks':checks,'dimensions':{'PCB_bounds':str(new.ESP32BoardEnvelope.Shape.BoundBox),'USB_socket_face_y_mm':face,'USB_guard_end_y_mm':p['usb_guard_end_y'],'guard_bore_width_mm':p['usb_guard_inner_width'],'guard_bore_height_mm':p['usb_guard_inner_height'],'keeper_to_upper_shell_clearance_mm':new.BoardKeeper.Shape.distToShape(new.UpperShell.Shape)[0],'keeper_head_to_lid_clearance_mm':min(h.distToShape(new.UpperShell.Shape)[0] for h in heads)},'limits':['Console scan alignment is approximate.','Ordinary axial USB cable access is obstructed by the installed console; all cable designs and partial connector engagement are not certified.','Check physical console clearance, cable insertion with adapter removed, and inability to connect USB while any console contacts remain engaged.']}
(r/'console-usb-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
