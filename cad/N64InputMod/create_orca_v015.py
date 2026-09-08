"""Build a clean v0.15 multi-plate Orca project using the saved v0.12 profiles."""
from pathlib import Path
import zipfile,json,uuid,xml.etree.ElementTree as E,numpy as np
r=Path(__file__).resolve().parent;src=r/'print/full-enclosure-v0.15'
with zipfile.ZipFile(r/'N64InputMod-full-enclosure-v0.12-Orca-complete.3mf') as z:
 settings=json.loads(z.read('Metadata/project_settings.config'))
 content_types=z.read('[Content_Types].xml')
settings['project_name']='N64InputMod v0.15 - independent keepers - M2 nut pause'
assert settings['layer_height']=='0.16' and settings['initial_layer_print_height']=='0.2'
assert settings['machine_pause_gcode'].strip()=='M400 U1' and settings['print_sequence']=='by layer'
core='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';prod='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
E.register_namespace('',core);E.register_namespace('p',prod)
model=E.Element('{'+core+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US','requiredextensions':'p'})
for k,v in [('Application','OrcaSlicer-2.4.2'),('OrcaSlicer','2.4.2'),('BambuStudio:3mfVersion','1'),('Title',settings['project_name'])]:E.SubElement(model,'{'+core+'}metadata',name=k).text=v
resources=E.SubElement(model,'{'+core+'}resources');build=E.SubElement(model,'{'+core+'}build',{'{'+prod+'}UUID':str(uuid.uuid4())})
config=E.Element('config');plates=[]
def md(el,key,value):E.SubElement(el,'metadata',key=key,value=str(value))
for i,name in enumerate(['Both shells - PLA - insert six M2 nuts at pause','Eight port keepers and PCB keeper - PLA','Optional LED window - PETG'],1):
 plate=E.SubElement(config,'plate');plates.append(plate)
 for k,v in [('plater_id',i),('plater_name',name),('locked','false'),('bed_type',settings['curr_bed_type']),('filament_map_mode','Auto For Flush'),('gcode_file','')]:md(plate,k,v)
# Plate origins follow Orca's existing 256 mm multi-plate layout.
specs=[('LowerShell',1,128,65,5),('UpperShell',1,128,165,5)]
specs += [(f'MalePortKeeper{i+1}',2,70+40*i,70,5) for i in range(4)]
specs += [('FemalePortKeeper',2,70+40*i,130,5) for i in range(4)]
specs += [('BoardKeeper',2,128,180,5),('LightWindow',3,128,128,3)]
origins=[(0,0),(307.2,0),(0,-307.2)];entries={};manifest=[]
rels=E.Element('Relationships',xmlns='http://schemas.openxmlformats.org/package/2006/relationships')
assembly=E.SubElement(config,'assemble')
dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
for i,(name,plate,x,y,extruder) in enumerate(specs):
 child=2*i+1;oid=child+1
 a=np.fromfile(src/(name+'.stl'),dtype=dt,offset=84)['v'].astype(float)
 verts,indices=np.unique(a.reshape(-1,3),axis=0,return_inverse=True);tri=indices.reshape(-1,3)
 lo=verts.min(0);hi=verts.max(0);cz=(lo[2]+hi[2])/2;verts[:,2]-=cz
 path=f'3D/Objects/{name}_{i+1}.model'
 mesh='<mesh><vertices>'+''.join(f'<vertex x="{v[0]:.9g}" y="{v[1]:.9g}" z="{v[2]:.9g}"/>' for v in verts)+'</vertices><triangles>'+''.join(f'<triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}"/>' for t in tri)+'</triangles></mesh>'
 entries[path]=f'<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xmlns="{core}"><resources><object id="{child}" type="model">{mesh}</object></resources><build/></model>'.encode()
 obj=E.SubElement(resources,'{'+core+'}object',{'id':str(oid),'type':'model','{'+prod+'}UUID':str(uuid.uuid4())})
 comps=E.SubElement(obj,'{'+core+'}components');E.SubElement(comps,'{'+core+'}component',{'{'+prod+'}path':'/'+path,'objectid':str(child),'{'+prod+'}UUID':str(uuid.uuid4()),'transform':'1 0 0 0 1 0 0 0 1 0 0 0'})
 ox,oy=origins[plate-1];tf=f'1 0 0 0 1 0 0 0 1 {x+ox} {y+oy} {cz}'
 E.SubElement(build,'{'+core+'}item',{'objectid':str(oid),'transform':tf,'printable':'1','{'+prod+'}UUID':str(uuid.uuid4())})
 E.SubElement(rels,'Relationship',Target='/'+path,Id=f'rel-{i+1}',Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
 co=E.SubElement(config,'object',id=str(oid));md(co,'name',name+'.stl');md(co,'extruder',extruder)
 part=E.SubElement(co,'part',id=str(child),subtype='normal_part')
 for k,v in [('name',name+'.stl'),('matrix',f'1 0 0 0 0 1 0 0 0 0 1 {cz} 0 0 0 1'),('source_file',name+'.stl'),('source_object_id',0),('source_volume_id',0),('source_offset_x',0),('source_offset_y',0),('source_offset_z',cz)]:md(part,k,v)
 instance=E.SubElement(plates[plate-1],'model_instance')
 for k,v in [('object_id',oid),('instance_id',0),('identify_id',100+i)]:md(instance,k,v)
 E.SubElement(assembly,'assemble_item',object_id=str(oid),instance_id='0',transform=tf,offset='0 0 0')
 assert lo[0]+x>5 and hi[0]+x<251 and lo[1]+y>5 and hi[1]+y<251
 manifest.append({'name':name,'plate':plate,'object_id':oid,'centre_xy':[x,y],'height':hi[2],'bounds_xy':[[lo[0]+x,lo[1]+y],[hi[0]+x,hi[1]+y]],'extruder':extruder,'triangles':len(tri)})
for a in manifest:
 for b in manifest:
  if a['object_id']>=b['object_id'] or a['plate']!=b['plate']:continue
  assert any(a['bounds_xy'][1][k]+5<b['bounds_xy'][0][k] or b['bounds_xy'][1][k]+5<a['bounds_xy'][0][k] for k in range(2)),(a,b)
# Keep schema order conventional: object definitions, plates, assembly.
config[:]=config.findall('object')+plates+[assembly]
custom=E.Element('custom_gcodes_per_layer');pl=E.SubElement(custom,'plate');E.SubElement(pl,'plate_info',id='1')
E.SubElement(pl,'layer',top_z='14.12',type='1',extruder='1',color='',extra='Insert SIX M2 nuts into the upper-shell closure pockets. Seat every nut below the printed rim, then resume.',gcode=settings['machine_pause_gcode'])
E.SubElement(pl,'mode',value='SingleExtruder')
entries.update({'[Content_Types].xml':content_types,'3D/3dmodel.model':E.tostring(model,encoding='utf-8',xml_declaration=True),'3D/_rels/3dmodel.model.rels':E.tostring(rels,encoding='utf-8',xml_declaration=True),'Metadata/model_settings.config':E.tostring(config,encoding='utf-8',xml_declaration=True),'Metadata/project_settings.config':json.dumps(settings,indent=2).encode(),'Metadata/custom_gcode_per_layer.xml':E.tostring(custom,encoding='utf-8',xml_declaration=True),'_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'})
with zipfile.ZipFile(r/'N64InputMod-v0.15-Orca-input.3mf','w',zipfile.ZIP_DEFLATED) as z:
 for n,data in entries.items():z.writestr(n,data)
(r/'orca-v0.15-layout.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Created 12 objects on plates [2,9,1]; plate 1 pause at Z=14.12.')
