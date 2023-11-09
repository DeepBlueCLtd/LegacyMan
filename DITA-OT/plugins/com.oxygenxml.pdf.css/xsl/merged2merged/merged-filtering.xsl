<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:ditaarch="http://dita.oasis-open.org/architecture/2005/"
    exclude-result-prefixes="xs ditaarch" version="2.0">
    <!-- 
                
        General filtering. 
    
    -->

    <!-- Some attributes are not relevant to our output. -->
    <xsl:template match="@xtrf"/>
    <xsl:template match="@xtrc"/>
    <xsl:template match="@ditaarch:DITAArchVersion"/>
    <xsl:template match="@domains"/>
    <xsl:template match="@ohref"/>
    <xsl:template match="@collection-type"/>
    <xsl:template match="@chunk"/>
    <xsl:template match="@resourceid"/>
    <xsl:template match="@first_topic_id"/>
    <xsl:template match="@locktitle"/>

</xsl:stylesheet>