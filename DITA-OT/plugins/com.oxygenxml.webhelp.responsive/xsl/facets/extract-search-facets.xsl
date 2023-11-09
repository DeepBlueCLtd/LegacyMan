<?xml version="1.0" encoding="UTF-8"?>
<!--
    
Oxygen Webhelp plugin
Copyright (c) 1998-2023 Syncro Soft SRL, Romania.  All rights reserved.

-->
<xsl:stylesheet version="3.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/2005/xpath-functions">

  <xsl:output method="text" encoding="UTF-8"/>
  
  <!-- Matches the root node in the temporary ditamap.-->
  <xsl:template match="/">
    <!-- Holds the xml structure that will be serialized as JSON. -->
    <xsl:variable name="xml">
      <map>
        <array key="facets">
          <xsl:apply-templates select="//*[contains(@class, ' subjectScheme/hasInstance ')]/*[contains(@class, ' subjectScheme/subjectdef ')]" mode="facets"/>
          <xsl:apply-templates select="//*[contains(@class, ' subjectScheme/hasKind ')]/*[contains(@class, ' subjectScheme/subjectdef ')]" mode="facets"/>
          <xsl:apply-templates select="//*[contains(@class, ' subjectScheme/hasNarrower ')]/*[contains(@class, ' subjectScheme/subjectdef ')]" mode="facets"/>
        </array>
      </map>
    </xsl:variable>
    
    <xsl:value-of select="xml-to-json($xml, map { 'indent' : true() })"/>
  </xsl:template>

  <!-- Matches the subjectdef element and generate the xml structure for the JSON serialization. -->
  <xsl:template match="*[contains(@class, ' subjectScheme/subjectdef ')]" mode="facets">
    <xsl:variable name="key">
      <xsl:choose>
        <xsl:when test="exists(@keys)">
          <xsl:value-of select="@keys" /> 
        </xsl:when>
        <xsl:when test="exists(@keyref)">
          <xsl:value-of select="@keyref" />
        </xsl:when>
      </xsl:choose>
    </xsl:variable>
  
    <xsl:variable name="navtitle">
      <xsl:choose>
        <xsl:when test="exists(@navtitle)">
          <xsl:value-of select="@navtitle" /> 
        </xsl:when>
        <xsl:when test="exists(*[contains(@class, ' map/topicmeta ')]/*[contains(@class, ' topic/navtitle ')])">
          <xsl:value-of select="*[contains(@class, ' map/topicmeta ')]/*[contains(@class, ' topic/navtitle ')]" />
        </xsl:when>
      </xsl:choose>
    </xsl:variable>
    
    
    <map>
      <string key="key"><xsl:value-of select="$key" /></string>
      <string key="navtitle"><xsl:value-of select="$navtitle" /></string>
      <array key="categories">
          <xsl:apply-templates select="subjectdef" mode="facets" />
      </array>
    </map>
    
  </xsl:template>
  
</xsl:stylesheet>