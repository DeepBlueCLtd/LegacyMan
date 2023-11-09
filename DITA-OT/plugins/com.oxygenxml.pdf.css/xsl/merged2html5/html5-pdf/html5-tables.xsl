<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="xs"
  version="2.0">
  
  <!-- Copied from: org.dita.html5/xsl/tables.xsl -->
  <!--
    If a table contains a mix of colspecs some with colwidth and some without,
    don't process the relative colwidths, this leads to table overflowing the page.
  -->
  <xsl:template match="*[contains(@class, ' topic/colspec ')]">
    <xsl:param name="totalwidth" as="xs:double"/>
    <xsl:choose>
      <xsl:when test="count(parent::node()/*[contains(@class, ' topic/colspec ')]) = 1
        or count(parent::node()/*[contains(@class, ' topic/colspec ')]) = count(parent::node()/*[contains(@class, ' topic/colspec ')]/@colwidth)">
        <xsl:next-match>
          <xsl:with-param name="totalwidth" select="$totalwidth"/>
        </xsl:next-match>
      </xsl:when>
      <xsl:otherwise>
        <col>
          <xsl:choose>
            <xsl:when test="not(empty(@colwidth)) and contains(@colwidth, '*')">
              <xsl:message terminate="no">[OXYTB01W][WARNING] Cannot process column width with value: <xsl:value-of select="@colwidth"/>. Not all table columns have width and the table will exceed the page width. To avoid this either remove this value or add a value for all columns.</xsl:message>
            </xsl:when>
            <xsl:when test="not(empty(@colwidth) or contains(@colwidth, '*'))">
              <xsl:attribute name="style" select="concat('width:', @colwidth)"/>
            </xsl:when>
          </xsl:choose>
        </col>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
</xsl:stylesheet>