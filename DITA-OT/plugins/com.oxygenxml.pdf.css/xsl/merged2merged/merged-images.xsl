<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" 
    xmlns:oxy="http://www.oxygenxml.com/extensions/author"
    xmlns:dita-ot="http://dita-ot.sourceforge.net/ns/201007/dita-ot"
    xmlns:ImageInfo="java:com.oxygenxml.dita.xsltextensions.ImageInfo"
    exclude-result-prefixes="#all" version="2.0">
    <!-- 
        
        Images.
        
    -->
    <!-- The temporary directory -->
    <xsl:param name="dita.temp.dir"/>
    
    <!-- The list of job images by URI, we can use them directly to convert images relative to absolute paths. -->
    <xsl:key name="jobImagesByUri" match="//file[@format='image'][not(@resource-only='true')]" use="@uri"/>
    
    <!-- Convert the href from relative (to the DITA map original file - as it is processed by the DITA-OT 
        previous ant targets) to absolute. -->
    <xsl:template match="*[contains(@class, ' topic/image ')]/@href">
        <xsl:attribute name="href">
            <xsl:value-of select="oxy:toAbsolute(..)"/>
        </xsl:attribute>
    </xsl:template>
    
    <!-- Deals with images not having width nor height specified in the document. -->
    <xsl:template match="*[contains(@class, ' topic/image ')][not(@width)][not(@height)]/@href" priority="2">
        
        <xsl:variable name="href" select="oxy:toAbsolute(..)"/>
        <xsl:variable name="image-size" select="ImageInfo:getImageSize($href)"/>
        
        <xsl:choose>
            <xsl:when test="not($image-size = '-1,-1')">
                <xsl:variable name="width-in-pixel">
                    <xsl:call-template name="length-to-pixels">
                        <xsl:with-param name="dimen" select="substring-before($image-size, ',')"/>
                    </xsl:call-template>
                </xsl:variable>
                <xsl:variable name="height-in-pixel">
                    <xsl:call-template name="length-to-pixels">
                        <xsl:with-param name="dimen" select="substring-after($image-size, ',')"/>
                    </xsl:call-template>
                </xsl:variable>
                <xsl:attribute name="dita-ot:image-width" select="floor(number($width-in-pixel))"/>
                <xsl:attribute name="dita-ot:image-height" select="floor(number($height-in-pixel))"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:message>Cannot get original image size for <xsl:value-of select="." />.</xsl:message>
            </xsl:otherwise>
        </xsl:choose>
        
        <xsl:next-match/>
    </xsl:template>
    
    <!-- Fixes the href, converting it from relative (to the DITA map original file) to absolute. -->
    <xsl:function name="oxy:toAbsolute" as="xs:string">
        <xsl:param name="elem" as="node()"/>
        <xsl:value-of select="oxy:toAbsolute($elem, 'href')"/>
    </xsl:function>
    
    <!-- Fixes the attributes, converting it from relative (to the DITA map original file) to absolute. -->
    <xsl:function name="oxy:toAbsolute" as="xs:string">
        <xsl:param name="elem" as="node()"/>
        <xsl:param name="attrName" as="xs:string"/>
        
        <xsl:variable name="job.file" select="resolve-uri('.job.xml', oxy:makeURL(concat($dita.temp.dir, '/')))"/>
        
        <xsl:choose>
            <xsl:when test="$elem/@scope = 'external' or oxy:isAbsolute($elem/@*[local-name() = $attrName])">
                <!-- The attribute is already absolute, return it directly. -->
                <xsl:value-of select="$elem/@*[local-name() = $attrName]"/>
            </xsl:when>
            <xsl:when test="not(doc-available($job.file))">
                <!-- 
                    There's no .job.xml file available, we use the input directory to absolutize the attribute.
                    This case is encountered when debugging the stylesheet or during tests.
                -->
                <xsl:value-of select="concat($input.dir.url, $elem/@*[local-name() = $attrName])"/>
            </xsl:when>
            <xsl:otherwise>
                <!-- 
                    There's a .job.xml file, we need it as context to match attribute uri.
                    This is necessary when using preprocess2, as the filenames are altered.
                -->
                <xsl:variable name="job" select="document($job.file)" as="document-node()?"/>
                
                <xsl:variable name="result">
                    <xsl:variable name="job-result" select="$job/key('jobImagesByUri', $elem/@*[local-name() = $attrName])/@result"/>
                    <xsl:variable name="job-result-contains" select="
                        if (empty($job-result)) then
                            $job//file[contains(@uri, $elem/@*[local-name() = $attrName])]/@result
                        else
                            $job-result"/>
                    
                    <xsl:value-of select="
                        if (empty($job-result-contains)) then
                            resolve-uri($elem/@*[local-name() = $attrName],($elem/ancestor-or-self::*[@xtrf]/@xtrf)[last()])
                        else
                            $job-result-contains"/>
                </xsl:variable>
                
                <xsl:value-of select="$result"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:function>
    
    <!-- Test whether URI is absolute -->
    <xsl:function name="oxy:isAbsolute" as="xs:boolean">
        <xsl:param name="uri" as="xs:anyURI"/>
        <xsl:sequence select="some $prefix in ('/', 'file:') satisfies starts-with($uri, $prefix) or contains($uri, '://')"/>
    </xsl:function>
    
    <!-- Change a filepath into an URI starting with file: -->
    <xsl:function name="oxy:makeURL" as="item()">
        <xsl:param name="filepath"/>
        <xsl:variable name="correctedPath" select="replace($filepath, '\\', '/')"/>
        <xsl:variable name="url">
            <xsl:choose>
                <!-- Mac / Linux paths start with / -->
                <xsl:when test="starts-with($correctedPath, '/')">
                    <xsl:value-of select="concat('file://', $correctedPath)"/>
                </xsl:when>
                <!-- Windows paths not start with / -->
                <xsl:otherwise>
                    <xsl:value-of select="concat('file:///', $correctedPath)"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:value-of select="iri-to-uri($url)"/>
    </xsl:function>
</xsl:stylesheet>