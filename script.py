import html
import gradio as gr
from deep_translator import GoogleTranslator
import json
import os
import re
settings_path = "extensions/google_translate_plus/settings.json"

default_params = {
    "Translate_user_input": True,
    "Translate_system_output": True,
    "language string": "ru",
    "translate_paragraphs_individually": True,
    "debug": False,
    "special_symbol": "~",

}
try:
    if os.path.exists(settings_path):
        with open(settings_path, "r") as file:
            params = json.load(file)
        
        for key in default_params:
            if key not in params:
                params[key] = default_params[key]
    else:
        params = default_params.copy()
        with open(settings_path, "w") as file:
            json.dump(params, file, ensure_ascii=False, indent=4)

except json.JSONDecodeError:
    print("[Google translate plus]: Warning: settings.json has an invalid structure. Using default settings.")
    params = default_params.copy()

language_codes = {'Afrikaans': 'af', 'Albanian': 'sq', 'Amharic': 'am', 'Arabic': 'ar', 'Armenian': 'hy', 'Azerbaijani': 'az', 'Basque': 'eu', 'Belarusian': 'be', 'Bengali': 'bn', 'Bosnian': 'bs', 'Bulgarian': 'bg', 'Catalan': 'ca', 'Cebuano': 'ceb', 'Chinese (Simplified)': 'zh-CN', 'Chinese (Traditional)': 'zh-TW', 'Corsican': 'co', 'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl', 'English': 'en', 'Esperanto': 'eo', 'Estonian': 'et', 'Finnish': 'fi', 'French': 'fr', 'Frisian': 'fy', 'Galician': 'gl', 'Georgian': 'ka', 'German': 'de', 'Greek': 'el', 'Gujarati': 'gu', 'Haitian Creole': 'ht', 'Hausa': 'ha', 'Hawaiian': 'haw', 'Hebrew': 'iw', 'Hindi': 'hi', 'Hmong': 'hmn', 'Hungarian': 'hu', 'Icelandic': 'is', 'Igbo': 'ig', 'Indonesian': 'id', 'Irish': 'ga', 'Italian': 'it', 'Japanese': 'ja', 'Javanese': 'jw', 'Kannada': 'kn', 'Kazakh': 'kk', 'Khmer': 'km', 'Korean': 'ko', 'Kurdish': 'ku', 'Kyrgyz': 'ky', 'Lao': 'lo', 'Latin': 'la', 'Latvian': 'lv', 'Lithuanian': 'lt', 'Luxembourgish': 'lb', 'Macedonian': 'mk', 'Malagasy': 'mg', 'Malay': 'ms', 'Malayalam': 'ml', 'Maltese': 'mt', 'Maori': 'mi', 'Marathi': 'mr', 'Mongolian': 'mn', 'Myanmar (Burmese)': 'my', 'Nepali': 'ne', 'Norwegian': 'no', 'Nyanja (Chichewa)': 'ny', 'Pashto': 'ps', 'Persian': 'fa', 'Polish': 'pl', 'Portuguese (Portugal, Brazil)': 'pt', 'Punjabi': 'pa', 'Romanian': 'ro', 'Russian': 'ru', 'Samoan': 'sm', 'Scots Gaelic': 'gd', 'Serbian': 'sr', 'Sesotho': 'st', 'Shona': 'sn', 'Sindhi': 'sd', 'Sinhala (Sinhalese)': 'si', 'Slovak': 'sk', 'Slovenian': 'sl', 'Somali': 'so', 'Spanish': 'es', 'Sundanese': 'su', 'Swahili': 'sw', 'Swedish': 'sv', 'Tagalog (Filipino)': 'tl', 'Tajik': 'tg', 'Tamil': 'ta', 'Telugu': 'te', 'Thai': 'th', 'Turkish': 'tr', 'Ukrainian': 'uk', 'Urdu': 'ur', 'Uzbek': 'uz', 'Vietnamese': 'vi', 'Welsh': 'cy', 'Xhosa': 'xh', 'Yiddish': 'yi', 'Yoruba': 'yo', 'Zulu': 'zu'}

def input_modifier(string):
    if not params['Translate_user_input']:
        if params.get('debug'):
            print("[Google translate plus]: Input text translation disabled")
        return string
    
    return translate_text(string, params['language string'], "en")


def output_modifier(string):
    if not params['Translate_system_output']:
        if params.get('debug'):
            print("[Google translate plus]: Output nput text translation disabled")
        return string
    
    return translate_text(string, "en", params['language string'])

def translate_text(string, sourcelang, targetlang):
    if params.get('debug'):
        print(f"[Google translate plus]: The text is currently being translated: \n{string}\n\n")
    special_symbol = params['special_symbol']
    fragments = re.split(f"{special_symbol}(.*?){special_symbol}", string)
    
    translated_fragments = []

    for idx, fragment in enumerate(fragments):
        if idx % 2 == 1:
            translated_fragments.append(fragment)
            continue

        if params.get('translate_paragraphs_individually', False):
            lines = fragment.splitlines()
            translated_lines = [
                str(GoogleTranslator(source=sourcelang, target=targetlang).translate(html.unescape(line))) if line.strip() else line 
                for line in lines
            ]
            translated_fragments.append("\n".join(translated_lines))
        else:
            translated_str = str(GoogleTranslator(source=sourcelang, target=targetlang).translate(html.unescape(fragment)))
            translated_fragments.append(html.escape(translated_str))

    translated_text = "".join(translated_fragments).replace(special_symbol, '')

    if params.get('debug'):
        print(f"[Google translate plus]: The text has been successfully translated. Result: \n{translated_text}\n\n")

    return translated_text
    

def bot_prefix_modifier(string):
    return string

def save_params():
    with open(settings_path, "w") as file:
        json.dump(params, file, ensure_ascii=False, indent=4)


def ui():
    # Finding the language name from the language code to use as the default value
    language_name = list(language_codes.keys())[list(language_codes.values()).index(params['language string'])]

    # Gradio elements
    
    with gr.Column():
        Translate_user_input = gr.Checkbox(value=params['Translate_user_input'], label='Translate user input')
        Translate_system_output = gr.Checkbox(value=params['Translate_system_output'], label='Translate system output')
        special_symbol = gr.Textbox(value=params['special_symbol'], label='Special symbol. Text between these characters will not be translated. Some characters may cause errors.', type='text',)
        language = gr.Dropdown(value=language_name, choices=[k for k in language_codes], label='Language')
        translate_paragraphs_individually = gr.Checkbox(value=params.get('translate_paragraphs_individually', False), label='Translate paragraphs individually')
    
    
    # Event functions to update the parameters in the backend
    Translate_user_input.change(lambda x: params.update({"Translate_user_input": x}) or save_params(), Translate_user_input, None)
    Translate_system_output.change(lambda x: params.update({"Translate_system_output": x}) or save_params(), Translate_system_output, None)
    special_symbol.change(lambda x: params.update({"special_symbol": x}) or save_params(), special_symbol, None)
    language.change(lambda x: params.update({"language string": language_codes[x]}), language, None)
    translate_paragraphs_individually.change(lambda x: params.update({"translate_paragraphs_individually": x}), translate_paragraphs_individually, None)
