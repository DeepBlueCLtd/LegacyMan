<!-- ============================================================= -->
<!--                    HEADER                                     -->
<!-- ============================================================= -->
<!--  MODULE:    DITA class Mod                                    -->
<!--  VERSION:   1.2                                               -->
<!--  DATE:      June 2023                                         -->
<!--  Delivered as file "class.mod"                                -->
<!-- ============================================================= -->
<!-- ============ Specialization of declared elements ============  -->
<!ENTITY % class                 "class">
<!ENTITY % title             "title">
<!ENTITY % body             "body">
<!ENTITY % summary       "summary">
<!ENTITY % signatures                    "signatures">
<!ENTITY % propulsion                   "propulsion">
<!ENTITY % propulsionRef                   "propulsionRef">
<!ENTITY % remarks                      "remarks">
<!ENTITY % span                           "span">
<!ENTITY % section.cnt                           "section.cnt">
<!ENTITY % arch-atts                           "arch-atts">
<!ENTITY % table                           "table">
<!ENTITY % xref                           "xref">
<!ENTITY % ul                           "ul">
<!ENTITY % ol                           "ol">
<!ENTITY % p                           "p">
<!ENTITY % fig                           "fig">
<!ENTITY % images                           "images">
<!ENTITY % image                           "image">
<!ENTITY % related-pages "related-pages">
<!ENTITY % related-links "related-links">

<!ELEMENT class              ((%title;), (%body;))>
<!ATTLIST class                   id ID #REQUIRED
                                  conref CDATA #IMPLIED
                                  %arch-atts;
                                  domains CDATA "&included-domains;"
>
<!ELEMENT body          ((%related-pages;)?, (%images;), (%summary;)?, (%signatures;)?, (%propulsion; | %propulsionRef;)?, (%remarks;)? )>
<!ATTLIST body              
                                        outputclass CDATA #IMPLIED
>
<!ELEMENT summary          ((%title;), (%table;)) >
<!ATTLIST summary id ID #REQUIRED
                                outputclass CDATA #IMPLIED
>
<!ELEMENT signatures    (%section.cnt;)* >
<!ATTLIST signatures id ID #REQUIRED
                                  outputclass CDATA #IMPLIED
>
<!ELEMENT propulsion    ((%title;)?, (%span;)*) >
<!ATTLIST propulsion    id ID #REQUIRED
                                  outputclass CDATA #IMPLIED
>
<!ELEMENT propulsionRef    ((%title;)?, (%xref;)?) >
<!ATTLIST propulsionRef    
                                  outputclass CDATA #IMPLIED
>
<!ATTLIST propulsionRef id ID #REQUIRED
>

<!ELEMENT remarks    ((%title;)?, (%span;)*) >
<!ATTLIST remarks     id ID #REQUIRED
                                  outputclass CDATA #IMPLIED
>
<!ELEMENT links     (%section.cnt;)* >
<!ATTLIST links    id ID #REQUIRED
                                  outputclass CDATA #IMPLIED
>
<!ELEMENT span    ((%ul; | %ol; | %p; | %table; | %fig;)*) >
<!ATTLIST span    
                                  id CDATA #IMPLIED
                                  conref CDATA #IMPLIED
                                  outputclass CDATA #IMPLIED
>
<!ELEMENT images              ((%title;), (%image;)*)>
<!ATTLIST images
                                  outputclass CDATA #IMPLIED
>

<!ELEMENT related-pages ((%title;), (%xref;)*) >
<!ATTLIST related-pages 
                                    id ID #REQUIRED
                                    outputclass CDATA #IMPLIED>
<!--specialization attributes-->
<!-- class extends reference -->
<!ATTLIST class              class  CDATA "- topic/topic  reference/reference class/class ">
<!-- body extends refBody, summary is compulsory, other 3 child elements (signature, propulsion, remarks) optional -->
<!ATTLIST body          class  CDATA "- topic/body reference/refBody class/body ">
<!-- related links  -->
<!ATTLIST related-links          class  CDATA "- topic/related-links class/related-links ">
<!-- summary extends properties.  -->
<!ATTLIST summary          class  CDATA "- topic/section class/summary ">
<!-- signatures extends section, allows free content in Phase 1. Constrained table in Phase 2 -->
<!ATTLIST signatures    class  CDATA "- topic/section class/signatures ">
<!-- extends section -->
<!ATTLIST remarks    class  CDATA "- topic/section class/remarks ">
<!-- images -->
<!ATTLIST images  class CDATA "- topic/section class/images ">
<!-- extends section -->
<!ATTLIST propulsion    class  CDATA "- topic/section class/propulsion ">
<!-- extends section -->
<!ATTLIST propulsionRef    class  CDATA "- topic/section class/propulsionRef ">
<!-- drop this, use standard version of related-links -->
<!ATTLIST related-pages    class  CDATA "- topic/section class/related-pages ">
<!-- table extends table -->
<!ATTLIST table    class  CDATA "- topic/table  class/table ">
<!-- title extends title -->
<!ATTLIST title    class  CDATA "- topic/title  class/title ">
<!-- sp extends p -->
<!ATTLIST span    class  CDATA "- topic/p  class/span ">
<!-- p extends p -->
<!ATTLIST p    class  CDATA "- topic/p  class/p ">
<!-- ul extends ul -->
<!ATTLIST ul    class  CDATA "- topic/ul  class/ul ">
<!-- ol extends ol -->
<!ATTLIST ol    class  CDATA "- topic/ol  class/ol ">
<!-- fig extends fig -->
<!ATTLIST fig    class  CDATA "- topic/fig  class/fig ">
<!-- xref extends xref -->
<!ATTLIST xref    class  CDATA "- topic/xref  class/xref ">
<!-- image -->
<!ATTLIST image  class CDATA "- topic/image class/image ">
