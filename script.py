import html
import gradio as gr
from deep_translator import GoogleTranslator
import json
import os

settings_path = "extensions/google_translate_plus/settings.json"

default_params = {
    "Translate_user_input": True,
    "Translate_system_output": True,
    "language string": "ru",
    "translate_paragraphs_individually": True,
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
    """
    This function is applied to your text inputs before
    they are fed into the model.
    """
    if not params['Translate_user_input']:
        return string

    if params.get('translate_paragraphs_individually', False):
        lines = string.splitlines()
        translated_lines = [
            GoogleTranslator(source=params['language string'], target='en').translate(line) if line.strip() else line 
            for line in lines
        ]
        translated_text = "\n".join(translated_lines)
    else:
        translated_text = GoogleTranslator(source=params['language string'], target='en').translate(string)
    return translated_text


def output_modifier(string):
    """
    This function is applied to the model outputs.
    """
    if not params['Translate_system_output']:
        return string

    if params.get('translate_paragraphs_individually', False):
        lines = string.splitlines()
        translated_lines = [
            GoogleTranslator(source='en', target=params['language string']).translate(html.unescape(line)) if line.strip() else line 
            for line in lines
        ]
        translated_text = "\n".join(translated_lines)
    else:
        translated_str = GoogleTranslator(source='en', target=params['language string']).translate(html.unescape(string))
        translated_text = html.escape(translated_str)

    return translated_text

def bot_prefix_modifier(string):
    """
    This function is only applied in chat mode. It modifies
    the prefix text for the Bot and can be used to bias its
    behavior.
    """

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
        language = gr.Dropdown(value=language_name, choices=[k for k in language_codes], label='Language')
        translate_paragraphs_individually = gr.Checkbox(value=params.get('translate_paragraphs_individually', False), label='Translate paragraphs individually')
    
    # Event functions to update the parameters in the backend
    Translate_user_input.change(lambda x: params.update({"Translate_user_input": x}) or save_params(), Translate_user_input, None)
    Translate_system_output.change(lambda x: params.update({"Translate_system_output": x}) or save_params(), Translate_system_output, None)
    language.change(lambda x: params.update({"language string": language_codes[x]}), language, None)
    translate_paragraphs_individually.change(lambda x: params.update({"translate_paragraphs_individually": x}), translate_paragraphs_individually, None)
