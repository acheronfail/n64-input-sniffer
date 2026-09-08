"""Replace shell meshes while preserving the complete Orca project layout/settings."""
from pathlib import Path
import struct,zipfile,re,xml.etree.ElementTree as E,json
r=Path(__file__).parent
with zipfile.ZipFile(r/'N64InputMod-full-enclosure-v0.10-Orca-complete.3mf') as z:data={n:z.read(n) for n in z.namelist()}
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};pn='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}path'
model=E.fromstring(data['3D/3dmodel.model']);config=E.fromstring(data['Metadata/model_settings.config'])
for name in ['LowerShell','UpperShell','BoardKeeper']:
 obj=next(o for o in config.findall('object') if o.find("metadata[@key='name']").get('value')==name+'.stl');oid=obj.get('id')
 comp=model.find(f"m:resources/m:object[@id='{oid}']/m:components/m:component",ns)
 path=comp.get(pn).lstrip('/')
 raw=(r/'print/full-enclosure-v0.12'/(name+'.stl')).read_bytes();vs=[];index={};ts=[]
 for i in range(struct.unpack_from('<I',raw,80)[0]):
  coords=struct.unpack_from('<9f',raw,84+50*i+12);tri=[]
  for j in range(3):
   v=coords[j*3:j*3+3]
   if v not in index:index[v]=len(vs);vs.append(v)
   tri.append(index[v])
  ts.append(tri)
 cz=(min(v[2] for v in vs)+max(v[2] for v in vs))/2
 mesh='<mesh><vertices>'+''.join(f'<vertex x="{v[0]}" y="{v[1]}" z="{v[2]-cz}"/>' for v in vs)+'</vertices><triangles>'+''.join(f'<triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}"/>' for t in ts)+'</triangles></mesh>'
 data[path]=re.sub(r'<mesh>.*?</mesh>',lambda m:mesh,data[path].decode(),flags=re.S).encode()
 s=data['3D/3dmodel.model'].decode()
 item=model.find(f"m:build/m:item[@objectid='{oid}']",ns);tf=item.get('transform').split();tf[-1]=str(cz)
 if name=='UpperShell':tf[10]='145' # Keep a useful gap between the deeper shells on plate 1.
 s=re.sub(r'(<item\b[^>]*objectid="'+oid+r'"[^>]*transform=")[^"]*"',lambda m:m[1]+' '.join(tf)+'"',s)
 data['3D/3dmodel.model']=s.encode()
 part=obj.find('part')
 for key,val in [('source_offset_x','0'),('source_offset_y','0'),('source_offset_z',str(cz)),('matrix',f'1 0 0 0 0 1 0 0 0 0 1 {cz} 0 0 0 1')]:
  md=part.find(f"metadata[@key='{key}']")
  if md is not None:md.set('value',val)
 print(name,len(ts),'triangles, height',cz*2)
data['Metadata/model_settings.config']=E.tostring(config,encoding='utf-8',xml_declaration=True)
# Discard stale slice results and thumbnails; Orca regenerates them on export.
for key in list(data):
 if key.endswith('.png') or key in ['Metadata/plate_1.json','Metadata/slice_info.config']:
  del data[key]
s=json.loads(data['Metadata/project_settings.config']);s['project_name']='N64InputMod v0.12 - console-facing USB with nut pauses';data['Metadata/project_settings.config']=json.dumps(s,indent=2).encode()
with zipfile.ZipFile(r/'N64InputMod-full-enclosure-v0.12-Orca-complete.3mf','w',zipfile.ZIP_DEFLATED) as z:
 for n,v in data.items():z.writestr(n,v)
