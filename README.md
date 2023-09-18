# Google translate plus
This is an extension for https://github.com/oobabooga/text-generation-webui.

This is an improved version of the https://github.com/oobabooga/text-generation-webui/tree/main/extensions/google_translate extension.

Developed with the aim to fix the following issues present in other translation extensions:
- Does not return an error if the text is too large for the Google Translate API. This extension translates each paragraph separately.
- Retains all paragraphs in the translated text. This extension translates each paragraph individually, and then merges them.
