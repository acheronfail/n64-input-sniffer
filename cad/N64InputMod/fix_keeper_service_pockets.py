from pathlib import Path
import sys,json
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A,Part,Mesh
r=Path(__file__).resolve().parent;d=A.openDocument(str(r/'N64InputMod.FCStd'))
p=json.loads((r/'parameters.json').read_text());lid=d.UpperShell.Shape
for obj in d.PrintParts.Group:
 if not obj.Name.startswith(('MalePortKeeper','FemalePortKeeper')):continue
 b=obj.Shape.BoundBox;c=p['connector_clearance']
 pocket=Part.makeBox(b.XLength+2*c,b.YLength+2*c,b.ZMax+c-p['seam_gap'],A.Vector(b.XMin-c,b.YMin-c,p['seam_gap']))
 lid=lid.cut(pocket)
lid=lid.removeSplitter();assert lid.isValid() and len(lid.Solids)==1
d.UpperShell.Shape=lid
Mesh.Mesh(lid.tessellate(.08)).write(str(r/'UpperShell.stl'))
Part.export(d.PrintParts.Group,str(r/'N64InputMod.step'))
d.recompute();d.save();d.saveCopy(str(r/'N64InputMod-v0.14.FCStd'))
report=json.loads((r/'validation.json').read_text())
report['parts']['UpperShell']={'valid':lid.isValid(),'solids':len(lid.Solids),'volume_mm3':lid.Volume,'bounds':str(lid.BoundBox)}
report['service_pocket_revision']='Vertical keeper pockets replace undercut lid clearances.'
(r/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Updated lid:',lid.Volume)
