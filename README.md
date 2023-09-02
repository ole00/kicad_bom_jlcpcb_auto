# kicad_bom_jlcpcb_auto
A KiCad BOM script for generating JLCPCB PCBA-compatible files with R and C part auto selection.

This KicCad BOM script is based on the following script:
https://gist.github.com/arturo182/a8c4a4b96907cfccf616a1edb59d0389

The database of basic parts was extracted from this source:
https://github.com/yaqwsx/jlcparts

Introduction
----------------------
This BOM generator adds JLCPCB/LCSC part number auto selection functionality
for basic SMT components. Currently it auto selects capacitors and resistors
from the database of **basic** parts (no extra fees are charged when using those
components during JLCPCB SMA). The default component database contains only 
basic parts, no extened parts are autoselected unless you manually add them
to the lcsc_default_components.xml database.

The auto selection decision works like this (all following conditions must be met)
* LCSC field must be empty (LCSC field is undefined in KiCad on that part)
* part reference must match "C" for capacitors and "R" for resistors (case sensitive)
* the package in lcsc_default_components.xml must match the footprint of the component
* the value of the component (as defined in KiCad) must match value (or alternative values)
  as defined in lcsc_default_components.xml


In another words, the auto assignment will not work on parts:
* that do have LCSC field already defined and filled in with a component reference
* that are not Resitors or Capacitors (let's say Inductors or Diodes)
* that have different package (for example 0201)
* that have unmatched value (like XK, instead of 10k for example)

Tips:
* If you want to check the full list of the default components, then take a look
at the lcsc_default_components.xml file. 

* If you want to check the full list of basic parts there is a basic_parts.csv file
in 'tools' subdirectory provided for your convenience.

* You can update the contents of the lcsc_default_components.xml and basic_parts.csv
  files by using python3 tools located in 'tools' subdirectory.
  
Installation and usage
-----------------------------
* clone this repo locally to your computer
* run KiCad Schematic editor
* enter: Menu->Tools->Generate BOM...
* near the bottom left corner of the dialogue press the small [+] button
* navigate through filesystem and select kicad_bom_jlcpcb_auto.xsl file from the
  cloned git repository
* when asked, give the new exporter a name or use the default one
* the new exporter is added to the list, select it and click the [Generate] button
  to create the <project_name>.csv file with the BOM contents
