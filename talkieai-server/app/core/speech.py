from abc import ABC, abstractmethod

import azure.cognitiveservices.speech as speechsdk

"""语音处理类，主要为语音转换，语音合成"""
class SpeechComponent(ABC):
    @abstractmethod
    def speech(self, content: str, output_path_str: str,
                   voice_name: str = None,
                   speech_rate: str = None,
                   feel: str = None,
                   targetLang: str = None):
        """语音合成"""
        pass

    @abstractmethod
    async def translate_text(self, speech_path: str, language: str):
        """语音转文字"""
        pass

    @abstractmethod
    async def get_voice_list(self):
        """获取语音列表"""
        pass

class AzureSpeechComponent(SpeechComponent):
    def __init__(self, key:str, region:str):
        self.speech_config = speechsdk.SpeechConfig(subscription=key, region=region)

    def speech(self, content: str, output_path_str: str,
                       voice_name: str = 'en-US-JennyNeural',
                       speech_rate: str = '1.0',
                       feel: str = 'neutral',
                       targetLang: str = 'en-US'):
        """文字转语音，可配置角色与语气，语速"""
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path_str)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_config)
        ssml = f'''
        <speak version="1.0"  xmlns:mstts="https://www.w3.org/2001/mstts" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="{targetLang}">
          <voice name="{voice_name}">
            <prosody rate="{speech_rate}">
              <mstts:express-as style="{feel}" styledegree="1.5">
                {content}
              </mstts:express-as>
            </prosody>
          </voice>
        </speak>
        '''
        speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(content))
        else:
            if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_synthesis_result.cancellation_details
                print("Speech synthesis canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    if cancellation_details.error_details:
                        print("Error details: {}".format(cancellation_details.error_details))
                        print("Did you set the speech resource key and region values?")
            raise Exception('语音合成失败')

    def translate_text(self, speech_path: str, language: str) -> str:
        """语音转文字"""
        languages = ["en-US", "zh-CN"]
        # 如果languages已经包含了language，就不需要再添加了,不包含需要添加，并且放在第一位
        if language not in languages:
            languages.insert(0, language)
        auto_detect_source_language_config = \
            speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=languages)
        audio_config = speechsdk.audio.AudioConfig(filename=speech_path)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config,
                                                       auto_detect_source_language_config=auto_detect_source_language_config,
                                                       audio_config=audio_config)
        speech_recognition_result = speech_recognizer.recognize_once_async().get()
        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(speech_recognition_result.text))
            return speech_recognition_result.text
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

    def get_voice_list(self):
        """通过synthesizer.getVoicesAsync()方法来获取所有支持的语音列表，内容太多，单猲配置在前端"""
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
        voice_list = speech_synthesizer.get_voices_async().get()
        # 迭代list，组装成对象数组进行返回
        voice_vo_list = []
        for voice in voice_list.voices:
            voice_vo_list.append(
                {'gender': voice.gender.value,
                 'locale': voice.locale,
                 'local_name': voice.local_name,
                 'name': voice.name,
                 'short_name': voice.short_name,
                 'voice_type': {'name': voice.voice_type.name, 'value': voice.voice_type.value},
                 'style_list': voice.style_list
                 })
        return voice_vo_list