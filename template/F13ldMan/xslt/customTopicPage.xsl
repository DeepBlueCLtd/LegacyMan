<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:toc="http://www.oxygenxml.com/ns/webhelp/toc" xmlns:index="http://www.oxygenxml.com/ns/webhelp/index" xmlns:oxygen="http://www.oxygenxml.com/functions" xmlns:d="http://docbook.org/ns/docbook" xmlns:whc="http://www.oxygenxml.com/webhelp/components" xmlns="http://www.w3.org/1999/xhtml" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:oxyf="http://www.oxygenxml.com/functions" exclude-result-prefixes="#all" version="2.0">
    
    <xsl:import href="inc/customHeader.xsl"/>
    <xsl:import href="inc/customFooter.xsl"/>
    <xsl:import href="inc/customSearch.xsl"/>
    
    <xsl:template match="whc:page_libraries[@page]" mode="copy_template">
        <xsl:param name="template_base_uri" tunnel="yes"/>
        <xsl:param name="i18n_context" tunnel="yes" as="element()*"/>
        <!-- [DOT_DIR]\plugins\com.oxygenxml.webhelp.responsive -->
        <xsl:variable name="pageLibRefsDir" select="'../page-templates-fragments/libraries/'"/>
        <xsl:variable name="pageLibRefsFileName">
            <xsl:choose>
                <xsl:when test="@page = 'main'">
                    <xsl:value-of select="'main-page-libraries.xml'"/>
                </xsl:when>
                <xsl:when test="@page = 'topic'">
                    <xsl:value-of select="'topic-page-libraries.xml'"/>
                </xsl:when>
                <xsl:when test="@page = 'search'">
                    <xsl:value-of select="'search-page-libraries.xml'"/>
                </xsl:when>
                <xsl:when test="@page = 'indexterms'">
                    <xsl:value-of select="'indexterms-page-libraries.xml'"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:message>Unknown page type <xsl:value-of select="@page"/></xsl:message>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        
        <xsl:variable name="pageLibraries">
            <xsl:call-template name="extractFileContent">
                <xsl:with-param name="href" select="concat($pageLibRefsDir, $pageLibRefsFileName)"/>
                <xsl:with-param name="template_base_uri" select="$template_base_uri"/>
            </xsl:call-template>
        </xsl:variable>
        
        
        <xsl:choose>
            <xsl:when test="oxyf:getParameter('webhelp.custom.search.engine.enabled') = 'true'">
                <xsl:apply-templates select="$pageLibraries" mode="remove-search-scripts" />
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="$pageLibraries" />
            </xsl:otherwise>
        </xsl:choose>
        
    </xsl:template>
    
</xsl:stylesheet>
