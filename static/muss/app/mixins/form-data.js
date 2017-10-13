import Mixin from '@ember/object/mixin';
import { isPresent } from "@ember/utils";

const FormDataAdapterMixin = Mixin.create({
    // Overwrite to change the request types on which Form Data is sent
    formDataTypes: ['POST', 'PUT', 'PATCH'],

    ajaxOptions: function(url, type, options){
        let data;

        if (options && 'data' in options){
            data = options.data;
        }

        let hash = this._super.apply(this, arguments);

        if(typeof FormData === 'function' && data && this.formDataTypes.includes(type)){
            let formData, root;

            formData = new FormData();
            root = data.data.attributes

            Object.keys(root).forEach(function(key){
                if(isPresent(root[key]) && key != "photo"){
                    //Others fields
                    formData.append(key, root[key]);
                } else if(key == "photo" && typeof(root[key]) != "string") {
                    //Photo field
                    formData.append(key, root[key]);
                }
            });

            hash.processData = false;
            hash.contentType = false;
            hash.data = formData;
        }

        return hash;
    }
});

export default FormDataAdapterMixin;
