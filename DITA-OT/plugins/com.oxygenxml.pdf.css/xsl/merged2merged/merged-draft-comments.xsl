<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" 
    exclude-result-prefixes="xs" version="2.0">
    <!-- Hides or shows the draft comments depending on the DITA-OT args.draft parameter. -->
    <xsl:template match="*[contains(@class, ' topic/draft-comment ')] | *[contains(@class, ' topic/required-cleanup ')] " mode="#all">
        <xsl:if test="$args.draft = 'yes'">
            <xsl:copy>
                <xsl:apply-templates select="@* | node()"/>
            </xsl:copy>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>