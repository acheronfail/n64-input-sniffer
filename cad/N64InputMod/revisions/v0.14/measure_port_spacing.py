"""Measure full-resolution shell apertures; no decimation or rescaling. mm."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
DT=np.dtype([('normal','<f4',3),('vertices','<f4',(3,3)),('attr','<u2')])
OLD=np.array([-63.7,-36.,36.,63.7])
results=[]
fig,axes=plt.subplots(2,1,figsize=(12,6),layout='constrained')
for ax,(name,delta,sign) in zip(axes,[('Top',(0,71.5,2.2),1),('Bottom',(0,103.5,-29.3),-1)]):
    tri=np.fromfile(ROOT/'reference'/f'{name}.stl',dtype=DT,offset=84)['vertices'].astype(float)
    tri+=delta
    keep=(tri[:,:,1].min(1)<8)&(tri[:,:,1].max(1)>-2)&(tri[:,:,0].min(1)<80)&(tri[:,:,0].max(1)>-80)&(tri[:,:,2].min(1)<12)&(tri[:,:,2].max(1)>-12)
    tri=tri[keep]
    samples=[[] for _ in OLD]
    for depth in [5.,6.,7.]:
        for z in np.arange(2.,10.01,.25)*sign:
            t=tri[(tri[:,:,2].min(1)<z)&(tri[:,:,2].max(1)>z)]
            # A non-degenerate triangle/plane intersection has exactly two ends.
            ends=[]
            for i,j in [(0,1),(1,2),(2,0)]:
                a,b=t[:,i],t[:,j]
                valid=(a[:,2]<z)!=(b[:,2]<z)
                f=(z-a[valid,2])/(b[valid,2]-a[valid,2])
                ends.append((np.flatnonzero(valid),a[valid]+f[:,None]*(b[valid]-a[valid])))
            ids=np.concatenate([i for i,p in ends]);p=np.concatenate([p for i,p in ends]);p=p[np.argsort(ids,kind='stable')].reshape(-1,2,3)
            p=p[p[:,:,1].min(1)<=depth]
            # Clip each section segment at the rear limit of the aperture rim.
            for i,j in [(0,1),(1,0)]:
                mask=p[:,i,1]>depth
                a=p[mask,i].copy();b=p[mask,j]
                f=(depth-a[:,1])/(b[:,1]-a[:,1])
                p[mask,i]=a+f[:,None]*(b-a)
            x=p[:,:,0].ravel()
            for k,c in enumerate(OLD):
                left=x[(x>c-13)&(x<c)];right=x[(x<c+13)&(x>c)]
                if not len(left) or not len(right):continue
                l,r=float(left.max()),float(right.min())
                samples[k].append({'z_mm':float(z),'depth_limit_y_mm':depth,'left_x_mm':l,'right_x_mm':r,'centre_x_mm':(l+r)/2})
                if depth==6:ax.plot([l,r],[z,z],'.',color='#207c83',markersize=2)
    centres=np.array([np.median([s['centre_x_mm'] for s in a]) for a in samples])
    origin=float(centres.mean());relative=centres-origin
    results.append({'scan':name+'.stl','translation_used_mm':delta,'aperture_centres_scan_x_mm':centres.tolist(),'symmetry_centre_x_mm':origin,'centres_relative_to_symmetry_mm':relative.tolist(),'sample_centre_ranges_mm':[[min(s['centre_x_mm'] for s in a),max(s['centre_x_mm'] for s in a)] for a in samples],'samples':samples})
    for c in OLD:ax.axvline(c+origin,color='#b74939',ls='--',lw=1)
    for c in [-64.04,-36,36,64.04]:ax.axvline(c+origin,color='#1973bc',lw=1)
    ax.set(title=f'{name}: full-resolution aperture edges',xlabel='Original scan X (mm)',ylabel='Aligned Z (mm)',xlim=(-80,80));ax.grid(alpha=.2)
centres=np.mean([r['centres_relative_to_symmetry_mm'] for r in results],axis=0)
report={'method':'Exact triangle/constant-Z intersections, aperture left/right midpoint, median over |Z|=2..10 mm in 0.25 mm steps and Y limits 5/6/7 mm. Independently remove each shell scan symmetry-centre offset. No scaling or rotation.','limitations':'Shell cut-outs, not installed socket/contact axes; sample spread is method sensitivity, not calibrated scan accuracy. Physical fit remains unverified.','scans':results,'mean_centres_relative_to_symmetry_mm':centres.tolist(),'symmetric_inner_half_spacing_mm':float((centres[2]-centres[1])/2),'symmetric_outer_half_spacing_mm':float((centres[3]-centres[0])/2),'previous_male_x_mm':OLD.tolist(),'recommended_male_x_mm':[-64.04,-36.,36.,64.04]}
(ROOT/'port-spacing-measurements.json').write_text(json.dumps(report,indent=2)+'\n')
fig.suptitle('N64 port spacing: v0.12 dashed red; proposed v0.13 blue (scan-centred)')
fig.savefig(ROOT/'port-spacing-comparison.png',dpi=180)
print(json.dumps({k:v for k,v in report.items() if k!='scans'},indent=2))
for s in results:print(s['scan'],s['aperture_centres_scan_x_mm'],s['sample_centre_ranges_mm'])
