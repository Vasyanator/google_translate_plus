# Google translate plus
An enhanced version of the extension available at https://github.com/oobabooga/text-generation-webui/tree/main/extensions/google_translate, yet lacking the redundant features found in https://github.com/janvarev/multi_translate.

Developed with the aim to fix the following issues present in other translation extensions:
- Does not return an error if the text is too large for the Google Translate API. This extension translates each paragraph separately.
- Retains all paragraphs in the translated text. This extension translates each paragraph individually, and then merges them.
