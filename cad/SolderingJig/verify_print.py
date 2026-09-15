"""Check the delivered Orca project against soldering jig STLs and toolpaths."""
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--slice-dir", type=Path, default=Path(__file__).resolve().parent/"slice"/"v1.1")
args=parser.parse_args()
import json,zipfile,hashlib,xml.etree.ElementTree as E,numpy as np,shutil
r=Path(__file__).resolve().parent;folder=args.slice_dir.resolve();p=folder/'N64-Soldering-Jig-v1.1.3mf'
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};pn='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}path'
dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
result_path=folder/'result.json'
result=json.loads(result_path.read_text()) if result_path.exists() else None
if result is not None:
 assert result['return_code']==0 and len(result['sliced_plates'])==1
 assert all(not a['warning_message'] for a in result['sliced_plates'])
# Orca 2.4.0 does not write result.json. Check its embedded slice metadata too.
def slice_warnings(archive):
 return [dict(n.attrib) for n in E.fromstring(archive.read('Metadata/slice_info.config')).iter('warning')]
with zipfile.ZipFile(r/'N64-Soldering-Jig-v1.3mf') as baseline:
 known_warnings=slice_warnings(baseline)
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 slice_info=E.fromstring(z.read('Metadata/slice_info.config'))
 assert len(slice_info.findall('plate'))==1
 for plate in slice_info.findall('plate'):
  values={n.get('key'):n.get('value') for n in plate.findall('metadata')}
  assert values['outside']=='false' and float(values['prediction'])>0
  assert all(o.get('skipped')=='false' for o in plate.findall('object'))
 warnings=slice_warnings(z)
 assert all(w in known_warnings for w in warnings), ('New slicer warnings',warnings)

 for i in [1]:assert z.read(f'Metadata/plate_{i}.gcode')==(folder/f'plate_{i}.gcode').read_bytes()
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
 layout=json.loads((r/'print-layout.json').read_text());expected={}
 for e in layout:expected[str(e['object_id'])]=e
 checks=[];bounds={}
 for obj in config.findall('object'):
  oid=obj.get('id');name=md(obj,'name');e=expected.pop(oid);item=items[oid]
  assert name==e['name']+'.stl'
  t=transform(tris('3D/3dmodel.model',oid),item.get('transform'))
  ox,oy=[(0,0),(307.2,0),(0,-307.2)][e['plate']-1]
  t-=np.array([e['centre_xy'][0]+ox,e['centre_xy'][1]+oy,0])
  original=np.fromfile(r/name,dtype=dt,offset=84)['v'].astype(float)
  # Orca preserves triangle order in this project. Compare all vertex coordinates.
  # Allow only differences from serialization precision. Do not allow changes to dimensions or orientation.
  assert t.shape==original.shape,(name,t.shape,original.shape)
  vertex_error=float(np.max(np.abs(t-original)))
  assert vertex_error<.00005,(name,vertex_error)
  assert md(obj,'extruder')==str(e['extruder'])
  bounds[oid]=[t.reshape(-1,3).min(0)+[*e['centre_xy'],0],t.reshape(-1,3).max(0)+[*e['centre_xy'],0]]
  checks.append({'name':name,'triangles':len(t),'max_vertex_error_mm':vertex_error,'source_sha256':hashlib.sha256((r/name).read_bytes()).hexdigest()})
 assert not expected
 plates=config.findall('plate');assert [len(a.findall('model_instance')) for a in plates]==[3]
 for plate in plates:
  bs=[bounds[md(i,'object_id')] for i in plate.findall('model_instance')]
  for lo,hi in bs:assert abs(lo[2])<.001 and all(lo[:2]>0) and all(hi[:2]<256)
  for i,(lo,hi) in enumerate(bs):
   for lo2,hi2 in bs[i+1:]:assert any(hi[:2]+5<lo2[:2]) or any(hi2[:2]+5<lo[:2])
 custom=E.fromstring(z.read('Metadata/custom_gcode_per_layer.xml'));layers=custom.findall('plate/layer')
 assert len(layers)==0
 assert not any(line.strip()=='M400 U1' for line in z.read('Metadata/plate_1.gcode').decode().splitlines())
 assert settings['enable_support']=='0'
report={'revision':'v1.1','printer':settings['printer_settings_id'],'bed':settings['curr_bed_type'],'plate_counts':[3],'slices':result,'inherited_profile_warnings':warnings,'geometry':checks,'embedded_gcode_matches_verified_files':True,'pauses':0,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(r/'print-validation.json').write_text(json.dumps(report,indent=2)+'\n')
# The checked slice stays in slice-dir. Promote it explicitly after review.
print('Verified',p)
if warnings:print('Inherited profile warnings (also present in retained release):',warnings)

# Check welded mesh topology for each of the three bed-oriented print files.
meshes={}
for f in r.glob('*.stl'):
 a=np.fromfile(f,dtype=dt,offset=84)['v']
 verts,ids=np.unique(np.round(a.reshape(-1,3).astype(float),4),axis=0,return_inverse=True);t=ids.reshape(-1,3)
 t=t[(t[:,0]!=t[:,1])&(t[:,1]!=t[:,2])&(t[:,0]!=t[:,2])]
 edges=np.sort(np.concatenate([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1)
 _,counts=np.unique(edges,axis=0,return_counts=True)
 assert np.all(counts==2),f.name
 meshes[f.name]={'watertight':True,'triangles':len(t),'dimensions_mm':np.ptp(a.reshape(-1,3),axis=0).tolist()}
(r/'mesh-validation.json').write_text(json.dumps(meshes,indent=2)+'\n')
print('All three meshes watertight; no print pauses or supports.')
