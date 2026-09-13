"""Verify the exact pause order and cap extrusion at all six M2 pockets."""
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--slice-dir", type=Path, default=Path(__file__).resolve().parent/"slice")
args=parser.parse_args()
import json,re,math,zipfile,hashlib,numpy as np
r=Path(__file__).resolve().parent;folder=args.slice_dir.resolve()
project=folder/'Enclosure-full-enclosure-v1.0-Orca-complete.3mf'
with zipfile.ZipFile(project) as archive:settings=json.loads(archive.read('Metadata/project_settings.config'))
dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
vertices=np.fromfile(r/'UpperShell.stl',dtype=dt,offset=84)['v'].reshape(-1,3)
ox,oy=map(float,settings['extruder_offset'][0].split('x'))
# Upper shell is roof-down, bed-centred in XY and placed at (128,165).
yoff=165+(float(vertices[:,1].min())+float(vertices[:,1].max()))/2-oy
centres={f'M2_{i+1}':(128+x-ox,yoff-y) for i,(x,y) in enumerate(json.loads((r/'parameters.json').read_text())['closure_screw_xy'])}
hits={name:[] for name in centres};pauses=[];x=y=0.;height=None;layer=None
lines=(folder/'plate_1.gcode').read_text().splitlines()
for idx,line in enumerate(lines):
 if line.startswith('; Z_HEIGHT:'):height=round(float(line.split(':')[1]),2)
 if line.startswith('; layer num/total_layer_count:'):layer=int(line.split(':')[1].split('/')[0])
 if line.strip()=='M400 U1':pauses.append({'layer':layer,'height':height,'line':idx+1})
 if not re.match(r'^G[0123] ',line):continue
 vals={k:float(v) for k,v in re.findall(r'([XYE])([-+\d.]+)',line.split(';')[0])}
 nx=vals.get('X',x);ny=vals.get('Y',y)
 if height is not None and 12.20<=height<=14.12 and line.startswith('G1 ') and vals.get('E',0)>0 and (nx!=x or ny!=y):
  for name,(cx,cy) in centres.items():
   lo,hi=1.35,1.75
   if min(x,nx)>cx+hi or max(x,nx)<cx-hi or min(y,ny)>cy+hi or max(y,ny)<cy-hi:continue
   steps=max(1,math.ceil(math.hypot(nx-x,ny-y)/.08))
   if any(lo<math.hypot(x+(nx-x)*i/steps-cx,y+(ny-y)*i/steps-cy)<hi for i in range(steps+1)):
    hits[name].append({'height':height,'line':idx+1})
 x,y=nx,ny
assert len(pauses)==1 and pauses[0]['height']==14.12 and pauses[0]['layer']==88,pauses
for name,events in hits.items():
 assert events,(name,'missing cap extrusion')
 assert all(e['height']==14.12 and e['line']>pauses[0]['line'] for e in events),(name,events)
for i in [2,3]:assert not any(l.strip()=='M400 U1' for l in (folder/f'plate_{i}.gcode').read_text().splitlines())
result={'revision':'v1.0','project_sha256':hashlib.sha256(project.read_bytes()).hexdigest(),'pauses':pauses,'all_six_caps_begin_after_pause':True,'other_plates_have_no_pause':True,'pockets':{name:{'centre_xy_mm':centres[name],'first_cap_extrusion':events[0],'cap_segments':len(events)} for name,events in hits.items()}}
(r/'pause-v1.0-toolpath-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
