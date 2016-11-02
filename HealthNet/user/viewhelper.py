def dict_from_url_kvp(kvp):
    kvp_arr = kvp.split('/')

    dict = {}

    for i in range(0, len(kvp_arr)-1, 2):
        dict[kvp_arr[i]] = int(kvp_arr[i+1])

    return dict