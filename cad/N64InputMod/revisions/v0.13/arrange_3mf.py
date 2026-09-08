from pathlib import Path
import zipfile,json,re,xml.etree.ElementTree as E
p=Path(__file__).resolve().parent/'N64InputMod-full-enclosure-v0.3.3mf'
with zipfile.ZipFile(p) as z:data={n:z.read(n) for n in z.namelist()}
c=E.fromstring(data['Metadata/model_settings.config'])
def md(el,key):return next(m.get('value') for m in el.findall('metadata') if m.get('key')==key)
objects={o.get('id'):(md(o,'name'),md(o,'extruder')) for o in c.findall('object')}
old=c.find('plate');instances={md(o,'object_id'):o for o in old.findall('model_instance')}
for o in c.findall('plate'):c.remove(o)
groups=[[],[],[]]
for oid,(name,extr) in objects.items():groups[int(extr)-1].append(oid)
positions={};names=['Enclosure and 4 shoes - rigid','4 soft pads - TPU','Optional LED window - translucent']
for i,ids in enumerate(groups):
 plate=E.SubElement(c,'plate')
 for key,val in [('plater_id',str(i+1)),('plater_name',names[i]),('locked','false'),('filament_map_mode','Auto For Flush'),('gcode_file','')]:E.SubElement(plate,'metadata',key=key,value=val)
 shoe_idx=0
 for oid in sorted(ids,key=int):
  name=objects[oid][0]
  if name.startswith('Lower'):x,y=128,70
  elif name.startswith('Upper'):x,y=128,140
  elif name.startswith('MaleClampShoe'):x,y=95+20*shoe_idx,190;shoe_idx+=1
  elif name.startswith('MaleClampPad'):x,y=307.2+98+20*shoe_idx,128;shoe_idx+=1
  else:x,y=128,128-307.2
  positions[oid]=(x,y);plate.append(instances[oid])
text=data['3D/3dmodel.model'].decode()
for oid,(x,y) in positions.items():
 pattern=r'(<item\b[^>]*\bobjectid="'+oid+r'"[^>]*\btransform=")[^"]*(")'
 text,n=re.subn(pattern,lambda m:m[1]+f'1 0 0 0 1 0 0 0 1 {x} {y} 0'+m[2],text)
 assert n==1,(oid,n)
data['3D/3dmodel.model']=text.encode();data['Metadata/model_settings.config']=E.tostring(c,encoding='utf-8',xml_declaration=True)
settings=json.loads(data['Metadata/project_settings.config']);settings['filament_colour']=['#424A52','#202020','#ACDFDA'];settings['project_name']='N64InputMod full enclosure v0.3';data['Metadata/project_settings.config']=json.dumps(settings,indent=2).encode()
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for name,content in data.items():z.writestr(name,content)
print('Separated plates:',[(names[i],len(v)) for i,v in enumerate(groups)])
