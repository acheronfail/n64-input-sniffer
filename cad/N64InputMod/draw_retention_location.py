from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
r=Path(__file__).resolve().parent
d=json.loads((r/'retention-location-section.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig,(ax,detail)=plt.subplots(1,2,figsize=(15,7),gridspec_kw={'width_ratios':[1.55,1]})
fig.patch.set_facecolor('#f5f7fa')
fig.suptitle('Where I interpreted your 6 mm measurement',fontsize=20,fontweight='bold',x=.055,ha='left',y=.97)
fig.text(.055,.908,'Side section through one male connector • flat side up, rounded side down',fontsize=12,color='#45566b')
nose=7+36**2/1450;point=nose-6
# Exact scan triangle intersections with the connector centre plane; scan X recentered by measured symmetry.
dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
tri=np.fromfile(r/'reference/Bottom.stl',dtype=dt,offset=84)['v'].astype(float)
measure=json.loads((r/'port-spacing-measurements.json').read_text())
origin=next(s['symmetry_centre_x_mm'] for s in measure['scans'] if s['scan']=='Bottom.stl')
tri+=(-origin,103.5,-29.3)
t=tri[(tri[:,:,0].min(1)<36)&(tri[:,:,0].max(1)>36)&(tri[:,:,1].min(1)<14)&(tri[:,:,1].max(1)>-12)&(tri[:,:,2].max(1)>-22)]
ends=[]
for i,j in [(0,1),(1,2),(2,0)]:
 a,b=t[:,i],t[:,j];mask=(a[:,0]<36)!=(b[:,0]<36)
 f=(36-a[mask,0])/(b[mask,0]-a[mask,0])
 ends.append((np.flatnonzero(mask),a[mask]+f[:,None]*(b[mask]-a[mask])))
ids=np.concatenate([i for i,p in ends]);p=np.concatenate([p for i,p in ends]);p=p[np.argsort(ids,kind='stable')].reshape(-1,2,3)
segments=p[:,:,1:]
for a in [ax,detail]:
 a.set_facecolor('white')
 for name,col in [('LowerShell','#397baa'),('UpperShell','#397baa')]:
  for w in d[name]:
   w=np.array(w);a.plot(w[:,0],w[:,1],color=col,lw=1.8)
 for w in d['MalePort3']:
  w=np.array(w);a.fill(w[:,0],w[:,1],color='#dce1e7',zorder=3);a.plot(w[:,0],w[:,1],color='#505c6a',lw=2,zorder=4)
 a.add_collection(LineCollection(segments,colors='#e58a35',linewidths=2.2,zorder=5))
 a.plot(point,-11,'s',color='#d62f48',markersize=7,zorder=7)
 a.set_aspect('equal');a.spines[['top','right']].set_visible(False)
 a.set_xlabel('Y position in CAD (mm)');a.set_ylabel('Z position (mm)')
 a.grid(alpha=.14)
ax.set_xlim(-32,13);ax.set_ylim(-22,19)
ax.annotate('Rear / wiring end\n(in my interpretation)',xy=(nose-33.5,-2),xytext=(-31,15),fontsize=10,ha='left',arrowprops={'arrowstyle':'->','color':'#45566b'})
ax.annotate('Front / mating face\n(in my interpretation)',xy=(nose,5),xytext=(-5,16),fontsize=10,ha='left',arrowprops={'arrowstyle':'->','color':'#45566b'})
ax.annotate('Current case',xy=(-12,-15.8),xytext=(-30,-20),color='#397baa',arrowprops={'arrowstyle':'->','color':'#397baa'})
ax.annotate('My assumed divot',xy=(point,-11),xytext=(-20,-7),color='#d62f48',arrowprops={'arrowstyle':'->','color':'#d62f48'},zorder=8)
ax.annotate('',xy=(point,12.7),xytext=(nose,12.7),arrowprops={'arrowstyle':'<->','color':'#d62f48'})
ax.text((point+nose)/2,13.3,'6 mm',color='#d62f48',ha='center',fontsize=11)
for y in [point,nose]:ax.plot([y,y],[11,13],color='#d62f48',lw=.9,ls=':')
detail.set_xlim(-4,9);detail.set_ylim(-17,-7)
detail.set_title('Detail at the marked position',fontsize=13,pad=14)
# Illustrative tab, not a completed design.
detail.add_patch(Rectangle((-4,-13.4),point+6,2.18,facecolor='#4d94c1',alpha=.23,edgecolor='#397baa',linestyle='--',zorder=6))
detail.annotate('',xy=(point,-6.5),xytext=(point,-15),arrowprops={'arrowstyle':'->','lw':2,'color':'#d62f48'},zorder=7)
detail.text(-3.7,-8.1,'Connector housing',color='#505c6a',fontsize=10)
detail.annotate('Scanned console rim',xy=(3,-12.3),xytext=(3.0,-16),fontsize=10,color='#ba641b',ha='center',arrowprops={'arrowstyle':'->','color':'#ba641b'})
detail.text(-3.7,-14.1,'Example printed tab',color='#397baa',fontsize=9)
fig.text(.055,.08,'Grey = supplied connector CAD     Blue = current case / illustrative tab     Orange = console shell scan',fontsize=11,color='#45566b')
fig.text(.055,.038,'This is my interpretation—not a confirmed screw location. Scan alignment is approximate; the real divot is not modelled in the STEP file.',fontsize=10,color='#45566b')
fig.subplots_adjust(top=.85,bottom=.18,left=.055,right=.98,wspace=.26)
fig.savefig(r/'male-screw-location-explained.png',dpi=160)
