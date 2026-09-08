"""Validate the delivered Orca project against final v0.14 STLs and toolpaths."""
from pathlib import Path
import json,zipfile,hashlib,xml.etree.ElementTree as E,numpy as np,shutil
r=Path(__file__).resolve().parent;folder=Path('/tmp/n64-v014-slice');p=folder/'N64InputMod-full-enclosure-v0.14-Orca-complete.3mf'
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};pn='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}path'
dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
result=json.loads((folder/'result.json').read_text());assert result['return_code']==0 and len(result['sliced_plates'])==3
assert all(not a['warning_message'] for a in result['sliced_plates'])
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 for i in [1,2,3]:assert z.read(f'Metadata/plate_{i}.gcode')==(folder/f'plate_{i}.gcode').read_bytes()
 settings=json.loads(z.read('Metadata/project_settings.config'))
 assert settings['printer_settings_id']=='Bambu Lab P1S 0.4 nozzle'
 config=E.fromstring(z.read('Metadata/model_settings.config'));roots={n:E.fromstring(z.read(n)) for n in z.namelist() if n.endswith('.model')}
 def md(o,k):return o.find(f"metadata[@key='{k}']").get('value')
 def transform(points,tf):
  a=np.array(list(map(float,tf.split())) if tf else [1,0,0,0,1,0,0,0,1,0,0,0]);return points@a[:9].reshape(3,3)+a[9:]
 def tris(path,oid):
  obj=roots[path].find(f"m:resources/m:object[@id='{oid}']",ns)
  points=np.array([[float(v.get(k)) for k in ['x','y','z']] for v in obj.findall('m:mesh/m:vertices/m:vertex',ns)])
  faces=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in obj.findall('m:mesh/m:triangles/m:triangle',ns)])
  chunks=[]
  if len(faces):chunks.append(points[faces])
  for c in obj.findall('m:components/m:component',ns):
   t=tris(c.get(pn,path).lstrip('/'),c.get('objectid'));chunks.append(transform(t,c.get('transform')))
  return np.concatenate(chunks)
 items={i.get('objectid'):i for i in roots['3D/3dmodel.model'].findall('m:build/m:item',ns)}
 layout=json.loads((r/'orca-v0.14-layout.json').read_text());expected={}
 for e in layout:expected.setdefault(e['name']+'.stl',[]).append(e)
 checks=[];bounds={}
 for obj in config.findall('object'):
  oid=obj.get('id');name=md(obj,'name');e=expected[name].pop(0);item=items[oid]
  t=transform(tris('3D/3dmodel.model',oid),item.get('transform'))
  ox,oy=[(0,0),(307.2,0),(0,-307.2)][e['plate']-1]
  t-=np.array([e['centre_xy'][0]+ox,e['centre_xy'][1]+oy,0])
  original=np.fromfile(r/'print/full-enclosure-v0.14'/name,dtype=dt,offset=84)['v'].astype(float)
  # Orca preserves triangle order in this project. Compare all vertex coordinates,
  # allowing only serialization precision, not changed dimensions or orientation.
  assert t.shape==original.shape,(name,t.shape,original.shape)
  vertex_error=float(np.max(np.abs(t-original)))
  assert vertex_error<.00005,(name,vertex_error)
  assert md(obj,'extruder')==str(e['extruder'])
  bounds[oid]=[t.reshape(-1,3).min(0)+[*e['centre_xy'],0],t.reshape(-1,3).max(0)+[*e['centre_xy'],0]]
  checks.append({'name':name,'triangles':len(t),'max_vertex_error_mm':vertex_error,'source_sha256':hashlib.sha256((r/'print/full-enclosure-v0.14'/name).read_bytes()).hexdigest()})
 assert all(not e for e in expected.values())
 plates=config.findall('plate');assert [len(a.findall('model_instance')) for a in plates]==[2,9,1]
 for plate in plates:
  bs=[bounds[md(i,'object_id')] for i in plate.findall('model_instance')]
  for lo,hi in bs:assert abs(lo[2])<.001 and all(lo[:2]>0) and all(hi[:2]<256)
  for i,(lo,hi) in enumerate(bs):
   for lo2,hi2 in bs[i+1:]:assert any(hi[:2]+5<lo2[:2]) or any(hi2[:2]+5<lo[:2])
 custom=E.fromstring(z.read('Metadata/custom_gcode_per_layer.xml'));layers=custom.findall('plate/layer')
 assert len(layers)==1 and float(layers[0].get('top_z'))==14.12
report={'revision':'v0.14','printer':settings['printer_settings_id'],'bed':settings['curr_bed_type'],'plate_counts':[2,9,1],'slices':result,'geometry':checks,'embedded_gcode_matches_verified_files':True,'pause_validation':json.loads((r/'pause-v0.14-toolpath-validation.json').read_text()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(r/'orca-v0.14-validation.json').write_text(json.dumps(report,indent=2)+'\n')
shutil.copy2(p,r/p.name)
print('Verified and delivered',p.name)
