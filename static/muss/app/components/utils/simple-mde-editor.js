import TextArea from "@ember/component/text-area";
import { inject as service} from '@ember/service';
import { isEmpty } from "@ember/utils";
import layout from '../../templates/components/utils/simple-mde-editor';

export default TextArea.extend({
    ajax: service('ajax'),
    change: null,
    currentEditor: null,
    layout,
    value: null,

    init() {
        this._super(...arguments);
        let self = this;

        this.set('toolbar', [
            "bold", "italic", "strikethrough", "heading", "|",
            "code", "quote", "unordered-list", "ordered-list", "|",
            "table", "link",
            {
                name: 'image',
                action: function customFunction(editor) {
                    let cm = editor.codemirror;

                    // append input element
                    let inputEle = document.createElement('input');
                    inputEle.setAttribute('type', 'file');
                    inputEle.setAttribute('multiple', true);
                    inputEle.setAttribute('accept', 'image/*');
                    inputEle.click();

                    //Upload file
                    inputEle.onchange = (evt) => {
                        let imgs = evt.currentTarget.files;
                        if (imgs.length) {
                            let formData = new window.FormData();

                            for (let i = 0; i < imgs.length; i++) {
                                formData.append('upload_img_' + i, imgs[i]);
                            }

                            self.get('ajax').request("/uploads/", {
                                method: 'POST',
                                processData: false,
                                contentType: false,
                                data: formData
                            }).then((response) => {
                                let options = editor.options;
                                let urls = response.data.urls;

                                urls.forEach((url) => {
                                    let imageMarkdownTag = options.insertTexts.image;
                                    cm.replaceSelection(imageMarkdownTag[0] + imageMarkdownTag[1].replace("#url#", url));
                                });
                            });
                        }
                    }
                },
                className: 'fa fa-picture-o',
                title: 'Insert Image',
            },
            "horizontal-rule", "|", "preview",
            /*"side-by-side", "fullscreen", "guide"*/
        ]);
    },
    didInsertElement() {
        this.set('currentEditor', new window.SimpleMDE({
            status: false,
            autofocus: true,
            toolbar: this.get('toolbar'),
            spellChecker: true,
            element: document.getElementById(this.elementId),
        }));
        this.get('currentEditor').value(this.get('value'));

        this.get('currentEditor').codemirror.on('change', () => {
            this.set('value', this.get('currentEditor').value());
        });
    },
    didReceiveAttrs() {
        const editor = this.get('currentEditor');
        if (isEmpty(editor)) {
            return;
        }
        const cursor = editor.codemirror.getDoc().getCursor();
        editor.value(this.get('value'));
        editor.codemirror.getDoc().setCursor(cursor);
    }
});
