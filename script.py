import html
import gradio as gr
from deep_translator import GoogleTranslator, DeeplTranslator, LibreTranslator
from extensions.google_translate_plus.lang_codes import language_codes
import json
import os
import re
import concurrent.futures

settings_path = "extensions/google_translate_plus/settings.json"

default_params = {
    "Translate_user_input": True,
    "Translate_system_output": True,
    "language string": "ru",
    "debug": False,
    "special_symbol": "~",
    "newline_symbol": "@",
    "engine": "google",
    "LibreTranslateAPI": "http://localhost:5000/",
    "LibreTranslateAPIkey": "",
    "DeeplAPIkey": "",
    "DeeplFreeAPI": True,
    "max_length": 1500,
    "disable_split": False,
    "disable_newline_replacement": False,
    "enable_input_caching": True,
    "translation_timeout": 10  # Timeout in seconds
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

def input_modifier(string):
    if not params.get('Translate_user_input', True):
        if params.get('debug', False):
            print("[Google translate plus]: Input text translation disabled")
        return string

    if params.get('enable_input_caching', True):
        if hasattr(input_modifier, 'previous_text') and hasattr(input_modifier, 'previous_translation'):
            if string == input_modifier.previous_text:
                if params.get('debug', False):
                    print("[Google translate plus]: Using cached translation")
                return input_modifier.previous_translation

    translated_text = translate_text(string, params.get('language string', 'ru'), "en")

    if params.get('enable_input_caching', True):
        input_modifier.previous_text = string
        input_modifier.previous_translation = translated_text

    return translated_text

def output_modifier(string):
    if not params.get('Translate_system_output', True):
        if params.get('debug', False):
            print("[Google translate plus]: Output text translation disabled")
        return string

    return translate_text(string, "en", params.get('language string', 'ru'))

def translate_text(string, sourcelang, targetlang):
    debug = params.get('debug', False)
    engine = params.get('engine', 'google')
    if debug:
        print("\n------[Google translate plus debug info]-----")
        print(f"[Google translate plus]: Using {engine.capitalize()} Translator...")

    MAX_LEN = params.get('max_length', 1500)
    special_symbol = params.get('special_symbol', '~')
    newline_symbol = params.get('newline_symbol', '@')
    disable_split = params.get('disable_split', False)
    disable_newline_replacement = params.get('disable_newline_replacement', False)
    LibreTranslateAPI = params.get('LibreTranslateAPI', "http://localhost:5000/")
    LibreTranslateAPIkey = params.get('LibreTranslateAPIkey', "")
    DeeplAPIkey = params.get('DeeplAPIkey', "")
    DeeplFreeAPI = params.get('DeeplFreeAPI', True)
    translation_timeout = params.get('translation_timeout', 10)

    if debug:
        print("[Google translate plus]: Translation parameters:")
        print(f"  Special symbol: {special_symbol}")
        print(f"  Newline symbol: {newline_symbol}")
        print(f"  Disable split: {disable_split}")
        print(f"  Disable newline replacement: {disable_newline_replacement}\n")
        print("[Google translate plus]: The text is currently being translated:")
        print("\033[32m" + string + "\033[0m\n")

    # Validate special_symbol and newline_symbol
    if not special_symbol:
        if debug:
            print("[Google translate plus]: Error: Special symbol cannot be empty.")
        return string
    if not newline_symbol:
        if debug:
            print("[Google translate plus]: Error: Newline symbol cannot be empty.")
        return string

    fragments = re.split(f"{re.escape(special_symbol)}(.*?){re.escape(special_symbol)}", string)

    translated_fragments = []
    try:
        for idx, fragment in enumerate(fragments):
            if idx % 2 == 1:
                # Text between special symbols is not translated
                translated_fragments.append(fragment)
                continue

            if not disable_newline_replacement:
                fragment = fragment.replace("\n", newline_symbol + " ")

            if disable_split or len(fragment) <= MAX_LEN:
                translated_str = translate_with_timeout(fragment, sourcelang, targetlang, engine, LibreTranslateAPI, LibreTranslateAPIkey, DeeplAPIkey, DeeplFreeAPI, translation_timeout)
                if translated_str is None:
                    return string  # Return original text if translation failed
                translated_fragments.append(translated_str)
            else:
                while len(fragment) > 0:
                    if len(fragment) <= MAX_LEN:
                        part = fragment
                        fragment = ''
                    else:
                        pos = fragment.rfind(newline_symbol, 0, MAX_LEN)
                        if pos == -1 or pos == 0:
                            pos = MAX_LEN
                        part = fragment[:pos]
                        fragment = fragment[pos:]

                    translated_part = translate_with_timeout(part, sourcelang, targetlang, engine, LibreTranslateAPI, LibreTranslateAPIkey, DeeplAPIkey, DeeplFreeAPI, translation_timeout)
                    if translated_part is None:
                        return string  # Return original text if translation failed
                    translated_fragments.append(translated_part)

    except Exception as e:
        if debug:
            print(f"[Google translate plus]: An error occurred during translation: {e}")
        return string

    translated_text = "".join(translated_fragments)

    if not disable_newline_replacement:
        regex_pattern = r'\s?{}\s?'.format(re.escape(newline_symbol))
        translated_text = re.sub(regex_pattern, '\n', translated_text)
    translated_text = translated_text.replace("&#x27;", "'").replace("&quot;", '"')

    if debug:
        print("[Google translate plus]: The text has been successfully translated. Result:")
        print("\033[32m" + translated_text + "\033[0m\n")
        print("---------------------------------------------")
    return translated_text

def translate_with_timeout(fragment, sourcelang, targetlang, engine, LibreTranslateAPI, LibreTranslateAPIkey, DeeplAPIkey, DeeplFreeAPI, timeout):
    debug = params.get('debug', False)
    attempt = 0
    max_attempts = 2
    while attempt < max_attempts:
        attempt += 1
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(perform_translation, fragment, sourcelang, targetlang, engine, LibreTranslateAPI, LibreTranslateAPIkey, DeeplAPIkey, DeeplFreeAPI)
                translated_str = future.result(timeout=timeout)
                return translated_str
        except concurrent.futures.TimeoutError:
            if attempt < max_attempts:
                if debug:
                    print("[Google translate plus]: Translation timed out. Retrying...")
                gr.warning("Translation timed out. Retrying...")
            else:
                if debug:
                    print("[Google translate plus]: Translation timed out again. Returning original text.")
                gr.error("Translation timed out again. Returning original text.")
                return None
        except Exception as e:
            if debug:
                print(f"[Google translate plus]: An error occurred during translation: {e}")
            gr.error(f"An error occurred during translation: {e}")
            return None

def perform_translation(fragment, sourcelang, targetlang, engine, LibreTranslateAPI, LibreTranslateAPIkey, DeeplAPIkey, DeeplFreeAPI):
    fragment_unescaped = html.unescape(fragment)
    if engine == 'google':
        translated_str = str(GoogleTranslator(source=sourcelang, target=targetlang).translate(fragment_unescaped))
    elif engine == 'libre':
        translated_str = str(LibreTranslator(
            source=sourcelang,
            target=targetlang,
            base_url=LibreTranslateAPI,
            api_key=LibreTranslateAPIkey
        ).translate(fragment_unescaped))
    elif engine == 'deepl':
        translated_str = str(DeeplTranslator(
            source=sourcelang,
            target=targetlang,
            api_key=DeeplAPIkey,
            use_free_api=DeeplFreeAPI
        ).translate(fragment_unescaped))
    else:
        translated_str = fragment  # No translation
    return translated_str

def bot_prefix_modifier(string):
    return string

def save_params():
    with open(settings_path, "w") as file:
        json.dump(params, file, ensure_ascii=False, indent=4)

def ui():
    # Finding the language name from the language code to use as the default value
    language_name = next((k for k, v in language_codes.items() if v == params.get('language string', 'ru')), 'English')
    engine_name = next((k for k, v in engines.items() if v == params.get('engine', 'google')), 'Google Translate')

    # Gradio elements
    with gr.Accordion("Google Translate Plus", open=False):
        with gr.Column():
            Translate_user_input = gr.Checkbox(value=params.get('Translate_user_input', True), label='Translate user input')
            Translate_system_output = gr.Checkbox(value=params.get('Translate_system_output', True), label='Translate system output')
            enable_input_caching = gr.Checkbox(value=params.get('enable_input_caching', True), label='Enable input caching',
                info='If enabled, identical input texts will use the cached translation instead of re-translating.')
            disable_split = gr.Checkbox(value=params.get('disable_split', False), label='Disable split',
                info='Disables splitting long text into paragraphs. May improve translation quality, but Google Translate may give an error due to too long text. This will also disable the special symbol.')
            disable_newline_replacement = gr.Checkbox(value=params.get('disable_newline_replacement', False), label='Disable newline replacement',
                info='Disables the replacement of a newline by a special character. Recommended when using LibreTranslate.')
            with gr.Accordion("Advanced", open=False):
                language = gr.Dropdown(value=language_name, choices=[k for k in language_codes], label='Language')
                engine = gr.Dropdown(value=engine_name, choices=[k for k in engines], label='Translation service')
                special_symbol = gr.Textbox(value=params.get('special_symbol', '~'), label='Special symbol.',
                    info='Text between two such syblols will not be translated. May cause inaccurate translations, and some symbols other than the standard ~ may cause errors.', type='text',
                    )
                newline_symbol = gr.Textbox(value=params.get('newline_symbol', '@'), label='Newline symbol',
                    info='Before translation, this symbol replaces the new line, and after translation it is removed. Needed to save strings after translation. Some symbols may cause errors.',
                    type='text',)
                max_length = gr.Number(value=params.get('max_length', 1500), label='Maximum text length',
                    info='If the text length exceeds this value, it will be divided into paragraphs before translation, each of which will be translated separately.',
                    precision=0)
                translation_timeout = gr.Number(value=params.get('translation_timeout', 10), label='Translation timeout (seconds)',
                    info='Maximum time to wait for translation before retrying or failing.',
                    precision=0)
                debug = gr.Checkbox(value=params.get('debug', False), label='Log translation debug info to console')
            with gr.Accordion("Translator settings", open=False):
                LibreTranslateAPI = gr.Textbox(value=params.get('LibreTranslateAPI', "http://localhost:5000/"), label='LibreTranslate API',
                    info='Your LibreTranslate address and port.',
                    type='text',)
                LibreTranslateAPIkey = gr.Textbox(value=params.get('LibreTranslateAPIkey', ""), label='LibreTranslate API key',
                    info='Your LibreTranslate API key',
                    type='text',)
                DeeplAPIkey = gr.Textbox(value=params.get('DeeplAPIkey', ""), label='Deepl API key',
                    info='Your Deepl Translator API key',
                    type='text',)
                DeeplFreeAPI = gr.Checkbox(value=params.get('DeeplFreeAPI', True), label='Use the free Deepl API')

    # Event functions to update the parameters in the backend
    Translate_user_input.change(lambda x: params.update({"Translate_user_input": x}) or save_params(), Translate_user_input, None)
    Translate_system_output.change(lambda x: params.update({"Translate_system_output": x}) or save_params(), Translate_system_output, None)
    enable_input_caching.change(lambda x: params.update({"enable_input_caching": x}) or save_params(), enable_input_caching, None)
    disable_split.change(lambda x: params.update({"disable_split": x}) or save_params(), disable_split, None)
    disable_newline_replacement.change(lambda x: params.update({"disable_newline_replacement": x}) or save_params(), disable_newline_replacement, None)

    # Advanced settings
    def update_special_symbol(x):
        if not x:
            raise gr.Error("Special symbol cannot be empty.")
        params.update({"special_symbol": x})
        save_params()
    special_symbol.change(update_special_symbol, special_symbol, None)

    def update_newline_symbol(x):
        if not x:
            raise gr.Error("Newline symbol cannot be empty.")
        params.update({"newline_symbol": x})
        save_params()
    newline_symbol.change(update_newline_symbol, newline_symbol, None)

    language.change(lambda x: params.update({"language string": language_codes[x]}) or save_params(), language, None)
    engine.change(lambda x: params.update({"engine": engines[x]}) or save_params(), engine, None)
    max_length.change(lambda x: params.update({"max_length": int(x)}) or save_params(), max_length, None)
    translation_timeout.change(lambda x: params.update({"translation_timeout": int(x)}) or save_params(), translation_timeout, None)
    debug.change(lambda x: params.update({"debug": x}) or save_params(), debug, None)

    # Translator settings
    LibreTranslateAPI.change(lambda x: params.update({"LibreTranslateAPI": x}) or save_params(), LibreTranslateAPI, None)
    LibreTranslateAPIkey.change(lambda x: params.update({"LibreTranslateAPIkey": x}) or save_params(), LibreTranslateAPIkey, None)
    DeeplAPIkey.change(lambda x: params.update({"DeeplAPIkey": x}) or save_params(), DeeplAPIkey, None)
    DeeplFreeAPI.change(lambda x: params.update({"DeeplFreeAPI": x}) or save_params(), DeeplFreeAPI, None)
