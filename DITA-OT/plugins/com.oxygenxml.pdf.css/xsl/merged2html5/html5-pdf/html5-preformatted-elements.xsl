<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="xs"
  version="2.0">
  
  <!-- 
    Add line numbering on topic/pre elements.
  -->
  <xsl:template match="*[contains(@class, ' topic/pre ')][contains(@outputclass, 'show-line-numbers')]" priority="10">
    <xsl:variable name="nm">
      <xsl:next-match/>
    </xsl:variable>
    <xsl:apply-templates select="$nm" mode="line-numbering"/>
  </xsl:template>
  
  <xsl:template match="*[contains(@class, ' topic/pre ')]" mode="line-numbering">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <span class="+ topic/pre-new-line pre-new-line"/>
      <xsl:apply-templates mode="#current"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="*[starts-with(@class, 'hl-')]" mode="line-numbering">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates mode="#current"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="*[contains(@class, ' topic/pre ')]//text()" mode="line-numbering">
    <xsl:analyze-string regex="\n" select=".">
      <xsl:matching-substring>
        <xsl:value-of select="."/>
        <span class="+ topic/pre-new-line pre-new-line"/>
      </xsl:matching-substring>
      <xsl:non-matching-substring>
        <xsl:value-of select="."/>
      </xsl:non-matching-substring>
    </xsl:analyze-string>
  </xsl:template>
  
  <!--
    Show whitespaces on topic/pre elements.
  -->
  <xsl:template match="*[contains(@class, ' topic/pre ')][contains(@outputclass, 'show-whitespace')]">
    <xsl:variable name="nm">
      <xsl:next-match/>
    </xsl:variable>
    <xsl:apply-templates select="$nm" mode="show-whitespace"/>
  </xsl:template>
  
  <xsl:template match="*[contains(@class, ' topic/pre ')]" mode="show-whitespace">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates mode="#current"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="*[starts-with(@class, 'hl-')]" mode="show-whitespace">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates mode="#current"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="*[contains(@class, ' topic/pre ')]//text()" mode="show-whitespace" name="show-whitespace.text">
    <xsl:param name="text" select="."/>
    <xsl:variable name="head" select="substring($text, 1, 1)"/>
    <xsl:variable name="tail" select="substring($text, 2)"/>
    <xsl:choose>
      <xsl:when test="$head = (' ', '&#xA0;')">
        <xsl:text>&#xb7;</xsl:text>
      </xsl:when>
      <xsl:when test="$head = ('&#x9;')">
        <xsl:text>&#xb7;</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$head"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:if test="$tail">
      <xsl:call-template name="show-whitespace.text">
        <xsl:with-param name="text" select="$tail"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>
  
</xsl:stylesheet>