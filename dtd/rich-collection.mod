<?xml version="1.0" encoding="UTF-8"?>
<!-- ============================================================= -->
<!--                    HEADER                                     -->
<!-- ============================================================= -->
<!--  MODULE:    DITA rich-collection MOD                          -->
<!--  VERSION:   1.2                                               -->
<!--  DATE:      June 2023                                         -->
<!--  Delivered as file "rich-collection.mod"                      -->
<!-- ============================================================= -->


<!-- ============================================================= -->
<!--                   ARCHITECTURE ENTITIES                       -->
<!-- ============================================================= -->

<!-- default namespace prefix for DITAArchVersion attribute can be
     overridden through predefinition in the document type shell   -->
<!ENTITY % DITAArchNSPrefix
  "ditaarch"
>

<!-- must be instanced on each topic type                          -->
<!ENTITY % arch-atts 
             "xmlns:%DITAArchNSPrefix; 
                        CDATA
                                  #FIXED 'http://dita.oasis-open.org/architecture/2005/'
              %DITAArchNSPrefix;:DITAArchVersion
                        CDATA
                                  '1.2'
"
>


<!-- ============================================================= -->
<!--                   SPECIALIZATION OF DECLARED ELEMENTS         -->
<!-- ============================================================= -->


<!ENTITY % concept-info-types 
  "%info-types;
  "
>

<!-- ============================================================= -->
<!--                   ELEMENT NAME ENTITIES                       -->
<!-- ============================================================= -->
<!ENTITY % rich-collection                "rich-collection" >
<!ENTITY % title                     "title" >
<!ENTITY % related-links                     "related-links" >

<!-- ============================================================= -->
<!--                    DOMAINS ATTRIBUTE OVERRIDE                 -->
<!-- ============================================================= -->


<!ENTITY included-domains 
  ""
>


<!-- ============================================================= -->
<!--                    ELEMENT DECLARATIONS                       -->
<!-- ============================================================= -->

<!--                    LONG NAME: Classlist  -->
<!ENTITY % rich-collection.content
 "
  ((%title;)?,
  (%body;)?,
  (%related-links;)?
  )                   
">
<!ENTITY % rich-collection.attributes
'            id         ID                               #REQUIRED
             conref     CDATA                            #IMPLIED
             %arch-atts;
             outputclass 
                        CDATA                            #IMPLIED
             domains    CDATA                "&included-domains;"    
'>
<!ELEMENT rich-collection %rich-collection.content; >
<!ATTLIST rich-collection %rich-collection.attributes; > 

<!-- ============================================================= -->
<!--                    SPECIALIZATION ATTRIBUTE DECLARATIONS      -->
<!-- ============================================================= -->

<!ATTLIST rich-collection         %global-atts;  class CDATA "- topic/topic concept/concept rich-collection/rich-collection ">
<!ATTLIST related-pages           %global-atts;  class CDATA "- topic/section  concept/title rich-collection/related-pages ">

<!-- related links  -->
<!ATTLIST related-links          class  CDATA "- topic/related-links rich-collection/related-links ">
<!-- ================== End DITA rich-collection  ======================== -->




