<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">

    <!-- We need this element in the output, it may contain the navtitle. -->    
    <xsl:template match="*[contains(@class, ' topic/titlealts ')]" >
        <div>
          <xsl:call-template name="commonattributes"/>      
          <xsl:apply-templates/>
        </div>
    </xsl:template>
    
  <xsl:template match="*[contains(@class, ' topic/titlealts ')]/*[contains(@class, ' topic/navtitle ')]" priority="2" >
      <div>
          <xsl:call-template name="commonattributes"/>      
          <xsl:apply-templates/>
        </div>
    </xsl:template>

    <!-- Ignore other children of titlealts. -->
  <xsl:template match="*[contains(@class, ' topic/titlealts ')]/*"  />
      
    
</xsl:stylesheet>