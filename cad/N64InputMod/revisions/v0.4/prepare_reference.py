import sys
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Mesh
from pathlib import Path
p=Path(__file__).parent
for name,delta in [('Top',(0,71.5,2.2)),('Bottom',(0,103.5,-29.3))]:
 m=Mesh.Mesh(str(p/'reference'/f'{name}.stl'))
 m.decimate(75000)
 mat=A.Matrix();mat.move(A.Vector(*delta));m.transform(mat)
 m.write(str(p/'reference'/f'{name}_aligned.stl'))
 print(name,m.CountFacets,flush=True)
