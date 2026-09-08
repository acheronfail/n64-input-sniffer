"""Run in FreeCAD Python, or execute build.FCMacro. Units: mm."""
import sys,os,json,math,traceback
from pathlib import Path
sys.path.insert(0,'/app/freecad/lib')
import FreeCAD as A, Part, Mesh
V=A.Vector
ROOT=Path(__file__).resolve().parent
P={'port_x':[-63.7,-36,36,63.7],'rear_y':-9.0,'front_y':-62.0,'half_width':84.0,'bottom_z':-16.0,'top_z':16.0,'wall':2.4,'connector_clearance':0.22,'nose_y':7.0,'curve_radius':1450.0,'pcb_width':18.0,'pcb_length':22.52,'pcb_thickness':1.6,'pcb_z':-8.6,'pcb_front_y':-59.0,'pcb_clearance':0.2,'keeper_gap':0.15,'keeper_thickness':1.8,'seam_gap':0.16,'usb_opening_width':10.0,'usb_opening_height':4.0,'usb_corner_radius':0.7,'usb_seam_tab_width':18.0,'usb_seam_inner_y':-58.9,'keeper_head_diameter':4.2,'closure_head_diameter':5.2,'clamp_head_diameter':6.4,'countersink_angle_deg':90.0,'closure_nut_af':4.3,'closure_nut_pocket_z':2.0,'closure_nut_pocket_height':2.0}
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
def countersink(x,y,z,head_d,shank_d,direction):
 # Conical clearance seat measured from the outer face toward the screw axis.
 depth=(head_d-shank_d)/2/math.tan(math.radians(P['countersink_angle_deg']/2))
 return Part.makeCone(head_d/2,shank_d/2,depth,V(x,y,z),V(0,0,direction))
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
 collars.extend([box(x-13.6,-28+bow(x),-13.6,27.2,21.5,27.2),box(x-13.2,-62,bz+wall,26.4,19,13.6-(bz+wall))])
 # Cable/solder access from housing tails to common cavity.
 cutters.extend([box(x-7,y-38,-5,14,5,10),box(x-9,-46,-5,18,10,10)])
collars=union(collars).common(outer)
feature('ConnectorCollars',collars)

shell=shell.fuse(collars)

for n,c in enumerate(cutters):

 shell=shell.cut(c)

shell=shell.removeSplitter()

feature('CapturedConnectorSeats',shell)
# Six M2 through screws with print-in captive nuts, accessible underneath.
screws=[(-77,-39),(77,-39),(-19,-19),(19,-19),(-79,-18),(79,-18)]
bosses=[];holes=[]
for x,y in screws:
 bosses.append(Part.makeCylinder(3.5 if abs(x)==79 else 4.3,29.6,V(x,y,-13.6)))
 holes.append(Part.makeCylinder(1.1,27,V(x,y,-13.7)))
for n,b in enumerate(bosses):
 b=b.common(outer)
 shell=shell.fuse(b)
for h in holes:shell=shell.cut(h)


