from rollyourown.seo import Tag, MetaTag, KeywordTag, Metadata 

class SiteMetadata(Metadata):
    title       = Tag(head=True, max_length=68)
    description = MetaTag(max_length=155)
    keywords    = KeywordTag()