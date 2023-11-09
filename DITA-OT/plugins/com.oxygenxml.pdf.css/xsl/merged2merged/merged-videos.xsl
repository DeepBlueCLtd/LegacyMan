<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:oxy="http://www.oxygenxml.com/extensions/author"
    exclude-result-prefixes="xs oxy"
    version="2.0">
    <!-- 
        
        Videos.
        
    -->
    <!-- Convert the data from relative to absolute. -->
    <xsl:template match="*[contains(@class, ' topic/object ')]/@data">
        <xsl:attribute name="{local-name()}">
            <xsl:value-of select="oxy:toAbsolute(.., local-name())"/>
        </xsl:attribute>
    </xsl:template>
    
    <!-- Convert quicktime videos outputclass from iframe to video. -->
    <xsl:template match="*[contains(@class, ' topic/object ')][contains(@outputclass, 'iframe')]/@outputclass">
        <xsl:variable name="extension" select="tokenize(../@data, '\.|/')[last()]"/>
        <xsl:choose>
            <xsl:when test="$extension = 'mov'">
                <xsl:attribute name="{local-name()}" select="'video'"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:next-match/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>