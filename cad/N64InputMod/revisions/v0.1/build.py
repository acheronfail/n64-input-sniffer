"""Run in FreeCAD Python, or execute build.FCMacro. Units: mm."""
import sys,os,json,math,traceback
from pathlib import Path
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A, Part, Mesh
V=A.Vector
ROOT=Path(__file__).resolve().parent
P={'port_x':[-63.7,-36,36,63.7],'rear_y':-9.0,'front_y':-62.0,'half_width':84.0,'bottom_z':-16.0,'top_z':16.0,'wall':2.4,'connector_clearance':0.22,'nose_y':7.0,'curve_radius':1450.0,'pcb_width':18.0,'pcb_length':22.52,'pcb_thickness':1.6,'pcb_z':4.0,'pcb_front_y':-59.0,'pcb_clearance':0.2,'clip_interference':0.15,'seam_gap':0.16}
if (ROOT/'parameters.json').exists(): P.update(json.loads((ROOT/'parameters.json').read_text()))
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2)+'\n')
D=A.newDocument('N64InputMod')
parts=D.addObject('App::DocumentObjectGroup','PrintParts');parts.Label='01 · Print parts'
refs=D.addObject('App::DocumentObjectGroup','Hardware');refs.Label='02 · Connector and board references'
hist=D.addObject('App::DocumentObjectGroup','Construction');hist.Label='03 · Construction stages (regenerate with build.py)'
scans=D.addObject('App::DocumentObjectGroup','Console');scans.Label='04 · Wesk scan reference — alignment approximate'
def feature(name,shape,group=hist,color=(.23,.25,.28)):
 o=D.addObject('Part::Feature',name);o.Shape=shape;group.addObject(o)
 if A.GuiUp:
  o.ViewObject.ShapeColor=color;o.ViewObject.LineColor=(.08,.09,.11);o.ViewObject.Visibility=group==parts or group==refs
 return o
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
def union(shapes):return shapes[0].multiFuse(shapes[1:]).removeSplitter() if len(shapes)>1 else shapes[0]
def clearance(s):
 c=P['connector_clearance'];return union([s.translated(V(*v)) for v in [(0,0,0),(c,0,0),(-c,0,0),(0,c,0),(0,-c,0),(0,0,c),(0,0,-c)]])
def bow(x):return x*x/P['curve_radius']
# Smooth closed outline: two curved faces and rounded shoulders, identical topology for loft.
def outline(w,front,rear,z):
 def v(x,y):return V(x,y,z)
 a=v(-w+8,front+3); b=v(w-8,front+3);c=v(w,front+11);e=v(w,rear-1);f=v(w-4,rear+bow(w-4));g=v(-w+4,rear+bow(w-4));h=v(-w,rear-1);i=v(-w,front+11)
 edges=[Part.Arc(a,v(0,front),b).toShape(),Part.Arc(b,v(w-2.343,front+5.343),c).toShape(),Part.makeLine(c,e),Part.Arc(e,v(w-1,rear+bow(w-4)-1),f).toShape(),Part.Arc(f,v(0,rear),g).toShape(),Part.Arc(g,v(-w+1,rear+bow(w-4)-1),h).toShape(),Part.makeLine(h,i),Part.Arc(i,v(-w+2.343,front+5.343),a).toShape()]
 return Part.Wire(edges)
w=P['half_width'];fr=P['front_y'];re=P['rear_y'];bz=P['bottom_z'];tz=P['top_z'];wall=P['wall']
outer=Part.makeLoft([outline(w-2.5,fr+2.5,re-.8,bz),outline(w,fr,re,bz+2.5),outline(w,fr,re,tz-3),outline(w-3,fr+2,re-.7,tz)],True,True)
inner=Part.makeLoft([outline(w-wall,fr+wall,re-wall,bz+wall),outline(w-wall,fr+wall,re-wall,tz-wall)],True,True)
feature('OuterContourLoft',outer);feature('InteriorLoft',inner)
shell=outer.cut(inner)

