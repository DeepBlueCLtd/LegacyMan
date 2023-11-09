<?xml version="1.0" encoding="UTF-8"?>
<!--
    
Oxygen Webhelp plugin
Copyright (c) 1998-2023 Syncro Soft SRL, Romania.  All rights reserved.

-->

<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    exclude-result-prefixes="#all"
    version="2.0">
    
    <xsl:import href="contextHelpMapDitaImpl.xsl"/>
    
    <!--
    XSLT extension point for the stylesheet used to produce the context-help-map.xml mapping file for context sensitive help system.
  -->
    <dita:extension 
        id="com.oxygenxml.webhelp.xsl.contextHelpMap" 
        behavior="org.dita.dost.platform.ImportXSLAction" 
        xmlns:dita="http://dita-ot.sourceforge.net"/>
  
  
    <xsl:import href="template:xsl/com.oxygenxml.webhelp.xsl.contextHelpMap"/>  
</xsl:stylesheet>