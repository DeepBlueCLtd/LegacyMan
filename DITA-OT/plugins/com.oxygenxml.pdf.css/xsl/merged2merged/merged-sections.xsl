<!-- 
    
    This stylesheet processes the sections from the main content.

-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="xs" version="2.0">
  
   <!-- 
      Generates the @id attributes if missing, so that the links from the TOC are working.
      There are links only to sections, not to their specializations! 
   -->
   <xsl:template match="*[@class = '- topic/section '][not(@id)]">
    <xsl:choose>
      <xsl:when test="$numbering-sections">
        <xsl:variable name="nm">
          <xsl:next-match/>
        </xsl:variable>
        <xsl:apply-templates select="$nm" mode="add-section-id">
          <xsl:with-param name="id" select="if(@id) then @id else generate-id(.)" />
        </xsl:apply-templates>
      </xsl:when>
      <xsl:otherwise>
        <xsl:next-match/>
      </xsl:otherwise>
    </xsl:choose>
   </xsl:template>
  
  <xsl:template match="*[@class = '- topic/section ']" mode="add-section-id">
        <xsl:param name="id"></xsl:param>
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:attribute name="id" select="$id"/>
      <xsl:copy-of select="node()"/>
    </xsl:copy>
  </xsl:template>
  
</xsl:stylesheet>
