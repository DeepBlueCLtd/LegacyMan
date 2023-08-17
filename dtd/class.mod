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
<!ENTITY % body             "body">
<!ENTITY % summary       "summary">
<!ENTITY % signatures                    "signatures">
<!ENTITY % propulsion                   "propulsion">
<!ENTITY % propulsionRef                   "propulsionRef">
<!ENTITY % remarks                      "remarks">
<!ENTITY % span                           "span">
<!ENTITY % images                           "images">
<!ENTITY % related-pages "related-pages">
<!ELEMENT class              ((%title;), (%body;))>
<!ATTLIST class                   id ID #REQUIRED
                                  conref CDATA #IMPLIED
                                  %arch-atts;
                                  domains CDATA "&included-domains;"
>
<!ELEMENT body          ((%images;), (%summary;), (%signatures;)?, (%propulsion; | %propulsionRef;)?, (%remarks;)?, (%related-pages;)? )>
<!ATTLIST body              
                                        outputclass CDATA #IMPLIED
>
<!ELEMENT summary          ((%table;)) >
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
<!ATTLIST propulsionRef id ID #REQUIRED>

<!ELEMENT remarks    ((%title;)?, (%span;)*) >
<!ATTLIST remarks     id ID #REQUIRED
                                  outputclass CDATA #IMPLIED
>
<!ELEMENT links     (%section.cnt;)* >
<!ATTLIST links    id ID #REQUIRED
                                  outputclass CDATA #IMPLIED
>
<!ELEMENT span    ((%ul; | %ol; | %p;)*) >
<!ATTLIST span    
                                  conref CDATA #IMPLIED
                                  outputclass CDATA #IMPLIED
>
<!ELEMENT images              ((%image;)*)>
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
<!-- summary extends properties.  -->
<!ATTLIST summary          class  CDATA "- topic/section class/summary ">
<!-- signatures extends section, allows free content in Phase 1. Constrained table in Phase 2 -->
<!ATTLIST signatures    class  CDATA "- topic/section class/signatures ">
<!-- extends section -->
<!ATTLIST propulsion    class  CDATA "- topic/section class/propulsion ">
<!-- extends section -->
<!ATTLIST propulsionRef    class  CDATA "- topic/section class/propulsionRef ">
<!-- extends section -->
<!ATTLIST remarks    class  CDATA "- topic/section class/remarks ">
<!-- extends section -->
<!ATTLIST related-pages    class  CDATA "- topic/section class/related-pages ">
<!-- sp extends p -->
<!ATTLIST span    class  CDATA "- topic/p  class/span ">
<!-- images -->
<!ATTLIST images             %global-atts;  class CDATA "- topic/body reference/refBody class/images ">