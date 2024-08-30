import React from 'react';

// LANGUAGES constant for Google Translate
const GOOGLE_TRANSLATE_LANGUAGES = {
    "af": "afrikaans",
    "am": "amharic",
    "ar": "arabic",
    "az": "azerbaijani",
    "ba": "bashkir",
    "be": "belarusian",
    "bg": "bulgarian",
    "bn": "bengali",
    "bo": "tibetan",
    "br": "breton",
    "bs": "bosnian",
    "ca": "catalan",
    "cs": "czech",
    "cy": "welsh",
    "da": "danish",
    "de": "german",
    "el": "greek",
    "en": "english",
    "es": "spanish",
    "et": "estonian",
    "eu": "basque",
    "fa": "persian",
    "fi": "finnish",
    "fo": "faroese",
    "fr": "french",
    "gl": "galician",
    "gu": "gujarati",
    "ha": "hausa",
    "haw": "hawaiian",
    "he": "hebrew",
    "hi": "hindi",
    "hr": "croatian",
    "ht": "haitian creole",
    "hu": "hungarian",
    "hy": "armenian",
    "id": "indonesian",
    "is": "icelandic",
    "it": "italian",
    "ja": "japanese",
    "jw": "javanese",
    "ka": "georgian",
    "kk": "kazakh",
    "km": "khmer",
    "kn": "kannada",
    "ko": "korean",
    "ku": "kurdish",
    "ky": "kyrgyz",
    "la": "latin",
    "lb": "luxembourgish",
    "lo": "lao",
    "lt": "lithuanian",
    "lv": "latvian",
    "mg": "malagasy",
    "mi": "maori",
    "mk": "macedonian",
    "ml": "malayalam",
    "mn": "mongolian",
    "mr": "marathi",
    "ms": "malay",
    "mt": "maltese",
    "my": "myanmar",
    "ne": "nepali",
    "nl": "dutch",
    "no": "norwegian",
    "oc": "occitan",
    "pa": "punjabi",
    "pl": "polish",
    "ps": "pashto",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "sd": "sindhi",
    "si": "sinhala",
    "sk": "slovak",
    "sl": "slovenian",
    "sm": "samoan",
    "sn": "shona",
    "so": "somali",
    "sq": "albanian",
    "sr": "serbian",
    "st": "southern sotho",
    "su": "sundanese",
    "sv": "swedish",
    "sw": "swahili",
    "ta": "tamil",
    "te": "telugu",
    "tg": "tajik",
    "th": "thai",
    "tk": "turkmen",
    "tl": "tagalog",
    "tr": "turkish",
    "tt": "tatar",
    "ug": "uyghur",
    "uk": "ukrainian",
    "ur": "urdu",
    "uz": "uzbek",
    "vi": "vietnamese",
    "xh": "xhosa",
    "yi": "yiddish",
    "yo": "yoruba",
    "zh": "chinese",
    "zu": "zulu"
};

// GoogleTranslateLanguageSelector component
const GoogleTranslateLanguageSelector = ({ translateLanguage, setTranslateLanguage }) => {
    return (
        <div className="form-group mt-3">
             
            <select
                id="google-language"
                className="form-select"
                value={translateLanguage}
                onChange={(e) => setTranslateLanguage(e.target.value)}
            >
                {Object.entries(GOOGLE_TRANSLATE_LANGUAGES).map(([code, name]) => (
                    <option key={code} value={code}>
                        {name.charAt(0).toUpperCase() + name.slice(1)}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default GoogleTranslateLanguageSelector;
