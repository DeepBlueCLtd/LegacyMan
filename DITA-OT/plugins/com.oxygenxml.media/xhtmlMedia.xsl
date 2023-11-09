<?xml version="1.0" encoding="UTF-8"?>
<!--
    
Oxygen Media conversion plugin
Copyright (c) 1998-2023 Syncro Soft SRL, Romania.  All rights reserved.
Licensed under the terms stated in the license file LICENSE 
available in the base directory of this plugin.

-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:custom-func="http://www.oxygenxml.com/custom/function"
  exclude-result-prefixes="custom-func"
  version="2.0">
  <!-- Parameter to disable embedding media resources and instead to link to them-->
  <xsl:param name="com.oxygenxml.xhtml.linkToMediaResources"/>
  
  <xsl:function name="custom-func:isSupportedExtension">
    <xsl:param name="srcValue"/>
    <xsl:choose>
      <xsl:when test="$com.oxygenxml.xhtml.linkToMediaResources = 'auto'">
        <xsl:variable name="extension" select="tokenize($srcValue, '\.|/')[last()]"/>
        <xsl:variable name="extensions-list" select="tokenize('mov mp4 m4v 3gp 3g2', '\s')"/>
        
        <xsl:sequence select="index-of($extensions-list, $extension)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:sequence select="true()"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:function>
  
  <xsl:template match="
    *[contains(@class, ' topic/object ')]
    [contains(@outputclass, 'video')]" priority="10" name="videoFormatter">
    <xsl:variable name="srcValue">
      <xsl:call-template name="generateSrcValue"/>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="not(custom-func:isSupportedExtension($srcValue)) or $com.oxygenxml.xhtml.linkToMediaResources = 'yes' or $com.oxygenxml.xhtml.linkToMediaResources = 'true'">
        <xsl:call-template name="generateLinkToMediaResource"/>
      </xsl:when>
      <xsl:otherwise>
        <div>
          <xsl:variable name="class">
            <xsl:choose>
              <xsl:when test="@width or @height">non-responsive</xsl:when>
              <xsl:otherwise>embed-responsive embed-responsive-16by9</xsl:otherwise>
            </xsl:choose>
          </xsl:variable>
          <xsl:attribute name="class" select="concat('video-container ',$class)"/>
          <video>
            <xsl:call-template name="commonattributes"/>
            <xsl:call-template name="setidaname"/>
            <xsl:choose>
              <xsl:when test="@outputclass">
                <xsl:attribute name="class" select="concat(@outputclass, ' ', 'embed-responsive-item')"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:attribute name="class" select="'embed-responsive-item'"/>
              </xsl:otherwise>
            </xsl:choose>
            <!-- The <video> element has a specific controls element which defines if controls should be present or not. -->
            <xsl:attribute name="controls">controls</xsl:attribute>
            <xsl:if test="@width">
              <xsl:attribute name="width" select="@width"/>
            </xsl:if>
            <xsl:if test="@height">
              <xsl:attribute name="height" select="@height"/>
            </xsl:if>
            <!-- Generic XHTML object, set all params as attributes on the element. -->
            <xsl:apply-templates select="*[contains(@class,' topic/param ')][not(@name='src')]"/>
            <xsl:call-template name="copySource"/>
          </video>
        </div>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <!-- Generate a link to the media resource -->
  <xsl:template name="generateLinkToMediaResource">
    <xsl:variable name="srcValue">
      <xsl:call-template name="generateSrcValue"/>
    </xsl:variable>
    <div class="mediaResourceLink">
      <a href="{$srcValue}" target="_blank">
        <xsl:value-of select="$srcValue"/>
      </a>
    </div>
  </xsl:template>
  
  <!-- Copy the source. Create the video <source> element -->
  <xsl:template name="copySource">
    <xsl:if
      test="*[contains(@class, ' topic/param ')][@name = 'src' or local-name() = 'source' or local-name() = 'media-source'] or @data">
      <source>
        <xsl:attribute name="src">
          <xsl:call-template name="generateSrcValue"/>
        </xsl:attribute>
        <xsl:if test="@type">
          <xsl:attribute name="type" select="@type"/>
        </xsl:if>
      </source>
    </xsl:if>
  </xsl:template>
  
  <!-- Gemerate the source attribute value -->
  <xsl:template name="generateSrcValue">
    <xsl:choose>
      <xsl:when test="@data">
        <xsl:value-of select="@data"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="*[contains(@class, ' topic/param ')][@name = 'src' or local-name() = 'source' or local-name() = 'media-source']/@href"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <!-- Create the XHTML audio element -->
  <xsl:template match="*[contains(@class, ' topic/object ')][contains(@outputclass, 'audio') or local-name() = 'audio']" priority="10">
    <xsl:choose>
      <xsl:when test="$com.oxygenxml.xhtml.linkToMediaResources = 'auto' or $com.oxygenxml.xhtml.linkToMediaResources = 'yes' or $com.oxygenxml.xhtml.linkToMediaResources = 'true'">
        <xsl:call-template name="generateLinkToMediaResource"/>
      </xsl:when>
      <xsl:otherwise>
        <audio>
          <xsl:call-template name="commonattributes"/>
          <xsl:call-template name="setidaname"/>
          <!-- The <audio> element has a specific controls element which defines if controls should be present or not. -->
          <xsl:if test="not(local-name() = 'audio') or controls">
            <xsl:attribute name="controls">controls</xsl:attribute>
          </xsl:if>
          <xsl:apply-templates select="*[contains(@class,' topic/param ')][not(@name='src')]"/>
          <xsl:call-template name="copySource"/>
        </audio>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <!-- Embedded iframe for object with specific output class or for video pointing to youtube website. -->
  <xsl:template match="*
    [contains(@class, ' topic/object ') or local-name() = 'video']
    [contains(@outputclass, 'iframe') or contains(media-source/@href, 'www.youtube.com') or contains(media-source/@href, 'player.vimeo.com')]" priority="11">
    <xsl:choose>
      <xsl:when test="$com.oxygenxml.xhtml.linkToMediaResources = 'auto' or $com.oxygenxml.xhtml.linkToMediaResources = 'yes' or $com.oxygenxml.xhtml.linkToMediaResources = 'true'">
        <xsl:call-template name="generateLinkToMediaResource"/>
      </xsl:when>
      <xsl:otherwise>
        <div>
          <xsl:variable name="class">
            <xsl:choose>
              <xsl:when test="@width or @height">non-responsive</xsl:when>
              <xsl:otherwise>embed-responsive embed-responsive-16by9</xsl:otherwise>
            </xsl:choose>
          </xsl:variable>
          <xsl:attribute name="class" select="$class"/>
          
          <iframe>
            <xsl:call-template name="commonattributes"/>
            <xsl:call-template name="setidaname"/>
            <xsl:choose>
              <xsl:when test="@outputclass">
                <xsl:attribute name="class" select="concat(@outputclass, ' ', 'embed-responsive-item')"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:attribute name="class" select="'embed-responsive-item'"/>
              </xsl:otherwise>
            </xsl:choose>
            <!-- The <video> element has a specific controls element which defines if controls should be present or not. -->
            <xsl:if test="not(local-name() = 'video') or controls">
              <xsl:attribute name="controls">controls</xsl:attribute>
            </xsl:if>
            <xsl:if test="media-controls[@value='true']">
              <xsl:attribute name="controls">true</xsl:attribute>
            </xsl:if>
            <xsl:if test="media-autoplay[@value='true']">
              <xsl:attribute name="autoplay">true</xsl:attribute>
            </xsl:if>
            <xsl:if test="media-loop[@value='true']">
              <xsl:attribute name="loop">true</xsl:attribute>
            </xsl:if>
            <xsl:if test="media-muted[@value='true']">
              <xsl:attribute name="muted">true</xsl:attribute>
            </xsl:if>
            <xsl:if test="@width">
              <xsl:attribute name="width" select="@width"/>
            </xsl:if>
            <xsl:if test="@height">
              <xsl:attribute name="height" select="@height"/>
            </xsl:if>
            <xsl:choose>
              <xsl:when test="@data">
                <xsl:attribute name="src" select="@data"/>
              </xsl:when>
              <xsl:when test="source/@value">
                <xsl:attribute name="src" select="source/@value"/>
              </xsl:when>
              <xsl:when test="media-source/@href">
                <xsl:attribute name="src" select="media-source/@href"/>
              </xsl:when>
            </xsl:choose>
            <xsl:if test="not(local-name() = 'video')">
              <!-- Generic XHTML object, set all params as attributes on the element. -->
              <xsl:apply-templates select="*[contains(@class,' topic/param ')]"/>
            </xsl:if>
          </iframe>
        </div>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <!-- Convert all params to name, value attributes.  -->
  <xsl:template match="*[contains(@class, ' topic/object ')][contains(@outputclass, 'iframe') or contains(@outputclass, 'audio')]/*[contains(@class, ' topic/param ')]" priority="10">
    <xsl:choose>
      <xsl:when test="$com.oxygenxml.xhtml.linkToMediaResources = 'auto' or $com.oxygenxml.xhtml.linkToMediaResources = 'yes' or $com.oxygenxml.xhtml.linkToMediaResources = 'true'">
        <!-- Ignore setting extra attributes. -->
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="{@name}"><xsl:value-of select="@value"/></xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template match="*[contains(@class, ' topic/object ')][contains(@outputclass, 'video')]/*[contains(@class, ' topic/param ')]" priority="10">
    <xsl:choose>
      <xsl:when test="$com.oxygenxml.xhtml.linkToMediaResources = 'yes' or $com.oxygenxml.xhtml.linkToMediaResources = 'true'">
        <!-- Ignore setting extra attributes. -->
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="{@name}"><xsl:value-of select="@value"/></xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>  
</xsl:stylesheet>