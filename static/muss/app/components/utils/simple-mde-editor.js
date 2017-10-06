import Ember from 'ember';
import layout from '../../templates/components/utils/simple-mde-editor';

const { TextArea, computed, merge, isEmpty } = Ember;
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
    buildSimpleMDEOptions: computed(function() {
        return {
            status: false,
            autofocus: true,
            toolbar: this.get('toolbar'),
            spellChecker: true
        };
    }),

    init() {
        this._super(...arguments);
        this.set('toolbar', defaultToolbar);
    },
    didInsertElement() {
        this.set('currentEditor', new window.SimpleMDE(
            merge({
                element: document.getElementById(this.elementId),
            }, this.get('buildSimpleMDEOptions'))
        ));
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
