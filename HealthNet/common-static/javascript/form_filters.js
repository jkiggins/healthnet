/**
 * Created by jake on 10/28/2016.
 */

function sucsessive_filters(form_id, ordered_ids)
{
    this.form = document.getElementById(form_id);
    this.ordered_names = ordered_names;
    this.form_arr = [];

    for (var i = 0; i < ordered_ids.length; i++)
    {
        var id = ordered_ids[i];
        var ele = documents.getElementById(id);
        var choice_arr = [];

        for(child in ele.children)
        {
            if(child.tagName() == 'OPTION') {
                choice_arr.append({label: child.innerHTML, value: child.getAttribute('value')});

                if((i > 0) && !child.hasAttribute("selected"))
                {
                    child.delete();
                }
            }
        }

        form_arr.append(choice_arr);

    }

    function onSelectionChange(e) {console.log("onSelectionChange Fired");}


}