# Solid local collars capture each housing; enclosing halves retain their axial shoulders.
male0=Part.Shape();male0.read(str(ROOT.parent/'n64-input-ControllerPortMale.step'));male0.translate(V(120,0,0))
female0=Part.Shape();female0.read(str(ROOT.parent/'n64-input-ControllerPortFemale.step'));female0.translate(V(-110,0,0))
hardware=[];cutters=[];collars=[]
for i,x in enumerate(P['port_x']):
 y=P['nose_y']+bow(x)
 m=male0.copy();m.translate(V(x,y,0));hardware.append(feature('MalePort'+str(i+1),m,refs,(.17,.18,.20)))
 f=female0.copy();f.translate(V(x,P['front_y']+13,0));hardware.append(feature('FemalePort'+str(i+1),f,refs,(.29,.30,.32)))
 # 0.22 mm radial clearance on the supplied housing, including keyed profiles and flange.
 for s in [m,f]:cutters.append(clearance(s))
 collars.extend([box(x-13.6,-28+bow(x),-13.6,27.2,21.5,27.2),box(x-13.2,-62,-10,26.4,19,23.6)])
 # Cable/solder access from housing tails to common cavity.
 cutters.extend([box(x-7,y-38,-5,14,5,10),box(x-9,-46,-5,18,10,10)])
collars=union(collars).common(outer)
feature('ConnectorCollars',collars)

shell=shell.fuse(collars)

for n,c in enumerate(cutters):

 shell=shell.cut(c)

shell=shell.removeSplitter()

feature('CapturedConnectorSeats',shell)
# Four M2.5 self-tapping lid fasteners, accessible underneath.
screws=[(-77,-39),(77,-39),(-19,-19),(19,-19)]
bosses=[];holes=[]
for x,y in screws:
 bosses.append(Part.makeCylinder(4.3,29.6,V(x,y,-13.6)))
 holes.append(Part.makeCylinder(1.05,27,V(x,y,-13.7)))
for n,b in enumerate(bosses):
 b=b.common(outer)
 shell=shell.fuse(b)
for h in holes:shell=shell.cut(h)


# Original console LED sight tunnel: clear passage below electronics, chamfered front entrance.
# rounded rectangle via paired cylinders joined by a box
led=union([Part.makeCylinder(3.3,70,V(x,-68,-9.3),V(0,1,0)) for x in [-2,2]]+[box(-2,-68,-12.6,4,70,6.6)])

shell=shell.cut(led)
# USB opening plus cable overmould recess: centre/front, PCB component side up.
usby=P['pcb_front_y'];pcbz=P['pcb_z'];L=P['pcb_length'];W=P['pcb_width']
usb=union([box(-5.5,-68,5.0,11,12,4.4),Part.makeCylinder(2.2,12,V(-5.5,-68,7.2),V(0,1,0)),Part.makeCylinder(2.2,12,V(5.5,-68,7.2),V(0,1,0))])
shell=shell.cut(usb)
# Broad replaceable translucent window accommodates LED placement variations.
window=box(-7.5,-55.5,12.8,15,15,10)
ledge=box(-9,-57,13.8,18,18,10)
shell=shell.cut(window.fuse(ledge))
base=shell.common(box(-150,-100,-30,300,150,30))
lid=shell.common(box(-150,-100,P['seam_gap'],300,150,40))
# PCB supports only at end corners; leave side solder rows and USB underside open.
support=[]
for x in [-8,6]:
 for y in [usby+.4,usby+L-2.4]:support.append(box(x,y,-13.6,2,2,pcbz+13.6))
# Resilient vertical clips: isolated cantilevers; nib interference only near rear corners.
for sign in [-1,1]:
 x=sign*(W/2+P['pcb_clearance'])
 armx=x if sign>0 else x-1
 support.append(box(armx,usby+L-5,-13.6,1,3,20.0))
 nibx=W/2-P['clip_interference'] if sign>0 else -W/2-.9
 support.append(box(nibx,usby+L-4.7,pcbz+P['pcb_thickness']+.15,1.05,2.4,.55))
# End stops resist cable insertion/removal. Front stops flank the USB connector.
for x in [-8,6]:support.append(box(x,usby-.8,-13.6,2,.8,19.2))
support.append(box(-7,usby+L+.2,-13.6,14,1.2,19.2))
base=base.fuse(union(support)).removeSplitter()
# Alignment pins in separate flange pads away from seats.
for x,y in [(-79,-49),(79,-49)]:
 pad=Part.makeCylinder(3.0,7,V(x,y,-4))
 base=base.fuse(pad.common(box(-150,-100,-30,300,150,30)))
 base=base.fuse(Part.makeCylinder(1.1,2.8,V(x,y,-.1)))
 lid=lid.fuse(pad.common(box(-150,-100,P['seam_gap'],300,150,30)))
 lid=lid.cut(Part.makeCylinder(1.3,3,V(x,y,0)))
# Clear lower-half screw shanks and countersinks; 2.1 mm pilot remains in lid.
for x,y in screws:
 base=base.cut(Part.makeCylinder(1.4,19,V(x,y,-17)))
 base=base.cut(Part.makeCylinder(2.7,3.5,V(x,y,-16.5)))
