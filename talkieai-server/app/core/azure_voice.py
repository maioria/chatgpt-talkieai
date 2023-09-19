import json

import azure.cognitiveservices.speech as speechsdk

from app.config import Config
from pydub import AudioSegment
import os
key = Config.AZURE_KEY
region = "eastasia"

speech_config = speechsdk.SpeechConfig(subscription=key, region=region)


def speech(content: str, output_path_str: str, voice_name: str = "en-US-JennyNeural"):
    """文本转语音"""
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path_str)
    speech_config.speech_synthesis_voice_name = voice_name
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )
    speech_synthesizer.get_voices_async().get()
    speech_synthesis_result = speech_synthesizer.speak_text_async(content).get()

    if (
        speech_synthesis_result.reason
        == speechsdk.ResultReason.SynthesizingAudioCompleted
    ):
        print("Speech synthesized for text [{}]".format(content))
    else:
        print("Speech synthesis failed: {}".format(speech_synthesis_result.reason))
        if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print(
                        "Error details: {}".format(cancellation_details.error_details)
                    )
                    print("Did you set the speech resource key and region values?")
        raise Exception("语音合成失败")


def speech_by_ssml(
    content: str,
    output_path_str: str,
    voice_name: str = "en-US-JennyNeural",
    speech_rate: str = "1.0",
    feel: str = "neutral",
    targetLang: str = "en-US",
):
    """可定制的文本转语音"""
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path_str)
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )
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
    speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()

    if (
        speech_synthesis_result.reason
        == speechsdk.ResultReason.SynthesizingAudioCompleted
    ):
        print("Speech synthesized for text [{}]".format(content))
    else:
        if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print(
                        "Error details: {}".format(cancellation_details.error_details)
                    )
                    print("Did you set the speech resource key and region values?")
        raise Exception("语音合成失败")


def speech_pronunciation(content: str, speech_path: str, language: str = "en-US"):
    """ 发音评估 """
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


# 压缩音频文件(如mp3)的语音转文字
def speech_translate_text_compress(speech_path: str, language: str) -> str:
    languages = ["zh-CN", "en-US"]
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
    done = False

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print("CLOSING on {}".format(evt))
        nonlocal done
        done = True

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognizing.connect(
        lambda evt: print("RECOGNIZING: {}".format(evt))
    )
    speech_recognizer.recognized.connect(
        lambda evt: print("RECOGNIZED: {}".format(evt))
    )
    speech_recognizer.session_started.connect(
        lambda evt: print("SESSION STARTED: {}".format(evt))
    )
    speech_recognizer.session_stopped.connect(
        lambda evt: print("SESSION STOPPED {}".format(evt))
    )
    speech_recognizer.canceled.connect(lambda evt: print("CANCELED {}".format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(0.5)

    speech_recognizer.stop_continuous_recognition()


# 语音转文字
def speech_translate_text(speech_path: str, language: str) -> str:
    languages = ["zh-CN", "en-US"]
    # 如果languages已经包含了language，就不需要再添加了,不包含需要添加，并且放在第一位
    if language not in languages:
        languages.insert(0, language)
    auto_detect_source_language_config = (
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=languages)
    )
    # 判断speech_path是不是.mp3结尾，如果是则使用mp3_file_path
    if speech_path.endswith(".mp3"):
        # mp3转wav
        wav_file_path = speech_path.replace(".mp3", ".wav")
        mp3_to_wav(speech_path, wav_file_path)
        audio_config = speechsdk.audio.AudioConfig(filename=wav_file_path)
    else:
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


class BinaryFileReaderCallback(speechsdk.audio.PullAudioInputStreamCallback):
    def __init__(self, filename: str):
        super().__init__()
        self._file_h = open(filename, "rb")

    def read(self, buffer: memoryview) -> int:
        print("trying to read {} frames".format(buffer.nbytes))
        try:
            size = buffer.nbytes
            frames = self._file_h.read(size)

            buffer[: len(frames)] = frames
            print("read {} frames".format(len(frames)))

            return len(frames)
        except Exception as ex:
            print("Exception in `read`: {}".format(ex))
            raise

    def close(self) -> None:
        print("closing file")
        try:
            self._file_h.close()
        except Exception as ex:
            print("Exception in `close`: {}".format(ex))
            raise


def compressed_stream_helper(compressed_format, mp3_file_path):
    callback = BinaryFileReaderCallback(mp3_file_path)
    stream = speechsdk.audio.PullAudioInputStream(
        stream_format=compressed_format, pull_stream_callback=callback
    )

    audio_config = speechsdk.audio.AudioConfig(stream=stream)

    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )

    done = False

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print("CLOSING on {}".format(evt))
        nonlocal done
        done = True

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognizing.connect(
        lambda evt: print("RECOGNIZING: {}".format(evt))
    )
    speech_recognizer.recognized.connect(
        lambda evt: print("RECOGNIZED: {}".format(evt))
    )
    speech_recognizer.session_started.connect(
        lambda evt: print("SESSION STARTED: {}".format(evt))
    )
    speech_recognizer.session_stopped.connect(
        lambda evt: print("SESSION STOPPED {}".format(evt))
    )
    speech_recognizer.canceled.connect(lambda evt: print("CANCELED {}".format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(0.5)

    speech_recognizer.stop_continuous_recognition()


def pull_audio_input_stream_compressed_mp3(mp3_file_path: str):
    # Create a compressed format
    compressed_format = speechsdk.audio.AudioStreamFormat(
        compressed_stream_format=speechsdk.AudioStreamContainerFormat.MP3
    )
    compressed_stream_helper(compressed_format, mp3_file_path)

def mp3_to_wav(input_path, output_path):
    sound = AudioSegment.from_mp3(input_path)
    sound.export(output_path, format="wav")