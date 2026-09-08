from pathlib import Path
import numpy as np,json,hashlib,zipfile
root=Path(__file__).resolve().parent
out=root/'print/full-enclosure-v0.15';out.mkdir(parents=True,exist_ok=True)
dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
specs=[('LowerShell',1,'Rigid material matching the proven enclosure print',False),('UpperShell',1,'Same as lower shell',True),('BoardKeeper',1,'Reuse existing keeper if available',False)]+[(f'MalePortKeeper{i}',1,'Rigid material; numbered left to right by increasing CAD X',True) for i in range(1,5)]+[('FemalePortKeeper',4,'Rigid material; all four identical',True),('LightWindow',1,'Optional translucent material; reuse existing window',False)]
manifest={'revision':'v0.15','status':'Independent contour retention; enlarged case; CAD and scan checks recorded separately; physical fit unverified','files':[]}
for name,qty,material,invert in specs:
 src=root/(name+'.stl');data=np.fromfile(src,dtype=dtype,offset=84).copy()
 rot=np.array([1,-1,-1] if invert else [1,1,1])
 data['v']*=rot;data['n']*=rot
 lo=data['v'].reshape(-1,3).min(0);hi=data['v'].reshape(-1,3).max(0)
 translation=np.array([-(lo[0]+hi[0])/2,-(lo[1]+hi[1])/2,-lo[2]])
 data['v']+=translation
 target=out/(name+'.stl')
 with target.open('wb') as f:
  f.write(('N64InputMod v0.15 | '+name+' | bed-oriented mm').encode().ljust(80,b' '));f.write(np.uint32(len(data)).tobytes());data.tofile(f)
 actual=data['v'].reshape(-1,3)
 assert abs(float(actual[:,2].min()))<.0001
 # Rigid transform must preserve all triangle edge lengths and topology.
 original=np.fromfile(src,dtype=dtype,offset=84)
 err=np.max(np.abs(np.linalg.norm(data['v'][:,1]-data['v'][:,0],axis=1)-np.linalg.norm(original['v'][:,1]-original['v'][:,0],axis=1)))
 assert err<.0001
 manifest['files'].append({'file':target.name,'print_quantity':qty,'material_or_note':material,'orientation':('Flat top face on bed' if 'Keeper' in name else 'Outside roof on bed') if invert else 'Broad lower face on bed','size_mm':np.ptp(actual,axis=0).tolist(),'bed_z_mm':float(actual[:,2].min()),'triangles':len(data),'max_edge_length_change_mm':float(err),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'output':str(out),'files':[(e['file'],e['print_quantity']) for e in manifest['files']]},indent=2))

with zipfile.ZipFile(root/"N64InputMod-full-enclosure-v0.15.zip","w",zipfile.ZIP_DEFLATED) as z:
 for filename in [e["file"] for e in manifest["files"]]+["manifest.json","PRINT-AND-ASSEMBLE.md"]:
  z.write(out/filename,"N64InputMod-full-enclosure-v0.15/"+filename)
