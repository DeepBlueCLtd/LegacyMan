<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="xs">

  <!-- EXM-31518 Generate something that can be styled for learning and training lcTime -->
  <xsl:template match="*[contains(@class, ' learningBase/lcTime ')]">
    <span>
      <xsl:call-template name="commonattributes"/>
      <b>Time: </b>
      <xsl:choose>
        <xsl:when test="empty(node())">
          <xsl:value-of select="@value"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates/>
        </xsl:otherwise>
      </xsl:choose>
    </span>
  </xsl:template>
  
</xsl:stylesheet>