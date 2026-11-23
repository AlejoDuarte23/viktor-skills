import json
import os
from html import escape
from math import hypot, isfinite
from pathlib import Path
from typing import TypedDict

import viktor as vkt


LOAD_FIELDS = ("axial_kn", "shear_x_kn", "shear_z_kn", "moment_x_knm", "moment_z_knm")
DEFAULT_COMBINATIONS = [
    {"combination": "LC-01", "axial_kn": 180, "shear_x_kn": 18, "shear_z_kn": 24, "moment_x_knm": 21, "moment_z_knm": 28},
    {"combination": "LC-02", "axial_kn": 240, "shear_x_kn": 24, "shear_z_kn": 32, "moment_x_knm": 20, "moment_z_knm": 21},
    {"combination": "LC-03", "axial_kn": -65, "shear_x_kn": -45, "shear_z_kn": 24, "moment_x_knm": -9, "moment_z_knm": 12},
]


class LoadCombination(TypedDict):
    name: str
    axial_kn: float
    shear_x_kn: float
    shear_z_kn: float
    moment_x_knm: float
    moment_z_knm: float


class CombinationResult(LoadCombination):
    shear_kn: float
    bending_knm: float


def plate_dimensions(width_mm: int, depth_mm: int, thickness_mm: int) -> dict[str, int]:
    dimensions = {
        "plate_width_mm": width_mm,
        "plate_depth_mm": depth_mm,
        "plate_thickness_mm": thickness_mm,
    }
    for value, (low, high) in zip(dimensions.values(), ((180, 650), (180, 650), (8, 75))):
        if type(value) is not int or not low <= value <= high:
            raise vkt.UserError("Enter whole numbers within the plate dimension ranges.")
    return dimensions


def load_combinations(rows: list[dict[str, str | int | float | None]]) -> list[LoadCombination]:
    if not rows or len(rows) > 30:
        raise vkt.UserError("Enter between 1 and 30 load combinations.")

    combinations: list[LoadCombination] = []
    names: set[str] = set()
    for index, row in enumerate(rows, start=1):
        name = str(row.get("combination") or "").strip()
        if not name or len(name) > 32 or name.casefold() in names:
            raise vkt.UserError(f"Give load combination {index} a unique name of up to 32 characters.")
        names.add(name.casefold())
        values = [row.get(field) for field in LOAD_FIELDS]
        if any(not isinstance(value, (int, float)) or not isfinite(value) for value in values):
            raise vkt.UserError(f"Enter a valid number in each load column for {name}. Use zero for unused loads.")
        axial, shear_x, shear_z, moment_x, moment_z = [float(value) for value in values]
        combinations.append({
            "name": name, "axial_kn": axial, "shear_x_kn": shear_x, "shear_z_kn": shear_z,
            "moment_x_knm": moment_x, "moment_z_knm": moment_z,
        })
    return combinations


def calculate(rows: list[LoadCombination]) -> list[CombinationResult]:
    results: list[CombinationResult] = []
    for row in rows:
        shear = hypot(row["shear_x_kn"], row["shear_z_kn"])
        bending = hypot(row["moment_x_knm"], row["moment_z_knm"])
        if not isfinite(shear) or not isfinite(bending):
            raise vkt.UserError(f"Enter smaller load values for {row['name']}.")
        results.append({**row, "shear_kn": shear, "bending_knm": bending})
    return results


class Parametrization(vkt.Parametrization):
    combinations = vkt.Table(
        "Load combinations",
        default=DEFAULT_COMBINATIONS,
        description="Enter the applied loads. Positive N is compression. Use zero for unused loads.",
    )
    combinations.combination = vkt.TextField("Combination")
    combinations.axial_kn = vkt.NumberField("N [kN]")
    combinations.shear_x_kn = vkt.NumberField("Vx [kN]")
    combinations.shear_z_kn = vkt.NumberField("Vz [kN]")
    combinations.moment_x_knm = vkt.NumberField("Mx [kN·m]")
    combinations.moment_z_knm = vkt.NumberField("Mz [kN·m]")

    plate_width_mm = vkt.IntegerField("Plate width", default=360, min=180, max=650, visible=False)
    plate_depth_mm = vkt.IntegerField("Plate depth", default=280, min=180, max=650, visible=False)
    plate_thickness_mm = vkt.IntegerField("Plate thickness", default=24, min=8, max=75, visible=False)


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.WebView("Geometry", duration_guess=1)
    def show_plate(self, params, **kwargs):
        dimensions = plate_dimensions(params.plate_width_mm, params.plate_depth_mm, params.plate_thickness_mm)
        template = Path(__file__).with_name("plate.html").read_text(encoding="utf-8")
        sdk_url = escape(os.environ["VIKTOR_JS_SDK_PATH"] + "v1.js", quote=True)
        html = template.replace("__VIKTOR_SDK__", sdk_url)
        return vkt.WebResult(html=html.replace("__PLATE_DIMENSIONS__", json.dumps(dimensions, allow_nan=False)))

    @vkt.DataView("Results", duration_guess=1)
    def show_summary(self, params, **kwargs):
        results = calculate(load_combinations(params.combinations))
        axial = max(results, key=lambda row: abs(row["axial_kn"]))
        shear = max(results, key=lambda row: row["shear_kn"])
        bending = max(results, key=lambda row: row["bending_knm"])
        return vkt.DataResult(vkt.DataGroup(
            vkt.DataItem("Load combinations", len(results)),
            vkt.DataItem("Largest axial magnitude", abs(axial["axial_kn"]), suffix="kN", explanation_label=axial["name"]),
            vkt.DataItem("Largest resultant shear", shear["shear_kn"], suffix="kN", explanation_label=shear["name"]),
            vkt.DataItem("Largest resultant bending", bending["bending_knm"], suffix="kN·m", explanation_label=bending["name"]),
            vkt.DataItem("Scope", "Applied loads only"),
        ))
