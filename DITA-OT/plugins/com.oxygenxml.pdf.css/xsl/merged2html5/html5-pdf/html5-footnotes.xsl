<?xml version="1.0" encoding="UTF-8"?>
<!-- 

  This stylesheet changes the default processing of the footnotes.
  For the PDF output they should not generate "a" links, but instead be a simple
  div that is floated as "footnote".

-->
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="xs">
  
  <!-- 
    Leave the footnote as a div, in the original context.
    In this way it can be styled with float: footnote.
  --> 
  <xsl:template match="*[contains(@class, ' topic/fn ')]">
    <span>
      <xsl:call-template name="commonattributes"/>
      <xsl:apply-templates/>
    </span>
  </xsl:template>
    
</xsl:stylesheet>