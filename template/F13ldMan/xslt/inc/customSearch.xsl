<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:toc="http://www.oxygenxml.com/ns/webhelp/toc" xmlns:index="http://www.oxygenxml.com/ns/webhelp/index" xmlns:oxygen="http://www.oxygenxml.com/functions" xmlns:d="http://docbook.org/ns/docbook" xmlns:whc="http://www.oxygenxml.com/webhelp/components" xmlns="http://www.w3.org/1999/xhtml" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:oxyf="http://www.oxygenxml.com/functions" exclude-result-prefixes="#all" version="2.0">


    <xsl:template match="whc:webhelp_top_menu" mode="copy_template">
        <xsl:if test="oxyf:getParameter('webhelp.show.top.menu') = 'yes'">
            <xsl:variable name="top_menu">
                <nav>
                    <xsl:call-template name="generateComponentClassAttribute">
                        <xsl:with-param name="compClass">
                            <xsl:choose>
                                <xsl:when test="oxyf:getParameter('webhelp.top.menu.activated.on.click') = 'yes'">
                                    <xsl:value-of>wh_top_menu c-menu activated-on-click</xsl:value-of>
                                </xsl:when>
                                <xsl:otherwise>wh_top_menu c-menu</xsl:otherwise>
                            </xsl:choose>
                        </xsl:with-param>
                    </xsl:call-template>
                    <xsl:attribute name="aria-label">Menu Container</xsl:attribute>
                    <xsl:copy-of select="@* except @class"/>
                    <xsl:choose>
                        <xsl:when test="string-length($WEBHELP_TOP_MENU_TEMP_FILE_URL) > 0 and doc-available($WEBHELP_TOP_MENU_TEMP_FILE_URL)">
                            <xsl:variable name="top-menu" select="doc($WEBHELP_TOP_MENU_TEMP_FILE_URL)"/>
                            <xsl:apply-templates select="$top-menu" mode="copy-top-menu"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <!-- The entire message should be output on a single line in order to be presented in the Results View. -->
                            <xsl:message>[OXYWH003W][WARN] Cannot read the top menu content from file: '<xsl:value-of select="$WEBHELP_TOP_MENU_TEMP_FILE_URL"/>'.</xsl:message>
                        </xsl:otherwise>
                    </xsl:choose>
                </nav>
            </xsl:variable>
            
            <xsl:call-template name="outputComponentContent">
                <xsl:with-param name="compContent" select="$top_menu"/>
                <xsl:with-param name="compName" select="local-name()"/>
            </xsl:call-template>
        </xsl:if>
        
    </xsl:template>
    

</xsl:stylesheet>
