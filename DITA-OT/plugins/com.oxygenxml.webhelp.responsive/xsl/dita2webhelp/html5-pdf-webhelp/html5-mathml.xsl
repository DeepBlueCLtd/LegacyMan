<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    exclude-result-prefixes="#all"
    version="2.0">

  <!-- 
    Overrides the org.dita-community.dita13.html\xsl\equation-d2html.xsl
    and adds the original element class attributes. In this way the element can 
    be styled using the same CSS rules for the html5 and direct - merged 
    based transformation. 
  -->
  <xsl:template match="*[contains(@class, ' equation-d/equation-inline ')]">
    <span>
      <xsl:call-template name="commonattributes"/>
      <!-- We need eqn-inline in the class value. Otherwise the above call template would be enough. -->
      <xsl:attribute name="class" select="concat(@class,' eqn-inline ',@outputclass)"/>
      <xsl:apply-templates>
        <xsl:with-param name="blockOrInline" tunnel="yes" select="'inline'"/>
      </xsl:apply-templates></span>
  </xsl:template>
  
  <xsl:template match="*[contains(@class, ' equation-d/equation-block ')]">
    <div>
      <xsl:call-template name="commonattributes"/>
      <!-- We need eqn-block in the class value. Otherwise the above call template would be enough. -->
      <xsl:attribute name="class" select="concat(@class,' eqn-block ',@outputclass)"/>
      <xsl:apply-templates>
        <xsl:with-param name="blockOrInline" tunnel="yes" select="'block'"/>
      </xsl:apply-templates>
    </div>
  </xsl:template>
  
  <!-- 
    Adds the scale attribute into the class attribute. In this way,
    codeblocks and equation-figure will be scaled.
  -->
  <xsl:template match="
    *[contains(@class, ' equation-d/equation-figure ')][@scale] |
    *[contains(@class, ' topic/pre ')][@scale]" priority="10">
    <xsl:variable name="scale" select="@scale"/>
    <xsl:variable name="result">
      <xsl:next-match/>
    </xsl:variable>
    <xsl:apply-templates select="$result" mode="process-scale-attribute">
      <xsl:with-param name="scale" select="$scale" tunnel="yes"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <xsl:template match="node() | @*" mode="process-scale-attribute">
    <xsl:copy>
      <xsl:apply-templates select="node() | @*" mode="#current"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="
    *[contains(@class, ' equation-d/equation-figure ')]/@class |
    *[contains(@class, ' topic/pre ')]/@class" mode="process-scale-attribute">
    <xsl:param name="scale" tunnel="yes"/>
    <xsl:choose>
      <xsl:when test="$scale">
        <xsl:variable name="css-class">
          <xsl:apply-templates select="$scale" mode="css-class"/>
        </xsl:variable>
        <xsl:attribute name="class" select="concat(., ' ', $css-class)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:next-match/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
</xsl:stylesheet>