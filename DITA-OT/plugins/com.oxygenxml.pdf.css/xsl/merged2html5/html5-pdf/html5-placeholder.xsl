<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="xs"
  version="2.0">
  
  <!--
    We need to store Table and Figure IDs contained in appendix and matter
    in order to use a custom numbering in the figurelist/tablelist.
  -->
  <xsl:key name="appendixFigureTableIds" match="//*[contains(@topicrefclass , 'bookmap/appendix')]//*[contains(@class , 'topic/table') or contains(@class , 'topic/fig')]" use="@id"/>
  <xsl:key name="matterFigureTableIds" match="//*[contains(@class , 'topic/topic')][@is-frontmatter or @is-backmatter]//*[contains(@class , 'topic/table') or contains(@class , 'topic/fig')]" use="@id"/>
  
  <!-- Add specific flags in listentry for elements that come from appendix and matter. -->
  <xsl:template match="*[contains(@class, 'listentry/entry')]" mode="div-it">
    <div>
      <xsl:variable name="id" select="substring(@href, 2)"/>
      <xsl:if test="key('appendixFigureTableIds', $id)">
        <xsl:attribute name="is-appendix" select="true()"/>
      </xsl:if>
      <xsl:if test="key('matterFigureTableIds', $id)">
        <xsl:attribute name="is-matter" select="true()"/>
      </xsl:if>
      <xsl:call-template name="div-it-element-content"/>
    </div>
  </xsl:template>
</xsl:stylesheet>