"""bryan-PC queue (needs cadquery/OCP): sew head_shell.stl / torso_cover.stl into B-rep and write *_occ.step.
Run from this folder: python export_covers_occ.py"""
from OCP.StlAPI import StlAPI_Reader
from OCP.TopoDS import TopoDS_Shape
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
for n in ("head_shell", "torso_cover"):
    s = TopoDS_Shape(); StlAPI_Reader().Read(s, n + ".stl")
    sw = BRepBuilderAPI_Sewing(0.01); sw.Add(s); sw.Perform()
    w = STEPControl_Writer(); w.Transfer(sw.SewedShape(), STEPControl_AsIs); w.Write(n + "_occ.step"); print("wrote", n + "_occ.step")
