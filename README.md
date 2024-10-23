# Google translate plus
This is an extension for https://github.com/oobabooga/text-generation-webui.

This is an improved version of the https://github.com/oobabooga/text-generation-webui/tree/main/extensions/google_translate extension.

## Functions
- Preserves strings after translation by replacing `\n` with `@ ` before translating the text and vice versa.
- Some text fragment may not be translated if it is taken between special characters (default `~`). Example: ```~### Instruction:~ <your instruction> ~### Response:~``` which the model will see as ```~### Instruction:~ <your translated instruction> ~### Response:~```
- You can enable or disable translation of user input and AI output.


Developed with the aim to fix the following issues present in other translation extensions:
- Does not return an error if the text is too large for the Google Translate API. This extension translates each paragraph separately.
- Retains all paragraphs in the translated text. This extension translates each paragraph individually, and then merges them.
