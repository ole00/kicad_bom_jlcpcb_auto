<!--XSL style sheet to convert EESCHEMA XML Partlist Format to grouped CSV BOM Format
    Copyright (C) 2014, Wolf Walter.
    Copyright (C) 2013, Stefan Helmert.
    Copyright (C) 2018, Kicad developers.
    Copyright (C) 2019, arturo182.
    Copyright (C) 2023, ole00.
    GPL v2.

    Based on: bom2grouped_csv_jlcpcb.xsl

	Functionality:
		Generation of JLCPCB PCBA compatible BOM

    How to use this is explained in eeschema.pdf chapter 14.  You enter a command line into the
    netlist exporter using a new (custom) tab in the netlist export dialog.
    The command line is
        xsltproc -o "%O.csv" "FullPathToFile/kicad_bom_jlcpcb_auto.xsl" "%I"
-->
<!--
    @package
    Generates a JLCPCB PCBA service compatible BOM

	Functionality:
    * Generate a comma separated value BOM list (csv file type).
    * Components are sorted by ref and grouped by same value+footprint
    * Unassigned Resistors and Capacitors are auto-selected from LCSC basic parts
      database file 'lcsc_default_components.xml'
    One value per line
    Fields are
    Comment,Designator,Footprint,LCSC

    The command line is
        xsltproc -o "%O.csv" "full_path/kicad_bom_jlcpcb_auto.xsl" "%I"
-->


<!DOCTYPE xsl:stylesheet [
  <!ENTITY nl  "&#xd;&#xa;">    <!--new line CR, LF, or LF, your choice -->
]>


<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output method="text"/>

	<xsl:variable name="digits" select="'1234567890'" />
	<!-- load LCSC default component database from .xml document-->
	<xsl:param name="lcsc" select="'lcsc_default_components.xml'"/>
	<xsl:variable name="docLcsc" select="document($lcsc)"/>

	<!-- for matching grouping of footprint and value combination -->
	<xsl:key name="partTypeByValueAndFootprint" match="comp" use="concat(footprint, '-', value)" />

	<!-- for table head and empty table fields-->
	<xsl:key name="headentr" match="field" use="@name"/>

	    <!-- main part -->
	<xsl:template match="/export">
	    <xsl:text>Comment,Designator,Footprint,LCSC</xsl:text>
	    <!-- all table entries -->
	    <xsl:apply-templates select="components"/>
	</xsl:template>

	<xsl:template match="components">
	    <!-- for Muenchian grouping of footprint and value combination -->
	    <xsl:for-each select="comp[count(. | key('partTypeByValueAndFootprint', concat(footprint, '-', value))[1]) = 1]">
		<xsl:sort select="@ref" />
		<xsl:text>&nl;</xsl:text>
		<xsl:text>"</xsl:text><xsl:value-of select="value"/><xsl:text>","</xsl:text>
		<!-- list of all references -->
		<xsl:for-each select="key('partTypeByValueAndFootprint', concat(footprint, '-', value))">
			<!-- strip non-digits from reference and sort based on remaining number -->
			<xsl:sort select="translate(@ref, translate(@ref, $digits, ''), '')" data-type="number" />
			<xsl:value-of select="@ref"/>
			<xsl:if test="position() != last()"><xsl:text>,</xsl:text></xsl:if>
		</xsl:for-each>
		<xsl:text>","</xsl:text>
		
		<xsl:value-of select="footprint"/><xsl:text>","</xsl:text>
		<!-- look for LCSC part number -->
		<xsl:choose>
			<!-- LCSC part number exists in its own field -->
			<xsl:when test="fields/field[@name='LCSC']!='' ">
				<xsl:value-of select="fields/field[@name='LCSC']"/>
			</xsl:when>
			<!-- LCSC part number not found -> search the default parts database -->
			<xsl:otherwise>
				<!-- check the database search is enabled -->
				<xsl:if test="(($docLcsc/lcsc/search[@enable='true']) or ($docLcsc/lcsc/search[@enable='yes']))">
					<!-- extract values from the current for-each scope (the BOM component) -->
					<xsl:variable name="v" select="value" />
					<xsl:variable name="fp" select="footprint" />
					<xsl:variable name="r" select="@ref" />

					<!-- search the part database: value, package and reference first letter must match -->
					<xsl:for-each select="$docLcsc/lcsc/comp">
						<xsl:if test="((starts-with($r,@ref)) and ((@value=$v) or (@altvalue1=$v) or (@altvalue2=$v)) and (contains($fp, @package)))">
							<xsl:value-of select="@pn" />
						</xsl:if>
					</xsl:for-each>
				</xsl:if>

			</xsl:otherwise>
		</xsl:choose>
		<!-- LCSC number closing double quote -->
		<xsl:text>"</xsl:text>
	    </xsl:for-each>
	</xsl:template>

	 <!-- table entries with dynamic table head -->
	<xsl:template match="fields">

	    <!-- remember current fields section -->
	    <xsl:variable name="fieldvar" select="field"/>

	    <!-- for all existing head entries -->
	    <xsl:for-each select="/export/components/comp/fields/field[generate-id(.) = generate-id(key('headentr',@name)[1])]">
		<xsl:variable name="allnames" select="@name"/>
		<xsl:text>,"</xsl:text>

		<!-- for all field entries in the remembered fields section -->
		<xsl:for-each select="$fieldvar">

		    <!-- only if this field entry exists in this fields section -->
		    <xsl:if test="@name=$allnames">
			<!-- content of the field -->
			<xsl:value-of select="."/>
		    </xsl:if>
		    <!--
			If it does not exist, use an empty cell in output for this row.
			Every non-blank entry is assigned to its proper column.
		    -->
                </xsl:for-each>

                <xsl:text>"</xsl:text>
	    </xsl:for-each>
	</xsl:template>

 </xsl:stylesheet>