# Console-light passage removed: the top window exposes the ESP32 LED.
usby=P['pcb_front_y'];pcbz=P['pcb_z'];L=P['pcb_length'];W=P['pcb_width']
# Close-fitting rounded rectangle around the 9.2 x 3.2 mm USB housing envelope.
uw=P['usb_opening_width'];uh=P['usb_opening_height'];ur=P['usb_corner_radius'];uz=pcbz+3.2
assert 0<ur<min(uw,uh)/2
usb=union([box(-uw/2+ur,-68,uz-uh/2,uw-2*ur,12,uh),box(-uw/2,-68,uz-uh/2+ur,uw,12,uh-2*ur)]+[Part.makeCylinder(ur,12,V(x,-68,z),V(0,1,0)) for x in [-uw/2+ur,uw/2-ur] for z in [uz-uh/2+ur,uz+uh/2-ur]])
shell=shell.cut(usb)
# Independent male-housing pressure shoes. Captive M3 nuts load the roof upwards;
# nuts are embedded during a paused roof-down print; 0.8 mm of plastic
# separates the nut pockets from the pressure-shoe guides.
clamp_parts=[];clamp_tools=[]
for i,x in enumerate(P['port_x']):
 cy_m=P['nose_y']+bow(x)-23.0
 # Reinforce above the flat housing surface without reducing its proven seat clearance.
 block=box(x-8,cy_m-6,7.0,16,12,9).common(outer)
 shell=shell.fuse(block)
 guide=box(x-6.2,cy_m-4.2,6.5,12.4,8.4,3.3)
 nut_r=5.8/math.sqrt(3)
 poly=[V(x+nut_r*math.cos(k*math.pi/3),cy_m+nut_r*math.sin(k*math.pi/3),10.6) for k in range(6)]
 nut=Part.Face(Part.makePolygon(poly+[poly[0]])).extrude(V(0,0,2.7))
 screw=Part.makeCylinder(1.65,9,V(x,cy_m,9))
 for tool in [guide,nut,screw,countersink(x,cy_m,tz,P['clamp_head_diameter'],3.3,-1)]:shell=shell.cut(tool)
 shoe=feature('MaleClampShoe'+str(i+1),box(x-6,cy_m-4,7.4,12,8,1.8),parts,(.35,.40,.44))
 pad=feature('MaleClampPad'+str(i+1),box(x-6,cy_m-4,6.6,12,8,.8),parts,(.10,.12,.14))
 clamp_parts.extend([shoe,pad])
# Broad replaceable translucent window accommodates LED placement variations.
window=box(-7.5,-55.5,12.8,15,15,10)
ledge=box(-9,-57,13.8,18,18,10)
shell=shell.cut(window.fuse(ledge))
# A 45-degree underside supports the LED recess, retaining a 0.6 mm flat land.
def window_wire(size,z):
 h=size/2;cy=-48
 pts=[V(-h,cy-h,z),V(h,cy-h,z),V(h,cy+h,z),V(-h,cy+h,z)]
 return Part.makePolygon(pts+[pts[0]])
window_taper=Part.makeLoft([window_wire(15,12.9),window_wire(16.8,13.8)],True,True)
window_ring=box(-9.4,-57.4,12.9,18.8,18.8,.9).cut(window_taper)
shell=shell.fuse(window_ring).cut(window_taper).removeSplitter()
feature('LEDWindowSupportTaper',window_ring)
base=shell.common(box(-150,-100,-30,300,150,30))
lid=shell.common(box(-150,-100,P['seam_gap'],300,150,40))
# Route the local seam through the USB centre for either board height.
tab_w=P['usb_seam_tab_width'];tab_y=P['usb_seam_inner_y'];gap=P['seam_gap']
if uz < 0:
 base=base.cut(box(-tab_w/2,-70,uz,tab_w,tab_y+70,30))
 tongue=shell.common(box(-tab_w/2+gap,-70,uz+gap,tab_w-2*gap,tab_y+70,1-uz-gap))
 lid=lid.fuse(tongue).removeSplitter()
else:
 lid=lid.cut(box(-tab_w/2,-70,gap,tab_w,tab_y+70,uz))
 tongue=shell.common(box(-tab_w/2+gap,-70,-.2,tab_w-2*gap,tab_y+70,uz+.2))
 base=base.fuse(tongue).removeSplitter()
feature('USBSeamTongue',tongue)

# Raised rigid pedestal: continuous perimeter walls and screw pillars support the proven keeper.
floorz=bz+wall;rail_top=pcbz-1.8
support=[]
# Low perimeter foundation connects the four seats while leaving the underside open.
for x in [-11.5,9.1]:support.append(box(x,usby-.8,floorz,2.4,L+1.6,rail_top-floorz))
for y in [usby-.8,usby+L-1.6]:support.append(box(-11.5,y,floorz,23,2.4,rail_top-floorz))
for x in [-8.8,6.4]:
 for y in [usby+.3,usby+L-2.7]:support.append(box(x,y,floorz,2.4,2.4,pcbz-floorz))
# Guides touch only the end corners, leaving the long solder-pad rows accessible.
for x in [-11.5,W/2+P['pcb_clearance']]:
 for y in [usby+.3,usby+L-2.7]:support.append(box(x,y,floorz,2.3,2.4,pcbz+.8-floorz))
