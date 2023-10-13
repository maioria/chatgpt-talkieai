import json

import azure.cognitiveservices.speech as speechsdk

from app.config import Config
from app.core.logging import logging
from pydub import AudioSegment
import os

key = Config.AZURE_KEY
region = "eastasia"

speech_config = speechsdk.SpeechConfig(subscription=key, region=region)

speech_synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config, audio_config=None
)


def speech_by_ssml(
    content: str,
    output_path_str: str,
    voice_name: str = "en-US-JennyNeural",
    speech_rate: str = "1.0",
    feel: str = "neutral",
    targetLang: str = "en-US",
):
    """可定制的文本转语音"""
    ssml = f"""
    <speak version="1.0"  xmlns:mstts="https://www.w3.org/2001/mstts" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="{targetLang}">
      <voice name="{voice_name}">
        <prosody rate="{speech_rate}">
          <mstts:express-as style="{feel}" styledegree="1.5">
            {content}
          </mstts:express-as>
        </prosody>
      </voice>
    </speak>
    """
    logging.info(ssml)
    speech_synthesis_result = speech_synthesizer.start_speaking_ssml_async(
        ssml
    ).get()  # Get the audio data stream
    audio_data_stream = speechsdk.AudioDataStream(speech_synthesis_result)

    if (
        speech_synthesis_result.reason
        == speechsdk.ResultReason.SynthesizingAudioStarted
    ):
        logging.info("init 1")
        audio_data_stream.save_to_wav_file(output_path_str)
        logging.info("init 2")
    else:
        logging.error(
            "Speech synthesis failed: {}".format(speech_synthesis_result.reason)
        )
        if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            logging.error(
                "Speech synthesis canceled: {}".format(cancellation_details.reason)
            )
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    logging.error(
                        "Error details: {}".format(cancellation_details.error_details)
                    )
                    logging.error(
                        "Did you set the speech resource key and region values?"
                    )
        raise Exception("语音合成失败")


def speech_pronunciation(content: str, speech_path: str, language: str = "en-US"):
    """发音评估"""
    audio_config = speechsdk.audio.AudioConfig(filename=speech_path)
    speech_config.speech_recognition_language = language
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )
    # "{\"referenceText\":\"good morning\",\"gradingSystem\":\"HundredMark\",\"granularity\":\"Phoneme\",\"EnableMiscue\":true}" 通过dict生成json
    json_param = {
        "referenceText": content,
        "gradingSystem": "HundredMark",
        "granularity": "Word",
        "EnableMiscue": True,
    }
    pronunciation_assessment_config = speechsdk.PronunciationAssessmentConfig(
        json_string=json.dumps(json_param)
    )

    pronunciation_assessment_config.apply_to(speech_recognizer)

    speech_recognition_result = speech_recognizer.recognize_once()
    pronunciation_assessment_result = speechsdk.PronunciationAssessmentResult(
        speech_recognition_result
    )
    result = {
        "accuracy_score": pronunciation_assessment_result.accuracy_score,
        "fluency_score": pronunciation_assessment_result.fluency_score,
        "completeness_score": pronunciation_assessment_result.completeness_score,
        "pronunciation_score": pronunciation_assessment_result.pronunciation_score,
    }
    original_words = pronunciation_assessment_result.words
    result_words = []
    # 循环words，获取每个单词的发音评估结果
    for word in original_words:
        result_words.append(
            {
                "word": word.word,
                "accuracy_score": word.accuracy_score,
                "error_type": word.error_type,
            }
        )
    result["words"] = result_words
    return result


# 单词发单评估，可以精确到每一个音素
def word_speech_pronunciation(word: str, speech_path: str, language: str = "en-US"):
    audio_config = speechsdk.audio.AudioConfig(filename=speech_path)
    speech_config.speech_recognition_language = language
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )
    # "{\"referenceText\":\"good morning\",\"gradingSystem\":\"HundredMark\",\"granularity\":\"Phoneme\",\"EnableMiscue\":true}" 通过dict生成json
    json_param = {
        "referenceText": word,
        "gradingSystem": "HundredMark",
        "granularity": "Phoneme",
        "EnableMiscue": True,
        "phonemeAlphabet": "IPA",
    }
    pronunciation_assessment_config = speechsdk.PronunciationAssessmentConfig(
        json_string=json.dumps(json_param)
    )

    pronunciation_assessment_config.apply_to(speech_recognizer)

    speech_recognition_result = speech_recognizer.recognize_once()
    pronunciation_assessment_result = speechsdk.PronunciationAssessmentResult(
        speech_recognition_result
    )
    result = {
        "accuracy_score": pronunciation_assessment_result.accuracy_score,
        "fluency_score": pronunciation_assessment_result.fluency_score,
        "completeness_score": pronunciation_assessment_result.completeness_score,
        "pronunciation_score": pronunciation_assessment_result.pronunciation_score,
    }
    original_words = pronunciation_assessment_result.words
    result_words = []
    # 循环words，获取每个单词的发音评估结果
    for word in original_words:

        # 获取音素评估结果
        phonemes = word.phonemes
        phonemes_list = []
        for phoneme in phonemes:
            phonemes_list.append(
                {
                    "phoneme": phoneme.phoneme,
                    "accuracy_score": phoneme.accuracy_score
                }
            )

        result_words.append(
            {
                "word": word.word,
                "accuracy_score": word.accuracy_score,
                "error_type": word.error_type,
                "phonemes": phonemes_list,
            }
        )
    result["words"] = result_words
    return result


# 语音转文字
def speech_translate_text(speech_path: str, language: str) -> str:
    # languages = ["zh-CN", "en-US"]
    languages = []
    # 如果languages已经包含了language，就不需要再添加了,不包含需要添加，并且放在第一位
    if language not in languages:
        languages.insert(0, language)
    auto_detect_source_language_config = (
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=languages)
    )
    audio_config = speechsdk.audio.AudioConfig(filename=speech_path)

    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config,
    )
    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print(
            "No speech could be recognized: {}".format(
                speech_recognition_result.no_match_details
            )
        )
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")


# 获取支持的语音列表，组装成对象数组进行返回
def get_voice_list():
    """通过synthesizer.getVoicesAsync()方法来获取所有支持的语音列表"""
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    voice_list = speech_synthesizer.get_voices_async().get()
    # 迭代list，组装成对象数组进行返回
    voice_vo_list = []
    for voice in voice_list.voices:
        voice_vo_list.append(
            {
                "gender": voice.gender.value,
                "locale": voice.locale,
                "local_name": voice.local_name,
                "name": voice.name,
                "short_name": voice.short_name,
                "voice_type": {
                    "name": voice.voice_type.name,
                    "value": voice.voice_type.value,
                },
                "style_list": voice.style_list,
            }
        )
    return voice_vo_list
