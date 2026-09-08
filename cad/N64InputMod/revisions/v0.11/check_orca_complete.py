import zipfile,xml.etree.ElementTree as E,json
from pathlib import Path
base=Path('/home/acheronfail/src/freecad-n64-input/N64InputMod');p=base/'N64InputMod-full-enclosure-v0.11-Orca-complete.3mf'
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};pn='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}path'
with zipfile.ZipFile(p) as z:
 roots={n:E.fromstring(z.read(n)) for n in z.namelist() if n.endswith('.model')}
 def tf(v,t):
  a=list(map(float,t.split())) if t else [1,0,0,0,1,0,0,0,1,0,0,0]
  return tuple(sum(v[j]*a[j*3+i] for j in range(3))+a[9+i] for i in range(3))
 def points(path,oid):
  o=roots[path].find(f"m:resources/m:object[@id='{oid}']",ns)
  vs=[tuple(float(v.get(k)) for k in ['x','y','z']) for v in o.findall('m:mesh/m:vertices/m:vertex',ns)]
  for c in o.findall('m:components/m:component',ns):vs.extend(tf(v,c.get('transform')) for v in points(c.get(pn,path).lstrip('/'),c.get('objectid')))
  return vs
 bounds={}
 for i in roots['3D/3dmodel.model'].findall('m:build/m:item',ns):
  vs=[tf(v,i.get('transform')) for v in points('3D/3dmodel.model',i.get('objectid'))]
  bounds[i.get('objectid')]=[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]
 c=E.fromstring(z.read('Metadata/model_settings.config'));md=lambda el,k:el.find(f"metadata[@key='{k}']").get('value')
 plates=c.findall('plate');assert [len(p.findall('model_instance')) for p in plates]==[7,4,1]
 for plate,origin in zip(plates,[(0,0),(307.2,0),(0,-307.2)]):
  bs=[bounds[md(i,'object_id')] for i in plate.findall('model_instance')]
  for lo,hi in bs:
   assert abs(lo[2])<0.0001
   assert all(lo[k]-origin[k]>=0 and hi[k]-origin[k]<=256 for k in range(2))
  for j,(lo,hi) in enumerate(bs):
   for lo2,hi2 in bs[j+1:]:assert any(hi[k]<lo2[k] or hi2[k]<lo[k] for k in range(2)),'Overlap'
 keeper=next(o for o in c.findall('object') if md(o,'name')=='BoardKeeper.stl')
 lo,hi=bounds[keeper.get('id')];assert md(keeper,'extruder')==md(next(o for o in c.findall('object') if md(o,'name')=='LowerShell.stl'),'extruder')
 assert all(abs(hi[k]-lo[k]-[32.9989166,23.7199974,1.7999997][k])<0.0001 for k in range(3))
 settings=json.loads(z.read('Metadata/project_settings.config'));assert settings['raft_first_layer_expansion']=='2' and settings['tree_support_wall_count']=='0'
 result={'parts':len(bounds),'plate_counts':[7,4,1],'bed_bounds_and_no_overlap':True,'keeper_size_mm':[hi[k]-lo[k] for k in range(3)],'orca_import_export':'checked separately by CLI'}
 (base/'orca-v0.11-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
