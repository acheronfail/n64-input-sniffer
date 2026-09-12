"""Full-resolution scan surface intersections for the extended v0.16 model.

Registration retains v0.13's intended tip engagement: adding 12 mm of missing
mating projection shifts both console scans +12 mm in Y. X is recentered using
the independently measured scan symmetry. This is an explicit assembly
assumption, not a measurement of installed socket/contact depth.
"""
from pathlib import Path
import json,numpy as np
from types import SimpleNamespace
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray,vtkPolyData
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersModeling import vtkCollisionDetectionFilter
vtk=SimpleNamespace(vtkPoints=vtkPoints,vtkCellArray=vtkCellArray,vtkPolyData=vtkPolyData,vtkTransform=vtkTransform,vtkCollisionDetectionFilter=vtkCollisionDetectionFilter)
from vtkmodules.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
r=Path(__file__).resolve().parent
p=json.loads((r/'parameters.json').read_text())
dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
def poly(tri):
 points=vtk.vtkPoints();points.SetData(numpy_to_vtk(np.ascontiguousarray(tri.reshape(-1,3)),deep=True))
 ids=np.arange(len(tri)*3,dtype=np.int64).reshape(-1,3)
 cells=vtk.vtkCellArray();cells.SetCells(len(tri),numpy_to_vtkIdTypeArray(np.column_stack([np.full(len(tri),3),ids]).ravel(),deep=True))
 out=vtk.vtkPolyData();out.SetPoints(points);out.SetPolys(cells);return out
models={}
for name in ['LowerShell','UpperShell','MaleConnectorAssembly']:
 tri=np.fromfile(r/(name+'.stl'),dtype=dt,offset=84)['v'].astype(float)
 models[name]=poly(tri)
measure=json.loads((r/'port-spacing-measurements.json').read_text())
report={'revision':'v0.16','registration_basis':__doc__,'mating_projection_mm':p['male_mating_length'],'decimation':False,'checks':{},'scan_transforms':{}}
for name,dy,dz in [('Top',71.5,2.2),('Bottom',103.5,-29.3)]:
 origin=next(s['symmetry_centre_x_mm'] for s in measure['scans'] if s['scan']==name+'.stl')
 delta=(-origin,dy+p['male_mating_length'],dz)
 report['scan_transforms'][name]=list(delta)
 tri=np.fromfile(r/'reference'/(name+'.stl'),dtype=dt,offset=84)['v'].astype(float)
 count=len(tri);tri+=delta
 # Keep whole original triangles intersecting an expanded assembly bounds box.
 mask=(tri[:,:,0].max(1)>-90)&(tri[:,:,0].min(1)<90)&(tri[:,:,1].min(1)<25)&(tri[:,:,1].max(1)>-75)&(tri[:,:,2].min(1)<20)&(tri[:,:,2].max(1)>-20)
 selected=tri[mask];scan=poly(selected)
 report['checks'][name]={'full_resolution_triangles':count,'ROI_triangles':len(selected),'models':{}}
 for model,obj in models.items():
  collision=vtk.vtkCollisionDetectionFilter();collision.SetInputData(0,obj);collision.SetInputData(1,scan)
  t0=vtk.vtkTransform();t1=vtk.vtkTransform();collision.SetTransform(0,t0);collision.SetTransform(1,t1)
  collision.SetBoxTolerance(.001);collision.SetCellTolerance(.000001);collision.SetNumberOfCellsPerNode(2);collision.SetCollisionModeToAllContacts();collision.Update()
  contacts=collision.GetNumberOfContacts()
  report['checks'][name]['models'][model]={'intersecting_triangle_pairs':int(contacts)}
  print(name,model,contacts,flush=True)
report['surface_intersections_pass']=all(m['intersecting_triangle_pairs']==0 for s in report['checks'].values() for m in s['models'].values())
report['limitations']='Surface intersection check under stated scan registration; no socket/contact geometry, insertion-depth certification, load test or calibrated scan accuracy.'
(r/'console-retention-fit.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['surface_intersections_pass'],report
