import sys,json
from pathlib import Path
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part
r=str(Path(__file__).resolve().parent)
d=A.openDocument(r+'/N64InputMod.FCStd')
f=d.FemalePort3.Shape
print('female',f.BoundBox)
for face in f.Faces:
 print(round(face.Area,3),face.Surface,face.BoundBox)
m=d.MalePort3.Shape
for y in [-33.5,-29.5,-27.5,-23.5,-6]:
 line=Part.makeLine(A.Vector(36,7+36**2/1450+y,-20),A.Vector(36,7+36**2/1450+y,20))
 print('male axis',y,[(e.Vertexes[0].Point.z,e.Vertexes[-1].Point.z) for e in m.common(line).Edges])
