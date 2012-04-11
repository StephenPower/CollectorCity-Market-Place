from django import template


register = template.Library()


@register.simple_tag
def upload_js():
    return """
    <!-- The template to display files available for upload -->
<script id="template-upload" type="text/x-tmpl">
{% for (var i=0, files=o.files, l=files.length, file=files[0]; i<l; file=files[++i]) { %}
    <tr class="template-upload fade">
        <td></td>
        <td class="preview"><span class="fade"></span></td>
        <td class="name">{%=file.name%}</td>
        <td class="size">{%=o.formatFileSize(file.size)%}</td>
        {% if (file.error) { %}
            <td class="error" colspan="2"><span class="label label-important">{%=locale.fileupload.error%}</span> {%=locale.fileupload.errors[file.error] || file.error%}</td>
        {% } else if (o.files.valid && !i) { %}
            <td>
                <div class="progress progress-success progress-striped active"><div class="bar" style="width:0%;"></div></div>
            </td>
            <td></td>

            <td class="start">{% if (!o.options.autoUpload) { %}
                <button class="btn btn-info">
                    <i class="icon-upload icon-white"></i> {%=locale.fileupload.start%}
                </button>
            {% } %}</td>
        {% } else { %}
            <td colspan="2"></td>
        {% } %}
        <td class="cancel">{% if (!i) { %}
            <button class="btn btn-warning">
                <i class="icon-ban-circle icon-white"></i> {%=locale.fileupload.cancel%}
            </button>
        {% } %}</td>
    </tr>
{% } %}
</script>
<!-- The template to display files available for download -->
<script id="template-download" type="text/x-tmpl">
{% for (var i=0, files=o.files, l=files.length, file=files[0]; i<l; file=files[++i]) { %}
    <tr class="template-download fade">
        {% if (file.error) { %}
            <td></td>
            <td></td>
            <td class="name">{%=file.name%}</td>
            <td class="size">{%=o.formatFileSize(file.size)%}</td>
            <td class="error" colspan="2"><span class="label label-important">{%=locale.fileupload.error%}</span> {%=locale.fileupload.errors[file.error] || file.error%}</td>
        {% } else { %}
            <td class="primary">{% if (file.is_primary) { %}
                <i class="icon-star"></i>
            {% } %}</td>
        
            <td class="preview">{% if (file.thumbnail_url) { %}
                <a href="{%=file.url%}" title="{%=file.name%}" rel="gallery" download="{%=file.name%}"><img src="{%=file.thumbnail_url%}"></a>
            {% } %}</td>
            <td class="name">
                <a href="{%=file.url%}" title="{%=file.name%}" rel="{%=file.thumbnail_url&&'gallery'%}" download="{%=file.name%}">{%=file.name%}</a>
            </td>
            <td class="size">{%=o.formatFileSize(file.size)%}</td>
            <td colspan="2"></td>
        {% } %}
        <td class="primary_set">
            <a href="{%=file.url_set_primary%}" class="btn btn-info"><i class="icon-star icon-white"></i> Primary</a>
        </td>
        <td class="delete">
            <button class="btn btn-danger" data-type="{%=file.delete_type%}" data-url="{%=file.delete_url%}">
                <i class="icon-trash icon-white"></i> {%=locale.fileupload.destroy%}
            </button>
            <input type="checkbox" name="delete" value="1" style="float: right;"/>
        </td>
    </tr>
{% } %}
</script>
    """