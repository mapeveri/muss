document.addEventListener('DOMContentLoaded', function() {
  new SimpleMDE({
    toolbar: ["bold", "italic", "strikethrough", "heading", "|",
    "code", "quote", "unordered-list", "ordered-list", "|",
    "table", "link", "image", "horizontal-rule", "|", "preview",
    "side-by-side", "fullscreen", "guide"]
  });
});
