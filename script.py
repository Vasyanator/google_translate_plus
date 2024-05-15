import html
import gradio as gr
from deep_translator import GoogleTranslator, DeeplTranslator, LibreTranslator
import json
import os
import re
settings_path = "extensions/google_translate_plus/settings.json"

default_params = {
    "Translate_user_input": True,
    "Translate_system_output": True,
    "language string": "ru",
    "debug": False,
    "special_symbol": "~",
    "newline_symbol": "@",
    "engine": "google",
    "LibreTranslateAPI":"http://localhost:5000/",
    "LibreTranslateAPIkey": "",
    "DeeplAPIkey": "",
    "DeeplFreeAPI": True,
    "max_length": 1500,
    "disable_split": False, 
    "disable_newline_replacement": False
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

engines = {'Deepl Translator': 'deepl', 'Google Translate': 'google', 'LibreTranslate (local)': 'libre'}
language_codes = {'Afrikaans': 'af', 'Albanian': 'sq', 'Amharic': 'am', 'Arabic': 'ar', 'Armenian': 'hy', 'Azerbaijani': 'az', 'Basque': 'eu', 'Belarusian': 'be', 'Bengali': 'bn', 'Bosnian': 'bs', 'Bulgarian': 'bg', 'Catalan': 'ca', 'Cebuano': 'ceb', 'Chinese (Simplified)': 'zh-CN', 'Chinese (Traditional)': 'zh-TW', 'Corsican': 'co', 'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl', 'English': 'en', 'Esperanto': 'eo', 'Estonian': 'et', 'Finnish': 'fi', 'French': 'fr', 'Frisian': 'fy', 'Galician': 'gl', 'Georgian': 'ka', 'German': 'de', 'Greek': 'el', 'Gujarati': 'gu', 'Haitian Creole': 'ht', 'Hausa': 'ha', 'Hawaiian': 'haw', 'Hebrew': 'iw', 'Hindi': 'hi', 'Hmong': 'hmn', 'Hungarian': 'hu', 'Icelandic': 'is', 'Igbo': 'ig', 'Indonesian': 'id', 'Irish': 'ga', 'Italian': 'it', 'Japanese': 'ja', 'Javanese': 'jw', 'Kannada': 'kn', 'Kazakh': 'kk', 'Khmer': 'km', 'Korean': 'ko', 'Kurdish': 'ku', 'Kyrgyz': 'ky', 'Lao': 'lo', 'Latin': 'la', 'Latvian': 'lv', 'Lithuanian': 'lt', 'Luxembourgish': 'lb', 'Macedonian': 'mk', 'Malagasy': 'mg', 'Malay': 'ms', 'Malayalam': 'ml', 'Maltese': 'mt', 'Maori': 'mi', 'Marathi': 'mr', 'Mongolian': 'mn', 'Myanmar (Burmese)': 'my', 'Nepali': 'ne', 'Norwegian': 'no', 'Nyanja (Chichewa)': 'ny', 'Pashto': 'ps', 'Persian': 'fa', 'Polish': 'pl', 'Portuguese (Portugal, Brazil)': 'pt', 'Punjabi': 'pa', 'Romanian': 'ro', 'Russian': 'ru', 'Samoan': 'sm', 'Scots Gaelic': 'gd', 'Serbian': 'sr', 'Sesotho': 'st', 'Shona': 'sn', 'Sindhi': 'sd', 'Sinhala (Sinhalese)': 'si', 'Slovak': 'sk', 'Slovenian': 'sl', 'Somali': 'so', 'Spanish': 'es', 'Sundanese': 'su', 'Swahili': 'sw', 'Swedish': 'sv', 'Tagalog (Filipino)': 'tl', 'Tajik': 'tg', 'Tamil': 'ta', 'Telugu': 'te', 'Thai': 'th', 'Turkish': 'tr', 'Ukrainian': 'uk', 'Urdu': 'ur', 'Uzbek': 'uz', 'Vietnamese': 'vi', 'Welsh': 'cy', 'Xhosa': 'xh', 'Yiddish': 'yi', 'Yoruba': 'yo', 'Zulu': 'zu'}

previous_text = None
previous_translation = None

def input_modifier(string):
    global previous_text, previous_translation
    
    if not params['Translate_user_input']:
        if params.get('debug'):
            print("[Google translate plus]: Input text translation disabled")
        return string
    
    if string == previous_text:
        if params.get('debug'):
            print("[Google translate plus]: Using cached translation")
        return previous_translation
    
    translated_text = translate_text(string, params['language string'], "en")
    
    previous_text = string
    previous_translation = translated_text
    
    return translated_text

def output_modifier(string):
    if not params['Translate_system_output']:
        if params.get('debug'):
            print("[Google translate plus]: Output text translation disabled")
        return string
    
    return translate_text(string, "en", params['language string'])

def translate_text(string, sourcelang, targetlang):
    debug = params.get('debug')
    engine = params.get('engine')
    if debug:
        print("\n------[Google translate plus debug info]-----")
        if engine == 'google':
            print("[Google translate plus]: Using Google Translate...")
        elif engine == 'libre':
            print("[Google translate plus]: Using LibreTranslate...")
        elif engine == 'deepl':
            print("[Google translate plus]: Using Deepl...")
        
    MAX_LEN = params.get('max_length', 1500)
    special_symbol = params.get('special_symbol', '~')
    newline_symbol = params.get('newline_symbol', '@')
    disable_split = params.get('disable_split', False)
    disable_newline_replacement = params.get('disable_newline_replacement', False)
    LibreTranslateAPI = params['LibreTranslateAPI']
    LibreTranslateAPIkey = params['LibreTranslateAPIkey']
    DeeplAPIkey = params['DeeplAPIkey']
    DeeplFreeAPI = params['DeeplFreeAPI']
    
    if debug:
        print("[Google translate plus]: Параметры перевода:" + f"Специальный символ: {special_symbol}\n" + f"Символ новой строки: {newline_symbol}\n" + f"Отключить разбиение: {disable_split}\n" + f"Отключить замену новой строки: {disable_newline_replacement}\n")
        print("[Google translate plus]: The text is currently being translated:", "\033[32m\n" + string)
        print("\n\n")

    if disable_newline_replacement:
        fragments = [string]
    else:
        fragments = re.split(f"{special_symbol}(.*?){special_symbol}", string)

    translated_fragments = []
    try:
        for idx, fragment in enumerate(fragments):
            if idx % 2 == 1:
                translated_fragments.append(fragment)
                continue

            if not disable_newline_replacement:
                fragment = fragment.replace("\n", newline_symbol + " ")

            if disable_split or len(fragment) <= MAX_LEN:
                if engine == 'google':
                    translated_str = str(GoogleTranslator(source=sourcelang, target=targetlang).translate(html.unescape(fragment)))
                elif engine == 'libre':
                    str(LibreTranslator(source=sourcelang, target=targetlang, base_url=LibreTranslateAPI, api_key=LibreTranslateAPIkey).translate(html.unescape(fragment)))
                elif engine == 'deepl':
                    str(DeeplTranslator(source=sourcelang, target=targetlang, api_key=DeeplAPIkey, use_free_api=DeeplFreeAPI).translate(html.unescape(fragment)))
                translated_fragments.append(html.escape(translated_str))
            else:
                while len(fragment) > MAX_LEN:
                    pos = fragment.rfind(newline_symbol, 0, MAX_LEN)
                    if pos == -1:
                        pos = MAX_LEN
                    part = fragment[:pos]
                    fragment = fragment[pos:]
                    if engine == 'google':
                        translated_part = str(GoogleTranslator(source=sourcelang, target=targetlang).translate(html.unescape(part)))
                    elif engine == 'libre':
                        translated_part = str(LibreTranslator(source=sourcelang, target=targetlang, base_url=LibreTranslateAPI, api_key=LibreTranslateAPIkey).translate(html.unescape(part)))
                    elif engine == 'deepl':
                        translated_part = str(DeeplTranslator(source=sourcelang, target=targetlang, api_key=DeeplAPIkey, use_free_api=DeeplFreeAPI).translate(html.unescape(part)))
                    translated_fragments.append(html.escape(translated_part))

                if engine == 'google':
                    translated_str = str(GoogleTranslator(source=sourcelang, target=targetlang).translate(html.unescape(fragment)))
                elif engine == 'libre':
                    str(LibreTranslator(source=sourcelang, target=targetlang, base_url=LibreTranslateAPI, api_key=LibreTranslateAPIkey).translate(html.unescape(fragment)))
                elif engine == 'deepl':
                    str(DeeplTranslator(source=sourcelang, target=targetlang, api_key=DeeplAPIkey, use_free_api=DeeplFreeAPI).translate(html.unescape(fragment)))
                translated_fragments.append(html.escape(translated_str))

    except:
        gr.Error("An error occurred during translation. The selected translator may not be available.")
        return string
    translated_text = "".join(translated_fragments)
    
    if not disable_newline_replacement:
        regex_pattern = r'\s?{}\s?'.format(re.escape(newline_symbol))
        translated_text = re.sub(regex_pattern, '\n', translated_text)

    if debug:
        print("[Google translate plus]: The text has been successfully translated. Result:", "\033[32m\n" + translated_text + "\033[0m\n\n")
        print("---------------------------------------------")
    return translated_text
    

def bot_prefix_modifier(string):
    return string

def save_params():
    with open(settings_path, "w") as file:
        json.dump(params, file, ensure_ascii=False, indent=4)


def ui():
    # Finding the language name from the language code to use as the default value
    language_name = list(language_codes.keys())[list(language_codes.values()).index(params['language string'])]
    engine = list(engines.keys())[list(engines.values()).index(params['engine'])]

    # Gradio elements
    with gr.Accordion("Google Translate Plus", open=False):
        with gr.Column():
            Translate_user_input = gr.Checkbox(value=params['Translate_user_input'], label='Translate user input')
            Translate_system_output = gr.Checkbox(value=params['Translate_system_output'], label='Translate system output')
            disable_split = gr.Checkbox(value=params['disable_split'], label='Disable split', 
                info='Disables splitting long text into paragraphs. May improve translation quality, but Google Translate may give an error due to too long text.')
            disable_newline_replacement = gr.Checkbox(value=params['disable_newline_replacement'], label='Disable newline replacement', 
                info='Disables the replacement of a newline by a special character. Recommended when using LibreTransalte.')
            with gr.Accordion("Advanced", open=False):
                language = gr.Dropdown(value=language_name, choices=[k for k in language_codes], label='Language')
                engine = gr.Dropdown(value=engine, choices=[k for k in engines], label='Translation service')
                special_symbol = gr.Textbox(value=params['special_symbol'], label='Special symbol.', 
                    info='Text between these symbols will not be translated. Some symbols may cause errors.', type='text',
                    )
                newline_symbol = gr.Textbox(value=params['newline_symbol'], label='newline symbol', 
                    info='Before translation, this symbol replaces the new line, and after translation it is removed. Needed to save strings after translation. Some symbols may cause errors.', 
                    type='text',)
                max_length = gr.Textbox(value=params['max_length'], label='Maximum text length', 
                    info='If the text length exceeds this value, it will be divided into paragraphs before translation, each of which will be translated separately.', 
                    type='text',)
                debug = gr.Checkbox(value=params.get('debug', False), label='Log translation debug info to console')
            with gr.Accordion("Translatorn settings", open=False):
                LibreTranslateAPI = gr.Textbox(value=params['LibreTranslateAPI'], label='LibreTranslate API', 
                    info='Your LibreTransalte address and port.', 
                    type='text',)
                LibreTranslateAPIkey = gr.Textbox(value=params['LibreTranslateAPIkey'], label='LibreTranslate API key', 
                    info='Your LibreTransalte API key', 
                    type='text',)
                DeeplAPIkey = gr.Textbox(value=params['DeeplAPIkey'], label='Deepl API key', 
                    info='Your Deepl Translator API key', 
                    type='text',)
                DeeplFreeAPI = gr.Checkbox(value=params['DeeplFreeAPI'], label='Use the free Deepl API')
    
    # Event functions to update the parameters in the backend
    Translate_user_input.change(lambda x: params.update({"Translate_user_input": x}) or save_params(), Translate_user_input, None)
    Translate_system_output.change(lambda x: params.update({"Translate_system_output": x}) or save_params(), Translate_system_output, None)
    disable_split.change(lambda x: params.update({"disable_split": x}) or save_params(), disable_split, None)
    disable_newline_replacement.change(lambda x: params.update({"disable_newline_replacement": x}) or save_params(), disable_newline_replacement, None)
    #adnanced
    special_symbol.change(lambda x: params.update({"special_symbol": x}) or save_params(), special_symbol, None)
    newline_symbol.change(lambda x: params.update({"newline_symbol": x}) or save_params(), newline_symbol, None)
    language.change(lambda x: params.update({"language string": language_codes[x]}), language, None)
    engine.change(lambda x: params.update({"engine": engines[x]}), engine, None)
    max_length.change(lambda x: params.update({"max_length": int(x)}) or save_params(), max_length, None)
    debug.change(lambda x: params.update({"debug": x}), debug, None)

    LibreTranslateAPI.change(lambda x: params.update({"LibreTranslateAPI": x}) or save_params(), LibreTranslateAPI, None)
    LibreTranslateAPIkey.change(lambda x: params.update({"LibreTranslateAPIkey": x}) or save_params(), LibreTranslateAPIkey, None)
    DeeplAPIkey.change(lambda x: params.update({"DeeplAPIkey": x}) or save_params(), DeeplAPIkey, None)
    DeeplFreeAPI.change(lambda x: params.update({"DeeplFreeAPI": x}) or save_params(), DeeplFreeAPI, None)
