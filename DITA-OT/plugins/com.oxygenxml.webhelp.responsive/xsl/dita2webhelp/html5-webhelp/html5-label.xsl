<?xml version="1.0" encoding="UTF-8"?>
<!--
    
Oxygen WebHelp Plugin
Copyright (c) 1998-2023 Syncro Soft SRL, Romania.  All rights reserved.

-->

<!--
  Generates a label component for each <keyword> that has 
  the @outputclass='label'. 
-->

<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  xmlns:xhtml="http://www.w3.org/1999/xhtml"
  xmlns:oxygen="http://www.oxygenxml.com/functions"
  exclude-result-prefixes="xs xhtml" version="2.0">
  
  <!-- Create a <div> which will contain all labels if at least one <keyword> with the @outputclass='label'exists -->
  <xsl:template match="*[contains(@class, ' topic/prolog ')][oxygen:getParameter('webhelp.labels.generation.mode') = 'keywords-label']">
    <xsl:if test="descendant::*[contains(@class, ' topic/keyword ')][@outputclass = 'label']">
      <div class="wh-label-container" role="group" aria-label="Labels">
        <xsl:apply-templates select="descendant::*[contains(@class, ' topic/keyword ')][@outputclass = 'label']" mode="labels-support" />
      </div>
    </xsl:if>
  </xsl:template>
  
  <!-- Create a <div> which will contain a label for every <keyword> that exists -->
  <xsl:template match="*[contains(@class, ' topic/prolog ')][oxygen:getParameter('webhelp.labels.generation.mode') = 'keywords']">
    <xsl:if test="descendant::*[contains(@class, ' topic/keyword ')]">
      <xsl:choose>
        <xsl:when test="descendant::*[contains(@class, ' topic/keyword ')][@outputclass = 'label']">
          <div class="wh-label-container" role="group" aria-label="Labels">
            <xsl:apply-templates select=".[@outputclass = 'label']" mode="labels-support" />
          </div>
        </xsl:when>
        <xsl:otherwise>
          <div class="wh-label-container" role="group" aria-label="Labels">
            <xsl:apply-templates select="." mode="labels-support" />
          </div>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!-- Matches the keyword that will be displayed as a label -->
  <xsl:template match="*[contains(@class, ' topic/keyword ')]" mode="labels-support">
    <a class="wh-label"
      href="{concat($PATH2PROJ, 'search.html?searchQuery=label:', normalize-space(text()))}">
      <span>
        <xsl:value-of select="text()" />
      </span>
    </a>
  </xsl:template>

</xsl:stylesheet>
