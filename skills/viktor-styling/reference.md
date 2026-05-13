## General
- Use simple but engineering tone no verbose on point to make application description
- It is Super Important if you are using an engineering equation to include the equation in latex in the app description, this will help user to know what is in the code.
- If the application has a vkt.Section, vkt.Step, vkt.Page, vkt.Tab the application title and introduction should not have orphan vkt.Text should have vkt.step_name.title or vkt.section_name.title = vkt.Text("# Title") this is **Important** otherwise the app will fail.

## vkt.Text - App Title, Subtitles, Descriptions
A vkt.Text field that can be used to display a static text (max. 1800 characters) as follows:

```python
class Parametrization(vkt.Parametrization):
    not_in_params = vkt.Text('My static text')
```
IMPORTANT: The value of the vkt.Text fields can be styled using Markdown:
```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    info1 = vkt.Text("""
Please select the wing model below ✈️
- 2D: Select 2D to model an **infinite wing**
- 3D: Select 3D to model a *finite wing*, along with the aspect ratio
    1. High AR for slender wings
    2. Low AR for delta wings
""")
    model = vkt.OptionField("Wing model", options=["2D", "3D"])
    ar = vkt.NumberField("AR", variant="slider", min=1, max=30)
    info2 = vkt.Text("""
### Block / in-line math

#### Lift Coefficient

$$
L = \\frac{1}{2} \\rho v^2 S C_L
$$

where $\\rho = \\frac{m}{v}$. Read more about this equation on
[this page](https://en.wikipedia.org/wiki/Lift_coefficient).

### Horizontal rules

---
---

and another...

---

# Heading level 1
## Heading level 2
""")
```
### Rendering Equations in LaTeX

* Always include engineering or math equations in **LaTeX** inside the app description for clarity.  
* Use `$$ ... $$` for block equations and `$ ... $` for inline equations.  
* **Preferred:** write equations as block equations, since they will be displayed vertically, one on top of the other, which improves readability.  
* For block equations, always put them on their **own line with blank lines before and after**.  

* Example of **block equation**:

```python
info = vkt.Text("""
### Bearing Capacity Equation

$$
Q_b = q_b \cdot A_p, \quad q_b = N_q \cdot \sigma'_v
$$

where $N_q$ is the bearing capacity factor.
""")
```

This will render as:

$$
Q_b = q_b \cdot A_p, \quad q_b = N_q \cdot \sigma'_v
$$

* Example of **inline equation**:

```python
info = vkt.Text("Soil stress is given by $\sigma'_v = \gamma' L$.")
```

This will render as:

Soil stress is given by \$\sigma'\_v = \gamma' L\$.

* Use valid LaTeX commands (`\bar{}`, `\overline{}`, `\dfrac{}`, etc.) instead of custom shortcuts. Invalid commands will break rendering.

**Important when writing LaTeX in Python strings**  
In normal Python strings, some sequences are treated as escapes:
- `\a` → bell character (so `\alpha` → `lpha`)  
- `\t` → tab (so `\tan` → tab + `an`)  
- `\n` → newline (so `N_c` or `\nabla` break)  

This corrupts LaTeX inside `vkt.Text`.  

**Fix**:  
Use a **raw string literal** `r""" ... """` or double backslashes `\\` to preserve LaTeX.


## Important for vkt.Text
Identation can make the title and app description to look bad, here and example:
```python
class Parametrization(vkt.Parametrization):
    ...
    # Example on how not to make the title and description
    intro = vkt.Text(
        """
        # Monopile Foundation Checker & Iterations

        This app checks whether a single vertical load is supported by a single
        monopile (axial compression) based on simplified geotechnical assumptions.
        """
    )
```
so the correct way will be 
```python
import textwrap

class Parametrization(vkt.Parametrization):
    intro = vkt.Text(textwrap.dedent("""\
        # Monopile Foundation Checker & Iterations

        This app checks whether a single vertical load is supported by a single
        monopile (axial compression) based on simplified geotechnical assumptions.
    """))
```
It is Super Important if you are using an engineering equation to include the equation in latex in the app description.

also if the app uses a vkt.Section or vkt.Step or vkt.Tab or vkt.Page the vkt.Text can't be orphan.

Important: This will fail because of how viktor works
```python
class Parametrization(vkt.Parametrization):
    intro = vkt.Text(textwrap.dedent("""
        # Footing Foundation Checker & Iterations.
    """))
    soil = vkt.Section('Soil parameters')
```
Correct way if a Section or Page, Step, Tab is needed:
```python
class Parametrization(vkt.Parametrization):
    app_outline = vkt.Section('Application Description') 
    app_outline.intro = vkt.Text(textwrap.dedent("""
        # Footing Foundation Checker & Iterations.
    """)) # no orphan vkt.Text
    soil = vkt.Section('Soil parameters')
```


## **Correct Usage of Titles in Parametrization with vkt.Section, vkt.Pages, vkt.Tab, vkt.Step [Important]**

Always place vkt.Text at the **lowest level inside a container**, such as inside a single Section. Never attach vkt.Text directly to Step, Page, or Tab, because the application will fail. The correct approach is to nest vkt.Text inside a Section.


