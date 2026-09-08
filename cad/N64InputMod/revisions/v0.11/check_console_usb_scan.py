"""Sample the approximately aligned console scan across the rear USB guard."""
from pathlib import Path
import numpy as np,json
r=Path(__file__).parent;p=json.loads((r/'parameters.json').read_text())
dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
a=np.fromfile(r/'reference/Top_aligned.stl',dtype=dtype,offset=84)['v'].astype(float)
xmax=p['usb_guard_inner_width']/2+p['usb_guard_wall'];zmin=p['usb_guard_inner_bottom_z']-p['usb_guard_wall'];zmax=p['usb_guard_inner_bottom_z']+p['usb_guard_inner_height']+p['usb_guard_wall']
a=a[(a[:,:,0].min(1)<=xmax)&(a[:,:,0].max(1)>=-xmax)&(a[:,:,2].min(1)<=zmax)&(a[:,:,2].max(1)>=zmin)]
u=a[:,1]-a[:,0];v=a[:,2]-a[:,0];den=u[:,0]*v[:,2]-u[:,2]*v[:,0];ok=abs(den)>1e-10
a=a[ok];u=u[ok];v=v[ok];den=den[ok]
def ray(x,z):
 aa=((x-a[:,0,0])*v[:,2]-(z-a[:,0,2])*v[:,0])/den
 bb=(u[:,0]*(z-a[:,0,2])-u[:,2]*(x-a[:,0,0]))/den
 hit=(aa>=0)&(bb>=0)&(aa+bb<=1)
 ys=a[hit,0,1]+aa[hit]*u[hit,1]+bb[hit]*v[hit,1]
 ys=ys[ys>-12]
 return None if not len(ys) else float(min(ys))
samples=[(float(x),float(z),ray(x,z)) for x in np.linspace(-xmax,xmax,45) for z in np.linspace(zmin,zmax,23)]
gaps=[y-p['usb_guard_end_y'] for x,z,y in samples if y is not None]
assert min(gaps)>0, 'Guard intersects sampled console surface'
# Check the forward travel required by a straight cable from the socket.
face=p['front_y']+p['rear_y']-p['pcb_console_inset']-(p['pcb_front_y']-1.7)
rays=[{'x_mm':x,'z_mm':z,'console_surface_y_mm':ray(x,z)} for x in [-4,0,4] for z in [9,10.2,11.4]]
blocked=[t for t in rays if t['console_surface_y_mm'] is not None and face<t['console_surface_y_mm']<face+25]
assert blocked,'25 mm axial insertion envelope unexpectedly unobstructed'
result={'revision':'v0.11','scan':'Top_aligned.stl (approximate registration)','sample_count':len(samples),'minimum_sampled_guard_end_clearance_mm':min(gaps),'USB_socket_face_y_mm':face,'guard_end_y_mm':p['usb_guard_end_y'],'axial_25mm_access_envelope_hits_console':True,'axial_sample_rays':rays,'limitations':'Sampled scan check only; does not certify exact console registration, every cable shape, or electrical disconnection before partial withdrawal permits USB access.'}
(r/'console-usb-scan-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
