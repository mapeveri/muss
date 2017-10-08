import TextArea from "@ember/component/text-area";
import { isEmpty } from "@ember/utils";
import layout from '../../templates/components/utils/simple-mde-editor';

const defaultToolbar = [
    "bold", "italic", "strikethrough", "heading", "|",
    "code", "quote", "unordered-list", "ordered-list", "|",
    "table", "link", "image", "horizontal-rule", "|", "preview",
    "side-by-side", "fullscreen", "guide"
];

export default TextArea.extend({
    layout,
    currentEditor: null,
    change: null,
    value: null,

    init() {
        this._super(...arguments);
        this.set('toolbar', defaultToolbar);
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
