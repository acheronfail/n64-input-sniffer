import struct,json
from pathlib import Path
import numpy as np
p=Path(__file__).parent;r={}
for f in p.glob('*.stl'):
 a=np.fromfile(f,dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]),offset=84)['v'].reshape(-1,3)
 r[f.name]={'min':a.min(0).tolist(),'max':a.max(0).tolist(),'size_mm':np.ptp(a,axis=0).tolist(),'triangles':len(a)//3}
print(json.dumps(r,indent=2));(p/'stl-dimensions.json').write_text(json.dumps(r,indent=2))
