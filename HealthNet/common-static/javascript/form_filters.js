function resolve_dependancy(e) {
    if(e.form.action[e.form.action.length-1] != 'd') {
        e.form.action += "d";
    }

    e.form.submit();
}

function submit_form(e) {
    if(e.form.action[e.form.action.length-1] == 'd') {
        e.form.action = e.form.action.substr(0, e.form.action.length-1)
    }

    e.form.submit();
}

function set_kvp(key, value) {
    url_arr = window.location.pathname.split('/');

    for(var i = url_arr.length; i >= 0; i--)
    {
        if(url_arr[i] == key){
            url_arr[i+1] = value;

            window.location = rebuild_url_from_array(url_arr);
        }
    }

    url_arr.push(key);
    url_arr.push(value);

    window.location.pathname = rebuild_url_from_array(url_arr);

}

function rebuild_url_from_array(arr) {
    url = "";

    for (var i = 0; i < arr.length; i++)
    {
        if (arr[i] != "") {
            url += "/";
            url += arr[i];
        }
    }

    return url;

}