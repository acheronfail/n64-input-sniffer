import numpy as np,json
from pathlib import Path
p=Path(__file__).parent;r={}
for f in p.glob('*.stl'):
 a=np.fromfile(f,dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]),offset=84)['v']
 v,ix=np.unique(np.round(a.reshape(-1,3).astype(float),4),axis=0,return_inverse=True); t=ix.reshape(-1,3)
 t=t[(t[:,0]!=t[:,1])&(t[:,1]!=t[:,2])&(t[:,0]!=t[:,2])]
 edges=np.sort(np.concatenate([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1)
 _,counts=np.unique(edges,axis=0,return_counts=True)
 r[f.name]={'boundary_edges':int(sum(counts==1)),'nonmanifold_edges':int(sum(counts>2)),'watertight_after_0_0001mm_weld':bool(np.all(counts==2))}
print(json.dumps(r,indent=2));(p/'mesh-validation.json').write_text(json.dumps(r,indent=2))

assert r, 'Run build.py before mesh checks'
assert all(x['watertight_after_0_0001mm_weld'] for x in r.values()), r
