function delete_object(url, object)
{
    var ok=confirm("Are you sure you want to delete this "+object+"?");
    if(ok)
    {
        document.location=url;
    return true;
    }
}

