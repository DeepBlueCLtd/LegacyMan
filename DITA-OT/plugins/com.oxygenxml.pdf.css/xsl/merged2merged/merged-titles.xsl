<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="xs" version="2.0">

  <xsl:variable name="deep-numbering" select="contains($css.params,'numbering=deep')" />

  <!-- Wraps the titles into a span - better styling options for numbering, one can isolate the number set as :before and the content in inline blocks for instance. -->
  <xsl:template
    match="*[contains(@class,' topic/topic ')]/*[contains(@class,' topic/title ')]|
           *[contains(@class,' topic/table ')]/*[contains(@class,' topic/title ')]|
           *[contains(@class,' topic/fig ')]/*[contains(@class,' topic/title ')]">
    <xsl:param name="is-in-list-of" select="false()"/>
    <xsl:copy>
      <xsl:apply-templates select="@*" />
      <xsl:choose>
        <xsl:when test="$is-in-list-of">
          <!-- Do not process PIs in list of figures/tables, they will be processed in the content. -->
          <ph class="- topic/ph topic/title-wrapper "><xsl:apply-templates select="node() except processing-instruction()" /></ph>
        </xsl:when>
        <xsl:otherwise>
          <ph class="- topic/ph topic/title-wrapper "><xsl:apply-templates /></ph>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>
  </xsl:template>
  
</xsl:stylesheet>