base=base.cut(led).removeSplitter();lid=lid.cut(union(support)).removeSplitter()
bo=feature('LowerShell',base,parts);bo.Label='Lower shell · PCB press fit · M2.5 clearance'
lo=feature('UpperShell',lid,parts);lo.Label='Upper shell · USB-C · LED window'
# Separate translucent insert, pressed into upper recess with a little adhesive if required.
wi=feature('LightWindow',box(-8.8,-56.8,13.95,17.6,17.6,1.7),parts,(.65,.9,.83));wi.Label='Optional translucent LED window'
if A.GuiUp:wi.ViewObject.Transparency=65
pcb=feature('ESP32BoardEnvelope',box(-W/2,usby,pcbz,W,L,P['pcb_thickness']),refs,(.12,.40,.32))
feature('ESP32ComponentKeepout',box(-6.5,usby+7,pcbz+1.6,13,12,3),refs,(.55,.56,.59))
feature('USBCEnvelope',box(-4.6,usby-1.7,pcbz+1.6,9.2,7.4,3.2),refs,(.72,.73,.76))
# Fit coupons isolate uncertain purchased-part dimensions before printing a full case.
gauge=base.common(box(-90,-26,-17,180,24,20))
gauge=gauge.fuse(box(-80,-22,-16,160,4,2.4)).removeSplitter()
go=feature('RearAlignmentGauge',gauge,hist);go.Label='PRINT FIRST · Four-plug lower alignment gauge'
gauge_top=lid.common(box(-90,-26,0,180,24,20)).fuse(box(-80,-22,12.6,160,4,2.4)).removeSplitter()
gt=feature('RearAlignmentGaugeUpper',gauge_top,hist)
bc=feature('BoardFitCoupon',base.common(box(-13,usby-2,-17,26,L+5,26)),hist)
fc=feature('FemaleFitCoupon',base.common(box(22,-66,-17,28,24,26)),hist)
meta=D.addObject('App::FeaturePython','DesignParameters');hist.addObject(meta)
for k,v in P.items():
 if isinstance(v,list):meta.addProperty('App::PropertyString',k,'Dimensions');setattr(meta,k,str(v))
 else:meta.addProperty('App::PropertyFloat',k,'Dimensions');setattr(meta,k,v)
meta.addProperty('App::PropertyString','Status','Documentation');meta.Status='FIT PROTOTYPE. Regenerate using parameters.json + build.py; insertion depth and PCB details require physical checks.'
# Geometry validity and unintended assembly intersections.
report={'status':'fit prototype; physical fit not yet verified','parts':{},'collisions':[],'parameters':P}
for obj in [bo,lo,wi,go,gt,bc,fc]:
 s=obj.Shape;report['parts'][obj.Name]={'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds':str(s.BoundBox)}
 if not s.isValid() or len(s.Solids)!=1:raise RuntimeError('Invalid or disconnected '+obj.Name)
for a in [bo,lo]:
 for b in hardware+[pcb]:
  vol=a.Shape.common(b.Shape).Volume
  if vol>.005:report['collisions'].append({'a':a.Name,'b':b.Name,'volume_mm3':vol})
report['shell_overlap_mm3']=base.common(lid).Volume
(ROOT/'validation.json').write_text(json.dumps(report,indent=2))
if report['collisions'] or report['shell_overlap_mm3']>.005:raise RuntimeError('Assembly interference; see validation.json')
for o in [bo,lo,wi,go,gt,bc,fc]:
 m=Mesh.Mesh(o.Shape.tessellate(.08));m.write(str(ROOT/(o.Name+'.stl')))
Part.export([bo,lo,wi],str(ROOT/'N64InputMod.step'))
# Embed lightweight references when available; raw scans are never required to open the CAD file.
for name in ['Top','Bottom']:
 path=ROOT/'reference'/(name+'_aligned.stl')
 if path.exists():
  o=D.addObject('Mesh::Feature','Console'+name);o.Mesh=Mesh.Mesh(str(path));scans.addObject(o)
  if A.GuiUp:o.ViewObject.Visibility=False;o.ViewObject.ShapeColor=(.38,.39,.41);o.ViewObject.DisplayMode='Shaded'
D.recompute()
if A.GuiUp:
 import FreeCADGui as G
 G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll()
D.recompute();D.saveAs(str(ROOT/'N64InputMod.FCStd'))
print(json.dumps(report,indent=2))
