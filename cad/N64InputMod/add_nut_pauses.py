"""Add native Orca pause markers to plate 1, for the supplied fixed layer profile."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,json
r=Path(__file__).parent;p=r/'N64InputMod-full-enclosure-v0.12-Orca-complete.3mf'
with zipfile.ZipFile(p) as z:data={n:z.read(n) for n in z.namelist()}
s=json.loads(data['Metadata/project_settings.config'])
assert s['layer_height']=='0.16' and s['initial_layer_print_height']=='0.2'
assert s['print_sequence']=='by layer'
# Retain the source project's bed, filament and flushing settings.
data['Metadata/project_settings.config']=json.dumps(s,indent=2).encode()
config=E.fromstring(data['Metadata/model_settings.config'])
for plate_config in config.findall('plate'):
 if plate_config.find("metadata[@key='plater_id']").get('value')=='2':
  bed=plate_config.find("metadata[@key='bed_type']")
  if bed is None:bed=E.SubElement(plate_config,'metadata',key='bed_type')
  bed.set('value','Textured PEI Plate')
data['Metadata/model_settings.config']=E.tostring(config,encoding='utf-8',xml_declaration=True)
root=E.Element('custom_gcodes_per_layer');plate=E.SubElement(root,'plate');E.SubElement(plate,'plate_info',id='1')
for z,msg in [(5.48,'Insert FOUR M3 nuts into the clamp pockets; seat below the printed rim before resuming.'),(14.12,'Insert SIX M2 nuts into the enclosure screw pockets; seat below the printed rim before resuming.')]:
 E.SubElement(plate,'layer',top_z=str(z),type='1',extruder='1',color='',extra=msg,gcode=s['machine_pause_gcode'])
E.SubElement(plate,'mode',value='SingleExtruder')
data['Metadata/custom_gcode_per_layer.xml']=E.tostring(root,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in data.items():z.writestr(n,v)
print('Plate 1: native pause markers before layers at Z=5.48 and Z=14.12 mm.')