# End stops flank USB and resist cable insertion/removal.
for x in [-8.8,6.4]:support.append(box(x,usby-1.6,floorz,2.4,1.6,pcbz+1-floorz))
support.append(box(-8.8,usby+L+P['pcb_clearance'],floorz,17.6,1.6,pcbz+1-floorz))
keeperz=pcbz+P['pcb_thickness']+P['keeper_gap'];kh=P['keeper_thickness'];cy=usby+L/2
for x in [-13,13]:support.append(Part.makeCylinder(3.5,keeperz-floorz,V(x,cy,floorz)))
cradle=union(support)
for x in [-13,13]:cradle=cradle.cut(Part.makeCylinder(.8,keeperz-floorz,V(x,cy,floorz+.6)))
base=base.fuse(cradle).removeSplitter()
# Open keeper frame: corner fingers retain the PCB; the centre and USB remain clear.
keep=[]
for x in [-11.5,9.3]:keep.append(box(x,usby+.2,keeperz,2.2,L+1.2,kh))
for y in [usby+L-.1]:keep.append(box(-11.5,y,keeperz,23,1.5,kh))
for x in [-9.5,7.8]:
 for y in [usby+.3,usby+L-2.7]:keep.append(box(x,y,keeperz,1.7,2.4,kh))
for x in [-13,13]:keep.append(Part.makeCylinder(3.5,kh,V(x,cy,keeperz)))
keeper=union(keep)
for x in [-13,13]:
 keeper=keeper.cut(Part.makeCylinder(1.1,kh+1,V(x,cy,keeperz-.5)))
ko=feature('BoardKeeper',keeper.removeSplitter(),parts,(.32,.37,.40));ko.Label='PCB keeper · two normal M2 x 8 screws · print flat'
# Alignment pins in separate flange pads away from seats.
for x,y in [(-79,-49),(79,-49)]:
 pad=Part.makeCylinder(3.0,7,V(x,y,-4))
 # Braces grow inward from the sidewall at 45 degrees in either print orientation.
 sign=1 if x>0 else -1
 def brace(z,outer_z):
  pts=[V(sign*76,y-3,z),V(sign*82,y-3,z),V(sign*82,y-3,outer_z)]
  wedge=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,6,0))
  footprint=Part.makeCylinder(3,abs(outer_z-z),V(x,y,min(z,outer_z)))
  return wedge.common(footprint).common(outer)
 base=base.fuse(brace(-4,-10))
 lid=lid.fuse(brace(3,9))
 base=base.fuse(pad.common(box(-150,-100,-30,300,150,30)))
 base=base.fuse(Part.makeCylinder(1.1,2.8,V(x,y,-.1)))
 lid=lid.fuse(pad.common(box(-150,-100,P['seam_gap'],300,150,30)))
 lid=lid.cut(Part.makeCylinder(1.3,3,V(x,y,0)))
# M2 closure clearance holes and flat-head seats; fully enclosed M2 pockets in lid.
for x,y in screws:
 base=base.cut(Part.makeCylinder(1.1,19,V(x,y,-17)))
 base=base.cut(countersink(x,y,bz,P['closure_head_diameter'],2.2,1))
 # Enclosed nut pockets: pause before their roof is printed in the roof-down lid.
 af=P['closure_nut_af'];nz=P['closure_nut_pocket_z'];nh=P['closure_nut_pocket_height'];nr=af/math.sqrt(3)
 along_y=abs(x)==79
 angle=math.pi/2 if along_y else 0
 pts=[V(x+nr*math.cos(angle+k*math.pi/3),y+nr*math.sin(angle+k*math.pi/3),nz) for k in range(6)]
 pocket=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,nh))
 lid=lid.cut(pocket)
