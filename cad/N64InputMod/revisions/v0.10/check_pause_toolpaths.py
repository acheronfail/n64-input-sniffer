"""Check native pauses and whether nut-pocket cap toolpaths begin after them."""
from pathlib import Path
import re,json,struct,math,zipfile
r=Path(__file__).parent;lines=Path('/tmp/n64-nut-slice/plate_1.gcode').read_text().splitlines()
raw=(r/'UpperShell.stl').read_bytes();ys=[]
for i in range(struct.unpack_from('<I',raw,80)[0]):
 v=struct.unpack_from('<9f',raw,84+50*i+12);ys.extend(v[j] for j in [1,4,7])
with zipfile.ZipFile(r/'N64InputMod-full-enclosure-v0.10-Orca-complete.3mf') as z:
 settings=json.loads(z.read('Metadata/project_settings.config'))
ox,oy=map(float,settings['extruder_offset'][0].split('x'))
yoff=145+(min(ys)+max(ys))/2-oy
centres={}
for i,x in enumerate([-63.7,-36,36,63.7]):centres['M3_'+str(i)]=(128+x-ox,yoff-(7+x*x/1450-23),1.95,2.5)
for i,(x,y) in enumerate([(-77,-49),(77,-49),(-19,-19),(19,-19),(-79,-18),(79,-18)]):centres['M2_'+str(i)]=(128+x-ox,yoff-y,1.35,1.75)
heights=[2.76,2.92,5.32,5.48,12.04,12.2,13.96,14.12];hits={z:{k:0 for k in centres} for z in heights}
x=y=0.;zheight=None;pauses=[];layer=None
for line in lines:
 if line.startswith('; Z_HEIGHT:'):zheight=round(float(line.split(':')[1]),2)
 if line.startswith('; layer num/total_layer_count:'):layer=int(line.split(':')[1].split('/')[0])
 if line.strip()=='M400 U1':pauses.append({'layer':layer,'height':zheight})
 if not re.match(r'^G[0123] ',line):continue
 vals={k:float(v) for k,v in re.findall(r'([XYE])([-+\d.]+)',line.split(';')[0])}
 nx=vals.get('X',x);ny=vals.get('Y',y)
 if zheight in hits and line.startswith('G1 ') and vals.get('E',0)>0 and (nx!=x or ny!=y):
  for name,(cx,cy,lo,hi) in centres.items():
   if min(x,nx)>cx+hi or max(x,nx)<cx-hi or min(y,ny)>cy+hi or max(y,ny)<cy-hi:continue
   steps=max(1,math.ceil(math.hypot(nx-x,ny-y)/.1))
   if any(lo<math.hypot(x+(nx-x)*i/steps-cx,y+(ny-y)*i/steps-cy)<hi for i in range(steps+1)):hits[zheight][name]+=1
 x,y=nx,ny
assert pauses==[{'layer':34,'height':5.48},{'layer':88,'height':14.12}],pauses
for name in centres:
 before,after=(5.32,5.48) if name.startswith('M3') else (13.96,14.12)
 assert hits[before][name]==0,(name,'cap printed too early',hits[before][name])
 assert hits[after][name]>0,(name,'cap not found',hits[after][name])
result={'pauses':pauses,'pocket_region_extrusions_by_height':hits,'all_ten_caps_begin_after_pause':True}
(r/'pause-toolpath-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