✅ Correct pattern:

```
class Parametrization(vkt.Parametrization):
    step1 = vkt.Step('Step 1', views=['my_view1'])
    step1.inputs = vkt.Section('Inputs')
    step1.inputs.intro = vkt.Text("""
        # Items and Target
        Enter the required data below.
    """)
```

```
class Parametrization(vkt.Parametrization):
    page_a = vkt.Page('Forecast', views=['my_view1', 'my_view2'])
    page_a.tab_a = vkt.Tab('Series')
    page_a.tab_a.series = vkt.Section('Series data')
    page_a.tab_a.series.intro = vkt.Text("""
        ## Series
        Enter the observed series values, one row per period.
    """)
```

⚠️ This is **wrong**. The application will fail if you try to assign vkt.Text directly to a container like Section, Page, Tab, or Step.

### **Wrong examples**

```python
class Parametrization(vkt.Parametrization):
    # Step with bound view
    step1 = vkt.Step('step1', views=['my_view1'])
    step1.title = vkt.Text("""# Items and Target""")  # ❌ WRONG

    # Section under the step
    step1.inputs = vkt.Section('inputs')
```

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    # Page with two views bound
    page_a = vkt.Page('Forecast', views=['my_view1', 'my_view2'])
    page_a.title = vkt.Text('## Forecast')  # ❌ WRONG

    # Tab A: Series input table
    page_a.tab_a = vkt.Tab('Series')
    page_a.tab_a.title = vkt.Text('## Series')  # ❌ WRONG
    page_a.tab_a.series = vkt.Section('Series data')
    page_a.tab_a.series.title = vkt.Text('Enter observed series values, one row per period')
```

## Manual line break
Line breaks can be used to improve how the the fields from the parametrization are arranged
```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    n1 = vkt.NumberField('N1')
    n2 = vkt.NumberField('N2')
    lb = vkt.LineBreak()  # split the fields in 2 pairs
    n3 = vkt.NumberField('N3')
    n4 = vkt.NumberField('N4')
```
## vkt.Text With Sections, Tabs, and Steps

When the parametrization uses containers such as `vkt.Tab`, `vkt.Step`, or `vkt.Section`, keep explanatory text and inputs inside the relevant container. Avoid orphan `vkt.Text` or input fields at the root level when the rest of the form is organized in containers.

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    tab_1 = vkt.Tab('Tab 1')
    tab_1.inputs = vkt.Section('Tab 1 inputs')
    tab_1.inputs.title = vkt.Text("## Tab 1 - Title")
    tab_1.inputs.input_1 = vkt.TextField('This is a text field')
    tab_1.inputs.input_2 = vkt.NumberField('This is a number field')

    tab_2 = vkt.Tab('Tab 2')
    tab_2.inputs = vkt.Section('Tab 2 inputs')
    tab_2.inputs.title = vkt.Text("## Tab 2 - Title")
    tab_2.inputs.input_1 = vkt.TextField('Text field in Tab 2')
    tab_2.inputs.input_2 = vkt.NumberField('Number field in Tab 2')
```

```python
class Parametrization(vkt.Parametrization):
    step_1 = vkt.Step("Step 1 - Input Your Data!")
    step_1.inputs = vkt.Section("Input data")
    step_1.inputs.intro = vkt.Text("""
# STAAD Design Ratio Analyzer
This app allows you to visualize a heat map from your STAAD.PRO model results.
You can filter and group them based on cross sections and visualize how they are distributed.""")
    step_1.inputs.table_input = vkt.Text("""
## 1.0 Create the Input Table!
Paste the design ratio data from your STAAD.PRO model!""")

    step_2 = vkt.Step("Step 2 - Post-Processing")
    step_2.filters = vkt.Section("Filters")
    step_2.filters.process = vkt.Text("""
## 2.0 Filter and Group
Group or filter by a specific cross section.
Use the options below to customize your view.
If you want to list all cross-sections after selecting one, you can select the "All" option!
""")
    step_2.filters.group = vkt.BooleanField("Group by cross-section")
    step_2.filters.ln_break = vkt.LineBreak()
    step_2.filters.cross_section = vkt.OptionField(
        "Filter by cross-section",
        options=["All"],
    )

class Controller(vkt.Controller):
    parametrization = Parametrization
```

## When to Split the Application Layout?
For simple application try to avoid spliting the application in vkt.Step, vkt.Section, vkt.Pages.
RULES:
    - if the are clear distinction between the inputs and they can be grouped in section of different kind you can ad a vkt.Section, for example a section for Geometry inputs, a section for Material inputs, a section for Loads.
    - if the application require separated results, for examples one structure results, an geotechnical results you can split the application in steps. or if there is a clear dependency between one part of the application and other and separated views and inputs are needed!
    - For the other type of grouping vkt.Tabs, vkt.Pages it is better to use it if the user explicitly ask for it.

Note: Refer back to the VIKTOR Core skill for more information about splitting the application with `vkt.Step`, `vkt.Tab`, `vkt.Page`, and `vkt.Section`.