base=base.removeSplitter();lid=lid.removeSplitter()
bo=feature('LowerShell',base,parts);bo.Label='Lower shell · raised ESP pedestal · split USB opening'
lo=feature('UpperShell',lid,parts);lo.Label='Upper shell · split USB notch · LED window · male clamps'
# Separate translucent insert, pressed into upper recess with a little adhesive if required.
wi=feature('LightWindow',box(-8.8,-56.8,13.95,17.6,17.6,1.7),parts,(.65,.9,.83));wi.Label='Optional translucent LED window'
if A.GuiUp:wi.ViewObject.Transparency=65
pcb=feature('ESP32BoardEnvelope',box(-W/2,usby,pcbz,W,L,P['pcb_thickness']),refs,(.12,.40,.32))
feature('ESP32ComponentKeepout',box(-6.5,usby+7,pcbz+1.6,13,12,3),refs,(.55,.56,.59))
usb_ref=feature('USBCEnvelope',box(-4.6,usby-1.7,pcbz+1.6,9.2,7.4,3.2),refs,(.72,.73,.76))
# Fit coupons isolate uncertain purchased-part dimensions before printing a full case.
gauge=base.common(box(-90,-26,-17,180,24,20))
gauge=gauge.fuse(box(-80,-22,-16,160,4,2.4)).removeSplitter()
go=feature('RearAlignmentGauge',gauge,hist);go.Label='PRINT FIRST · Four-plug lower alignment gauge'
gauge_top=lid.common(box(-90,-26,0,180,24,20)).fuse(box(-80,-22,12.6,160,4,2.4)).removeSplitter()
gt=feature('RearAlignmentGaugeUpper',gauge_top,hist)
bc=feature('BoardFitCoupon',base.common(box(-18,fr-1,-17,36,(usby+L+3)-(fr-1),34)),hist)
fc=feature('FemaleFitCoupon',base.common(box(22,-66,-17,28,24,26)),hist)
meta=D.addObject('App::FeaturePython','DesignParameters');hist.addObject(meta)
for k,v in P.items():
 if isinstance(v,list):meta.addProperty('App::PropertyString',k,'Dimensions');setattr(meta,k,str(v))
 else:meta.addProperty('App::PropertyFloat',k,'Dimensions');setattr(meta,k,v)
meta.addProperty('App::PropertyString','Status','Documentation');meta.Status='FIT PROTOTYPE. Regenerate using parameters.json + build.py; insertion depth and PCB details require physical checks.'
# Geometry validity and unintended assembly intersections.
report={'status':'fit prototype; physical fit not yet verified','parts':{},'collisions':[],'parameters':P}
for obj in [bo,lo,wi,ko,go,gt,bc,fc]+clamp_parts:
 s=obj.Shape;report['parts'][obj.Name]={'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds':str(s.BoundBox)}
 if not s.isValid() or len(s.Solids)!=1:raise RuntimeError('Invalid or disconnected '+obj.Name)
for a in [bo,lo,ko]+clamp_parts:
 for b in hardware+[pcb,usb_ref,D.getObject('ESP32ComponentKeepout')]:
  vol=a.Shape.common(b.Shape).Volume
  if vol>.005:report['collisions'].append({'a':a.Name,'b':b.Name,'volume_mm3':vol})
report['shell_overlap_mm3']=base.common(lid).Volume
report['keeper_overlap_mm3']=keeper.common(base).Volume+keeper.common(lid).Volume
report['clamp_shell_overlap_mm3']=sum(o.Shape.common(base).Volume+o.Shape.common(lid).Volume for o in clamp_parts)
(ROOT/'validation.json').write_text(json.dumps(report,indent=2))
if report['collisions'] or report['shell_overlap_mm3']>.005 or report['keeper_overlap_mm3']>.005 or report['clamp_shell_overlap_mm3']>.005:raise RuntimeError('Assembly interference; see validation.json')
for o in [bo,lo,wi,ko,go,gt,bc,fc]:
 m=Mesh.Mesh(o.Shape.tessellate(.08));m.write(str(ROOT/(o.Name+'.stl')))
for name,obj in [('MaleClampShoe',clamp_parts[0]),('MaleClampPad',clamp_parts[1])]:Mesh.Mesh(obj.Shape.tessellate(.08)).write(str(ROOT/(name+'.stl')))
Part.export([bo,lo,wi,ko]+clamp_parts,str(ROOT/'N64InputMod.step'))
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
